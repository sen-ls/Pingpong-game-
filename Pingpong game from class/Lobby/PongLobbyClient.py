import threading
import socket
import re
from Settings.utility import MESSAGE_ENDING, create_normal_message, create_debug_message, create_system_message, create_error_message, get_client_settings, get_common_settings
import time
import subprocess
import os


class MessageHandlingThread(threading.Thread):
    """
    This class defines a thread which handles the incoming TCP messages (i.e. chat, lobby)
    """
    def __init__(self, conn, user, buffer_size, message_encoding, message_decoding, gui_master, verbose=False):
        """
        Initialization of the message handling thread
        :param conn: Socket specifying the TCP connection to the server
        :param user: String specifying the name of the user
        :param buffer_size: Integer specifying the buffer's capacity
        :param message_encoding: String specifying the encoding scheme
        :param message_decoding: String specifying the decoding scheme
        :param gui_master: ClientMainWindow specifying the corresponding GUI
        :param verbose: Boolean specifying if additional information should be displayed
        """
        self.gui_master = gui_master
        self.user = user
        self.connection = conn
        self.buffer_size = buffer_size
        self.message_encoding = message_encoding
        self.message_decoding = message_decoding

        # Indicates if the thread is active
        self.running = True

        # Indicates if the thread terminated correctly
        self.ended = False

        # Process executing the game GUI
        self.game_client = None

        threading.Thread.__init__(self)

        # Defines the print function for verbose prints
        self.verbose_print = (lambda x: print(x)) if verbose else lambda *x: None

        # Parameters received from TCP message necessary for subprocess call
        self.player_id = None

        # Parameters received from GUI necessary for subprocess call
        self.fps = None

    def stop(self):
        """
        Stops the thread
        """
        self.running = False
        self.verbose_print('Stopping thread...')

    def handle_incoming_message(self, message):
        """
        Dummy function/Interface for game logic
        Checks for valid message patterns and executes appropriate actions
        :param message: String representing the received message
        """

