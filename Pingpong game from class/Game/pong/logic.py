import math
from Game.pong import Geometry


class Logic(object):
    """
    initializes a game without any active players. As soon as players send join game, they will be either player or opponent.
    First Player to join the game is:       firstPlayer
    Second Player to join is:               secondPlayer
    
    """
    def __init__(self, ball_speed = 20):

        #Possible Features:
        self.size_x = 800 # self.features[0]
        self.size_y = 600
        size = 15
        self.ball = Geometry.Ball(self.size_x/2, self.size_y/2, size, ball_speed)

        self.angle_list = [60, 45, 30, -0, -30, -45, -60, -60]

        self.moving_speed = 1

        self.calc_bouncing_point_x_and_remainder()
        self.calc_bouncing_point_y_and_remainder()


    def player_update(self, player, key):
        """
        takes the pressed key from the main loop
        """
        if key is None:
            pass
        elif key == "UP":
            player = self._move_player_up(player)
            return player

        elif key == "DOWN":
            player = self._move_player_down(player)
            return player

        return player

    def get_state(self, players):
        """
        Moves ball and returns player score differences and the ball
        :param players: Player_list containing both players
        :return first_player_score_diff, second_player_score_diff, self.ball: player score differences, ball
        """
        first_player_score_diff = players[0].score
        second_player_score_diff = players[1].score
        self._update_ball(players)
        first_player_score_diff = players[0].score - first_player_score_diff
        second_player_score_diff = players[1].score - second_player_score_diff

        return first_player_score_diff, second_player_score_diff, self.ball

    def _move_player_up(self, player):
        if player.y > 0:
            player.y -= self.moving_speed
        return player

    def _move_player_down(self, player):
        if player.y + 120 < self.size_y - 20:
            player.y += self.moving_speed
        return player

    def calc_bouncing_point_x_and_remainder(self):
        """
        Calculates how many iterations it takes to reach the next paddel and how big the remainder in x direction
        is after the bounce. Has to be called after every x bounce only. Also calculates the x-Position after the bounce to have
        a constant movement speed
        :return:
        """
        self.movement_x = int(self.ball.direction * self.ball.v * math.cos(self.ball.angle))


        if self.ball.direction == -1: #Going left: Bounce Point is at x = 50
            self.iter_to_x = int((self.ball.x - self.ball.r/2 - 50) / abs(self.movement_x))
            self.remainder_x = float(float(self.ball.x - self.ball.r/2 - 50) / float(abs(self.movement_x)) - self.iter_to_x)
            self.new_pos_x = 50 + abs(self.movement_x) * (1. - self.remainder_x)
        else: #Going right: Bounce Point is at size_x - 50 - ball.r , as the ball is defined in its center
            self.iter_to_x = int((self.size_x - 50 - self.ball.r/2 - self.ball.x) / abs(self.movement_x))
            self.remainder_x = float(float(self.size_x - 50 - self.ball.r/2 - self.ball.x) / float(abs(self.movement_x)) - self.iter_to_x)
            self.new_pos_x = self.size_x - 50 - abs(self.movement_x) * (1. - self.remainder_x)

    def calc_bouncing_point_y_and_remainder(self,diff = -1,diff_2 = 0, players = None):
        """
        Calculates how many iterations it takes to reach the top / bottom and how big the remainder in y direction
        is after the bounce. Has to be called after every y or x bounce
        :return:
        """

        self.movement_y = int(abs(self.ball.direction) * self.ball.v * -math.sin(self.ball.angle))

        if self.movement_y > 0.0:
            self.iter_to_y = int((self.size_y - self.ball.r/2 - self.ball.y) / abs(self.movement_y))
            self.remainder_y = float(self.size_y - self.ball.r/2 - self.ball.y) / float(abs(self.movement_y)) - self.iter_to_y
            self.new_pos_y = self.size_y - self.ball.r/2 - abs(self.movement_y) * (1. - self.remainder_y)
            if self.iter_to_y == 0 and self.remainder_y >= diff and diff_2 == 0:
                self.ball.y += self.movement_y * diff
                self.calc_bouncing_point_y_and_remainder()
            elif self.iter_to_y == 0 and self.remainder_y < diff and diff_2 == 0:
                self.ball.y = self.size_y - self.ball.r/2 - abs(self.movement_y) * (diff - self.remainder_y)
                self.ball.angle *= -1
                self.calc_bouncing_point_y_and_remainder()
            elif self.iter_to_y != 0 and diff != -1 and diff_2 != 0:
                self.ball.y = self.size_y - self.ball.r/2 - abs(self.movement_y) * diff
                if self.collide(self.ball.y,players):
                    self.ball.x = self.new_pos_x
                    self.calc_bouncing_point_x_and_remainder()
                    self.calc_bouncing_point_y_and_remainder(-1,diff_2)
                else:
                    self.ball.y = self.size_y - self.ball.r/2 - abs(self.movement_y) * diff_2
                    self.ball.x += self.movement_x
            elif diff == -1 and diff_2 != 0:
                self.ball.y = self.size_y - self.ball.r/2 - abs(self.movement_y) * diff_2

        elif self.movement_y < 0.0:
            self.iter_to_y = int((self.ball.y - self.ball.r/2) / abs(self.movement_y))
            self.remainder_y = float(float(self.ball.y - self.ball.r/2) / float(abs(self.movement_y)) - self.iter_to_y)
            self.new_pos_y = self.ball.r/2 + abs(self.movement_y) * (1. - self.remainder_y)
            if self.iter_to_y == 0 and self.remainder_y >= diff and diff_2 == 0:
                self.ball.y += self.movement_y * diff
                self.calc_bouncing_point_y_and_remainder()
            elif self.iter_to_y == 0 and self.remainder_y < diff and diff_2 == 0:
                self.ball.y = self.ball.r/2 + abs(self.movement_y) * (diff - self.remainder_y)
                self.ball.angle *= -1
                self.calc_bouncing_point_y_and_remainder()
            elif self.iter_to_y != 0 and diff != -1 and diff_2 != 0:
                self.ball.y = self.ball.r/2 + abs(self.movement_y) * diff
                if self.collide(self.ball.y,players):
                    self.ball.x = self.new_pos_x
                    self.calc_bouncing_point_x_and_remainder()
                    self.calc_bouncing_point_y_and_remainder(-1,diff_2)
                else:
                    self.ball.y += self.movement_y * diff_2
                    self.ball.x += self.movement_x
            elif diff == -1 and diff_2 != 0:
                self.ball.y += self.movement_y * diff_2

        else:
            self.iter_to_y = self.iter_to_x + self.size_x #If angle == 0 --> Ball will not touch the top or bottom
            self.remainder_y = 0
            self.new_pos_y = self.size_y / 2

    def _update_ball(self,players):
        if self.iter_to_x == 0:
            if self.iter_to_y == 0 and self.remainder_x <= self.remainder_y:
                if self.collide(self.remainder_x*self.movement_y + self.ball.y, players):
                    self.ball.x = self.new_pos_x
                    self.ball.y += self.remainder_x*self.movement_y
                    diff = 1. - self.remainder_x
                    self.calc_bouncing_point_y_and_remainder(diff)
                    self.calc_bouncing_point_x_and_remainder()
                else:
                    self.ball.x += self.movement_x
                    self.iter_to_x -= 1
                    self.ball.y = self.new_pos_y

            elif self.iter_to_y == 0 and self.remainder_x > self.remainder_y:
                self.ball.angle *= -1
                diff = self.remainder_y - self.remainder_x
                diff_2 = 1. - self.remainder_x
                self.ball.y += self.remainder_y*self.movement_y
                self.calc_bouncing_point_y_and_remainder(diff,diff_2)

            else:
                if self.collide(self.remainder_x*self.movement_y + self.ball.y, players):
                    self.ball.y += self.movement_y*self.remainder_x
                    diff = 1. - self.remainder_x
                    self.ball.x = self.new_pos_x
                    self.calc_bouncing_point_y_and_remainder()
                    self.ball.y += diff * self.movement_y
                    self.calc_bouncing_point_y_and_remainder()
                    self.calc_bouncing_point_x_and_remainder()
                else:
                    self.ball.x += self.movement_x
                    self.ball.y += self.movement_y
                    self.iter_to_x -= 1
                    self.iter_to_y -= 1

        elif self.iter_to_y == 0:
            self.ball.angle *= -1
            self.ball.y = self.new_pos_y
            self.calc_bouncing_point_y_and_remainder()
            self.ball.x += self.movement_x
            self.iter_to_x -= 1
        else:
            self.ball.x += self.movement_x
            self.ball.y += self.movement_y
            self.iter_to_x -= 1
            self.iter_to_y -= 1

        if self.ball.x > self.size_x or self.ball.x < 0:
            if self.ball.x > self.size_x:
                players[0].add_point()
            else:
                players[1].add_point()
            self.ball.angle = math.radians(0)
            if not (players[1].score == 11 or players[0].score == 11):
                self.ball.x = self.size_x / 2
                self.ball.y = self.size_y /2
                self.calc_bouncing_point_y_and_remainder()
                self.calc_bouncing_point_x_and_remainder()
        #print("Iter_to_x: {} ||  Iter_to_y: {}".format(self.iter_to_x,self.iter_to_y))


    def collide(self,ball_y,players):
        #Better Collision Mechanics
        if self.ball.direction < 0:
            y_distance = ball_y - players[0].y
        else:
            y_distance = ball_y - players[1].y

        if y_distance >= 0 and y_distance <= 140:
            self.ball.angle = math.radians(self.angle_list[int(y_distance/20)])
            self.ball.direction *= -1
            return True
        else:
            return False

    def increase_velocity(self):
        """
        Increases Ball_velocity exponentially everytime
        :return:
        """
        self.ball.v = int(self.ball.v * 1.2)
        if self.ball.v > 75:
            self.ball.v = 75
        print("Ball Velocity = {}".format(self.ball.v))
        return

    def reset_velocity(self, v):
        """
        Resets the Ball_speed after a point was scored
        :return:
        """
        self.ball.v = v
