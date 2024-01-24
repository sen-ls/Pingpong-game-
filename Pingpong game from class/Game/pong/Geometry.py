"""
File should substitude pygame and can be filled with geometrical shapes
"""
import math

class Ball(object):
    """
    Class substitudes the ball and thus only needs x and y coordinates
    """
    def __init__(self, x, y, r, v):
        self.x = x
        self.y = y
        self.r = r
        self.v = v

        self.angle = math.radians(0)
        self.direction = 1

class Client_Player(object):
    def __init__(self, x, name, color):
        self.x = x
        self.y = 230
        self.score = 0
        self.name = name
        self.color = color

    def move_ip(self, dy):
        self.y += dy
        return
