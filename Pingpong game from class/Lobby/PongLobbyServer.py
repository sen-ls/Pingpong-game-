import socket
import threading
import re
import time
from Settings.utility import create_system_message, create_debug_message, create_error_message, get_common_settings, get_server_settings, MESSAGE_ENDING
from Game.match import Match
from Miscellaneous.ReadWriteLock import ReadWriteLock


class DiscoveryHandlingThread(threading.Thread):
    """
    This class defines a thread which handles the discovery of the lobby
    maintained by the server. If a correct request is sent, the server
    answers with a valid response including the used port number. Otherwise
    an error is submitted.
    """
    def __init__(self, ip, udp_port, tcp_port, buffer_size, message_ending, message_encoding, message_decoding, verbose=False):
        """
        Initialization of the discovery thread;
        :param ip: String specifying the ip to bind the udp socket to
        :param udp_port: Integer specifying the port where UDP traffic is expected
        :param tcp_port: Integer specifying the port we announce to the client
        :param buffer_size: Integer specifying the buffer's capacity
        :param message_ending: String specifying the protocol dependant message delimiter
        :param message_encoding: String specifying the encoding scheme
        :param message_decoding: String specifying the decoding scheme
        :param verbose: Boolean specifying if more output is requested
        """
        self.ip = ip
        self.udp_port = udp_port
        self.tcp_port = tcp_port
        self.buffer_size = buffer_size
        self.message_ending = message_ending
        self.message_encoding = message_encoding
        self.message_decoding = message_decoding

        # Defines the print function for verbose prints
        self.verbose_print = (lambda x: print(x)) if verbose else lambda *x: None

        # Indicates if the thread is active
        self.running = True
        threading.Thread.__init__(self)

    def create_response(self, message):
        """
        Returns the respective response depending on the validity of the received message
        :param message: String specifying the received decoded message
        :return: String representing the appropriate reponse
        """
        self.verbose_print(create_debug_message('Answering message {} on discovery port'.format(message)))
        if message == 'DISCOVER_LOBBY{}'.format(self.message_ending):
            return 'LOBBY {}{}'.format(self.tcp_port, self.message_ending)
        else:
            return 'ERR_CMD_NOT_UNDERSTOOD{}'.format(self.message_ending)

    def stop(self):
        """
        Stops the thread
        """
        self.running = False
        self.verbose_print(create_system_message('Stopping discovery thread...'))

    def run(self):
        """
        Creates a socket, binds to the provided address and port, waits for incoming
        UDP messages and sends a response back
        """
        self.verbose_print(create_debug_message('Setting up socket...'))

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        # Loop to tackle server port release delay
        while True:
            try:
                server_socket.bind((self.ip, self.udp_port))
                break
            except OSError:
                pass
        server_socket.settimeout(1)

        print(create_system_message('Server listening for UDP messages on {}:{}'.format(self.ip, self.udp_port)))
        while self.running:
            try:
                data, addr = server_socket.recvfrom(self.buffer_size)
                print(create_system_message('[{}]: {}'.format(addr[0], data.decode(self.message_decoding))))
            except ConnectionError:
                print(create_error_message('Connection to {} was closed during transmission'.format(addr)))
                continue
            except socket.timeout:
                continue
            server_socket.sendto(self.create_response(data.decode(self.message_decoding)).encode(self.message_encoding), addr)
        print(create_system_message('Discovery thread shut down.'))


