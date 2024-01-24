# -*- coding: utf-8 -*-
"""
Created on Fri May 29 18:46:02 2020

@author: Nikolas,Sen
"""
import sys
import pygame
import socket
import time
import os

os.environ['SDL_VIDEODRIVER'] = 'windib'
pygame.init()

import Settings.utility as utility
from pygame.locals import *
from Game.pong.gui import Gui
from Game.pong.player import Player


class Client(Player):
    def __init__(self, color, name, host_ip, host_UDP, player_id, features, opp_color, dims, fps, moving_speed):
        Player.__init__(self, color, name, None, player_id)
        self.opponent = Player(opp_color, "Opponent", None, player_id+1) # each Client creates an Opponent
        self.ip = host_ip
        self.set_left_pos()
        self.UDP_Port = host_UDP
        self.key_list = ""
        self.dy = 0
        self.game = True
        self.clock = pygame.time.Clock()
        self.ball_no = 1

        self.assign_features(features)

        self.dims = [800, 600]
        self.ball_x = self.dims[0] / 2

        #TODO: TEST
        self.x_ratio = 800 / dims[0]
        self.y_ratio = 600 / dims[1]

        self.start = None
        self.send_event = pygame.USEREVENT + 1
        self.render_event = pygame.USEREVENT + 2
        self.inv_FPS = int(1000/fps) #(1 / FPS)*

        #TODO: Fix console problem
        self._gui = Gui(self.color, self.name, self.opponent.color, self.opponent.name, self.id, self.ball_size)

        self.moving_speed = moving_speed #Has to be given by server or default = 2

        self.timer = 0

        self.ready = ("I_AM_READY" + utility.MESSAGE_ENDING).encode("ascii")

        self.timeout_value = 0.001
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        successful = False
        port = 57000
        while not successful:
            print("Testing: {}".format(port))
            try:
                self.client_socket.bind(("0.0.0.0", port))
                successful = True
            except OSError:
                port = max(((port + 1) % 65536), 1025)
                continue
        self.client_socket.settimeout(self.timeout_value)
        self.buffer_size = 1400
        print("Finished initialization")

    def assign_features(self, features):
        """
        Assigns the features to the right format
        :param features: Can have any features that we accepted
        :return: None
        """
        """for i in range(0, len(features)):
            if features[i] == "DIMS":
                self.x_ratio = 800. / float(features[i+1])
                self.y_ratio = 600. / float(features[i+2])
            elif features[i] == "BALL_SIZE":
        self.ball_size = int(features[i+1])
        """
        self.ball_size = features
        return

    def send_keys(self):
        """
        Sends the keys list to the match server via UDP and adds sequence number to it
        :return: None
        """
        message = "{} KEYS_PRESSED {}".format(self.seq, self.key_list[:-1] if self.key_list else self.key_list)
        message_enc = message.encode("ascii")

        self.client_socket.sendto(message_enc, (self.ip, self.UDP_Port))
        self.change_pos(self.id, self.dy)
        self.key_list = ""
        self.seq += 1
        self.dy = 0

    def _process_events(self):
        """
        Processes all pygame Events.
        KEYS: Fills key_list with UP and DOWN

        """
        key = pygame.key.get_pressed()
        if key[K_UP]:
            self.key_list += "UP,"
            self.dy -= self.moving_speed

        if key[K_DOWN]:
            self.key_list += "DOWN,"
            self.dy += self.moving_speed

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("QUIT")
                self.client_socket.close()
                sys.exit()

            elif event.type == self.send_event:
                self.send_keys()

            elif event.type == self.render_event:
                self.render_gui()

    def change_pos(self, player_num, dy):
        """
        Change Player positions, changes them already without consent of server but can correct it afterwards
        :param player_num: Player_id
        :param dy: change in y direction
        :return: None
        """
        if player_num == self.id:
            if (self.y + dy >= 0 and self.y + dy <= self.dims[1] - 140):
                self.move_ip(dy)
                self._gui.update_player(player_num, self.y)
            else:
                if(dy < 0):
                    dy = -self.y
                else:
                    dy = 460 - self.y
                self.move_ip(dy)
                self._gui.update_player(player_num, self.y)
        else:
            self.opponent.move_ip(dy)
            self._gui.update_player(player_num, self.opponent.y)
        return

    def update_player(self, command):
        """
        Calculates dy for the change of position for the players
        :param command: includes which player needs to be updated and how much
        :return: None
        """
        y_server = int(self.y_ratio * int(command[4]))
        if int(command[2]) == self.id:
            dy = y_server - int(self.y)
        else:
            dy = y_server - int(self.opponent.y)
        if not dy == 0:
            self.change_pos(int(command[2]), dy)
        return

    def update_score(self):
        """
        Checks which Player gets the point
        :return: None
        """
        if self.ball_x < 150:
            id = 2
            if self.id == 1:
                self.opponent.score += 1
                score = self.opponent.score
            else:
                self.score += 1
                score = self.score
        else:
            id = 1
            if self.id == 2:
                self.opponent.score += 1
                score = self.opponent.score
            else:
                self.score += 1
                score = self.score
        self._gui.update_score(id, score)

        if self.score >= 11 or self.opponent.score >= 11:
            self.game = False

        return

    def update_ball(self, command):
        """
        Updates the ball, if ball number changes the TCP_SOCKET will be opened to receive
        :param command: Received command including ball number and velocity
        :return: None
        """
        ball_x = int(self.x_ratio * int(command[3]))
        ball_y = int(self.y_ratio * int(command[4]))
        self._gui.update_ball(ball_x, ball_y, command[5], command[6])
        if not self.ball_no == int(command[2]):
            self.update_score()
            self.ball_no = int(command[2])
        self.ball_x = ball_x
        return

    def handle_comm(self, comm):
        """
        Handles all incoming UDP messages
        :param comm: Received Command
        :return:
        """
        comm_dec = comm.decode("ascii")
        comm_list = comm_dec.split(utility.MESSAGE_ENDING)
        comm_list = comm_list[:-1]
        for command in comm_list:
            split_list = command.split(" ")
            if split_list[1] == "UPDATE_PLAYER":
                self.update_player(split_list)
            elif split_list[1] == "UPDATE_BALL":
                self.update_ball(split_list)
            else:
                print("invalid command")
        self.clock.tick()
        return

    def display_time(self):
        """
        Displays the time from when the GUI starts
        :return: None
        """
        self._gui.display_time(time.perf_counter()-self.start)
        return

    def render_gui(self):
        """
        Renders the GUI and depending on dimensions uses an image or just a color
        :return: None
        """
        self._gui.blit_background()
        self._gui.render_parts()
        self.display_time()

    def run(self):
        """
        Main (run) method will first wait for the server to send an update, then starts synchronous timers and handles the game flow
        :return: None
        """
        print("Start client logic")

        self.start = time.perf_counter()

        self.send_keys()
        self.render_gui()
        self._gui.render_screen()
        self._gui.render_font()

        start = time.perf_counter()

        while self.game:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("QUIT")
                    self.client_socket.close()
                    pygame.quit()
                    sys.exit()

            if time.perf_counter() - start > 0.25:
                self.send_keys()
                self.render_gui()
                self._gui.render_screen()
                self._gui.render_font()
                start = time.perf_counter()
            try:
                self.client_socket.recvfrom(self.buffer_size)
                break
            except socket.timeout:
                continue
            except ConnectionError:
                continue


        pygame.time.set_timer(self.send_event, 50)
        pygame.time.set_timer(self.render_event, self.inv_FPS)

        # Main Game Loop
        while self.game:
            self._process_events()

            try:
                comm, addr = self.client_socket.recvfrom(self.buffer_size)
                self.handle_comm(comm)
            except socket.timeout:
                continue
            except ConnectionError:
                self.game = False
                continue

        # Determine who won if Game ended regularly
        if self.score >= 11:
            won = True
            game_over_screen = True
        elif self.opponent.score >= 11:
            won = False
            game_over_screen = True
        else:
            game_over_screen = False

        #Close Socket
        self.client_socket.close()

        start = time.perf_counter()
        while game_over_screen:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("QUIT Game Over Screen")
                    game_over_screen = False

            if time.perf_counter() - start > 0.25:
                self._gui.end(won)
                start = time.perf_counter()

        print("Closing GUI")
        pygame.quit()
        sys.exit()