#        message.replace(MESSAGE_ENDING, '')
        self.verbose_print('Handling: {}'.format(message))

        # Regular expression matching to identify message type
        message_chat_msg = re.match(r'CHAT_MSG ([A-Za-z0-9_.!]+) (L_OBBY|U_[A-Za-z0-9_.!]+|G_[A-Za-z0-9_.!]+) (.*)', message)
        message_err = re.match(r'(ERR[^ ]*) (.*)', message)
        message_available_games = re.match(r'AVAILABLE_GAMES (.*)', message)
        message_match_created = re.match(r'MATCH_CREATED', message)
        message_games = re.match(r'GAMES ([A-Za-z0-9_.!]+) (.*)', message)
        message_match_features = re.match(r'MATCH ([A-Za-z0-9_.!]+) ([A-Za-z0-9_.!]+) (.*)', message)
        message_disconnecting_you = re.match(r'DISCONNECTING_YOU (.*)', message)
        message_connection_closed = re.match(r'asdasdwa', message)
        message_match_joined = re.match(r'MATCH_JOINED (\d)', message)
        message_match_started = re.match(r'MATCH_STARTED (\d{5}) 1,(\d{1,3},\d{1,3},\d{1,3}),2,(\d{1,3},\d{1,3},\d{1,3})', message)
        message_game_ended = re.match(r'GAME_ENDED (.*)', message)

        if message_chat_msg:
            self.verbose_print(create_debug_message("Received valid CHAT_MSG"))
            if message_chat_msg.group(2) == "L_OBBY":
                prefix = "LOBBY"
            elif message_chat_msg.group(2).startswith("U_"):
                prefix = "PRIVATE"
            elif message_chat_msg.group(2).startswith("G_"):
                prefix = "MATCH"
            else:
                prefix = ""
            LobbyClient.set_chat("[{}] {}: {}".format(prefix, message_chat_msg.group(1) if message_chat_msg.group(1)!=self.user else "You", message_chat_msg.group(3)))
        elif message_err:
            self.verbose_print(create_debug_message("Received valid ERR"))
            LobbyClient.set_chat("[SYSTEM]: {} ({})".format(message_err.group(2), message_err.group(1)))
        elif message_available_games:
            self.verbose_print(create_debug_message("Received valid AVAILABLE_GAMES"))
        elif message_match_created:
            self.verbose_print(create_debug_message("Received valid MATCH_CREATED"))
            LobbyClient.set_chat(create_system_message("Your match was created."))
        elif message_games:
            self.verbose_print(create_debug_message("Received valid GAMES"))
            LobbyClient.set_open_matches(message_games.group(2).split(",") if message_games.group(2) else [])
        elif message_match_features:
            self.verbose_print(create_debug_message("Received valid MATCH_FEATURES"))
            LobbyClient.set_features(message_match_features.group(3).split(","))
        elif message_disconnecting_you or message_connection_closed:
            self.verbose_print(create_debug_message("Received valid DISCONNECTING_YOU"))
            LobbyClient.set_chat(create_system_message("Connection to server closed. ({})".format(message_disconnecting_you.group(1) if message_disconnecting_you else "Connection lost")))
            self.stop()
        elif message_match_joined:
            self.verbose_print(create_debug_message("Received valid MATCH_JOINED"))
            self.player_id = int(message_match_joined.group(1))
            LobbyClient.set_chat(create_system_message("You joined the match as Player {}".format(self.player_id)))
            self.gui_master.button_state_joined_match()
        elif message_match_started:
            self.verbose_print(create_debug_message("Received valid MATCH_CREATED"))
            # color,name,TCP_Socket,player_id,opp_color,opp_name,host_UDP
            LobbyClient.set_chat(create_system_message("Your match starts now!"))
            program_name = os.sep.join([os.path.dirname(__file__), "..", "GUIGame.py"])
            self.connection.settimeout(None)
            command = "python \"{}\" -pc {} -n {} -ip {} -udp {} -pid {} -oc {} {} -v {}".format(program_name,
                                                                                        message_match_started.group(2 if self.player_id == 1 else 3),
                                                                                        self.user,
                                                                                        self.connection.getpeername()[0],
                                                                                        int(message_match_started.group(1)),
                                                                                        self.player_id,
                                                                                        message_match_started.group(3 if self.player_id == 1 else 2),
                                                                                        "-f {}".format(self.fps) if self.fps else "",
                                                                                        1)
            self.game_client = subprocess.Popen(command,
                                                shell=True)

            def leaving_match(process):
                process.wait()
                LobbyClient.execute_command('/leaving_match User closed the window')

            threading.Thread(target=leaving_match, args=(self.game_client, )).start()

            self.connection.settimeout(1)
        elif message_game_ended:
            self.verbose_print(create_debug_message("Received valid GAME_ENDED"))
            LobbyClient.set_chat(create_system_message("Your game ended. {}".format(message_game_ended.group(1))))
            self.game_client.terminate()
            self.fps = None
            self.player_id = None

    def run(self):
        """
        Listens for incoming messages, identifies the message type and reacts appropriately
        """
        self.connection.settimeout(1)
        while self.running:
            try:
                self.verbose_print(create_debug_message('Waiting for data...'))
                data = self.connection.recv(self.buffer_size).decode(self.message_decoding)
            except ConnectionResetError:
                print(create_error_message('Connection closed by the server.'))
                self.stop()
                break
            except ConnectionRefusedError:
                print(create_error_message('Connection closed due to unreachable port.'))
                self.stop()
                break
            except socket.timeout:
                continue
            for i in data.split(MESSAGE_ENDING):
                if i:
                    self.handle_incoming_message(i)
        self.connection.close()
        self.ended = True


