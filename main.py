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

my_map = Map(screen)
my_map.draw()

controller = SignalController(screen, my_map.stoplines)
controller.start()

bus = Bus(screen,
          controller,
          my_map, lane="R"
          # path=[my_map.grid["R"][1],
          #     my_map.grid["R"][4],
          #     my_map.grid["R"][5],
          #     my_map.grid["R"][2]]
          #
          )
bus.move()

turtle.mainloop()