class MatchHandlingThread(threading.Thread):
    """
    This class defines a thread which handles a Match object. It is responsible for
    sending the MATCH_STARTED message as soon as two players joined the match, running the match
    and cleaning up afterwards.
    """
    def __init__(self, match, message_encoding, verbose=False):
        """

        :param match:
        :param message_encoding:
        :param verbose:
        """
        self.match = match
        self.message_encoding = message_encoding
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.verbose_print = (lambda x: print(x)) if verbose else lambda *x: None

    @staticmethod
    def create_message_match_started(udp_port, color_list):
        """
        Returns the message content for MATCH_STARTED
        :param udp_port: Integer specifying an udp port for the match
        :param color_list: List of two Triplets (R,G,B) specifying the colors of the participants
        :return: String representing the message content
        """
        return 'MATCH_STARTED {} {}'.format(udp_port, ",".join(['1'] + [",".join(color_list[0])] + ['2'] + [",".join(color_list[1])]))

    def run(self):
        while not self.match.match_full():
            pass
        colors = list(map(lambda x: x.get_color(), self.match.get_player_list()))
        message_match_started = self.create_message_match_started(self.match.get_udp_port(), colors)
        time.sleep(2)
        self.verbose_print(create_system_message(message_match_started))
        try:
            for i in self.match.get_player_list():
                i.get_tcp_socket().sendall((message_match_started + MESSAGE_ENDING).encode(self.message_encoding))
            # Wait for a second to let threads throw socket.timeout and restart loop
            print(create_system_message("Starting match \'{}\'".format(self.match.game_name)))
            time.sleep(1)
            #TODO: Get GAME_ENDED message into loop form match.py
            self.match.run()
        except ConnectionError:
            print(create_error_message("Could not start match \'{}\' due to ConnectionError."))
            pass
        ClientHandlingThread.remove_match(self.match)
        ClientHandlingThread.free_udp_port(self.match.udp_port)
        print(create_system_message('Match thread for match \'{}\' shut down.'.format(self.match.game_name)))


