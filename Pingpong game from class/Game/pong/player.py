# -*- coding: utf-8 -*-
"""
Created on Fri May 22 17:28:21 2020

@author: Nikolas
"""


class Player(object):
    def __init__(self, color, name, tcp_socket, player_id):
        """
        Initialization of the player object used in a match object as participants
        :param color: Triple of Integers (Red, Green, Blue) specifying the color of the player
        :param name: String specifying the user's name
        :param score: Integer specifying the user's score
        :param tcp_socket: Socket specifying the user's tcp socket to the lobby
        :param first_player: Boolean specifying whether the player is the first or second player
        """
        self.color = color
        self.name = name
        self.score = 0
        self.tcp_socket = tcp_socket
        self.is_joined = True

        # Initial values
        if tcp_socket is None:
            self.ip = None
        else:
            self.ip = tcp_socket.getpeername()[0]
        self.is_ready = False

        self.y = 230
        self.angles = [60,45,30,0,-30,-45,-60]
        self.x = 50

        # PLayer ID specific
        self.id = player_id
        """
        if self.id == 1:
            self.udp_port = 50000
        else:
            self.set_right_pos()
            self.udp_port = 50001
        """
        self.udp_port = None

        #Has valid UDP-Port so even if Port is not known, the code doesn't throw errors
        self.udp_port_init = False
        self.seq = 0

    def is_player_joined(self):
        """
        Returns if Player has already joined a game, so that he can't join multiple Games at the same time
        :return: None
        """
        return self.is_joined

    def move_ip(self, dy):
        self.y += dy
        return

    def get_name(self):
        """
        Returns the player's name
        :return: String representing the player's name
        """
        return self.name

    def set_ready(self, ready=True):
        """
        Marks the player as ready
        :param ready: Boolean specifying the ready state to set to
        """
        self.is_ready = ready
            
    def set_udp_port(self, udp_port):
        """
        Gives each player its UDP_Port for the server to send the data to
        :param udp_port: Integer specifying the udp port number
        """
        self.udp_port = udp_port
        self.udp_port_init = True
   
    def has_udp_port(self):
        """
        Checks if a udp port is assigned
        :return: Boolean which is True if udp port is initialized
        """
        return self.udp_port_init

    def add_point(self):
        self.score += 1
        return self.score

    def get_tcp_socket(self):
        """
        Returns the tcp socket
        :return: Socket specifying the connection tot the lobby
        """
        return self.tcp_socket

    def get_color(self):
        """
        Returns RGB color
        :return: Triple of Integers (Red, Green, Blue) representing a color
        """
        return self.color
    
    def set_left_pos(self):
        """
        Sets Padel position to the left
        """
        self.x = 50

    def set_right_pos(self):
        """
        Sets Padel position to the right
        """
        self.x = 750

