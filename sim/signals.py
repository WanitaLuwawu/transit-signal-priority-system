import turtle

class SignalController:
    def __init__(self, screen, stoplines):
        self.screen = screen
        self.stoplines = stoplines

        # Timing (milliseconds)
        self.green_time = 3000
        self.yellow_time = 2000
        self.extension_time = 2500
        self.remaining = self.green_time

        # State
        self.phase = "NS"               # "NS" or "EW"
        self.state = "GREEN"            # "GREEN" or "YELLOW"
        self.priority_requested = False
        self.extension_used = False

        # Stopline groups by phase
        # keys make reference to approach direction
        self.ns_keys = ("NB", "SB", "RN_L", "RN_R", "RN_C", "RS_L", "RS_R", "RS_C")
        self.ew_keys = ("EB", "WB", "RE_T", "RE_B", "RE_C", "RW_T", "RW_B", "RW_C")
        self.ns_set = set(self.ns_keys)
        self.ew_set = set(self.ew_keys)

        self.apply_colors()

        # Printer Turtle for displaying priority state
        self.printer = turtle.Turtle()
        self.printer.hideturtle()
        self.printer.penup()
        self.printer.goto(-300, 320)

    def start(self):
        self.remaining = self.green_time # phase timer set to green_time
        self.tick()

    def tick(self):
        if self.remaining > 0: # while the current phase is green...
            # check whether conditions for green light extension have been met:
            # 1. priority has been requested
            # 2. an extension has not been used during this phase
            if self.priority_requested and not self.extension_used:
                self.remaining += self.extension_time # extend green_time
                self.extension_used = True            # do not allow another extension during this phase

                self.printer.clear()
                self.printer.write("GREEN+", font=("Arial", 14, "bold")) # notify the user of green light extension

            self.remaining -= 100               # reduce green_time
            self.screen.ontimer(self.tick, 100) # continue countdown to next phase
        else: # swap phase
            self.to_yellow()

    # schedule the next green phase for the end of yellow_time
    def schedule_next(self):
        if self.state == "YELLOW":
            self.screen.ontimer(self.swap_phase, self.yellow_time)

    def swap_phase(self):
        self.phase = "EW" if self.phase == "NS" else "NS" # swap active phase
        self.state = "GREEN"                              # set active phase state to "GREEN"
        self.priority_requested = False                   # set active phase priority to default state
        self.extension_used = False
        self.printer.clear()                              # clear previous output
        self.remaining = self.green_time                  # phase timer set to green_time
        self.apply_colors_green_approach_only()           # recolor the phases separately to avoid a huge redraw spike
        self.screen.ontimer(self.apply_colors, 25)
        self.tick()                                       # start countdown to next phase swap

    def request_priority(self, approach):
        # only allow requests during GREEN
        if self.state != "GREEN":
            return False

        # reject unknown approaches
        if approach not in self.stoplines:
            return False

        # NS phase approaches
        if approach in self.ns_set and self.phase == "NS":
            self.priority_requested = True
            return True

        # EW phase approaches
        if approach in self.ew_set and self.phase == "EW":
            self.priority_requested = True
            return True

        return False

    # determine the phase to which each stopline/approach belongs
    def approach_phase(self, approach):
        if approach in self.ns_set:
            return "NS"
        if approach in self.ew_set:
            return "EW"
        return None

    def to_yellow(self):
        self.state = "YELLOW"
        self.apply_colors()
        self.schedule_next()

    def apply_colors(self):
            # the active phase is either green or yellow
            # the other phase is red
            if self.phase == "NS":
                ns = "green" if self.state == "GREEN" else "yellow"
                ew = "red"
            else:
                ew = "green" if self.state == "GREEN" else "yellow"
                ns = "red"

            # only recolor the phase that is not turning green
            # this avoids a huge redraw spike
            if ns != "green":
                for k in self.ns_keys:
                    self.stoplines[k].fillcolor(ns)

            if ew != "green":
                for k in self.ew_keys:
                        self.stoplines[k].fillcolor(ew)

    def apply_colors_green_approach_only(self):
        # only recolor the phase that is turning green.
        # this avoids a huge redraw spike.

        if self.phase == "NS":
            green_group = self.ns_keys
        else:
            green_group = self.ew_keys

        for k in green_group:
            self.stoplines[k].fillcolor("green")

    # get the current color of a stopline/approach
    def get_color(self, approach):
        return self.stoplines[approach].fillcolor()