class LobbyClient:

    verbose = False

    verbose_print = (lambda x: print(x)) if verbose else lambda *x: None

    # Currently active MessageHandlingThread
    message_handler = None

    # Currently used TCP socket connected to server
    lobby_socket = None

    # List of names of currently open matches on the server
    open_matches = []
    # State variable to determine changes in the list
    open_matches_modified = False

    # List of names of features belonging to the requested match
    match_features = []
    # State variable to determine changes in the list
    match_features_modified = False

    # List of address tuples belonging to running servers
    lobbies = []

    # Lock used to prevent loss of chat messages
    chat_lock = threading.Lock()
    # List of chat messages received since the last GUI update
    chat = []

    @staticmethod
    def discover_lobby(demo=False):
        """
        Returns a tuple to create a socket if a answered to the UDP message is received
        :param demo: Boolean specifying whether a local (False) or remote (True) server is contacted
        :return None
        """
        # Load persistent client settings
        broadcast_address, demo_server, port, demo_port, buffer_size, features = [get_client_settings(x) for x in ['broadcast_address',
                                                                                           'demo_server',
                                                                                                   'udp_port',
                                                                                                        'demo_port',
                                                                                                   'buffer_size',
                                                                                                   'features']]

        # Load persistent common settings
        message_encoding, message_decoding = [get_common_settings(x) for x in ['message_encoding',
                                                                               'message_decoding']]

        # Create UDP socket for the UDP handshake
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        LobbyClient.verbose_print(create_debug_message('Created UDP socket for handshake.'))

        # Clear lobbies variable for consecutive discover attempts
        LobbyClient.lobbies = []

        # Send DISCOVERY message
        client_socket.sendto('DISCOVER_LOBBY{}'.format(MESSAGE_ENDING).encode(message_encoding), (demo_server if demo else broadcast_address, demo_port if demo else port))
        LobbyClient.verbose_print(create_debug_message('Sent DISCOVER message.'))
        client_socket.settimeout(1)

        # Get all responses and add them to lobbies
        while True:
            try:
                data, addr = client_socket.recvfrom(buffer_size)
                response = re.match(r'LOBBY (\d{5})' + MESSAGE_ENDING, data.decode(message_decoding))
            except socket.timeout:
                break
            except ConnectionError:
                break
            if response:
                LobbyClient.lobbies.append((addr[0], int(response.group(1))))
                LobbyClient.verbose_print(create_debug_message('Adding new lobby to lobbies.'))
        client_socket.close()
        LobbyClient.verbose_print(create_debug_message('Found lobbies: {}'.format(LobbyClient.lobbies)))
        return LobbyClient.lobbies

    @staticmethod
    def set_open_matches(list_of_match_names):
        """
        Sets the internal match list
        :param list_of_match_names: List of String specifying match names
        :return None
        """
        LobbyClient.open_matches = list_of_match_names
        LobbyClient.open_matches_modified = True
        LobbyClient.verbose_print(create_debug_message('Set open_matches to: {}'.format(list_of_match_names)))

    @staticmethod
    def get_open_matches():
        """
        Return the internal match list if it was modified recently
        :return: List of Strings representing the match names
        """
        start = time.perf_counter()
        wait_time = 5
        while not LobbyClient.open_matches_modified:
            if time.perf_counter()-start > wait_time:
                return []
            pass
        LobbyClient.open_matches_modified = False
        LobbyClient.verbose_print(create_debug_message('Get open_matches: {}'.format(LobbyClient.open_matches)))
        return LobbyClient.open_matches

    @staticmethod
    def set_chat(message):
        """
        Adds a new message to the chat
        :param message: String specifying a chat message
        :return: None
        """
        LobbyClient.chat_lock.acquire()
        LobbyClient.chat.append(message)
        LobbyClient.verbose_print(create_debug_message('Adding chat message {}'.format(message)))
        LobbyClient.chat_lock.release()

    @staticmethod
    def get_chat():
        """
        Returns the current chat list and clears it
        :return: List of Strings representing the latest chat messages
        """
        LobbyClient.chat_lock.acquire()
        chat_content = LobbyClient.chat
        LobbyClient.chat = []
        LobbyClient.chat_lock.release()
        if chat_content:
            LobbyClient.verbose_print(create_debug_message('Get chat: {}'.format(chat_content)))
        return chat_content

    @staticmethod
    def set_features(list_of_feature_names):
        """
        Sets the features of the requested match
        :param list_of_feature_names: List of Strings specifying the match's parameters
        :return: None
        """
        LobbyClient.match_features = list_of_feature_names
        LobbyClient.match_features_modified = True
        LobbyClient.verbose_print(create_debug_message('Set match_features to {}'.format(list_of_feature_names)))

    @staticmethod
    def get_features():
        """
        Returns the features of the current match if they were modified recently
        :return: List of Strings representing the match feature parameters
        """
        start = time.perf_counter()
        wait_time = 5
        while not LobbyClient.match_features_modified:
            if time.perf_counter()-start > wait_time:
                return []
            pass
        LobbyClient.match_features_modified = False
        LobbyClient.verbose_print(create_debug_message('Get match_features: {}'.format(LobbyClient.match_features)))
        return LobbyClient.match_features

    @staticmethod
    def create_command_message(command):
        """
        Translates a command line order into a valid protocol message
        :param command: String specifying the command line input
        :return: String representing the content of response
        """
        LobbyClient.verbose_print(create_debug_message("Handling: {}".format(command)))
        if command.startswith('list_games'):
            LobbyClient.verbose_print(create_debug_message("Valid list_games"))
            return 'LIST_GAMES'
        elif command.startswith('create_match'):
            arguments = re.match(r'create_match ([A-Za-z0-9_.!]+) ([A-Za-z0-9_.!]+) ([A-Za-z0-9_.!,]+)', command)
            if arguments:
                LobbyClient.verbose_print(create_debug_message("Valid create_match"))
                provided_features = map(lambda x: x.lower(), get_client_settings('features'))
                requested_features = arguments.group(3).lower().split(",")
                for i in requested_features:
                    if i not in provided_features:
                        return None
                return 'CREATE_MATCH {} {} {}'.format(*arguments.groups())
            return None
        elif command.startswith('list_matches'):
            arguments = re.match(r'list_matches ([A-Za-z0-9_.!]+)', command)
            if arguments:
                LobbyClient.verbose_print(create_debug_message("Valid list_matches"))
                return 'LIST_MATCHES {}'.format(arguments.group(1))
            return None
        elif command.startswith('match_features'):
            arguments = re.match(r'match_features ([A-Za-z0-9_.!]+)', command)
            if arguments:
                LobbyClient.verbose_print(create_debug_message("Valid match_features"))
                return 'MATCH_FEATURES {}'.format(arguments.group(1))
            return None
        elif command.startswith('join_match'):
            arguments = re.match(r'join_match ([A-Za-z0-9_.!]+) (\d{1,3},\d{1,3},\d{1,3})', command)
            if arguments:
                LobbyClient.verbose_print(create_debug_message("Valid join_match"))
                return 'JOIN_MATCH {} {}'.format(arguments.group(1), arguments.group(2))
            return None
        elif command.startswith('i_am_ready'):
            arguments = re.match(r'i_am_ready', command)
            if arguments:
                LobbyClient.verbose_print(create_debug_message("Valid i_am_ready"))
                return 'I_AM_READY'
            return None
        elif command.startswith('leaving_match'):
            arguments = re.match(r'leaving_match (.*)', command)
            if arguments:
                LobbyClient.verbose_print(create_debug_message("Valid leaving_match"))
                return 'LEAVING_MATCH {}'.format(arguments.group(1))
        else:
            LobbyClient.verbose_print(create_debug_message("Invalid command"))
            return None

    @staticmethod
    def handle_handshake(name, tcp_socket, lobby_addr, features, buffer_size, message_encoding, message_decoding):
        """
        Takes an address pair and attempts to perform a handshake
        :param name: String specifying the user name
        :param tcp_socket: Socket specifying the used connection for communication to the server
        :param lobby_addr: Tuple (String, int) specifying the ip and port to connect to
        :param features: List of Strings specifying the client's supported features
        :param buffer_size: Integer specifying the buffer's capacity
        :param message_encoding: String specifying the encoding scheme
        :param message_decoding: String specifying the decoding scheme
        :return: Match object representing the result of the regular expression matching which is None if no or invalid response was received
        """
        LobbyClient.verbose_print(create_debug_message('Initialize handshake...'))
        response = None
        try:
            tcp_socket.connect(lobby_addr)
            # Send handshake message (HELLO)
            LobbyClient.verbose_print(create_debug_message('Sending HELLO...'))
            tcp_socket.send(
                'HELLO {} {}{}'.format(name, ",".join(features), MESSAGE_ENDING).encode(message_encoding))
            tcp_socket.settimeout(5)
            LobbyClient.verbose_print(create_debug_message('Waiting for WELCOME...'))
            response = tcp_socket.recv(buffer_size)
        except ConnectionError:
            print(create_error_message('Connection error occurred.'))
            pass
        except socket.timeout:
            print(create_error_message('Timeout occurred.'))
            pass
        tcp_socket.settimeout(None)
        if response:
            # Check if handshake response is correct
            features = re.match(r'WELCOME (.*)?' + MESSAGE_ENDING, response.decode(message_decoding))
            message_disconnecting_you = re.match(r'DISCONNECTING_YOU (.*)', response.decode(message_decoding))
            if features:
                LobbyClient.verbose_print(create_debug_message("Received features: {}".format(features.group(1))))
                return features.group(1)
            elif message_disconnecting_you:
                print(create_error_message('Could not complete hand shake. Reason: {}'.format(message_disconnecting_you.group(1))))
        return None

    @staticmethod
    def union_features(server_features, client_features):
        """
        Returns a list of shared features
        :param server_features: String specifying a comma-separated list of features
        :param client_features: String specifying a comma-separated list of features
        :return: List of Strings representing the shared features
        """
        output = []
        for i in server_features.lower().split(","):
            if i in client_features.lower().split(",") and i.lower() != "basic":
                output.append(i)
        LobbyClient.verbose_print(create_debug_message("Common features: {}".format(output)))
        return output

    @staticmethod
    def connect_to_lobby(user_name, lobby_addr, gui_master):
        """
        Performs the TCP handshake, creates a MessageHandlingClient for the user, starts it and returns
        the address and common features if successful
        :param user_name: String specifying the name of the user
        :param lobby_addr: Tuple of (String, int) specifying the address pair to connect to
        :param gui_master: ClientMainWindow specifying the responsible GUI instance for the user
        :return: Tuple of (Tuple of (String, int), List of Strings) representing the address pair of the server and the common features
        """
        broadcast_address, port, buffer_size, features = [get_client_settings(x) for x in ['broadcast_address',
                                                                                                   'udp_port',
                                                                                                   'buffer_size',
                                                                                                   'features']]

        message_encoding, message_decoding = [get_common_settings(x) for x in ['message_encoding',
                                                                               'message_decoding']]
        if lobby_addr:
            name = user_name
            # Terminate a currently running MessageHandlingThread
            if LobbyClient.message_handler:
                LobbyClient.message_handler.stop()
                while not LobbyClient.message_handler.ended:
                    pass
            try:
                # Perform TCP handshake
                LobbyClient.lobby_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                LobbyClient.verbose_print(create_debug_message('Connecting to lobby {}'.format(lobby_addr)))
                server_features = LobbyClient.handle_handshake(name, LobbyClient.lobby_socket, lobby_addr, features, buffer_size, message_encoding, message_decoding)

                # Check if handshake successful
                if server_features:
                    LobbyClient.verbose_print(create_debug_message('Valid handshake.'))
                    LobbyClient.message_handler = MessageHandlingThread(LobbyClient.lobby_socket, name, buffer_size, message_encoding, message_decoding, gui_master, LobbyClient.verbose)
                    LobbyClient.message_handler.start()
                    LobbyClient.verbose_print(create_debug_message('Lobby joined'))
                else:
                    LobbyClient.verbose_print(create_debug_message('Invalid handshake'))
                    return None, None
            except ConnectionError:
                LobbyClient.verbose_print(create_debug_message('Connection lost during TCP Handshake'))
                return None, None
            return lobby_addr, LobbyClient.union_features(server_features, ",".join(get_client_settings('features')))
        else:
            # no lobby found return Error
            LobbyClient.verbose_print(create_debug_message('No lobby address given.'))
            return None, None

    @staticmethod
    def end_client():
        """
        Method for GUI to stop a currently running MessageHandlingThread
        :return: None
        """
        if LobbyClient.message_handler:
            LobbyClient.message_handler.stop()

    @staticmethod
    def execute_command(command):
        """
        Provides an interface for the GUI to use already implemented console commands
        :param command: String representing a console command
        :return: None
        """
        # Loads common settings
        message_encoding, message_decoding = [get_common_settings(x) for x in ['message_encoding',
                                                                               'message_decoding']]
        # Check if application should stop
        if command == '/quit':
            LobbyClient.verbose_print(create_debug_message('Connecting to lobby'))
            LobbyClient.message_handler.stop()
        elif LobbyClient.lobby_socket:
            # Check if command or chat message
            if command.startswith('/'):
                message = LobbyClient.create_command_message(command[1:])
                # Check if command was correct
                if message:
                    message = message.encode(message_encoding)
                    LobbyClient.lobby_socket.sendall(message + '{}'.format(MESSAGE_ENDING).encode(message_encoding))
                    create_system_message("Sending: {}".format(message))
                else:
                    create_error_message('Could not execute \'{}\''.format(command))
            else:
                # Regular expressions to determine receiver
                chat_message_user = re.match(r'u:([A-Za-z0-9_.!]+) ([A-Za-z0-9_.! ]+)', command)
                chat_message_game = re.match(r'g:([A-Za-z0-9_.!]+) ([A-Za-z0-9_.! ]+)', command)

                if chat_message_user:
                    message = 'CHAT_MSG U_'.encode(message_encoding) + chat_message_user.group(1).encode(
                        message_encoding) + " ".encode(message_encoding) + chat_message_user.group(2).encode('utf-8')
                elif chat_message_game:
                    message = 'CHAT_MSG G_'.encode(message_encoding) + chat_message_game.group(1).encode(
                        message_encoding) + " ".encode(message_encoding) + chat_message_game.group(2).encode('utf-8')
                else:
                    message = 'CHAT_MSG L_OBBY '.encode(message_encoding) + command.encode('utf-8')
                LobbyClient.lobby_socket.sendall(message + '{}'.format(MESSAGE_ENDING).encode(message_encoding))


