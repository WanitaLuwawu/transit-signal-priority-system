import turtle


class Map:
    def __init__(self, screen):
        self.screen = screen

        # Geometry constants
        self.world = 300  # half-size of world
        self.road_width = 60
        self.inner_margin = self.world
        self.stop_setback = 12
        self.stop_thickness = 6

        # Colors
        self.concrete = "#808588"
        self.road = "black"
        self.lane = "white"
        self.stop_line = "red"

        # Cartographer Turtle
        self.cartographer = turtle.Turtle(visible=False)
        self.cartographer.speed(0)
        self.cartographer.penup()

        self.stoplines = {}

        # Derived geometry (used by Bus)
        self.m = self.inner_margin
        self.rw = self.road_width
        self.h = self.rw / 2
        self.inner = self.m - self.rw
        self.ring_mid = self.inner + self.h

        rol = self.ring_mid + self.h / 2  # ring_outer_lane
        ril = self.ring_mid - self.h / 2  # ring_inner_lane
        lo = self.h / 2  # lane offset for central roads = 15

        self.grid = {
            "R": {1: (-rol, rol),
                  2: (lo, rol),
                  3: (rol, rol),
                  4: (-rol, -lo),
                  5: (lo, -lo),
                  6: (rol, -lo),
                  7: (-rol, -rol),
                  8: (lo, -rol),
                  9: (rol, -rol),
                  },
            "L": {1: (-ril, ril),
                  2: (-lo, ril),
                  3: (ril, ril),
                  4: (-ril, lo),
                  5: (-lo, lo),
                  6: (ril, lo),
                  7: (-ril, -ril),
                  8: (-lo, -ril),
                  9: (ril, -ril),
                  }
        }

        # Lane centers
        self.ring_lane_offset = 15
        self.central_lane_offset = 15

    def draw_rect(self, x1, y1, x2, y2, color):
        t = self.cartographer
        t.goto(x1, y1)
        t.setheading(0)
        t.color(color)
        t.begin_fill()
        t.pendown()

        t.goto(x2, y1)
        t.goto(x2, y2)
        t.goto(x1, y2)
        t.goto(x1, y1)

        t.end_fill()
        t.penup()

    def draw(self):
        w = self.world
        rw = self.road_width
        m = self.inner_margin

        # concrete background
        self.draw_rect(-w, -w, w, w, self.concrete)

        # Outer ring road "donut"
        self.draw_rect(-w, -w, w, w, self.road)
        self.draw_rect(-(w - rw), -(w - rw), (w - rw), (w - rw), self.concrete)

        # Central vertical road
        self.draw_rect(-rw / 2, -m, rw / 2, m, self.road)

        # Central horizontal road
        self.draw_rect(-m, -rw / 2, m, rw / 2, self.road)

        self.draw_central_stop_lines()
        self.draw_ring_stop_lines()
        self.draw_central_lane_dividers()
        self.draw_ring_lane_dividers()

    def new_stopline(self, x, y, w, h, color):
        t = turtle.Turtle()
        t.hideturtle()
        t.penup()
        t.shape("square")
        t.shapesize(stretch_wid=h / 20, stretch_len=w / 20)  # turtle square is 20x20
        t.fillcolor(color)
        t.speed(0)
        t.goto(x, y)
        t.showturtle()
        return t

    def draw_central_stop_lines(self):
        rw = self.road_width
        h = rw / 2
        s = self.stop_setback
        t = self.stop_thickness

        # NB stop line (northbound approaching center)
        y = -(h + s + t / 2)
        self.stoplines["NB"] = self.new_stopline(0, y, rw, t, "red")

        # SB stop line
        y = (h + s + t / 2)
        self.stoplines["SB"] = self.new_stopline(0, y, rw, t, "red")

        # WB stop line
        x = (h + s + t / 2)
        self.stoplines["WB"] = self.new_stopline(x, 0, t, rw, "red")

        # EB stop line
        x = -(h + s + t / 2)
        self.stoplines["EB"] = self.new_stopline(x, 0, t, rw, "red")

    def draw_ring_stop_lines(self):
        rw = self.road_width
        m = self.inner_margin

        d = self.stop_setback
        t = self.stop_thickness

        h = rw / 2
        inner = m - rw

        ring_height = (m - inner)  # thickness of the ring road band

        # North ring stoplines
        self.stoplines["RN_L"] = self.new_stopline(
            x=-(h + d) - t / 2,
            y=(inner + m) / 2,
            w=t,
            h=ring_height,
            color="red"
        )

        self.stoplines["RN_R"] = self.new_stopline(
            x=(h + d) + t / 2,
            y=(inner + m) / 2,
            w=t,
            h=ring_height,
            color="red"
        )

        self.stoplines["RN_C"] = self.new_stopline(
            x=0,
            y=inner - d - t / 2,
            w=rw,
            h=t,
            color="red"
        )

        # East ring stoplines
        self.stoplines["RE_T"] = self.new_stopline(
            x=(inner + m) / 2,
            y=(h + d) + t / 2,
            w=ring_height,
            h=t,
            color="red"
        )

        self.stoplines["RE_B"] = self.new_stopline(
            x=(inner + m) / 2,
            y=-(h + d) - t / 2,
            w=ring_height,
            h=t,
            color="red"
        )

        self.stoplines["RE_C"] = self.new_stopline(
            x=inner - d - t / 2,
            y=0,
            w=t,
            h=rw,
            color="red"
        )

        # South ring stoplines
        self.stoplines["RS_L"] = self.new_stopline(
            x=-(h + d) - t / 2,
            y=-(inner + m) / 2,
            w=t,
            h=ring_height,
            color="red"
        )

        self.stoplines["RS_R"] = self.new_stopline(
            x=(h + d) + t / 2,
            y=-(inner + m) / 2,
            w=t,
            h=ring_height,
            color="red"
        )

        self.stoplines["RS_C"] = self.new_stopline(
            x=0,
            y=-inner + d + t / 2,
            w=rw,
            h=t,
            color="red"
        )

        # West ring stoplines
        self.stoplines["RW_T"] = self.new_stopline(
            x=-(inner + m) / 2,
            y=(h + d) + t / 2,
            w=ring_height,
            h=t,
            color="red"
        )

        self.stoplines["RW_B"] = self.new_stopline(
            x=-(inner + m) / 2,
            y=-(h + d) - t / 2,
            w=ring_height,
            h=t,
            color="red"
        )

        self.stoplines["RW_C"] = self.new_stopline(
            x=-inner + d + t / 2,
            y=0,
            w=t,
            h=rw,
            color="red"
        )

    def draw_line(self, x1, y1, x2, y2, color, width=2):
        t = self.cartographer
        t.color(color)
        t.width(width)
        t.penup()
        t.goto(x1, y1)
        t.pendown()
        t.goto(x2, y2)
        t.penup()

    def draw_dashed_line(self, x1, y1, x2, y2, color, width=2, dash=12, gap=10):
        t = self.cartographer
        t.color(color)
        t.width(width)

        dx = x2 - x1
        dy = y2 - y1
        dist = (dx ** 2 + dy ** 2) ** 0.5
        if dist == 0:
            return

        ux = dx / dist
        uy = dy / dist

        step = dash + gap
        n = int(dist // step)

        for i in range(n + 1):
            start = i * step
            end = min(start + dash, dist)

            sx = x1 + ux * start
            sy = y1 + uy * start
            ex = x1 + ux * end
            ey = y1 + uy * end

            t.penup()
            t.goto(sx, sy)
            t.pendown()
            t.goto(ex, ey)

        t.penup()

    def draw_central_lane_dividers(self):
        rw = self.road_width
        m = self.inner_margin
        h = rw / 2

        d = self.stop_setback
        t = self.stop_thickness

        iw = rw + d + t
        hiw = h + d + t

        self.draw_dashed_line(0, -m + iw, 0, -hiw, self.lane, width=2)
        self.draw_dashed_line(0, hiw, 0, m - iw, self.lane, width=2)

        self.draw_dashed_line(-m + iw, 0, -hiw, 0, self.lane, width=2)
        self.draw_dashed_line(hiw, 0, m - iw, 0, self.lane, width=2)

    def draw_ring_lane_dividers(self):
        rw = self.road_width
        m = self.inner_margin
        h = rw / 2

        d = self.stop_setback
        t = self.stop_thickness

        iw = rw + d + t
        hiw = h + d + t

        inner = m - rw
        ring_mid = inner + h

        self.draw_dashed_line(-ring_mid, ring_mid, -hiw, ring_mid, self.lane, width=2)
        self.draw_dashed_line(hiw, ring_mid, ring_mid, ring_mid, self.lane, width=2)

        self.draw_dashed_line(-ring_mid, -ring_mid, -hiw, -ring_mid, self.lane, width=2)
        self.draw_dashed_line(hiw, -ring_mid, ring_mid, -ring_mid, self.lane, width=2)

        self.draw_dashed_line(ring_mid, -ring_mid, ring_mid, -hiw, self.lane, width=2)
        self.draw_dashed_line(ring_mid, hiw, ring_mid, ring_mid, self.lane, width=2)

        self.draw_dashed_line(-ring_mid, ring_mid, -ring_mid, hiw, self.lane, width=2)
        self.draw_dashed_line( -ring_mid, -hiw, -ring_mid, -ring_mid, self.lane, width=2)

