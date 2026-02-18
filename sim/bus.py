import turtle

class Bus:
    def __init__(self, screen, controller, map):
        self.screen = screen
        self.controller = controller

        # World Geometry
        self.w = map.world
        self.m = map.inner_margin
        self.rw = map.road_width
        self.h = map.rw / 2
        self.inner = self.m - self.rw
        self.ring_mid = self.inner + self.h
        self.ring_outer_lane = self.ring_mid + self.h / 2
        self.ring_inner_lane = self.ring_mid - self.h / 2

        self.stoplines = map.stoplines

        # Driving speeds
        self.go_speed = 4
        self.slow_speed = 1.5
        self.stop_speed = 0
        self.step = self.go_speed

        # Stopline approach order for each corner (outer ring)
        self.approaches = ["RN_S", "RE_S", "RS_S", "RW_S"]
        self.current_approach_index = 0
        self.is_late = False
        self.priority_requested = False

        self.chassis = self.new_bus()

    def new_bus(self):
        bus = turtle.Turtle()
        bus.hideturtle()
        bus.shape("square")
        bus.shapesize(stretch_wid=0.6, stretch_len=1.2)
        bus.color("blue")
        bus.penup()

        bus.path = [
            (-self.ring_outer_lane, -self.ring_outer_lane),
            (self.ring_outer_lane, -self.ring_outer_lane),
            (self.ring_outer_lane, self.ring_outer_lane),
            (-self.ring_outer_lane, self.ring_outer_lane)
        ]
        bus.goto(bus.path[0])
        bus.target_index = 1
        bus.setheading(0)  # heading toward path[1]
        bus.showturtle()
        return bus

    def stop_point_for(self, key):
        t = self.stoplines[key]
        return t.xcor(), t.ycor()

    def move(self):
        bus = self.chassis
        tx, ty = bus.path[bus.target_index]
        x, y = bus.position()

        # --- Stopline logic ---
        approach = self.approaches[self.current_approach_index]
        colour = self.controller.get_colour(approach)
        sx, sy = self.stop_point_for(approach)

        # Determine which axis the bus is moving along
        if abs(tx - x) >= self.go_speed:
            # moving horizontally
            dist_to_stop = sx - x
            direction = 1 if tx > x else -1
        else:
            # moving vertically
            dist_to_stop = sy - y
            direction = 1 if ty > y else -1

        # --- Zones ---
        slow_zone = 100 # start slowing in yellow
        stop_zone = 60 # stop in red/yellow, buffer for step size

        # distance remaining along axis
        dist_remaining = dist_to_stop * direction

        # --- Decide speed ---
        if colour in ("red") and dist_remaining <= stop_zone and dist_remaining > 0:
            self.step = 0  # STOP immediately if we would enter stop zone
        elif colour in ("red", "yellow") and dist_remaining > stop_zone and dist_remaining <= slow_zone:
            self.step = self.slow_speed  # SLOW gradually
        else:
            self.step = self.go_speed  # GO

        # Priority request if bus is late
        request_zone = 120
        if self.is_late and not self.priority_requested and 0 < dist_to_stop * direction < request_zone:
            if self.controller.request_priority(approach):
                self.priority_requested = True

        # --- Movement along square path ---
        dx = tx - x
        dy = ty - y

        # reached target corner?
        if abs(dx) < self.go_speed and abs(dy) < self.go_speed:
            bus.goto(tx, ty)
            bus.target_index = (bus.target_index + 1) % len(bus.path)
            # next approach stopline
            self.current_approach_index = (self.current_approach_index + 1) % len(self.approaches)
            self.priority_requested = False
            self.screen.ontimer(self.move, 20)
            return

        # Choose heading along axis
        if abs(dx) >= self.go_speed:
            bus.setheading(0 if dx > 0 else 180)
        else:
            bus.setheading(90 if dy > 0 else 270)

        # Move (0 step = stopped)
        bus.forward(self.step)

        # Schedule next move
        self.screen.ontimer(self.move, 20)

