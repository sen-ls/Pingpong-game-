import socket
import threading
import re
import utility


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
        (Use of multiple attributes instead of global variables to enable dynamic tests
        and expandability (e.g. load balancing, multiple lobbies, etc.))
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
        self.verbose = verbose
        threading.Thread.__init__(self)

    def create_response(self, message):
        """
        Returns the respective response depending on the validity of the received message
        :param message: String specifying the received decoded message
        :return: String representing the appropriate reponse
        """
        if message == 'DISCOVER_LOBBY{}'.format(self.message_ending):
            return 'LOBBY {}{}'.format(self.tcp_port, self.message_ending)
        else:
            return 'ERR_CMD_NOT_UNDERSTOOD{}'.format(self.message_ending)

    def run(self):
        """
        Creates a socket, binds to the provided address and port, waits for incoming
        UDP messages and sends a response back
        """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        server_socket.bind((self.ip, self.udp_port))

        print('Server listening on {}:{}'.format(self.ip, self.udp_port))
        while True:
            try:
                data, addr = server_socket.recvfrom(self.buffer_size)
                print('[{}]: {}'.format(addr[0], data.decode(self.message_decoding)))
            except ConnectionError:
                print('Connection to {} was closed during transmission'.format(addr))
                continue
            server_socket.sendto(self.create_response(data.decode(self.message_decoding)).encode(self.message_encoding), addr)


class ClientHandlingThread(threading.Thread):
    """
    This class defines a thread which handles the received messages from a client.
    Current state: Command line interaction
    TODO: Rewrite and integrate into GUI
    """
    # List of user connections of chat participants
    user_list = []

    def __init__(self, connection, user, buffer_size, message_ending, message_encoding, message_decoding, verbose=False):
        """
        Initialization of the client handling thread;
        (Use of multiple attributes instead of global variables to enable dynamic tests
        and expandability (e.g. private chats in separated windows,
         separation of functionalities in general, etc.))
        :param connection: Socket specifying the TCP connection end point
        :param user: String specifying the user name
        :param buffer_size: Integer specifying the buffer's capacity
        :param message_ending: String specifying the protocol dependant message delimiter
        :param message_encoding: String specifying the encoding scheme
        :param message_decoding: String specifying the decoding scheme
        :param verbose: Boolean specifying if more output is requested
        """
        self.connection = connection
        self.user = user
        self.buffer_size = buffer_size
        self.message_ending = message_ending
        self.message_encoding = message_encoding
        self.message_decoding = message_decoding
        # Adding new user connection to list of lobby participants
        ClientHandlingThread.user_list.append(connection)
        threading.Thread.__init__(self)
        self.start()

    def run(self):
        """
        Receives messages from clients, categorizes them and invokes the required behaviour until the
        user closes its client
        TODO: Extend range of received and sent message types
        """
        while True:
            #TODO: Check for different message type patterns, decompose and compute the content, generate new message
            # to implement: AVAILABLE_GAMES MATCH_CREATED GAMES MATCH MATCH_JOINED
            # maybe at another spot: MATCH_STARTED GAME_ENDED (talk with game development group)
            try:
                data = self.connection.recv(self.buffer_size).decode(self.message_decoding)
                message = re.match(r'CHAT_MSG (L_OBBY|U_[A-Za-z0-9_.!]+|G_[A-Za-z0-9_.!]+) (.*)' + self.message_ending, data)
                if message:
                    for i in ClientHandlingThread.user_list:
                        #TODO: Receiver handling and UTF-8
                        i.send('CHAT_MSG {} {} {}{}'.format(
                            self.user, message.group(1), message.group(2), self.message_ending).encode(self.message_encoding))
            except ConnectionResetError:
                print('{} left the chat.'.format(self.user))
                ClientHandlingThread.user_list.remove(self.connection)
                break


def set_up_tcp_socket(bind_address, tcp_port, connections_amount=1):
    """
    Sets up a listening standard tcp socket with the given parameters
    (Convenience function)
    :param bind_address: String specifying the address to listen to
    :param tcp_port: Integer specifying the port to listen to
    :param connections_amount: Integer specifying the amount of allowed concurrent connections
    :return: Socket representing a TCP socket with given attributes
    """
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind((bind_address, tcp_port))
    tcp_socket.listen(connections_amount)
    return tcp_socket


def main():
    """
    Main loop:
    - reads all necessary information from the settings.json file
    - initializes and starts the discovery thread (DISCOVER_LOBBY & LOBBY XY)
    - creates a TCP socket and listens to it to enable interaction with user
    - welcomes users and starts respective client handling thread
    """
    bind_address, udp_port, tcp_port, buffer_size, features = [
        utility.get_server_settings(x) for x in ['bind_address',
                                                 'udp_port',
                                                 'tcp_port',
                                                 'buffer_size',
                                                 'features']]

    message_encoding, message_decoding = [utility.get_common_settings(x) for x in ['message_encoding',
                                                                                   'message_decoding']]
    # Start thread that handles UDP messages
    DiscoveryHandlingThread(bind_address,
                            udp_port,
                            tcp_port,
                            buffer_size,
                            utility.MESSAGE_ENDING,
                            message_encoding,
                            message_decoding).start()

    # Create socket that handles TCP messages
    lobby_socket = set_up_tcp_socket(bind_address, tcp_port)

    # List of client handling threads
    threads = []

    while True:
        conn, addr = lobby_socket.accept()
        data = conn.recv(buffer_size)
        response = re.match(r'HELLO ([A-Za-z0-9_.!]*) BASIC(.*)' + utility.MESSAGE_ENDING, data.decode('ascii'))
        # Check if handshake message is correct
        if response:
            # Create and send handshake answer
            print('{} joined the lobby.'.format(response.group(1)))
            conn.send('WELCOME {}{}'.format(
                ",".join([",".join([i.get('name')] + [str(i) for i in i.get('parameters')]) for i in features]),
                utility.MESSAGE_ENDING).encode('ascii'))
            # Take care of client with respective thread
            threads.append(ClientHandlingThread(conn,
                                                response.group(1),
                                                buffer_size,
                                                utility.MESSAGE_ENDING,
                                                message_encoding,
                                                message_decoding))
        else:
            # invalid handshake message received; send error
            conn.send('ERR_CMD_NOT_UNDERSTOOD{}'.format(utility.MESSAGE_ENDING).encode('ascii'))


if __name__ == "__main__":
    main()
