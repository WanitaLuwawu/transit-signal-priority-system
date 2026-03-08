import turtle


class Map:
    def __init__(self, screen):
        self.screen = screen

        # Geometry constants
        self.world = 300               # half-size of world
        self.road_width = 60           # road width
        self.inner_margin = self.world # map edge
        self.stop_setback = 12         # setback distance of stoplines from city block edge
        self.stop_thickness = 6        # thickness of stoplines

        # Colors
        self.concrete = "#808588"      # city block
        self.road = "black"            # road
        self.lane = "white"            # lane divider
        self.stop_line = "red"         # initial stopline color

        # Cartographer Turtle for drawing map details
        self.cartographer = turtle.Turtle(visible=False)
        self.cartographer.speed(0)
        self.cartographer.penup()

        # Empty list of stoplines
        self.stoplines = {}

        # Derived geometry (used by Bus)
        self.m = self.inner_margin          # map edge
        self.rw = self.road_width           # road width
        self.h = self.rw / 2                # lane width = 0.5 * road_width
        self.inner = self.m - self.rw       # city block edge
        self.ring_mid = self.inner + self.h # centre lane of ring road

        rol = self.ring_mid + self.h / 2  # ring_outer_lane
        ril = self.ring_mid - self.h / 2  # ring_inner_lane
        lo = self.h / 2  # lane offset for central roads = 15

        self.grid = {
            "R": {1: (-rol, rol), # Right lane, "R", for each node:
                  2: (lo, rol),   # 1-2-3
                  3: (rol, rol),  # | | |
                  4: (-rol, -lo), # 4-5-6
                  5: (lo, -lo),   # | | |
                  6: (rol, -lo),  # 7-8-9
                  7: (-rol, -rol),
                  8: (lo, -rol),
                  9: (rol, -rol),
                  },
            "L": {1: (-ril, ril), # Left lane, "L", for each node:
                  2: (-lo, ril),  # 1-2-3
                  3: (ril, ril),  # | | |
                  4: (-ril, lo),  # 4-5-6
                  5: (-lo, lo),   # | | |
                  6: (ril, lo),   # 7-8-9
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
        t.goto(x1, y1)        # top left corner of the rectangle
        t.setheading(0)       # face eastwards
        t.color(color)        # set fill color
        t.begin_fill()        # start marking the fill area
        t.pendown()

        t.goto(x2, y1)        # top right corner
        t.goto(x2, y2)        # bottom right corner
        t.goto(x1, y2)        # bottom left corner
        t.goto(x1, y1)        # top left corner (starting pos)

        t.end_fill()          # fill the marked area
        t.penup()

    # used to draw entire map
    def draw(self):
        w = self.world          # half-size of world
        rw = self.road_width    # road width
        m = self.inner_margin   # map edge

        # to draw ring road:
        # 1. draw a black rectangle with the same dimensions as the map
        # 2. draw a grey rectangle with each side being one road_width shorter than the map
        self.draw_rect(-w, -w, w, w, self.road)
        self.draw_rect(-(w - rw), -(w - rw), (w - rw), (w - rw), self.concrete)

        # draw the vertical road through the central node
        self.draw_rect(-rw / 2, -m, rw / 2, m, self.road)

        # draw the horizontal road through the central node
        self.draw_rect(-m, -rw / 2, m, rw / 2, self.road)

        # draw stoplines
        self.draw_central_stop_lines()
        self.draw_ring_stop_lines()

        # draw lane dividers
        self.draw_central_lane_dividers()
        self.draw_ring_lane_dividers()

    def new_stopline(self, x, y, w, h, color):
        t = turtle.Turtle()
        t.hideturtle()
        t.penup()
        t.shape("square")
        t.shapesize(stretch_wid=h / 20, stretch_len=w / 20)  # default Turtle square is 20x20
        t.fillcolor(color)                                   # initial stopline color
        t.speed(0)
        t.goto(x, y)                                         # "stamp" stopline in position
        t.showturtle()
        return t

    def draw_central_stop_lines(self):
        rw = self.road_width    # road width
        h = rw / 2              # lane width = 0.5 * road_width
        s = self.stop_setback   # setback distance of stoplines from city block edge
        t = self.stop_thickness # thickness of stoplines

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
        rw = self.road_width    # road width
        m = self.inner_margin   # map edge

        d = self.stop_setback   # setback distance of stoplines from city block edge
        t = self.stop_thickness # thickness of stoplines

        h = rw / 2              # lane width = 0.5 * road_width
        inner = m - rw          # city block edge

        ring_height = (m - inner)  # thickness of ring road band

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
        t.color(color)        # line color
        t.width(width)        # line width
        t.penup()
        t.goto(x1, y1)        # starting pos
        t.pendown()
        t.goto(x2, y2)        # end pos
        t.penup()

    def draw_dashed_line(self, x1, y1, x2, y2, color, width=2, dash=12, gap=10):
        t = self.cartographer
        t.color(color)          # dash color
        t.width(width)          # dash width

        # length of dashed line
        dx = x2 - x1
        dy = y2 - y1
        dist = (dx ** 2 + dy ** 2) ** 0.5

        # if the start and end points are the same, do not draw
        if dist == 0:
            return

        # normalize the direction so that each step moves exactly one unit
        ux = dx / dist
        uy = dy / dist

        step = dash + gap     # one step along the line is a dash and a gap
        n = int(dist // step) # number of full dash-gap patterns that fit along the line

        for i in range(n + 1):
            start = i * step              # starting distance along the line for this dash
            end = min(start + dash, dist) # ending distance of the dash cannot extend past the line

            # convert distances to coordinates
            sx = x1 + ux * start
            sy = y1 + uy * start
            ex = x1 + ux * end
            ey = y1 + uy * end

            t.penup()
            t.goto(sx, sy) # move to the starting pos of the dash
            t.pendown()
            t.goto(ex, ey) # draw the dash segment

        t.penup()

    def draw_central_lane_dividers(self):
        rw = self.road_width    # road width
        m = self.inner_margin   # map edge
        h = rw / 2              # lane width = 0.5 * road_width

        d = self.stop_setback   # setback distance of stoplines from city block edge
        t = self.stop_thickness # thickness of stoplines

        iw = rw + d + t # intersection width = road_width + stop_setback + stop_thickness
        hiw = h + d + t # half intersection width = (0.5 * road_width) + stop_setback + stop_thickness

        # vertical lane divider through nodes 8, 5, and 2
        self.draw_dashed_line(0, -m + iw, 0, -hiw, self.lane, width=2)
        self.draw_dashed_line(0, hiw, 0, m - iw, self.lane, width=2)

        # horizontal lane divider through nodes 4, 5, and 6
        self.draw_dashed_line(-m + iw, 0, -hiw, 0, self.lane, width=2)
        self.draw_dashed_line(hiw, 0, m - iw, 0, self.lane, width=2)

    def draw_ring_lane_dividers(self):
        rw = self.road_width    # road width
        m = self.inner_margin   # map edge
        h = rw / 2              # lane width = 0.5 * road_width

        d = self.stop_setback   # setback distance of stoplines from city block edge
        t = self.stop_thickness # thickness of stoplines

        iw = rw + d + t  # intersection width = road_width + stop_setback + stop_thickness
        hiw = h + d + t  # half intersection width = (0.5 * road_width) + stop_setback + stop_thickness

        inner = m - rw       # city block edge
        ring_mid = inner + h # center of ring road

        # horizontal lane divider through nodes 1, 2, and 3
        self.draw_dashed_line(-ring_mid, ring_mid, -hiw, ring_mid, self.lane, width=2)
        self.draw_dashed_line(hiw, ring_mid, ring_mid, ring_mid, self.lane, width=2)

        # horizontal lane divider through nodes 7, 8, and 9
        self.draw_dashed_line(-ring_mid, -ring_mid, -hiw, -ring_mid, self.lane, width=2)
        self.draw_dashed_line(hiw, -ring_mid, ring_mid, -ring_mid, self.lane, width=2)

        # vertical lane divider through nodes 9, 6, and 3
        self.draw_dashed_line(ring_mid, -ring_mid, ring_mid, -hiw, self.lane, width=2)
        self.draw_dashed_line(ring_mid, hiw, ring_mid, ring_mid, self.lane, width=2)

        # vertical lane divider through nodes 1, 4, and 7
        self.draw_dashed_line(-ring_mid, ring_mid, -ring_mid, hiw, self.lane, width=2)
        self.draw_dashed_line( -ring_mid, -hiw, -ring_mid, -ring_mid, self.lane, width=2)

