import turtle
from sim.map import Map
from sim.signals import SignalController

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

turtle.mainloop()
