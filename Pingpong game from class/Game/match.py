import Settings.utility as utility
import socket
import math
import time
#import pygame
#pygame.init()

from Game.pong.logic import Logic
from Game.pong.player import Player
from Game.pong.Geometry import Ball


class Match(object):
    """
    The main class of the pong match including the server. 
    The main loop is located here.
    """
    def __init__(self, game_type, game_name, features, udp_port):
        """
        Initialization of a Match object used to hold and perform a match
        :param game_type: String specifying the type of game
        :param game_name: String specifying the name of the match
        :param features: List of String specifying the features and parameters
        :param udp_port: Integer specifying the udp port number
        """
        # Organizational variables
        self.game_type = game_type
        self.game_name = game_name
        self.udp_port = udp_port
        if not isinstance(self.udp_port, int):
            raise TypeError("UDP-Port has to be an integer!")

        #Assigns all possible features and processes them.
        """ Possible Features: 
            Challenge: Increases Ball_speed over time
            Speed: Gives Speed of Ball
        """
        self.challenge = False
        self.challenge_type = 1
        self.assign_features(features)

        # Game logic initialization
        self._logic = Logic(self.ball_speed)
        self.ball_no = 1
        self.ball_seq = 0
        self.game_ended = False
        self.first_player, self.second_player = None, None
        self.player_seq = 0
        self.ball_velocity_update = 660 / self.challenge_type

        # Holds all participants as player objects
        self.player_list = []
        self.buffer_size = 1400 #Correct maximum buffer

        # UDP socket for match
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.server_socket.bind(("0.0.0.0", self.udp_port))

        # timeout in seconds
        self.timeout_value = 1/20
        self.server_socket.settimeout(self.timeout_value)

        self.start_time = None
        self.end_time = None
        self.timer = 0

        print(utility.create_system_message('Match \'{}\' created. Listening for UDP messages on {}:{}'.format(self.game_name, "0.0.0.0", self.udp_port)))
        #TODO: Print has to be replaced by a signal to see if match creation was successful
        #TODO: Raise Exception als Signal?

    def assign_features(self, features):
        """
        Checks which Features the game should have and processes them in attributes
        :param features: String, Containing Strings and their String Values
        :return None:
        """
        feature_list = features.split(",")
        for i in range(0, len(feature_list)):
            if feature_list[i] == "CHALLENGE":
                self.challenge = True
                self.challenge_type = int(feature_list[i+1]) + 1
            elif feature_list[i] == "SPEED":
                self.ball_speed = int(feature_list[i+1])
            self.features = features
        return

    def get_udp_port(self):
        """
        Returns the udp port where the server expects incoming messages
        :return: Integer representing an udp port number
        """
        return self.udp_port

    def players_ready(self):
        """
        Returns if all players are ready
        :return: Boolean which is true if all players are ready
        """
        return len(self.player_list) == 2 and all(map(lambda x: x.is_ready, self.player_list))

    def match_full(self):
        """
        Returns if enough players joined the game
        :return: Boolean which is true if two players participate in a game
        """
        return len(self.player_list) == 2

    def add_player(self, name, player_color, tcp_socket):
        """
        adds players and creates the GUI once both players have joined
        :param name: String specifying the name of the player
        :param player_color: Triple of Integers (Red, Green, Blue) specifying the color of the players padel
        :param tcp_socket: Socket specifying the client's tcp socket connected to the lobby, for SCORE_UPDATE
        :return: Boolean which is True if a player could be added
        """
        if not self.first_player:
            self.first_player = Player(player_color, name, tcp_socket, 1)
            self.player_list.append(self.first_player)
#            print("Player 1: {} added".format(name))
            return True
        elif not self.second_player:
            self.second_player = Player(player_color, name, tcp_socket, 2)
            self.player_list.append(self.second_player)