class ClientHandlingThread(threading.Thread):
    """
    This class defines a thread which handles the received messages from a client.
    Current state: Command line interaction
    """
    # Constant for user name until handshake is complete
    initial_user_name = '<Anonymous user>'

    # List of chat participants as tuples (name, socket)
    user_list_lock = ReadWriteLock()
    user_list = []

    # List of open matches as DummyMatches
    open_match_lock = ReadWriteLock()
    open_match = []

    # List of available udp ports
    open_udp_ports_lock = ReadWriteLock()
    open_udp_ports = []
    for port in range(54010, 54101):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.bind(('', port))
            s.close()
        except OSError:
            continue
        open_udp_ports.append(port)

    @staticmethod
    def check_match_name_taken(name):
        """
        Checks if the list of matches contains a match with the given name
        :param name: String specifying the name of a match
        :return: Boolean which is True if the name is taken
        """
        ClientHandlingThread.open_match_lock.acquire_read_lock()
        for i in ClientHandlingThread.open_match:
            if i.game_name == name:
                ClientHandlingThread.open_match_lock.release_read_lock()
                return True
        ClientHandlingThread.open_match_lock.release_read_lock()
        return False

    @staticmethod
    def get_player_id(match_name):
        """
        Returns the amount players in a match and returns the value as ID for the least new user
        :param match_name: String specifying the name of a match
        :return: Integer representing the ID for the requesting client
        """
        return len(ClientHandlingThread.find_match(match_name).player_list)

    @staticmethod
    def create_match(kind, name, feature, udp_port):
        #TODO: DELETE standard feature
        """
        Creating new match, adding it to the open match list, give the responsibility to a thread and start it
        :return: Boolean if game was created
        """

        ClientHandlingThread.open_match_lock.acquire_write_lock()
        if udp_port:
            new_match = Match(kind, name, feature, udp_port)
            ClientHandlingThread.open_match.append(new_match)
            match_handler = MatchHandlingThread(new_match, get_common_settings('message_encoding'))
            match_handler.setDaemon(True)
            match_handler.start()
            ClientHandlingThread.open_match_lock.release_write_lock()
            return True
        else:
            ClientHandlingThread.open_match_lock.release_write_lock()
            return False

    @staticmethod
    def check_match_full(match_name):
        """
        Dummy function
        Checks if a match has already enough players
        :param match_name: String specifying the name of the match
        :return: Boolean which is True if the match has enough participants
        """
        match = ClientHandlingThread.find_match(match_name)
        return len(match.player_list) > 1 if match else True

    @staticmethod
    def find_match(match_name):
        """
        Searches a match with the given match name
        :param match_name: String specifying the name of the requested match
        :return: Match object representing the match with the requested name if the name exists
        """
        ClientHandlingThread.open_match_lock.acquire_read_lock()
        matches = ClientHandlingThread.open_match
        ClientHandlingThread.open_match_lock.release_read_lock()
        for i in matches:
            if i.game_name == match_name:
                return i
        return None

    @staticmethod
    def get_user_match(user_name):
        """
        Searches a match with the given user name in the list of participants
        :param user_name: String specifying the user name
        :return: Match object representing the match with the requested user if the user is contained anywhere
        """
        ClientHandlingThread.open_match_lock.acquire_read_lock()
        matches = ClientHandlingThread.open_match
        ClientHandlingThread.open_match_lock.release_read_lock()
        for i in matches:
            if user_name in [j.name for j in i.player_list]:
                return i
        return None

    @staticmethod
    def get_player_instance_of_user(user_name):
        """
        Searches the player instance of the user with the given name
        :param user_name: String specifying the user name
        :return: Player object representing the user with the given name if it exists
        """
        ClientHandlingThread.open_match_lock.acquire_read_lock()
        matches = ClientHandlingThread.open_match
        ClientHandlingThread.open_match_lock.release_read_lock()

        for i in matches:
            for j in i.player_list:
                if j.name == user_name:
                    return j
        return None

    @staticmethod
    def get_user_names():
        """
        Returns a List with the names of connected users
        :return: List of String representing names of connected users
        """
        ClientHandlingThread.user_list_lock.acquire_read_lock()
        return_message = [i[0] for i in ClientHandlingThread.user_list]
        ClientHandlingThread.user_list_lock.release_read_lock()
        return return_message

    @staticmethod
    def get_user_sockets():
        """
        Returns all sockets of connected users
        :return: List of Sockets representing connections to users
        """
        ClientHandlingThread.user_list_lock.acquire_read_lock()
        return_message = [i[1] for i in ClientHandlingThread.user_list]
        ClientHandlingThread.user_list_lock.release_read_lock()
        return return_message

    @staticmethod
    def get_user_sockets_of(list_of_names):
        """
        Returns all sockets that belong to provided user names
        :param list_of_names: List of Strings specifying potential user names
        :return: List of Sockets representing available sockets for the given list
        """
        ClientHandlingThread.user_list_lock.acquire_read_lock()
        users = ClientHandlingThread.user_list
        ClientHandlingThread.user_list_lock.release_read_lock()

        user_sockets = []
        for i in users:
            if i[0] in list_of_names:
                user_sockets.append(i[1])
        return user_sockets

    @staticmethod
    def reserve_udp_port():
        """
        Returns and removes an element of the open poprt range
        :return: Integer representing a open udp port
        """
        # Get port
        ClientHandlingThread.open_udp_ports_lock.acquire_write_lock()
        try:
            reserved_port = ClientHandlingThread.open_udp_ports.pop(0)
        except IndexError:
            reserved_port = None
        ClientHandlingThread.open_udp_ports_lock.release_write_lock()
        # Check if available port exists
        if reserved_port:
            # Check if port is still unused
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                s.bind(('', reserved_port))
                s.close()
            except OSError:
                s.close()
                reserved_port = ClientHandlingThread.reserve_udp_port()
        return reserved_port

    @staticmethod
    def free_udp_port(port):
        """
        Frees a given udp port if not open already
        :param port: Integer specifying a port number to free
        :return: Boolean which is true if port was freed
        """
        ClientHandlingThread.open_udp_ports_lock.acquire_write_lock()
        if port in ClientHandlingThread.open_udp_ports:
            ClientHandlingThread.open_udp_ports_lock.release_write_lock()
            return False
        ClientHandlingThread.open_udp_ports.append(port)
        ClientHandlingThread.open_udp_ports_lock.release_write_lock()
        return True

    @staticmethod
    def add_player_to_match(match_name, player_name, player_color, tcp_socket):
        """
        Adds a player to a specified match
        :param match_name: String specifying the name of the match
        :param player_name: String specifying the player name
        :param player_color: Triple (Red, Green, Blue) specifying the player's color
        :param tcp_socket: Socket specifying the connection to the lobby
        :return: Boolean which is True if player could be added
        """
        match = ClientHandlingThread.find_match(match_name)
        if match:
            return match.add_player(player_name, player_color, tcp_socket)
        return False

    @staticmethod
    def remove_match(match):
        """
        Removes match from known matches
        :param match: Match specifying a pong match
        """
        ClientHandlingThread.open_match_lock.acquire_write_lock()
        try:
            ClientHandlingThread.open_match.remove(match)
        except ValueError:
            pass
        ClientHandlingThread.open_match_lock.release_write_lock()

    @staticmethod
    def remove_connection_tuple(connection_tuple):
        """
        Removes socket from known sockets
        :param connection_tuple: Tuple (String, Socket, ClientHandlingThread) specifying the connection tuple (name, corresponding socket) to delete
        """
        ClientHandlingThread.user_list_lock.acquire_write_lock()
        try:
            ClientHandlingThread.user_list.remove(connection_tuple)
        except ValueError:
            pass
        ClientHandlingThread.user_list_lock.release_write_lock()

    @staticmethod
    def get_responsible_thread_for_user(name):
        """
        Returns the ClientHandlingThread for the given user name
        :param name: String specifying the user name the search client is responsible for
        :return: ClientHandlingThread representing the responsible thread for the given user
        """
        ClientHandlingThread.user_list_lock.acquire_read_lock()
        users = ClientHandlingThread.user_list
        ClientHandlingThread.user_list_lock.release_read_lock()

        for i in users:
            if name == i[0]:
                return i[2]
        return None

    def __init__(self, connection, features, buffer_size, message_ending, message_encoding, message_decoding, verbose=False):
        """
        Initialization of the client handling thread;
        :param connection: Socket specifying the TCP connection end point
        :param features: List of dictionaries specifying a feature provided by the server per dictionary
        :param buffer_size: Integer specifying the buffer's capacity
        :param message_ending: String specifying the protocol dependant message delimiter
        :param message_encoding: String specifying the encoding scheme
        :param message_decoding: String specifying the decoding scheme
        :param verbose: Boolean specifying if more output is requested
        """
        ClientHandlingThread.user_list_lock.acquire_write_lock()
        self.connection = connection
        self.features = features
        self.buffer_size = buffer_size
        self.message_ending = message_ending
        self.message_encoding = message_encoding
        self.message_decoding = message_decoding

        # Defines the print function for verbose prints
        self.verbose_print = (lambda x: print(x)) if verbose else lambda *x: None

        # Indicates if the thread is active
        self.running = True
        self.user = ClientHandlingThread.initial_user_name

        threading.Thread.__init__(self)

    def leave_match(self):
        """
        removes the client from the current match
        :return: None
        """
        match = ClientHandlingThread.get_user_match(self.user)
        if match:
            match.remove_player(self.user)
            print(create_system_message("\'{}\' left \'{}\'.".format(self.user, match.game_name)))

    def update_user_name(self):
        """
        Inserts the correct name for the stored connection_tuple
        @:return: Boolean which is True if user name could be updated
        """
        ClientHandlingThread.user_list_lock.acquire_write_lock()
        try:
            ClientHandlingThread.user_list.remove((ClientHandlingThread.initial_user_name, self.connection, self))
            ClientHandlingThread.user_list_lock.release_write_lock()
        except ValueError:
            ClientHandlingThread.user_list_lock.release_write_lock()
            return False
        if self.user not in ClientHandlingThread.get_user_names():
            ClientHandlingThread.user_list.append((self.user, self.connection, self))
            ClientHandlingThread.user_list_lock.release_write_lock()
            return True
        else:
            ClientHandlingThread.user_list_lock.release_write_lock()
            return False

    def handle_handshake(self):
        """
        Waits for a HELLO message of the client, verifies it and sends a WELCOME message back
        """
        # Creating waiting time for the handshake initiation
        self.connection.settimeout(60)

        data = ""
        # Waiting for HELLO message
        try:
            self.verbose_print('Waiting for incoming handshake...')
            data = self.connection.recv(self.buffer_size)
        except ConnectionError:
            create_error_message('Could not perform handshake due to connection error')
            self.stop()
        except socket.timeout:
            create_error_message('Client timed out during handshake')
            self.stop()
        self.connection.settimeout(None)

        # Verifying HELLO message
        response = re.match(r'HELLO ([A-Za-z0-9_.!]*) (.*)' + MESSAGE_ENDING, data.decode('ascii'))
        if response and "basic" in response.group(2).lower():
            self.user = response.group(1)
            self.verbose_print('Received valid HELLO message from client {}.'.format(self.user))

            # Check if user already exists
            if self.update_user_name():

                # Create and send handshake answer
                try:
                    self.verbose_print(create_debug_message('Sending WELCOME message to {}...'.format(self.user)))
                    self.connection.send('WELCOME {}{}'.format(
                        ",".join([",".join([i.get('name')] + [str(i) for i in i.get('parameters')]) for i in self.features]),
                        MESSAGE_ENDING).encode('ascii'))
                except ConnectionError:
                    print(create_error_message('Could not complete handshake with {} due to connection error.'.format(self.user)))
                    self.stop()
                print(create_system_message('\'{}\' joined the lobby.'.format(self.user)))
            else:
                print(create_error_message('{} already taken.'.format(self.user)))
                self.user = ClientHandlingThread.initial_user_name
                self.connection.send('DISCONNECTING_YOU Name already taken.{}'.format(MESSAGE_ENDING).encode(self.message_encoding))
                self.stop()
        else:
            # invalid handshake message received; send error
            self.verbose_print('Received invalid handshake message.')
            self.connection.send('ERR_CMD_NOT_UNDERSTOOD{}'.format(MESSAGE_ENDING).encode(self.message_encoding))
            self.stop()

    def check_features(self, feature_string):
        """
        Checks if the server provides requested features
        :param feature_string: String specifying a comma-separated list holding features
        :return: Boolean which is true if all features are provided by the server
        """
        self.verbose_print('Checking features in {}'.format(feature_string))
        requested_features = feature_string.lower().split(",")
        provided_features = map(lambda x: x.get('name').lower(), self.features)
        for i in requested_features:
            if i not in provided_features:
                return False
        return True

    def create_response(self, message):
        """
        Matches a message to message types, verifies the message format and creates the encoded response content
        :param message: String specifying a received message
        :return: String specifying an adequate encoded response
        """
        self.verbose_print('Creating response for {}'.format(message))

        message_list_games = re.match(r'LIST_GAMES', message)
        message_create_match = re.match(r'CREATE_MATCH ([A-Za-z0-9_.!]+) ([A-Za-z0-9_.!]+) ([A-Za-z0-9_.!,]+)', message)
        message_chat_msg = re.match(r'CHAT_MSG (L_OBBY|U_[A-Za-z0-9_.!]+|G_[A-Za-z0-9_.!]+) (.*)', message)
        message_list_matches = re.match(r'LIST_MATCHES ([A-Za-z0-9_.!]+)', message)
        message_match_features = re.match(r'MATCH_FEATURES ([A-Za-z0-9_.!]+)', message)
        message_join_match = re.match(r'JOIN_MATCH ([A-Za-z0-9_.!]+) (\d{1,3},\d{1,3},\d{1,3})', message)
        message_i_am_ready = re.match(r'I_AM_READY', message)
        message_leaving_match = re.match(r'LEAVING_MATCH (.*)', message)

        response = ""
        receiver = [self.connection]

        if message_list_games:
            response = 'AVAILABLE_GAMES Pong'
        elif message_create_match:
            if message_create_match.group(1).lower() != 'pong':
                response = "ERR_FAILED_TO_CREATE Support for {} is not provided.".format(message_create_match.group(1).lower())
            elif self.check_match_name_taken(message_create_match.group(2)):
                response = "ERR_FAILED_TO_CREATE A match with your chosen name already exists."
            elif not self.check_features(message_create_match.group(3).lower()):
                response = "ERR_FAILED_TO_CREATE Your requested features are not supported."
            elif self.create_match(message_create_match.group(1), message_create_match.group(2), "CHALLENGE,1,SPEED,50", ClientHandlingThread.reserve_udp_port()):
                """elif self.create_match(message_create_match.group(1), message_create_match.group(2), message_create_match.group(3), ClientHandlingThread.reserve_udp_port()):"""
                response = 'MATCH_CREATED'
            else:
                response = 'ERR_FAILED_TO_CREATE Currently no UDP port is available to host your match.'
        elif message_chat_msg:
            if message_chat_msg.group(1) == "L_OBBY":
                receiver = ClientHandlingThread.get_user_sockets()
            elif message_chat_msg.group(1).startswith("U_"):
                name = message_chat_msg.group(1).replace("U_", "", 1)
                receiver = ClientHandlingThread.get_user_sockets_of([name])
            elif message_chat_msg.group(1).startswith("G_"):
                game = ClientHandlingThread.find_match(message_chat_msg.group(1).replace("G_", "", 1))
                receiver = ClientHandlingThread.get_user_sockets_of(list(map(lambda x: x.get_name(), game.get_player_list()))) if game else []
            response = 'CHAT_MSG {} {} {}{}'.format(self.user, message_chat_msg.group(1), message_chat_msg.group(2), self.message_ending)
        elif message_list_matches:
            matches = []
            for i in self.open_match:
                if i.game_type.lower() == message_list_matches.group(1).lower() and not i.match_full():
                    matches.append(i.game_name)
            response = 'GAMES {} {}{}'.format(message_list_matches.group(1), ",".join(matches), self.message_ending)
        elif message_match_features:
            send = None
            for i in self.open_match:
                if i.game_name == message_match_features.group(1):
                    send = i
                    break
            response = 'MATCH {} {} {}{}'.format(send.game_type, send.game_name, send.features, self.message_ending) \
                if send else 'ERR_GAME_NOT_EXIST The match \'{}\' does not exist.'.format(message_match_features.group(1))
        elif message_join_match:
            match_name = message_join_match.group(1)
            if ClientHandlingThread.get_user_match(self.user) is None:
                if self.check_match_name_taken(match_name):
                    if not self.check_match_full(match_name):
                        if ClientHandlingThread.add_player_to_match(match_name, self.user, tuple(message_join_match.group(2).split(",")), ClientHandlingThread.get_user_sockets_of(self.user)[0]):
                            response = "MATCH_JOINED {}".format(self.get_player_id(match_name))
                        else:
                            response = "ERR_FAILED_TO_JOIN The server was not able to add another player to the match."
                    else:
                        response = "ERR_FAILED_TO_JOIN The chosen match is already full."
                else:
                    response = "ERR_FAILED_TO_JOIN The chosen match does no longer exist."
            else:
                response = "ERR_FAILED_TO_JOIN You are already in another match."
            print(create_system_message("\'{}\' could not join match \'{}\'. {}".format(
                self.user, match_name, " ".join(response.split(" ")[1:])) if response.startswith("ERR")
                                        else "\'{}\' joined \'{}\'.".format(self.user, match_name)))
        elif message_i_am_ready:
            player = ClientHandlingThread.get_player_instance_of_user(self.user)
            if player:
                player.set_ready(self.user)
            receiver = []
        elif message_leaving_match:
            self.leave_match()
        elif not message:
            response = message
            receiver = []
        else:
            response = 'ERR_CMD_NOT_UNDERSTOOD'
        if message:
            self.verbose_print(create_system_message('Received:\t{}'.format(message)))
            self.verbose_print(create_system_message('Sent:\t\t{}'.format(response)))
            self.verbose_print('Sent to {} user'.format(len(receiver)))

        return (response.encode(self.message_encoding) if not message_chat_msg else
                (" ".join(response.split(' ')[:2]) + " ").encode(self.message_encoding)
                + " ".join(response.split(' ')[2:]).encode('utf-8')), receiver

    def stop(self):
        """
        Stops the thread
        """
        self.leave_match()
        self.running = False
        ClientHandlingThread.remove_connection_tuple((self.user, self.connection, self))
        self.connection.close()
        print(create_system_message('{} left the lobby.'.format(self.user)))
        self.verbose_print('Stopping thread...')

    def run(self):
        """
        Receives messages from clients, categorizes them and invokes the required behaviour until the
        user closes its client
        """
        # Adding new user connection to list of lobby participants
        self.verbose_print('Adding new connection to connection list')
        ClientHandlingThread.user_list_lock.acquire_write_lock()
        ClientHandlingThread.user_list.append((self.user, self.connection, self))
        ClientHandlingThread.user_list_lock.release_write_lock()

        self.handle_handshake()
        if self.running:
            self.connection.settimeout(1)
        while self.running:
            try:
                self.verbose_print('Waiting for incoming data from {}...'.format(self.user))
                data = self.connection.recv(self.buffer_size).decode(self.message_decoding)
                if not data:
                    self.verbose_print('Connection was closed by client')
                    self.stop()
                    continue
                for i in data.split(self.message_ending):
                    if i:
                        response, receiver_list = self.create_response(i)
                        for receiver_socket in receiver_list:
                            receiver_socket.sendall(response)
                        self.verbose_print('Sent message to all {} receivers'.format(len(receiver_list)))
            except ConnectionError:
                self.stop()
                continue
            except OSError:
                continue
            except socket.timeout:
                continue
        print(create_system_message('Client thread shut down.'))