def main():
    
    """
    Main loop:
    - reads all necessary information from the settings.json file
    - discovers a lobby (DISCOVER_LOBBY & LOBBY XY)
    - cconnects to the received lobby
    - creates and sends HELLO message to server
    """
    broadcast_address, port, buffer_size, features = [get_client_settings(x) for x in ['broadcast_address',
                                                                                     'udp_port',
                                                                                     'buffer_size',
                                                                                     'features']]

    message_encoding, message_decoding = [get_common_settings(x) for x in ['message_encoding',
                                                                           'message_decoding']]

    # Find lobby
    lobby_addr = LobbyClient.discover_lobby(True)
    # Check if lobby found
    if lobby_addr:
        lobby_addr = lobby_addr[0]
        create_normal_message('Found lobby!')
        # Enable command line input
        input_loop_running, message_handler, lobby_socket, chat_message = True, None, None, ''
        while input_loop_running:
            if message_handler and message_handler.running:
                message = input('')
                chat_message = message.lower()
            if not message_handler or not message_handler.running:
                while True:
                    retry_connection = input("Connection to server closed. Do you want to reconnect? (y/n)\t" if message_handler else "Connecting to lobby? (y/n)\t")
                    if retry_connection.lower() == 'y':
                        try:
                            name = input('Enter your username:\t')
                            lobby_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            server_features = LobbyClient.handle_handshake(name, lobby_socket, lobby_addr, features, buffer_size, message_encoding, message_decoding)
                            if server_features:
                                create_system_message('Valid handshake...')
                                message_handler = MessageHandlingThread(lobby_socket, name, buffer_size, message_encoding, message_decoding, False)
                                message_handler.start()
                                create_normal_message('You joined the lobby!')
                                break
                        except ConnectionError:
                            continue
                    elif retry_connection.lower() == 'n':
                        create_system_message('Closing client...')
                        input_loop_running = False
                        break
            else:
                if chat_message == '/quit':
                    create_system_message('You left the lobby!')
                    message_handler.stop()
                    continue
                if lobby_socket:
                    chat_message_user = re.match(r'u:([A-Za-z0-9_.!]+) ([A-Za-z0-9_.! ]+)', chat_message)
                    chat_message_game = re.match(r'g:([A-Za-z0-9_.!]+) ([A-Za-z0-9_.! ]+)', chat_message)
                    if chat_message.startswith('/'):
                        message = LobbyClient.create_command_message(chat_message[1:])
                        if message:
                            message = message.encode(message_encoding)
                            lobby_socket.sendall(message + '{}'.format(MESSAGE_ENDING).encode(message_encoding))
                        else:
                            create_error_message('Could not execute \'{}\''.format(chat_message))
                    else:
                        if chat_message_user:
                            message = 'CHAT_MSG U_'.encode(message_encoding) + chat_message_user.group(1).encode(
                                message_encoding) + " ".encode(message_encoding) + chat_message_user.group(2).encode('utf-8')
                        elif chat_message_game:
                            message = 'CHAT_MSG G_'.encode(message_encoding) + chat_message_game.group(1).encode(
                                message_encoding) + " ".encode(message_encoding) + chat_message_game.group(2).encode('utf-8')
                        else:
                            message = 'CHAT_MSG L_OBBY '.encode(message_encoding) + chat_message.encode('utf-8')
                        lobby_socket.sendall(message + '{}'.format(MESSAGE_ENDING).encode(message_encoding))
    else:
        # no lobby found
        create_error_message('Could not connect to server.')