#            print("Player 2: {} added".format(name))
            self.is_full = True
            return True
        else:
            return False

    def remove_player(self, name):
        """
        Removes a player from a match if he exists
        :param name: String specifying the player's name
        :return:
        """
        for (player_name, player) in list(map(lambda x: (x.name, x), self.player_list)):
            if player_name == name:
                self.player_list.remove(player)
                if self.first_player == player:
                    self.first_player = None
                else:
                    self.second_player = None
                return True
        return False

    def get_player_info(self, type_of_info):
        """
        Returns information about joined players
        Keys:
                "length": returns amount of players in Match
                "names": returns List with names of both players (in order?)
        TODO: Can be updated with new get methods
        TODO: Decide for output format (most-likely string)
        :param type_of_info: String specifying the key
        :return Integer/String representing the requested value if the key exists
        """
        if type_of_info == "length":
            return len(self.player_list)
        elif type_of_info == "names":
            player_names = []
            for player in self.player_list:
                player_names.append(player.name)
            return player_names            
        else:
            return "This parameter is unknown"

    def get_player_list(self):
        """
        Returns players
        :return: List of Player objects representing the match participants
        """
        return self.player_list

    def match_player_ip(self, ip):
        """
        Matches Player ip addresses against ip addresses of incoming messages
        :param ip: String specifying the ip address of an incoming message
        """
        for player in self.player_list:
            if ip == player.ip:
                return player.id
        return None

    def keys_pressed(self, keys, player_id):
        """
        Methods executes KEYS_PRESSED Command
        :param keys: List of Strings specifying a comma separated key list
        :param player: Player object specifying the sender of the command, which has to be updated
        """
        player = self.player_list[player_id-1]
        keys_split = keys.split(",")
        if len(keys_split) > 0:
            for key in keys_split:
                self.player_list[player_id-1] = self._logic.player_update(player, key)
        return

    def check_for_valid_command(self, command, player_id):
        """
        Matches Commands against existing commands and executes them if they are valid
        Only valid command: [SEQ] KEYS_PRESSED [List<Keys>]
        :param command: String specifying a command without message ending
        :param player: Player object specifying the sender of the message
        """
        command_split = command.split(" ")
        if not (command_split[1] == "KEYS_PRESSED"):
            return

        self.player_list[player_id-1].seq = int(command_split[0])
        self.keys_pressed(command_split[2], player_id)      

    def handle_messages(self, commands, ip_address):
        """
        Handles Protocol Messages
        :param commands: Byte array specifying an encoded message from an udp datagram
        :param ip_address: String specifying the ip address of the sender
        :return Player object representing the player belonging to the given ip address
        """
        player_id = self.match_player_ip(ip_address)
        if not (player_id == 1 or player_id == 2):
            return None
        
        command_dec = commands.decode("ascii")
        single_message_list = command_dec.split(utility.MESSAGE_ENDING)
        if not len(single_message_list) == 1:
            single_message_list = single_message_list[:- 1]
        for command in single_message_list:
            self.check_for_valid_command(command, player_id)
        return player_id
        
    def set_udp_port(self, addr):
        """
        Tries to set UDP_Port of incoming message to a player. Only used until either both UDP_Ports are known or
        a certain time period passed
        :param addr: String specifying the address the user to add the port to
        :return Boolean which is True if a valid ip was received
        """
        if self.first_player.has_udp_port() and self.second_player.has_udp_port():
            return False
        if addr:
            if addr[0] == self.first_player.ip and not self.first_player.has_udp_port(): #necessary for 2 player test on one device
                self.first_player.set_udp_port(addr[1])
                print("First Player UDP: {}".format(addr))
            elif addr[0] == self.second_player.ip and not self.second_player.has_udp_port():
                if self.second_player.ip != self.first_player.ip or self.second_player.ip == self.first_player.ip and self.first_player.udp_port != addr[1]:
                    print("Second Player UDP: {}".format(addr))
                    self.second_player.set_udp_port(addr[1])
#            print("Das darf nicht sein!!!!!!!!!!!!!!!!!!!!!!!!!")
        return True

    #TODO: Comments
    def update_ball(self, ball):
#        if not self.start_time:
#            self.start_time = time.perf_counter()
#        self.end_time = time.perf_counter()
#        time_passed = self.end_time - self.start_time
        message = " UPDATE_BALL %s %s %s %s %s%s" % (self.ball_no, int(ball.x), int(ball.y), int(ball.v * math.cos(ball.angle)), int(ball.v * -math.sin(ball.angle)), utility.MESSAGE_ENDING)
        self.send_udp_message(message, True)
        self.start_time = self.end_time

    #TODO: Y_V implementieren 
    def update_player(self, player):
        message = " UPDATE_PLAYER %s %s %s %s %s%s" % (player.id, player.x, player.y, 0, 5, utility.MESSAGE_ENDING)
        self.send_udp_message(message, False)

    def send_udp_message(self, message, ball):
        for player in self.player_list:
            if player.udp_port:
