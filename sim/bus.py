import turtle

class Bus:
    def __init__(self, screen, controller, map, lane="R", path=None, is_late=False, delay=0, color="blue"):
        self.screen = screen
        self.controller = controller

        # World Geometry
        self.w = map.world                                # half-size of world
        self.m = map.inner_margin                         # map edge
        self.rw = map.road_width                          # road width
        self.h = map.rw / 2                               # width of one lane = 0.5 * road_width
        self.inner = self.m - self.rw                     # "concrete" block edge
        self.ring_mid = self.inner + self.h               # centre lane of ring road
        self.ring_outer_lane = self.ring_mid + self.h / 2 # outer lane of ring road (lane on map edge)
        self.ring_inner_lane = self.ring_mid - self.h / 2 # inner lane of ring road (lane on city block edge)

        # Stoplines
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
        self.delay = delay              # lateness is simulated by "delay"
        self.active = delay == 0        # the bus starts moving when delay == 0
        self.priority_requested = False

        # Zones
        self.slow_zone = 60 # distance from the stopline at which te bus begins to slow
        self.stop_zone = 20 # distance from the stopline at which the bus stops

        # Map nodes for the specified lane
        g = map.grid[lane] # the grid is as follows:
                           # 1-2-3
                           # | | |
                           # 4-5-6
                           # | | |
                           # 7-8-9

        # Bus Turtle shown on Screen
        raw_path = path or [g[7], g[9], g[3], g[1]]
        closed_path = self.close_loop(raw_path, g)
        self.chassis = self.new_bus(closed_path, color)

        # Approaches/Stoplines on the defined path
        self.approaches = self.infer_approaches()

        self.distance_travelled = 0

    def new_bus(self, path, color):
        bus = turtle.Turtle()                           # bus chassis
        bus.hideturtle()
        bus.shape("square")
        bus.shapesize(stretch_wid=0.6, stretch_len=1.2) # default turtle square is 20x20
        bus.color(color)                                # bus color
        bus.penup()
        bus.path = path                                 # bus path
        bus.goto(bus.path[0])                           # go to starting node (first node on path)
        bus.target_index = 1                            # the first target node is the second node on the path
        bus.showturtle()
        return bus

    def close_loop(self, path, grid):
        # ring road nodes in clockwise order
        ring = [grid[1], grid[2], grid[3], grid[6], grid[9], grid[8], grid[7], grid[4]]
        n = len(ring)

        # find the first and last ring nodes in the path
        first_ring_node = next((p for p in path if p in ring), None)
        last_ring_node = next((p for p in reversed(path) if p in ring), None)

        # can't close the loop if no ring nodes are found
        if last_ring_node is None or first_ring_node is None:
            return path
        # already closed if the path starts and ends on the same ring node
        if last_ring_node == first_ring_node:
            return path

        # index of the last ring node in the ring (return journey starts here)
        si = ring.index(last_ring_node)
        # index of the first ring node in the ring (return journey ends here)
        ei = ring.index(first_ring_node)

        # extract only the ring nodes from the path, preserving order
        ring_nodes_in_path = [p for p in path if p in ring]

        # vote on direction by checking each consecutive ring node pair
        cw_votes = 0
        ccw_votes = 0
        for i in range(len(ring_nodes_in_path) - 1):
            i1 = ring.index(ring_nodes_in_path[i])      # ring index of current node
            i2 = ring.index(ring_nodes_in_path[i + 1])  # ring index of next node
            cw_steps = (i2 - i1) % n  # steps needed to reach i2 going clockwise
            ccw_steps = (i1 - i2) % n # steps needed to reach i2 going counter-clockwise
            if cw_steps <= ccw_steps:
                cw_votes += 1  # this pair suggests clockwise travel
            else:
                ccw_votes += 1 # this pair suggests counter-clockwise travel

        # the majority vote determines the overall direction
        going_cw = cw_votes >= ccw_votes

        # build the return leg indices by stepping from si in the inferred direction
        if going_cw:
            indices = [(si + i) % n for i in range(1, n)] # step forward through ring
        else:
            indices = [(si - i) % n for i in range(1, n)] # step backward through ring

        # convert indices back to coordinates
        route = [ring[i] for i in indices]
        if first_ring_node in route:
            return_leg = route[:route.index(first_ring_node)]
            return path + return_leg

        return path # return original path if something went wrong

    def infer_approaches(self):
        path = self.chassis.path               # bus path
        approaches = []                        # empty list of approaches

        for i in range(len(path)):             # for each node/path segment...
            x1, y1 = path[i]                   # coordinates of the current node
            x2, y2 = path[(i + 1) % len(path)] # coordinates of the next node
                                               # modulo allows the path to wrap around (closed loop route)

            horizontal = y1 == y2              # bus heading

            leg_stops = []                     # temporary list of stoplines found along this path segment

            for key, t in self.stoplines.items():           # for each stopline...
                sx, sy = t.xcor(), t.ycor()                 # stopline positions
                sw, sh = t.shapesize()[1], t.shapesize()[0] # stopline dimensions

                if horizontal:
                    # conditions for a stop-line belonging to this path segment:
                    # 1. stopline is close to the road (same Y level)
                    # 2. stopline lies between two path nodes
                    # 3. stopline is vertically oriented (taller than wide)
                    if abs(sy - y1) < 20 and min(x1, x2) < sx < max(x1, x2) and sh > sw:
                        leg_stops.append((abs(sx - x1), key)) # Store distance from start node
                else:
                    # conditions for a stop-line belonging to this path segment:
                    # 1. stopline is close to the road (same X level)
                    # 2. stopline lies between two path nodes
                    # 3. stopline is horizontally oriented (wider than tall)
                    if abs(sx - x1) < 20 and min(y1, y2) < sy < max(y1, y2) and sw > sh:
                        leg_stops.append((abs(sy - y1), key)) # Store distance from start node

            # sort stoplines along the path segment by distance
            leg_stops.sort(key=lambda s: s[0])

            # remove stoplines that are less than one road_width from the node
            # effectively removes stoplines/approaches to the central node for the default path around ring road
            filtered = [(d, key) for d, key in leg_stops if d > self.rw]

            # direction of the path segment
            dx = x2 - x1
            dy = y2 - y1

            # list of stoplines relevant to the bus direction
            chosen = []

            for _, key in filtered:
                if horizontal:
                    # bus travelling east
                    if dx > 0 and (key.endswith("_L") or key.endswith("_C") or key == "EB"):
                        chosen.append(key)

                    # bus travelling west
                    elif dx < 0 and (key.endswith("_R") or key.endswith("_C") or key == "WB"):
                        chosen.append(key)
                else:
                    # bus travelling north
                    if dy > 0 and (key.endswith("_B") or key.endswith("_C") or key == "NB"):
                        chosen.append(key)

                    # bus travelling south
                    elif dy < 0 and (key.endswith("_T") or key.endswith("_C") or key == "SB"):
                        chosen.append(key)

            # store the approaches associated with this path segment
            approaches.append(chosen)

        # return list of approaches for the full route
        return approaches

    # return stopline coordinates
    def stop_point_for(self, key):
        t = self.stoplines[key]
        return t.xcor(), t.ycor()

    # return current stopline on approach
    def current_approach(self):
        leg = self.approaches[self.current_leg_index]
        return leg[self.current_stop_index] if leg else None

    # return distance to stopline or target node
    def dist_remaining(self, tx, ty, x, y, sx, sy):
        if abs(tx - x) >= self.go_speed:
            # return horizontal distance if bus heading is horizontal
            return (sx - x) * (1 if tx > x else -1)
        else:
            # return vertical distance if bus heading is vertical
            return (sy - y) * (1 if ty > y else -1)

    # return bus speed
    def decide_speed(self, color, dist):
        # if already on stopline, clear the intersection
        if dist <= 0:
            return self.go_speed

        # if within stop_zone and stopline is red or yellow, stop
        elif color in ("red", "yellow") and dist <= self.stop_zone:
            return 0

        # if within slow_zone and stopline is red or yellow, slow down
        elif color in ("red", "yellow") and dist <= self.slow_zone:
            return self.slow_speed

        # if green, go
        else:
            return self.go_speed

    # ignore current stopline once cleared
    def advance_stopline(self, approach, dist, leg):
        if approach and dist < 0:                      # if the current stopline has been cleared
            if self.current_stop_index < len(leg) - 1: # and there are more path segments to cover
                self.current_stop_index += 1           # advance to the next stopline

    def request_priority(self, approach, dist):
        # conditions to request priority:
        # 1. bus is late
        # 2. bus has not already requested priority on this path segment
        # 3. bus is within the request zone
        if self.is_late and not self.priority_requested and self.stop_zone < dist < 100:
            if approach and self.controller.request_priority(approach):
                self.priority_requested = True

    def move(self):
        # Count down to start
        if not self.active:
            self.delay -= 20        # lateness is simulated by "delay"
            if self.delay <= 0:     # the bus starts moving when delay == 0
                self.active = True
            return

        bus = self.chassis          # bus Turtle

        tx, ty = bus.path[bus.target_index] # current target node
        x, y = bus.position()               # current bus position

        leg = self.approaches[self.current_leg_index] # list of stoplines associated with this path segment
        approach = self.current_approach()            # current stopline on approach

        if approach:                                    # if there is a stopline on the current approach...
            color = self.controller.get_color(approach) # get its color and position
            sx, sy = self.stop_point_for(approach)
        else:                                         # if there is no stopline on the current approach...
            color = "green"                           # behave as though there is a green stoplight (go)
            sx, sy = tx, ty                           # the target node becomes the stop point

        dist = self.dist_remaining(tx, ty, x, y, sx, sy) # distance to stopline or target node
        self.step = self.decide_speed(color, dist)
        self.advance_stopline(approach, dist, leg)       # advance to next stopline once current one is cleared
        self.request_priority(approach, dist)            # request priority if conditions are met

        # Distance to target node
        dx = tx - x
        dy = ty - y

        dist_to_target = (dx ** 2 + dy ** 2) ** 0.5

        if dist_to_target < self.go_speed:                                               # if near the target node...
            bus.goto(tx, ty)                                                             # snap to fit
            bus.target_index = (bus.target_index + 1) % len(bus.path)                    # advance to next node
            self.current_leg_index = (self.current_leg_index + 1) % len(self.approaches) # advance to next path segment
            self.current_stop_index = 0                                                  # first stopline on new segment
            self.priority_requested = False                                              # reset priority request for new segment
            return

        # set the travel direction
        if abs(dx) >= self.go_speed:
            bus.setheading(0 if dx > 0 else 180)  # east or west
        else:
            bus.setheading(90 if dy > 0 else 270) # north or south

        # advance the bus
        self.distance_travelled += self.step
        bus.forward(self.step)

    def reset(self):
        self.active = False
        self.chassis.hideturtle()
        self.chassis.goto(self.chassis.path[0])
        self.chassis.target_index = 1
        self.current_leg_index = 0
        self.current_stop_index = 0
        self.priority_requested = False
        self.chassis.showturtle()