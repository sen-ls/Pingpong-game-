import threading
import socket
import re
import utility


def discover_lobby(address, port, buffer_size, message_encoding, message_decoding):
    """
    Returns a tuple to create a socket if a answered to the UDP message is received
    :param address: String specifying the ip address to send to
    :param port: Integer specifying the port number to send to
    :param buffer_size: Integer specifying the buffer's capacity
    :return: Tuple (String, Integer) representing the ip address and port of the incoming message
    TODO: Handle multiple received answers
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    client_socket.sendto('DISCOVER_LOBBY{}'.format(utility.MESSAGE_ENDING).encode(message_encoding), (address, port))
    client_socket.settimeout(5)
    try:
        data, addr = client_socket.recvfrom(buffer_size)
        client_socket.close()
        response = re.match(r'LOBBY (\d{5})'+utility.MESSAGE_ENDING, data.decode(message_decoding))
    except socket.timeout:
        print('No answer to lobby discovery received.')
        return None
    return (addr[0], int(response.group(1))) if response else None


class MessageHandlingThread(threading.Thread):
    """
    This class defines a thread which handles the incoming messages (e.g. chat, lobby/game messages)
    TODO: Extend range of received and sent message types
    """
    def __init__(self, conn, user, buffer_size, message_encoding, message_decoding, verbose=False):
        """
        Initialization of the message handling thread
        (Use of multiple attributes instead of global variables to enable dynamic tests
        and expandability (e.g. load balancing, etc.))
        :param conn: Socket specifying the TCP connection to the server
        :param user: String specifying the name of the user
        :param buffer_size: Integer specifying the buffer's capacity
        :param message_encoding: String specifying the encoding scheme
        :param message_decoding: String specifying the decoding scheme
        """
        self.user = user
        self.connection = conn
        self.buffer_size = buffer_size
        self.message_encoding = message_encoding
        self.message_decoding = message_decoding
        self.verbose = verbose
        threading.Thread.__init__(self)

    def run(self):
        """
        Listens for incoming messages, identifies the message type and reacts appropriately
        """
        while True:
            try:
                data = self.connection.recv(self.buffer_size).decode(self.message_decoding)
                message = re.match(
                    r'CHAT_MSG ([A-Za-z0-9_.!]+) (L_OBBY|U_[A-Za-z0-9_.!]+|G_[A-Za-z0-9_.!]+) (.*)'+utility.MESSAGE_ENDING, data)
                if message and message.group(1) != self.user:
                    print('{}: {}'.format(message.group(1), message.group(3)))
            except ConnectionResetError:
                print('Connection closed by the server.')
                break
            except ConnectionRefusedError:
                print('Connection closed due to unreachable port.')
                break


def main():
    """
    Main loop:
    - reads all necessary information from the settings.json file
    - discovers a lobby (DISCOVER_LOBBY & LOBBY XY)
    - cconnects to the received lobby
    - creates and sends HELLO message to server
    """
    broadcast_address, port, buffer_size = [utility.get_client_settings(x) for x in ['broadcast_address',
                                                                                     'udp_port',
                                                                                     'buffer_size']]

    message_encoding, message_decoding = [utility.get_common_settings(x) for x in ['message_encoding',
                                                                                   'message_decoding']]

    # Find lobby
    lobby_addr = discover_lobby(broadcast_address, port, buffer_size, message_encoding, message_decoding)
    # Check if lobby found
    if lobby_addr:
        print('Found lobby!')
        lobby_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Connecting to lobby...')
        try:
            lobby_socket.connect(lobby_addr)
            lobby_socket.settimeout(5)
            name = input('Username:\t')
            # Send handshake message (HELLO)
            lobby_socket.send('HELLO {} BASIC{}'.format(name, utility.MESSAGE_ENDING).encode(message_encoding))
            reponse = lobby_socket.recv(buffer_size)
            # Check if handshake reponse is correct
            #TODO: Check union of client features and server features
            features = re.match(r'WELCOME BASIC(.*)?'+utility.MESSAGE_ENDING, reponse.decode(message_decoding))
            if features:
                print('You joined the lobby!')
                # Start thread to handle incoming messages
                MessageHandlingThread(lobby_socket, name, buffer_size, message_encoding, message_decoding).start()
                # Enable command line input
                #TODO: Replace command line input with button binds on GUI (but for now command line is fine)
                while True:
                    #TODO: Place to implement message sending by checking chat_message for certain pattern
                    # suggested pattern -> /list_games /create_game /list_matches /match_features /join_match
                    chat_message = input('')
                    if chat_message == '/quit':
                        break
                    lobby_socket.sendall('CHAT_MSG L_OBBY '.encode(message_encoding)
                                         + chat_message.encode('utf-8')
                                         + '{}'.format(utility.MESSAGE_ENDING).encode(message_encoding))
            else:
                print('Could not join the lobby...')
        except ConnectionRefusedError:
            print('Could not join lobby due to closed port {}'.format(lobby_addr[1]))
        except socket.timeout:
            print('Did not receive any answer from {}'.format(":".join(lobby_addr)))
    else:
        # no lobby found
        print('Error: Could not connect to {}'.format(lobby_addr))


if __name__ == "__main__":
    main()
