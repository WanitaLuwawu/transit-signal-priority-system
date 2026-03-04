import turtle

class Bus:
    def __init__(self, screen, controller, map, lane="R", path=None, is_late=False, delay=0, color="blue"):
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
        self.step = self.go_speed

        # Stopline tracking
        self.current_leg_index = 0
        self.current_stop_index = 0

        # Priority
        self.is_late = is_late
        self.active = delay == 0
        self.delay = delay
        self.priority_requested = False

        # Zones
        self.slow_zone = 60
        self.stop_zone = 20

        g = map.grid[lane]
        self.chassis = self.new_bus(path or [g[7], g[9], g[3], g[1]], color)
        self.approaches = self.infer_approaches()

        self.color = color

    def new_bus(self, path, color):
        bus = turtle.Turtle()
        bus.hideturtle()
        bus.shape("square")
        bus.shapesize(stretch_wid=0.6, stretch_len=1.2)
        bus.color(color)
        bus.penup()
        bus.path = path
        bus.goto(bus.path[0])
        bus.target_index = 1
        bus.setheading(0)
        bus.showturtle()
        return bus

    def infer_approaches(self):
        path = self.chassis.path
        approaches = []

        for i in range(len(path)):
            x1, y1 = path[i]
            x2, y2 = path[(i + 1) % len(path)]

            horizontal = y1 == y2

            leg_stops = []
            for key, t in self.stoplines.items():
                sx, sy = t.xcor(), t.ycor()
                sw, sh = t.shapesize()[1], t.shapesize()[0]

                if horizontal:
                    if abs(sy - y1) < 20 and min(x1, x2) < sx < max(x1, x2) and sh > sw:
                        leg_stops.append((abs(sx - x1), key))
                else:
                    if abs(sx - x1) < 20 and min(y1, y2) < sy < max(y1, y2) and sw > sh:
                        leg_stops.append((abs(sy - y1), key))

            leg_stops.sort(key=lambda s: s[0])

            filtered = [(d, key) for d, key in leg_stops if d > self.rw]

            dx = x2 - x1
            dy = y2 - y1

            chosen = []

            for _, key in filtered:
                if horizontal:
                    if dx > 0 and (key.endswith("_L") or key.endswith("_C") or key == "EB"):
                        chosen.append(key)
                    elif dx < 0 and (key.endswith("_R") or key.endswith("_C") or key == "WB"):
                        chosen.append(key)
                else:
                    if dy > 0 and (key.endswith("_B") or key.endswith("_C") or key == "NB"):
                        chosen.append(key)
                    elif dy < 0 and (key.endswith("_T") or key.endswith("_C") or key == "SB"):
                        chosen.append(key)

            approaches.append(chosen)

        return approaches

    def stop_point_for(self, key):
        t = self.stoplines[key]
        return t.xcor(), t.ycor()

    def current_approach(self):
        leg = self.approaches[self.current_leg_index]
        return leg[self.current_stop_index] if leg else None

    def dist_remaining(self, tx, ty, x, y, sx, sy):
        if abs(tx - x) >= self.go_speed:
            return (sx - x) * (1 if tx > x else -1)
        else:
            return (sy - y) * (1 if ty > y else -1)

    def decide_speed(self, colour, dist):
        if dist <= 0:
            return self.go_speed
        elif colour == "red" and dist <= self.stop_zone:
            return 0
        elif colour in ("red", "yellow") and dist <= self.slow_zone:
            return self.slow_speed
        else:
            return self.go_speed

    def advance_stopline(self, approach, dist, leg):
        if approach and dist < 0:
            if self.current_stop_index < len(leg) - 1:
                self.current_stop_index += 1

    def request_priority(self, approach, dist):
        if self.is_late and not self.priority_requested and 0 < dist < 120:
            if approach and self.controller.request_priority(approach):
                self.priority_requested = True

    def move(self):
        if not self.active:
            self.delay -= 20
            if self.delay <= 0:
                self.active = True
            return

        bus = self.chassis
        tx, ty = bus.path[bus.target_index]
        x, y = bus.position()

        leg = self.approaches[self.current_leg_index]
        approach = self.current_approach()

        if approach:
            colour = self.controller.get_colour(approach)
            sx, sy = self.stop_point_for(approach)
        else:
            colour = "green"
            sx, sy = tx, ty

        dist = self.dist_remaining(tx, ty, x, y, sx, sy)
        self.step = self.decide_speed(colour, dist)
        self.advance_stopline(approach, dist, leg)
        self.request_priority(approach, dist)

        dx = tx - x
        dy = ty - y

        dist_to_target = (dx ** 2 + dy ** 2) ** 0.5

        if dist_to_target < self.go_speed:
            bus.goto(tx, ty)
            bus.target_index = (bus.target_index + 1) % len(bus.path)
            self.current_leg_index = (self.current_leg_index + 1) % len(self.approaches)
            self.current_stop_index = 0
            self.priority_requested = False
            return

        if abs(dx) >= self.go_speed:
            bus.setheading(0 if dx > 0 else 180)
        else:
            bus.setheading(90 if dy > 0 else 270)

        bus.forward(self.step)