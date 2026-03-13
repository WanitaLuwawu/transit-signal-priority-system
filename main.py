import turtle
import tkinter as tk

from sim.map import Map
from sim.signals import SignalController
from sim.bus import Bus


# Window setup

def close_window():
    turtle.bye()

screen = turtle.Screen()
screen.setup(800, 800)
screen.title("Transit Signal Priority Simulation")

turtle.listen()
turtle.onkey(close_window, "Escape")

root = screen._root
root.attributes('-fullscreen', True)


# Layout

control_frame = tk.Frame(root, width=500, bg="#f2f2f2")
control_frame.pack(side="left", fill="y")
control_frame.pack_propagate(False)

canvas = screen.getcanvas()
canvas.pack(side="right", fill="both", expand=True)

title = tk.Label(
    control_frame,
    text="Transit Signal Priority",
    font=("Arial", 16, "bold"),
    bg="#f2f2f2"
)
title.pack(pady=(20,10))

controls_frame = tk.LabelFrame(
    control_frame,
    text="Signal Settings",
    font=("Arial", 12, "bold"),
    padx=10,
    pady=10,
    bg="#f2f2f2"
)

controls_frame.pack(fill="x", padx=15, pady=10)

# UI controls (sliders)

green_slider = tk.Scale(
    control_frame,
    from_=1000, to=8000, resolution=100,
    orient="horizontal",
    label="Green Time (ms)"
)
green_slider.set(4000)
green_slider.pack(in_=controls_frame, pady=8, fill="x")

yellow_slider = tk.Scale(
    control_frame,
    from_=1000, to=8000, resolution=100,
    orient="horizontal",
    label="Yellow Time (ms)"
)
yellow_slider.set(2000)
yellow_slider.pack(in_=controls_frame, pady=8, fill="x")

extension_slider = tk.Scale(
    control_frame,
    from_=1000, to=8000, resolution=100,
    orient="horizontal",
    label="TSP Extension (ms)"
)
extension_slider.set(2500)
extension_slider.pack(in_=controls_frame, pady=8, fill="x")

delay_slider = tk.Scale(
    control_frame,
    from_=0, to=60000, resolution=500,
    orient="horizontal",
    label="Late Bus Delay (ms)"
)
delay_slider.set(3000)
delay_slider.pack(in_=controls_frame, pady=8, fill="x")

# Results Table

results_frame = tk.LabelFrame(
    control_frame,
    text="Simulation Results",
    font=("Arial", 12, "bold"),
    padx=10,
    pady=10,
    bg="#f2f2f2"
)

results_frame.pack(fill="x", padx=15, pady=10)

recovery_time_var = tk.StringVar(value="0.00")

tk.Label(
    results_frame,
    text="Recovery Time",
    font=("Arial", 12)
).pack()

tk.Label(
    results_frame,
    textvariable=recovery_time_var,
    font=("Arial", 22, "bold")
).pack(pady=(0,10))

tk.Label(
    results_frame,
    text="seconds",
    font=("Arial", 10)
).pack()

# Delay table

table_frame = tk.Frame(results_frame)
table_frame.pack(pady=10)

headers = ["Delay", "Initial", "Current", "Recovered"]

for c, h in enumerate(headers):
    tk.Label(
        table_frame,
        text=h,
        font=("Arial", 11, "bold"),
        width=10
    ).grid(row=0, column=c, padx=4, pady=2)

tk.Label(table_frame, text="With TSP").grid(row=1, column=0, sticky="w")
tk.Label(table_frame, text="Without TSP").grid(row=2, column=0, sticky="w")

initial_tsp = tk.StringVar(value="0.00")
current_tsp = tk.StringVar(value="0.00")
recovered_tsp = tk.StringVar(value="0.00")

initial_shadow = tk.StringVar(value="0.00")
current_shadow = tk.StringVar(value="0.00")
recovered_shadow = tk.StringVar(value="0.00")

tk.Label(table_frame, textvariable=initial_tsp).grid(row=1, column=1)
tk.Label(table_frame, textvariable=current_tsp).grid(row=1, column=2)
tk.Label(table_frame, textvariable=recovered_tsp).grid(row=1, column=3)

tk.Label(table_frame, textvariable=initial_shadow).grid(row=2, column=1)
tk.Label(table_frame, textvariable=current_shadow).grid(row=2, column=2)
tk.Label(table_frame, textvariable=recovered_shadow).grid(row=2, column=3)

