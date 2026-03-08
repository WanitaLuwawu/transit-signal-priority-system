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

# Bus with zero delay
baseline_bus = Bus(screen,
          controller,
          my_map, lane="R"
            # , path=[my_map.grid["R"][1],
            #     my_map.grid["R"][4],
            #     my_map.grid["R"][5],
            #     my_map.grid["R"][2]]
        )

# Bus with 1.5s delay
late_bus = Bus(screen,
          controller,
          my_map, lane="R"
            # , path=[my_map.grid["R"][1],
            #     my_map.grid["R"][4],
            #     my_map.grid["R"][5],
            #     my_map.grid["R"][2]]
          , color="orange"
          , is_late=True
          , delay = 1500
        )

# Printer Turtle for displaying recovery time
recovery_printer = turtle.Turtle()
recovery_printer.hideturtle()
recovery_printer.penup()
recovery_printer.goto(-300, -340)

# recovery time counter
recovery_time = 0

def sim_loop():
    # move each bus
    baseline_bus.move()
    late_bus.move()

    # distance between the buses
    x1, y1 = baseline_bus.chassis.pos() # baseline_bus pos
    x2, y2 = late_bus.chassis.pos()     # late_bus pos

    dx = x2 - x1
    dy = y2 - y1

    dist = (dx**2 + dy**2)**0.5

    # distance from baseline_bus at which late_bus has recovered from delay
    recovery_zone = baseline_bus.slow_zone

    global recovery_time

    if baseline_bus.current_leg_index > 0 and late_bus.current_leg_index > 0 and late_bus.is_late:
                                     # after the first path segment...
        if dist <= recovery_zone:    # if late_bus is within recovery_zone...
            late_bus.is_late = False # it is not late anymore

            # print recovery time
            recovery_printer.write(f"Recovery Time: {round(recovery_time/1000, 2)}s", font=("Arial", 14, "bold"))

    recovery_time += 20             # increment recovery_time each loop
    screen.ontimer(sim_loop, 20) # continue loop

# Start sim
sim_loop()

turtle.mainloop()