def set_up_tcp_socket(bind_address, tcp_port, connections_amount=10, timeout=1):
    """
    Sets up a listening standard tcp socket with the given parameters
    (Convenience function)
    :param bind_address: String specifying the address to listen to
    :param tcp_port: Integer specifying the port to listen to
    :param connections_amount: Integer specifying the amount of allowed concurrent connections
    :param timeout: Float specifying the amount of seconds for the socket timeout
    :return: Socket representing a TCP socket with given attributes
    """
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            tcp_socket.bind((bind_address, tcp_port))
            break
        except OSError:
            pass
    tcp_socket.listen(connections_amount)
    tcp_socket.settimeout(timeout)
    return tcp_socket


class ServerThread(threading.Thread):
    """
    This class defines a server thread which is responsible for creating a UDP discovery thread
    and accepting new TCP connections from clients
    """
    def __init__(self, verbose=False):
        """
        Initializes a ServerThread object
        :param verbose: Boolean specifying whether a more detailed output should be provided
        """
        threading.Thread.__init__(self)
        self.running = True
        self.verbose = verbose

    def stop(self):
        """
        Stops the thread
        :return: None
        """
        self.running = False

    def run(self):
        """
        Reads all necessary information from the settings.json file, initializes and starts
        the discovery thread (DISCOVER_LOBBY & LOBBY XY), creates a TCP socket and listens
        to it to enable interaction with user and starts respective client handling thread
        :return None
        """
        # Load server settings
        bind_address, udp_port, tcp_port, buffer_size, features = [
            get_server_settings(x) for x in ['bind_address',
                                                     'udp_port',
                                                     'tcp_port',
                                                     'buffer_size',
                                                     'features']]
        # Load common settings
        message_encoding, message_decoding = [get_common_settings(x) for x in ['message_encoding',
                                                                                'message_decoding']]
        # Start thread that handles UDP messages
        discovery_thread = DiscoveryHandlingThread(bind_address,
                                                   udp_port,
                                                   tcp_port,
                                                   buffer_size,
                                                   MESSAGE_ENDING,
                                                   message_encoding,
                                                   message_decoding)
        discovery_thread.start()

        # Create socket that handles TCP messages
        lobby_socket = set_up_tcp_socket(bind_address, tcp_port)
        print(create_system_message("Server listening for TCP messages on {}:{}".format(bind_address, tcp_port)))

        # List of client handling threads
        threads = []

        while self.running:
            try:
                conn, addr = lobby_socket.accept()

                # Take care of client with respective thread
                new_client_thread = ClientHandlingThread(conn,
                                                    features,
                                                    buffer_size,
                                                    MESSAGE_ENDING,
                                                    message_encoding,
                                                    message_decoding, self.verbose)
                new_client_thread.start()
                threads.append(new_client_thread)
            except socket.timeout:
                pass
            except KeyboardInterrupt:
                self.running = False

        # Close all threads
        discovery_thread.stop()
        for i in threads:
            if i.running:
                i.stop()
        print(create_system_message('Server shut down.'))


def main():
    """
    Starts and runs a ServerThread
    :return: None
    """
    server = ServerThread()
    server.run()


if __name__ == "__main__":
    main()
