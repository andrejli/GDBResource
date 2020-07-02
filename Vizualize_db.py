"""import turtle

# set turtle to draw graph
DEFAULT_MARGIN = 50
turtle.reset()
turtle.speed(0)
objects = dict()  # dictionary contains id's and position on canvas
# set turtle canvas


# load database from .json
mocking_objects = [535657222, 657845671, 111,555,6665,333,777]
# vizualize objects

    # generate object position on canvas
    # TODO There must be logic written to this position generator.
#  Objects can cot be generated randomly or
# Best will be vizualize object and all associated links and then go to another obj.

    # draw object
def draw_first_object(id):
    turtle.setpos(0, 0)
    turtle.shape('circle')
    turtle.stamp()
    turtle.left(-90)
    turtle.pu()
    turtle.setpos(-100, -125)
    turtle.left(35)
    turtle.pd()
    # write id and position to objects dictionary
    objects[id] = [turtle.position()[0], turtle.position()[1]]
    return


def draw_object(id):
    turtle.shape('circle')
    turtle.stamp()
    turtle.left(15)
    turtle.pu()
    turtle.fd(DEFAULT_MARGIN)
    turtle.pd()
    # write id and position to objects dictionary
    objects[id] = [turtle.position()[0], turtle.position()[1]]
    print(objects)
    return


# M A I N   P R O C E D U R E
for i in mocking_objects:
    if i == mocking_objects[0]:
        draw_first_object(i)
    else:
        draw_object(i)
input()


# vizualize links
    # search objects position
    #draw line from to object

# check protected zone"""
