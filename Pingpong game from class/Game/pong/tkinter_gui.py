import re
import tkinter
import os
import random
from Settings.utility import MESSAGE_ENDING
import socket
import threading
import time

frequency = 1 / 60


def create_udp_socket():
    port = 50000
    while True:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.bind(('', port))
            print("Port: ", port)
            return s
        except OSError:
            port = max(1025, port + 1) % 65536
            continue


class SendingThread(threading.Thread):
    def __init__(self, gamegui):
        super().__init__()
        self.running = True
        self.gamegui = gamegui

    def stop(self):
        self.running = False

    def run(self):
        while self.running:
            if self.gamegui.key_list:
                message = '{} KEYS_PRESSED {}'.format(self.gamegui.seq_no, ",".join(self.gamegui.key_list))
    #            print("GameGUI sending: ", message)
                self.gamegui.udp_socket.sendto(message.encode("ascii"), (self.gamegui.tcp_socket.getpeername()[0], self.gamegui.match_udp))
                self.gamegui.change_position(self.gamegui.player_id, self.gamegui.dy)
                self.gamegui.dy = 0
                self.gamegui.key_list = []
                self.gamegui.seq_no += 1
            time.sleep(frequency)
        print("Sender thread ended.")


class UDPReceiverThread(threading.Thread):
    def __init__(self, gamegui):
        super().__init__()
        self.running = True
        self.gamegui = gamegui
        self.ball_seq = 0
        self.player_seq = 0

    def stop(self):
        self.running = False

    def run(self):
        while self.running:
            try:
                data = self.gamegui.udp_socket.recv(1400).decode("ascii")
                for i in data.split(MESSAGE_ENDING):
                    if i:
    #                    print("UDPReceiver: ", i)
                        message_update_ball = re.match(r'(.*) UPDATE_BALL (.*) (.*) (.*) (.*) (.*)', i)
                        message_update_player = re.match(r'(.*) UPDATE_PLAYER (.*) (.*) (.*) (.*) (.*)', i)
                        if message_update_ball:
                            if int(message_update_ball.group(2)) > self.gamegui.ball_number:
                                self.gamegui.ball_number = int(message_update_ball.group(2))
                            if self.ball_seq < int(message_update_ball.group(1)):
                                self.gamegui.update_ball(int(float(message_update_ball.group(3))), int(float(message_update_ball.group(4))))
                                self.ball_seq = int(message_update_ball.group(1))
                        elif message_update_player:
                            if self.player_seq < int(message_update_player.group(1)):
                                self.gamegui.update_player(int(float(message_update_player.group(2))), int(float(message_update_player.group(4))))
                                self.player_seq = int(message_update_player.group(1))
            except socket.timeout:
                pass
            except OSError:
                break
            time.sleep(1/30)
        print("UDP Receiving thread ended.")


class TCPReceiverThread(threading.Thread):
    def __init__(self, gamegui):
        super().__init__()
        self.running = True
        self.gamegui = gamegui

    def stop(self):
        self.running = False

    def run(self):
        while self.running:
            try:
                messages = (self.gamegui.tcp_socket.recv(1000)).decode("ascii")
                message_list = messages.split(MESSAGE_ENDING)
                message_list = message_list[:- 1]
                for message in message_list:
#                    print("TCPReceiver: ", message)
                    command = message.split(" ")
                    if int(command[1]) == self.gamegui.player_id:
                        self.gamegui.left_score_value.set(command[2])
                    else:
                        self.gamegui.right_score_value.set(command[2])
                    if int(command[2]) >= 11:
                        self.gamegui.game = False
                        self.stop()
            except socket.timeout:
                pass
            except ConnectionError:
                print("GAME ENDED")
                self.gamegui.game = False
                self.stop()
            time.sleep(frequency)
        print("TCP Receiving thread ended.")


