import turtle

class Map:
    def __init__(self, screen):
        self.screen = screen

        # Geometry constants
        self.world = 300 # half-size of world
        self.road_width = 60
        self.inner_margin = self.world

        # Colors
        self.grass = "#2e7d32"
        self.road = "black"
        self.lane = "white"
        self.stop_line = "red"
        self.stop_setback = 12
        self.stop_thickness = 6

        # Cartographer Turtle
        self.cartographer = turtle.Turtle(visible=False)
        self.cartographer.speed(0)
        self.cartographer.penup()

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

        # Grass background
        self.draw_rect(-w, -w, w, w, self.grass)

        # Outer ring road "donut"
        self.draw_rect(-w, -w, w, w, self.road)
        self.draw_rect(-(w - rw), -(w - rw), (w - rw), (w - rw), self.grass)

        # Central vertical road
        self.draw_rect(-rw/2, -m, rw/2, m, self.road)

        # Central horizontal road
        self.draw_rect(-m, -rw/2, m, rw/2, self.road)

        self.draw_central_stop_lines()
        self.draw_ring_stop_lines()
        self.draw_central_lane_dividers()
        self.draw_ring_lane_dividers()

    def draw_central_stop_lines(self):
        rw = self.road_width
        m = self.inner_margin
        
        d = self.stop_setback
        t = self.stop_thickness

        h = rw / 2
        inner = m - rw

        # Central stop lines
        y1 = -(rw/2 + d)
        self.draw_rect(-rw/2, y1, rw/2, y1 + t, self.stop_line)
        y2 = (rw/2 + d)
        self.draw_rect(-rw/2, y2 - t, rw/2, y2, self.stop_line)
        x1 = (rw/2 + d)
        self.draw_rect(x1, -rw/2, x1 + t, rw/2, self.stop_line)
        x2 = -(rw/2 + d)
        self.draw_rect(x2 - t, -rw/2, x2, rw/2, self.stop_line)

    def draw_ring_stop_lines(self):
        rw = self.road_width
        m = self.inner_margin

        d = self.stop_setback
        t = self.stop_thickness

        h = rw / 2
        inner = m - rw

        # North
        self.draw_rect(-(h + d), inner, -(h + d) - t, m, self.stop_line)
        self.draw_rect( (h + d), inner,  (h + d) + t, m, self.stop_line)
        self.draw_rect(-h, inner - d, h, inner - d - t, self.stop_line)

        # East
        self.draw_rect(inner,  (h + d), m,  (h + d) + t, self.stop_line)
        self.draw_rect(inner, -(h + d), m, -(h + d) - t, self.stop_line)
        self.draw_rect(inner - d, -h, inner - d - t, h, self.stop_line)

        # South
        self.draw_rect(-(h + d), -m, -(h + d) - t, -inner, self.stop_line)
        self.draw_rect( (h + d), -m,  (h + d) + t, -inner, self.stop_line)
        self.draw_rect(-h, -inner + d, h, -inner + d + t, self.stop_line)

        # West
        self.draw_rect(-m,  (h + d), -inner,  (h + d) + t, self.stop_line)
        self.draw_rect(-m, -(h + d), -inner, -(h + d) - t, self.stop_line)
        self.draw_rect(-inner + d, -h, -inner + d + t, h, self.stop_line)

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

        # total length
        dx = x2 - x1
        dy = y2 - y1
        dist = (dx ** 2 + dy ** 2) ** 0.5

        if dist == 0:
            return

        # unit direction
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

        iw = rw + d + t # intersection width
        hiw = h + d + t # half intersection width

        # Vertical road centerline (x = 0), split around the intersection square
        self.draw_dashed_line(0, -m + iw, 0, -hiw, self.lane, width=2)
        self.draw_dashed_line(0, hiw, 0, m - iw, self.lane, width=2)

        # Horizontal road centerline (y = 0)
        self.draw_dashed_line(-m + iw, 0, -hiw, 0, self.lane, width=2)
        self.draw_dashed_line(hiw, 0, m - iw, 0, self.lane, width=2)

    def draw_ring_lane_dividers(self):
        rw = self.road_width
        m = self.inner_margin
        h = rw / 2

        d = self.stop_setback
        t = self.stop_thickness

        iw = rw + d + t  # intersection width
        hiw = h + d + t  # half intersection width

        inner = m - rw
        ring_mid = inner + h

        # Top segment (split around the central road opening)
        self.draw_dashed_line(-ring_mid, ring_mid, -hiw, ring_mid, self.lane, width=2)
        self.draw_dashed_line(hiw, ring_mid, ring_mid, ring_mid, self.lane, width=2)

        # Bottom segment
        self.draw_dashed_line(-ring_mid, -ring_mid, -hiw, -ring_mid, self.lane, width=2)
        self.draw_dashed_line(hiw, -ring_mid, ring_mid, -ring_mid, self.lane, width=2)

        # Right segment
        self.draw_dashed_line(ring_mid, -ring_mid, ring_mid, -hiw, self.lane, width=2)
        self.draw_dashed_line(ring_mid, hiw, ring_mid, ring_mid, self.lane, width=2)

        # Left segment
        self.draw_dashed_line(-ring_mid, -ring_mid, -ring_mid, -hiw, self.lane, width=2)
        self.draw_dashed_line(-ring_mid, hiw, -ring_mid, ring_mid, self.lane, width=2)