#                print("Updates: ", str(self.ball_seq if ball else self.player_seq), message)
                mes_enc = (str(self.ball_seq if ball else self.player_seq) + message).encode("ascii")
                self.server_socket.sendto(mes_enc, (player.ip, player.udp_port))
        if ball:
            self.ball_seq += 1
        else:
            self.player_seq += 1

    def update_score(self, score, player_id):
        """
        Updates the score and sends the changed score 'score' of the player 
        with id 'player_id' to both players via the established TCP_Socket
        And resets the Ball velocity to its start value
        :param score: Integer with the score of the scoring player
        :param player_id: Integer which is the Player ID of the scoring player
        :return None
        """
        self._logic.reset_velocity(self.ball_speed)
        message = "SCORE_UPDATE %s %s%s" % (player_id, score, utility.MESSAGE_ENDING)
#        print("Message: ", message)
        mes_enc = message.encode("ascii")
        try:
            self.first_player.tcp_socket.sendall(mes_enc)
            self.second_player.tcp_socket.sendall(mes_enc)
        except OSError:
            self.game_ended = True
            print("Verbindung durch Client getrennt")
        #TODO: Test


    def execute_update(self, command, address_tuple):
        """
        Executes the update 

        :param score: Integer with the score of the scoring player
        :param player_id: Integer wgich is the Player ID of the scoring player
        :return None
        """
        if address_tuple:
            ip_address = address_tuple[0]
            player_id = self.handle_messages(command, ip_address)
            if player_id:
                self.update_player(self.player_list[player_id-1])

    def send_ball_update(self):
        """
        Receives Current State from the Logic and sends a ball_update to the Clients
        :return:
        """
        first_player_score_diff, second_player_score_diff, ball = self._logic.get_state(self.player_list)
        if first_player_score_diff == 1 or second_player_score_diff == 1:
            self.ball_no += 1
            if first_player_score_diff == 1:
                self.update_score(self.first_player.score, 1)
            else:
                self.update_score(self.second_player.score, 2)
        self.update_ball(ball)
        if(self.ball_seq % self.ball_velocity_update == 0 and self.challenge):
            self._logic.increase_velocity()

    def handle_i_am_ready(self, data, id):
        """
        Method Checks for incoming TCP I_AM_READY message and makes the Clients status to raedy
        :param data: Received encoded message
        :param id: Player ID of the Player that sent the message
        :return:
        """
        message = data.decode("ascii")
        commands = message.split(utility.MESSAGE_ENDING)
        commands = commands[:-1]
        for command in commands:
            if command == "I_AM_READY":
                self.player_list[id-1].set_ready()

    def run(self):
        """
        Main method of this class.
        It tries to match UDP_ports to players and execute commands and updates only players with known UDP_Ports
        ->
        Executes incoming commands and updates both players
        """
        starting_players = self.player_list.copy()

        # Clear buffers
        #time.sleep(4)
        try:
            self.server_socket.recvfrom(self.buffer_size)
            self.server_socket.recvfrom(self.buffer_size)
        except ConnectionError:
            pass
        except socket.timeout:
            pass

        while not self.players_ready():
            pass

        """Starts Timer to send Ball_Updates"""
        self.timer = time.perf_counter()
        print("Timer started, both are ready")

        udp_set = False

        while not self.game_ended:
            if time.perf_counter() - self.timer >= 0.03:
                self.send_ball_update()
                self.timer = time.perf_counter()

            try:
                comm, addr = self.server_socket.recvfrom(self.buffer_size)
                if not udp_set:
                    udp_set = not self.set_udp_port(addr)
                self.execute_update(comm, addr)
            except socket.timeout:
                pass
            except ConnectionError:
                print('Connection was closed during run loop in match')
                break
            if not self.first_player or not self.second_player or self.first_player.score >= 11 or self.second_player.score >= 11:
                self.game_ended = True

        message_match_ended = "GAME_ENDED {}"
        for i in starting_players:
            message = "You won" if self.first_player == i and (self.first_player.score >= 11 or not self.second_player)\
                                   or self.second_player == i and (self.second_player.score >= 11 or not self.first_player) else "You lost"
            i.get_tcp_socket().sendall((message_match_ended.format(message) + utility.MESSAGE_ENDING).encode("ascii"))

#        print("Game is Over")

    """   if time.perf_counter() - self.timer >= 0.03:
            self.send_ball_update()
            self.timer = time.perf_counter()
            
                        for event in pygame.event.get():
                if event.type == pygame.USEREVENT + 1:
                    self.send_ball_update()
    """
