import pygame
import os
import random
pygame.init()


class Gui(object):
    """
    class to render the gui
    """
    def __init__(self, color_1, name, color_2, opp_name, id, ball_size = 15):
        """General Screen"""
        self.game_dimension = [800, 600]
        self.width, self.height = self.game_dimension[0], self.game_dimension[1] + 150
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Pong Group 05")
        icon = pygame.image.load(os.sep.join([os.path.dirname(__file__), 'gui-icons', 'racket_16px.png']))
        pygame.display.set_icon(icon)

        """self.right_side determines if Gui has to Mirror the X-Position of the ball"""
        self.id = id
        if self.id == 2:
            self.right_side = True
        else:
            self.right_side = False

        """Time Font specific"""
        self.rtt = None
        self.small_font = pygame.font.SysFont("Times", 20)

        """Name specific"""
        self.name = name
        self.opp_name = opp_name
        self.scale_name()

        """Scores"""
        self.player_score = 0
        self.opponent_score = 0
        self.font = pygame.font.SysFont("Times", 65)
        self.font_fgcolor = (103, 103, 103)

        """Background specific"""
        seed = random.randint(0, 8)
        if seed == "test":
            self.background = pygame.image.load(os.sep.join([os.path.dirname(__file__), 'gui-icons', 'Test-Feld.png']))
        else:
            self.background = pygame.image.load(os.sep.join([os.path.dirname(__file__), 'gui-icons', ('Ping-Pong_score_' + str(seed) + '.png')]))

        """Ball specific"""
        self.ball_size = ball_size
        self.ball_x = (self.width - self.ball_size) / 2
        self.ball_y = (self.game_dimension[1] - self.ball_size) / 2


        """Ball skin"""
        seed_ball = random.randint(0, 1)
        if seed == 3 or seed == 8:
            seed_ball = 1
        elif seed == 0 or seed == 5:
            seed_ball = 0
        elif seed == 6 or seed == 7:
            seed_ball = 2
        if self.ball_size == 15 or self.ball_size == 10:
            self.ball = pygame.image.load(os.sep.join([os.path.dirname(__file__), 'gui-icons', 'Ball_' + str(self.ball_size) + '_' + str(seed_ball) + '.png']))
        else:
            self.ball = pygame.image.load(os.sep.join([os.path.dirname(__file__), 'gui-icons', 'Ball_15_' + str(seed_ball) + '.png']))

        """Paddle specific"""
        self.color_1 = [int(color_1[0]), int(color_1[1]), int(color_1[2])]
        self.color_2 = [int(color_2[0]), int(color_2[1]), int(color_2[2])]
        self.player_is_skin = True
        self.opp_is_skin = True
        self.paddle_height = 140
        self.paddle_width = 20

        """Player Paddle"""
        if self.color_1[0] == 1 and self.color_1[1] == 2 and self.color_1[2] >= 50 and self.color_1[2] <= 60:
            skin = (self.color_1[2] - 50) % 8
            self.paddle_1 = pygame.image.load(os.sep.join([os.path.dirname(__file__), 'gui-icons', ('Paddle_' + str(skin) + '.png')]))
        else:
            self.paddle_1 = pygame.Rect(30, (self.game_dimension[1]-140)/2, 20, 140)
            self.player_is_skin = False

        """Opponent Paddle"""
        if self.color_2[0] == 1 and self.color_2[1] == 2 and self.color_2[2] >= 50 and self.color_2[2] <= 60:
            skin = (self.color_2[2] - 50) % 8
            self.paddle_2 = pygame.image.load(os.sep.join([os.path.dirname(__file__), 'gui-icons', ('Paddle_' + str(skin) + '.png')]))
        else:
            self.paddle_2 = pygame.Rect(750, (self.game_dimension[1]-140)/2, 20, 140)
            self.opp_is_skin = False

        """Player specific"""
        self.first_player_x = self.width * 1/16 - self.paddle_width     #30
        self.second_player_x = self.width * 15/16                       #750
        self.first_player_y = (self.game_dimension[1] - self.paddle_height) / 2
        self.second_player_y = (self.game_dimension[1] - self.paddle_height) / 2

        """Rects for efficient updates of the GUI"""
        self.seperate_line = pygame.Rect(0,  self.game_dimension[1], self.game_dimension[0], 3)
        self.time_rect = pygame.Rect(5,  self.game_dimension[1] + 120, 170, 30)
        self.screen_rect = pygame.Rect(0, 0, self.width, self.height)
        self.game_rect = pygame.Rect(0, 0, self.game_dimension[0], self.game_dimension[1])
        self.score_rect = pygame.Rect(self.game_dimension[0] / 2 - 125, self.game_dimension[1], 250, 150)
        self.ball_rect = pygame.Rect(self.ball_x, self.ball_y,self.ball_size,self.ball_size)
        self.ball_rect_2 = pygame.Rect(self.ball_x, self.ball_y,self.ball_size,self.ball_size)
        self.paddle_rect_1 = pygame.Rect(0, 0,self.game_dimension[0] * 1/16,self.game_dimension[1])
        self.paddle_rect_2 = pygame.Rect(self.game_dimension[0]*15/16, 0,self.game_dimension[0] * 1/16,self.game_dimension[1])

        """Game Over Screen"""
        self.lost = pygame.image.load(os.sep.join([os.path.dirname(__file__), 'gui-icons', 'LOST.png']))
        self.won = pygame.image.load(os.sep.join([os.path.dirname(__file__), 'gui-icons', 'WON.png']))

    def scale_name(self):
        """
        Scales names so that it fits in the Box
        :return:
        """
        if len(self.name) > 8:
            self.name = self.name[:8]
        self.name_font = pygame.font.SysFont("Times", 20)

        if len(self.opp_name) <= 8:
            self.opp_name_font = pygame.font.SysFont("Times", 20)
        else:
            self.opp_name_font = pygame.font.SysFont("Times", 15)
        return

    def display_time(self, time):
        """
        Displays the time in seconds since the player gui opened
        :param time: Time that has elapsed
        :return: None
        """
        pygame.draw.rect(self.screen, self.font_fgcolor, self.time_rect)
        self.screen.blit(self.small_font.render("Elapsed time: %.0f s" % time, -1, (0, 0, 0)), (5, 720))
        pygame.display.update(self.time_rect)
        return

    def render_font(self):
        """
        Renders Font of Score and Players Names
        :return: None
        """
        """Blit the Scores"""
        if self.player_score < 10:
            self.screen.blit(self.font.render(str(self.player_score), -1, self.font_fgcolor), (self.width / 2 - 91 , self.game_dimension[1] + 65))
        else:
            self.screen.blit(self.font.render(str(self.player_score), -1, self.font_fgcolor), (self.width / 2 - 111 , self.game_dimension[1] + 65))

        if self.opponent_score < 10:
            self.screen.blit(self.font.render(str(self.opponent_score), -1, self.font_fgcolor), (self.width / 2 + 59, self.game_dimension[1] + 65))
        else:
            self.screen.blit(self.font.render(str(self.opponent_score), -1, self.font_fgcolor), (self.width / 2 + 43, self.game_dimension[1] + 65))
        """Blit the Names"""
        self.screen.blit(self.name_font.render(self.name, -1, self.font_fgcolor), (self.game_dimension[0] / 2 - 120, self.game_dimension[1] + 8))
        self.screen.blit(self.opp_name_font.render(self.opp_name, -1, self.font_fgcolor), (self.game_dimension[0] / 2 + 35, self.game_dimension[1] + 8))
        pygame.display.update(self.score_rect)
        return

    def blit_background(self):
        """
        Blits background image and fills it with a specific gray colour
        Usage: If Dimensions == [800,600]
        :return: None
        """
        self.screen.fill([67, 67, 67])
        self.screen.blit(self.background, (0,0))
        pygame.draw.rect(self.screen, (0, 0, 0), self.seperate_line)

    def render_screen(self):
        """
        Updates the complete Screen
        :return: None
        """
        pygame.display.update(self.screen_rect)
        return

    def render_parts(self):
        """
        Renders Background, ball and players and changes the second ball rect which is important for the screen.update(rect) method
        :return: None
        """
        self.screen.blit(self.ball, (self.ball_x, self.ball_y))
        self.draw_players()
        pygame.display.update(self.paddle_rect_1)
        pygame.display.update(self.paddle_rect_2)
        pygame.display.update(self.ball_rect)
        pygame.display.update(self.ball_rect_2)
        self.ball_rect_2.x = self.ball_x
        self.ball_rect_2.y = self.ball_y
        return

    def update_ball(self,X,Y,X_V,Y_V):
        """
        Updates Ball Position. If Player has ID 2 his Ball-X-Coordinates are mirrored
        :param X: Current X-Position of the Ball
        :param Y: Current Y-Position of the Ball
        :param X_V: Current X-Velocity of the Ball
        :param Y_V: Current Y-Velocity of the Ball
        :return: None
        """
        if self.right_side:
            self.ball_x = self.game_dimension[0] - X
        else:
            self.ball_x = X

        self.ball_x -= int(self.ball_size/2)
        self.ball_y = Y - int(self.ball_size/2)

        self.ball_rect.x = self.ball_x
        self.ball_rect.y = self.ball_y
        return

    def update_player(self, id, player_rect):
        """
        Updates the Y-Position of the Player with ID: id
        :param id: Player ID, only own id is relevant, Opponent ID is interpreted as 3
        :param player_rect: Upper Y Position of the Player
        :return: None
        """
        if id == self.id:
            self.first_player_y = player_rect
        else:
            self.second_player_y = player_rect

    def update_score(self, id, score):
        """
        Updates the Score of the scoring Player with ID: id
        :param id: Player ID, only own id is relevant, Opponent ID is interpreted as 3
        :param score: Updated Score of this Player
        :return: None
        """
        if id == self.id:
            self.player_score = score
        else:
            self.opponent_score = score
        self.render_font()

    def draw_players(self):
        """
        Draws players and checks ifthey need rect.draw or .blit
        :return: None
        """
        if self.player_is_skin:
            self.draw_skin_player(self.id)
        else:
            self.draw_colored_player(self.id)

        if self.opp_is_skin:
            self.draw_skin_player(3)
        else:
            self.draw_colored_player(3)
        return

    def draw_skin_player(self, id):
        """
        If Player wants a skin then blit its image
        :param id: Player ID, only own id is relevant, Opponent ID is interpreted as 3
        :return: None
        """
        if id == self.id:
            self.screen.blit(self.paddle_1, (self.first_player_x, self.first_player_y))
        else:
            self.screen.blit(self.paddle_2, (self.second_player_x, self.second_player_y))
        return

    def draw_colored_player(self, id):
        """
        If Player wants a color then draw the player a rect
        :param id: Player ID, only own id is relevant, Opponent ID is interpreted as 3
        :return: None
        """
        if id == self.id:
            pygame.draw.rect(self.screen, self.color_1, pygame.Rect(self.first_player_x, self.first_player_y, 20, 140))
        else:
            pygame.draw.rect(self.screen, self.color_2, pygame.Rect(self.second_player_x, self.second_player_y, 20, 140))
        return

    def end(self, is_won):
        """
        Renders the Game Over Screen depending on your status if you won or lost
        :param is_won: True if player won or False if player lost
        :return:
        """
        if is_won:
            self.blit_background()
            self.screen.blit(self.won, (0, 0))
            self.render_screen()
            self.render_font()
        else:
            self.blit_background()
            self.screen.blit(self.lost, (0, 0))
            self.render_screen()
            self.render_font()

"""
Ping-Pong-Icon made by:
Icons made by <a href="https://www.flaticon.com/authors/freepik" title="Freepik">Freepik</a> from <a href="https://www.flaticon.com/" title="Flaticon"> www.flaticon.com</a>
"""
