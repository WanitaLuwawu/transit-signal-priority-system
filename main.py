import turtle
from sim.map import Map
from sim.signals import SignalController
from sim.bus import Bus

def close_window():
    turtle.bye()

screen = turtle.Screen()
screen.setup(800, 800)
screen.title("Transit Signal Priority Simulation")

turtle.listen()
turtle.onkey(close_window, "Escape")

# Draw map
my_map = Map(screen)
my_map.draw()

# Initialize stoplines
controller = SignalController(screen, my_map.stoplines)
controller.start()

initial_delay = 3000
initial_delay_sec = initial_delay / 1000

# Late bus with TSP
late_bus = Bus(screen,
          controller,
          my_map, lane="R"
             # , path=[my_map.grid["R"][1],
             #     my_map.grid["R"][2],
             #     my_map.grid["R"][5],
             #     my_map.grid["R"][4]]
          , color="orange"
          , is_late=True
          , delay = initial_delay
        )

# Printer Turtle for value labels
label_printer = turtle.Turtle()
label_printer.hideturtle()
label_printer.penup()

# Printer Turtle for recovery time
recovery_time_printer = turtle.Turtle()
recovery_time_printer.hideturtle()
recovery_time_printer.penup()

# Initialise recovery time
label_printer.goto(-300, 320)
label_printer.write(
    "Recovery Time:",
    font=("Arial", 14, "bold")
)
recovery_time_printer.goto(-150, 320)
recovery_time_printer.write(
    "0.00",
    font=("Arial", 14, "bold")
)

label_printer.goto(-100, 320)
label_printer.write(
    "s",
    font=("Arial", 14, "bold")
)

# Print Table
label_printer.goto(-300, -365)
label_printer.write(
    "Delay With TSP [sec]",
    font=("Arial", 14, "bold")
)

label_printer.goto(-300, -390)
label_printer.write(
    "Delay Without TSP [sec]",
    font=("Arial", 14, "bold")
)

label_printer.goto(-60, -340)
label_printer.write(
            "Initial",
            font=("Arial", 14, "bold")
        )
label_printer.goto(50, -340)
label_printer.write(
            "Current",
            font=("Arial", 14, "bold")
        )
label_printer.goto(160, -340)
label_printer.write(
            "Recovered",
            font=("Arial", 14, "bold")
        )

label_printer.goto(-60, -390)
label_printer.write(
        f"{initial_delay_sec:.2f}\n"
        f"{initial_delay_sec:.2f}",
            font=("Arial", 14, "bold")
        )


# Printer Turtle for delay/table values
delay_printer = turtle.Turtle()
delay_printer.hideturtle()
delay_printer.penup()
delay_printer.goto(50, -390)
delay_printer.write(
        "0.00\t     0.00\n"
        "0.00\t     0.00",
            font=("Arial", 14, "bold")
        )

# Loop control variable for scheduling display updates
display_counter = 0

sim_time = 0 # The time for which the sim has been running
dt = 0.02    # The real-world time corresponding to each frame (20ms = 0.02s)

# The distance travelled by the baseline bus during the late bus's delay
base_shadow_distance = late_bus.go_speed / dt * initial_delay_sec
scheduled_time = base_shadow_distance / late_bus.go_speed * dt

# Initialise tha late shadow; the late bus without TSP
late_shadow_distance = 0
late_shadow_time = 0

def sim_loop():

    late_bus.move()

    if late_bus.active:# When late_bus starts moving...

        global sim_time, base_shadow_distance, late_shadow_distance, scheduled_time, late_shadow_time
        sim_time += 20
        actual_time = sim_time / 1000  # time elapsed by late bus

        # Check whether the current light would have been red without TSP...
        baseline_red = controller.would_be_red_without_tsp( # for the baseline bus
            late_bus.current_approach(),
            scheduled_time * 1000
        )

        shadow_red = controller.would_be_red_without_tsp( # for the late shadow
            late_bus.current_approach(),
            late_shadow_time * 1000
        )

        # Advance the baseline and late shadow buses if the current light would be green without TSP
        if not baseline_red:
            base_shadow_distance += late_bus.go_speed

        if not shadow_red:
            late_shadow_distance += late_bus.go_speed

        # Delay Calculations
        scheduled_time = base_shadow_distance / late_bus.go_speed * dt   # time elapsed by baseline bus
        late_shadow_time = late_shadow_distance / late_bus.go_speed * dt # time elapse by late shadow

        current_delay = max(0, scheduled_time - actual_time)             # current delay = how much longer than the late bus has the baseline bus been running?
        current_shadow_delay = max(0, scheduled_time - late_shadow_time) # current shadow delay = how much longer than the late shadow has the baseline bus been running?

        recovered_delay = max(0, initial_delay_sec - current_delay)      # how much of initial delay has been recovered
        recovered_shadow_delay = initial_delay_sec - current_shadow_delay

        # Loop control variable for scheduling display updates
        global display_counter
        display_counter += 1

        if late_bus.is_late and display_counter % 10 == 0: # If the late bus is late, and it's time to update the delay output...
            if current_delay == 0:       # Stop updating the output when current delay reaches zero because
                late_bus.is_late = False # the late bus isn't late anymore

            # Update the recovery time on display
            recovery_time_printer.clear()
            recovery_time_printer.write(
            f"{actual_time:.2f}",
            font = ("Arial", 14, "bold"))

            # Update the delay on display
            delay_printer.clear()
            delay_printer.write(
                f"{current_delay:.2f}\t     {recovered_delay:.2f}\n"
                f"{current_shadow_delay:.2f}\t     {recovered_shadow_delay:.2f}",
                font=("Arial", 14, "bold")
            )

    screen.ontimer(sim_loop, 20)

# Start sim
sim_loop()

turtle.mainloop()