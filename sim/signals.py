import turtle

class SignalController:
    def __init__(self, screen, stoplines):
        self.screen = screen
        self.stoplines = stoplines

        # Timing (milliseconds)
        self.green_time = 4000
        self.yellow_time = 1500
        self.extension_time = 2000

        # State
        self.phase = "NS" # "NS" or "EW"
        self.state = "GREEN" # "GREEN" or "YELLOW"
        self.priority_requested = False
        self.extension_used = False

        # Stopline groups by phase
        self.ns_keys = ("NB", "SB", "RN_L", "RN_R", "RN_S", "RS_L", "RS_R", "RS_S")
        self.ew_keys = ("EB", "WB", "RE_T", "RE_B", "RE_S", "RW_T", "RW_B", "RW_S")
        self.ns_set = set(self.ns_keys)
        self.ew_set = set(self.ew_keys)

        self.apply_colours()

    def apply_colours(self):
            if self.phase == "NS":
                ns = "green" if self.state == "GREEN" else "yellow"
                ew = "red"
            else:
                ew = "green" if self.state == "GREEN" else "yellow"
                ns = "red"

            for k in self.ns_keys:
                self.stoplines[k].fillcolor(ns)

            for k in self.ew_keys:
                self.stoplines[k].fillcolor(ew)

    def start(self):
        # Begin the cycle
        self.schedule_next()

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

    def schedule_next(self):
        # Decide how long until the next transition
        if self.state == "GREEN":
            delay = self.green_time

            # Green extension: apply at most once per green
            if self.priority_requested and not self.extension_used:
                delay += self.extension_time
                self.extension_used = True

            self.screen.ontimer(self.to_yellow, delay)

        elif self.state == "YELLOW":
            self.screen.ontimer(self.swap_phase, self.yellow_time)

    def to_yellow(self):
        self.state = "YELLOW"
        self.apply_colours()
        self.schedule_next()

    def swap_phase(self):
        # Move to next phase and reset extension/request flags
        self.phase = "EW" if self.phase == "NS" else "NS"
        self.state = "GREEN"
        self.priority_requested = False
        self.extension_used = False

        # Step 1: set the new phase to green first
        self.apply_colours_green_approach_only()

        # Step 2: shortly after, finish the rest
        self.screen.ontimer(self.apply_colours, 30)

        # Then schedule the next transition
        self.schedule_next()

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