class GameGUI(tkinter.Toplevel):
    def __init__(self, color, name, TCP_Socket, player_id, opp_color, host_UDP, dims=[800, 600], moving_speed = 5, master=None):
        super().__init__(master)

        # Game state
        self.game = True
        self.is_ready = False

        # Game Logic
        self.dy = 0
        self.moving_speed = moving_speed

        # Unused
        self.color = color
        self.opponent_color = opp_color

        # Player info
        self.player_id = player_id
        if self.player_id == 2:
            self.is_treated_as_right_side = True
        else:
            self.is_treated_as_right_side = False
        self.tcp_socket = TCP_Socket
        self.tcp_socket.settimeout(0.01)

        # UDP connection info outgoing
        self.match_udp = host_UDP
        self.seq_no = 0
        self.sending_interval = 50

        # UDP connection info incoming
        self.udp_timeout = 0.001
        self.udp_socket = create_udp_socket()
        self.udp_socket.settimeout(self.udp_timeout)

        # Establish sizes
        self.width, self.height, self.total_height, self.paddle_width, self.paddle_height = dims[0], dims[1], dims[1] + 150, 20, 140
        self.geometry("{}x{}".format(self.width, self.total_height))

        # Window settings
        self.title("Pong Group 5")
        self.icon = tkinter.PhotoImage(file=os.sep.join([os.path.dirname(__file__), 'gui-icons', 'racket.png']), master=self)
        self.tk.call('wm', 'iconphoto', self._w, self.icon)
        self.resizable(False, False)

        # Create surface
        self.canvas = tkinter.Canvas(self, bg="black", width=self.width, height=self.total_height)

        # Background image
        self.background_image = tkinter.PhotoImage(file=os.sep.join([os.path.dirname(__file__), 'gui-icons', 'Ping-Pong_score_' + str(random.randint(0, 4)) +'.png']))
        self.field = self.canvas.create_image(self.width/2, self.total_height/2, image=self.background_image)
        self.canvas.pack(fill="both", expand=True)

        # Font types
        self.score_font = ("Helvetica", 30, "bold")
        self.name_font = ("Helvetica", 20, "bold")

        ## Left player
        # Left paddle
        self.left_pos = [self.width*1/16, self.height/2]
        self.paddle_image_left = tkinter.PhotoImage(file=os.sep.join([os.path.dirname(__file__), 'gui-icons', 'wood-paddle__shade_1.png']))
        self.left = self.canvas.create_image(*self.left_pos,
                                             image=self.paddle_image_left)

        # Left score
        self.left_score_pos = [self.width/2-75, self.height + 100]
        self.left_score_value = tkinter.StringVar()
        self.left_score_value.set("0")
        self.left_score = self.canvas.create_text(*self.left_score_pos, text=self.left_score_value.get(), font=self.score_font)

        # Left name
        self.left_name_pos = [self.width/2-75, self.height + 20]
        self.left_name_value = tkinter.StringVar()
        self.left_name_value.set(name)
        self.left_name = self.canvas.create_text(*self.left_name_pos, text=self.left_name_value.get(), font=self.name_font)

        ## Right player
        # Right score
        self.right_score_pos = [self.width/2+75, self.height + 100]
        self.right_score_value = tkinter.StringVar()
        self.right_score_value.set("0")
        self.right_score = self.canvas.create_text(*self.right_score_pos, text=self.right_score_value.get(), font=self.score_font)

        # Right name
        self.right_name_pos = [self.width/2+75, self.height + 20]
        self.right_name_value = tkinter.StringVar()
        self.right_name_value.set("User 2")
        self.right_name = self.canvas.create_text(*self.right_name_pos, text=self.right_name_value.get(), font=self.name_font)

        # Right paddle
        self.right_pos = [self.width-self.width*1/16, self.height/2]
        self.paddle_image_right = tkinter.PhotoImage(file=os.sep.join([os.path.dirname(__file__), 'gui-icons', 'wood-paddle__shade_2.png']))
        self.right = self.canvas.create_image(*self.right_pos,
                                             image=self.paddle_image_right)

        # Ball
        self.ball_number = 0
        self.ball_pos = [self.width/2 +7, self.height/2 +7]
        self.ball_image = tkinter.PhotoImage(file=os.sep.join([os.path.dirname(__file__), 'gui-icons', 'Ball_15_orange.png']))
        self.ball = self.canvas.create_image(*self.ball_pos,
                                             image=self.ball_image)

        # Ready button
        self.button_pos = [135, self.height+75]
        self.button_image = tkinter.PhotoImage(file=os.sep.join([os.path.dirname(__file__), 'gui-icons', 'Button_2.png']))
        self.button = tkinter.Button(self, image=self.button_image, command=self.button_action)
        self.button_window = self.canvas.create_window(*self.button_pos, window=self.button, width=148, height=43)

        # Button binds
        self.key_list = []
        self.bind('<Up>', self.add_up_message)
        self.bind('<Down>', self.add_down_message)

        self.receive_loop, self.sending_loop = None, None

    def add_up_message(self, event):
        self.key_list.append('UP')
        self.dy -= self.moving_speed

    def add_down_message(self, event):
        self.key_list.append('DOWN')
        self.dy += self.moving_speed

    def button_action(self):
        self.button.config(state="disabled")
        self.tcp_socket.sendall('I_AM_READY{}'.format(MESSAGE_ENDING).encode("ascii"))
        self.is_ready = True
        print("READY")

    def change_position(self, player_id, dy):
        if player_id == self.player_id:
            if (self.left_pos[1] + dy >= 70 and self.left_pos[1] + dy <= self.height - 70):
                pass
            else:
                if(dy < 0):
                    dy = 70 - self.left_pos[1]
                else:
                    dy = self.dims[1] - 70 - self.left_pos[1]
                self.left_pos[1] += dy
                self.canvas.move(self.left,
                 0,
                 dy)
        else:
            self.right_pos[1] += dy
            self.canvas.move(self.right,
             0,
             dy)


    def update_player(self, player_id, y_pos):
        if player_id == self.player_id:
            dy = y_pos - self.left_pos[1]
        else:
            dy = y_pos - self.right_pos[1]
        if not dy == 0:
            self.change_position(player_id, dy)

    def update_ball(self, x, y):
        dx = x - self.ball_pos[0]
        dy = y - self.ball_pos[1]
        if self.is_treated_as_right_side:
            dx = -dx
        self.canvas.move(self.ball, dx, dy)
        self.ball_pos = [x,y]

    def receive_tcp(self):
        """
        Tries to receive TCP Message from Match-Server which should be SCORE_UPDATED
        :return:
        """
        try:
            messages = (self.tcp_socket.recv(1000)).decode("ascii")
            message_list = messages.split(MESSAGE_ENDING)
            message_list = message_list[:- 1]
            for message in message_list:
                command = message.split(" ")
                if int(command[1]) == self.player_id:
                    self.left_score_value.set(command[2])
                else:
                    self.right_score_value.set(command[2])
                if int(command[2]) >= 11:
                    if self.receive_loop:
                        self.after_cancel(self.receive_loop)
                    if self.sending_loop:
                        self.after_cancel(self.sending_loop)
                    self.game = False
        except socket.timeout:
            pass
        except ConnectionError:
            print("GAME ENDED")
            self.game = False
            pass

    def receive_udp_messages(self):
        data = ""
        try:
            data = self.udp_socket.recv(1400).decode("ascii")
            for i in data.split(MESSAGE_ENDING):
