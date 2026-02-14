import turtle
from map import Map

screen = turtle.Screen()
screen.setup(700, 700)

m = Map(screen)
m.draw()
turtle.mainloop()