# Map and signals

my_map = Map(screen)
my_map.draw()

controller = SignalController(screen, my_map.stoplines)

# Simulation state

sim_running = False
sim_tick = 20

initial_delay = 3000
initial_delay_sec = initial_delay / 1000

sim_time = 0
dt = sim_tick / 1000

display_counter = 0


# Bus Initialisation

late_bus = Bus(
    screen,
    controller,
    my_map,
    lane="R",
    color="orange",
    is_late=True,
    delay=initial_delay
)


# Shadow bus initialisation

base_shadow_distance = late_bus.go_speed / dt * initial_delay_sec
scheduled_time = base_shadow_distance / late_bus.go_speed * dt

late_shadow_distance = 0
late_shadow_time = 0


# Start simulation
def start_sim():

    global sim_running
    global initial_delay_sec
    global base_shadow_distance
    global scheduled_time

    if sim_running:
        return

    controller.green_time = green_slider.get()
    controller.yellow_time = yellow_slider.get()
    controller.extension_time = extension_slider.get()

    late_bus.delay = delay_slider.get()

    initial_delay_sec = late_bus.delay / 1000

    base_shadow_distance = late_bus.go_speed / dt * initial_delay_sec
    scheduled_time = base_shadow_distance / late_bus.go_speed * dt

    initial_tsp.set(f"{initial_delay_sec:.2f}")
    initial_shadow.set(f"{initial_delay_sec:.2f}")

    controller.start()

    sim_running = True
    sim_loop()

# Reset simulation
def reset_sim():

    global sim_running
    global sim_time
    global actual_time
    global scheduled_time
    global late_shadow_time
    global base_shadow_distance
    global shadow_distance
    global late_shadow_distance

    sim_running = False
    sim_time = 0

    actual_time = 0
    base_shadow_distance = late_bus.go_speed / dt * initial_delay_sec
    scheduled_time = base_shadow_distance / late_bus.go_speed * dt
    late_shadow_time = 0
    shadow_distance = 0
    late_shadow_distance = 0

    late_bus.reset()

    controller.reset()

    recovery_time_var.set("0.00")
    current_tsp.set("0.00")
    recovered_tsp.set("0.00")
    current_shadow.set("0.00")
    recovered_shadow.set("0.00")


# Loop simulation
def sim_loop():

    if not sim_running:
        return

    late_bus.move()

    if late_bus.active:

        global sim_time
        global base_shadow_distance
        global late_shadow_distance
        global scheduled_time
        global late_shadow_time
        global display_counter

        sim_time += sim_tick
        actual_time = sim_time / 1000

        baseline_red = controller.would_be_red_without_tsp(
            late_bus.current_approach(),
            scheduled_time * 1000
        )

        shadow_red = controller.would_be_red_without_tsp(
            late_bus.current_approach(),
            late_shadow_time * 1000
        )

        if not baseline_red:
            base_shadow_distance += late_bus.go_speed

        if not shadow_red:
            late_shadow_distance += late_bus.go_speed

        scheduled_time = base_shadow_distance / late_bus.go_speed * dt
        late_shadow_time = late_shadow_distance / late_bus.go_speed * dt

        current_delay = max(0, scheduled_time - actual_time)
        current_shadow_delay = max(0, scheduled_time - late_shadow_time)

        recovered_delay = max(0, initial_delay_sec - current_delay)
        recovered_shadow_delay = initial_delay_sec - current_shadow_delay

        display_counter += 1

        if late_bus.is_late and display_counter % 10 == 0:

            if current_delay == 0:
                late_bus.is_late = False

            recovery_time_var.set(f"{actual_time:.2f}")

            current_tsp.set(f"{current_delay:.2f}")
            recovered_tsp.set(f"{recovered_delay:.2f}")

            current_shadow.set(f"{current_shadow_delay:.2f}")
            recovered_shadow.set(f"{recovered_shadow_delay:.2f}")

    screen.ontimer(sim_loop, sim_tick)


# Buttons
button_frame = tk.Frame(control_frame, bg="#f2f2f2")
button_frame.pack(pady=20)

start_btn = tk.Button(
    control_frame,
    text="Start",
    command=start_sim,
    width=10
)
start_btn.pack(in_=button_frame, pady=6)

reset_btn = tk.Button(
    control_frame,
    text="Reset",
    command=reset_sim,
    width=10
)
reset_btn.pack(in_=button_frame, pady=6)

# Start program
turtle.mainloop()
