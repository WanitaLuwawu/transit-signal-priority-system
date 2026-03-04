import turtle

class SignalController:
    def __init__(self, screen, stoplines):
        self.screen = screen
        self.stoplines = stoplines

        # Timing (milliseconds)
        self.green_time = 3000
        self.yellow_time = 1500
        self.extension_time = 2000

        # State
        self.phase = "NS" # "NS" or "EW"
        self.state = "GREEN" # "GREEN" or "YELLOW"
        self.priority_requested = False
        self.extension_used = False

        # Stopline groups by phase
        self.ns_keys = ("NB", "SB", "RN_L", "RN_R", "RN_C", "RS_L", "RS_R", "RS_C")
        self.ew_keys = ("EB", "WB", "RE_T", "RE_B", "RE_C", "RW_T", "RW_B", "RW_C")
        self.ns_set = set(self.ns_keys)
        self.ew_set = set(self.ew_keys)

        self.apply_colours()

    def start(self):
        self.remaining = self.green_time
        self.tick()

    def tick(self):
        if self.remaining > 0:
            self.remaining -= 100
            # Apply extension immediately when requested
            if self.priority_requested and not self.extension_used:
                self.remaining += self.extension_time
                self.extension_used = True
            self.screen.ontimer(self.tick, 100)
        else:
            self.to_yellow()

    def schedule_next(self):
        if self.state == "YELLOW":
            self.screen.ontimer(self.swap_phase, self.yellow_time)

    def swap_phase(self):
        self.phase = "EW" if self.phase == "NS" else "NS"
        self.state = "GREEN"
        self.priority_requested = False
        self.extension_used = False
        self.remaining = self.green_time
        self.apply_colours_green_approach_only()
        self.screen.ontimer(self.apply_colours, 25)
        self.tick()

    def request_priority(self, approach):
        # Only allow requests during GREEN
        if self.state != "GREEN":
            return False

        # Reject unknown approaches
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

    def approach_phase(self, approach):
        if approach in self.ns_set:
            return "NS"
        if approach in self.ew_set:
            return "EW"
        return None

    def to_yellow(self):
        self.state = "YELLOW"
        self.apply_colours()
        self.schedule_next()

    def apply_colours(self):
            if self.phase == "NS":
                ns = "green" if self.state == "GREEN" else "yellow"
                ew = "red"
            else:
                ew = "green" if self.state == "GREEN" else "yellow"
                ns = "red"

            if ns != "green":
                for k in self.ns_keys:
                    self.stoplines[k].fillcolor(ns)

            if ew != "green":
                for k in self.ew_keys:
                        self.stoplines[k].fillcolor(ew)

    def apply_colours_green_approach_only(self):
        # Only recolour the side that is becoming green.
        # This avoids a huge redraw spike.

        if self.phase == "NS":
            green_group = self.ns_keys
        else:
            green_group = self.ew_keys

        for k in green_group:
            self.stoplines[k].fillcolor("green")

    def get_colour(self, approach):
        return self.stoplines[approach].fillcolor()