#                print(i)
                """
                message_update_ball = re.match(r'(.*) UPDATE_BALL (.*) (.*) (.*) (.*) (.*)', i)
                message_update_player = re.match(r'(.*) UPDATE_PLAYER (.*) (.*) (.*) (.*) (.*)', i)
                if message_update_ball:
#                    print("Received: UPDATED_BALL")
                    if int(message_update_ball.group(2)) > self.ball_number:
                        self.ball_number = int(message_update_ball.group(2))
                        self.receive_tcp()
                    self.update_ball([int(float(message_update_ball.group(3))), int(float(message_update_ball.group(4)))])
                elif message_update_player:
#                    print("Received: UPDATED_PLAYER")
                    self.update_player(int(float(message_update_player.group(2))), int(float(message_update_player.group(4))))
                """
                if i:
                    print("Got: ", i)
                    message_split = i.split(" ")
                    message_type = message_split[1]
                    if message_type == "UPDATE_BALL":
                        if int(message_split[2]) > self.ball_number:
                            self.ball_number = int(message_split[2])
                            print("RECEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEIVE")
                            self.receive_tcp()
                        self.update_ball(int(float(message_split[3])), int(float(message_split[4])))
                    elif message_type == "UPDATE_PLAYER":
                        self.update_player(int(float(message_split[2])), int(float(message_split[3])))
                        if not int(float(message_split[5])) == self.moving_speed:
                            self.moving_speed = int(float(message_split[5]))
       #            print(self.ball_pos, self.left_pos, self.right_pos)
        except socket.timeout:
            pass
        except OSError:
            return
        self.receive_loop = self.after(int(self.udp_timeout*50000), self.receive_udp_messages)
#        self.receive_loop = self.after(1000, self.receive_udp_messages)

    def send_udp_messages(self):
        message = '{} KEYS_PRESSED {}'.format(self.seq_no, ",".join(self.key_list))
        print("GameGUI sending: ", message)
        self.udp_socket.sendto(message.encode("ascii"), (self.tcp_socket.getpeername()[0], self.match_udp))
        self.change_position(self.player_id,self.dy)
        self.dy = 0
        self.key_list = []
        self.seq_no += 1
#        self.sending_loop = self.after(self.sending_interval, self.send_udp_messages)
#        self.sending_loop = self.after(1000, self.send_udp_messages)

    def run(self):
        sender = SendingThread(self)
        udp_receiver = UDPReceiverThread(self)
        tcp_receiver = TCPReceiverThread(self)
        try:
            while not self.is_ready:
                pass
            sender.start()
            udp_receiver.start()
            tcp_receiver.start()
#        self.after(int(self.udp_timeout*50000), self.receive_udp_messages)
#        self.after(self.sending_interval, self.send_udp_messages)
#        self.after(1, self.receive_udp_messages)
#        self.after(1, self.send_udp_messages())
#        self.mainloop()
            while self.game:
                pass
        except KeyboardInterrupt:
            self.game = False
        finally:
            sender.stop()
            udp_receiver.stop()
            tcp_receiver.stop()
            self.udp_socket.close()
            self.destroy()

