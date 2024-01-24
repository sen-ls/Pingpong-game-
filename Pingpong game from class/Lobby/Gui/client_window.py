# -*- coding: utf-8 -*-

import os
import tkinter

if __name__ == "__main__":
    from Lobby.PongLobbyClient import LobbyClient
    from Lobby.Gui.join_game_dialog import JoinGameDialog
    from Lobby.Gui.create_match_dialog import CreateMatchDialog
else:
    from ..PongLobbyClient import LobbyClient
    from .join_game_dialog import JoinGameDialog
    from .create_match_dialog import CreateMatchDialog
    from Settings.utility import create_system_message


class ClientMainWindow(tkinter.Toplevel):
    """
    This class defines the client's most relevant window containing multiple buttons
    to interact with a lobby as well as a chat window to communicate with others
    """
    def __init__(self, menu=None):
        """
        Initializes a ClientMainWindow object
        :param menu: EntryWindow specifying the reference to the parent window
        """
        super().__init__()

        self.exists = True
        self.menu = menu
        self.selectedLobby = None
        self.supported_features = []

        #sets window title
        self.title('Pong Client')
        #sets background color
        self.configure(background = 'black')
        #sets little windowicon
        image = tkinter.PhotoImage(file=os.sep.join([os.path.dirname(__file__), 'pong_icon.png']), master=self)
        self.tk.call('wm', 'iconphoto', self._w, image)

        self.protocol('WM_DELETE_WINDOW', self.exit_window)
        
        """"HEADER FRAME"""
        self.headerFrame = tkinter.Frame(self, bg = 'black')
        
        #Welcome to the Pong Game Title Label
        self.titleLabel = tkinter.Label(self.headerFrame, 
                                        bg = 'black', 
                                        fg = 'white', 
                                        font = ('Comic Sans MS', 15), 
                                        text = "Welcome to the Pong Game-Client!")
        self.titleLabel.grid(row = 1, column = 1, columnspan = 3)
        
        #placeholder between Title Label and Name insertion
        self.placeholder1 = tkinter.Frame(self.headerFrame, bg = 'black', height = 10, width = 60)
        self.placeholder1.grid(row = 2, column = 1)

        #Name insertion descrition Label TODO: CURSOR BLINKING
        self.insertNameLabel = tkinter.Label(self.headerFrame,
                                             bg = 'black',
                                             fg = 'white',
                                             width = 20,
                                             font = ('Comic Sans MS', 15),
                                             text = "Chose your name: ",
                                             anchor = 'w')
        self.insertNameLabel.grid(row = 3, column = 1)

        #placeholder between Name insertion descriptor and entry Widget
        self.placeholder2 = tkinter.Frame(self.headerFrame, bg = 'black', height = 10, width = 60)
        self.placeholder2.grid(row = 3, column = 2)
        
        self.nameEntry = tkinter.Entry(self.headerFrame,
                                       font = ('Comic Sans MS', 15),
                                       fg = 'white',
                                       bg = 'gray12',
                                       width = 22,
                                       justify = 'center')

        self.nameEntry.grid(row = 3, column = 3)
        self.headerFrame.grid(row = 1, column = 1)
        
        
        """ SERVER FRAME """       
        self.serverFrame = tkinter.Frame(self, bg = 'black')
        
        #placeholder between Header and Server Frame
        self.placeholder3 = tkinter.Frame(self.serverFrame, bg = 'black', height = 10, width = 10)
        self.placeholder3.grid(row = 1, column = 1)
        
        #placeholder between left border and search Server Button
        self.placeholder4 = tkinter.Frame(self.serverFrame, bg = 'black', width = 5, height = 2)
        self.placeholder4.grid(row = 2, column = 1)
        

        self.demo_var = tkinter.IntVar()
        self.demo_checkbox = tkinter.Checkbutton(self.serverFrame,
                                                            text = "Remote",
                                                            font = ('Comic Sans MS', 12),
                                                            bg = 'black',
                                                            fg = 'white',
                                                            selectcolor="black",
                                                            variable = self.demo_var,
                                                            onvalue = 1,
                                                            offvalue = 0)
        self.demo_checkbox.grid(row=2, column=2)
        
        #placeholder between checkbutton and search Server
        self.placeholder20 = tkinter.Frame(self.serverFrame, bg = 'black', width = 10, height = 2)
        self.placeholder20.grid(row = 2, column = 3)

        #search Server Button
        self.button_find_lobby = tkinter.Button(self.serverFrame,
                                                bg = 'gray10',
                                                fg = 'white',
                                                bd = 0,
                                                font = ('Comic Sans MS', 12),
                                                text = 'Find Lobby',
                                                activeforeground = 'thistle3',
                                                activebackground = 'black',
                                                command = self.find_lobbies)
        self.button_find_lobby.grid(row = 2, column = 4)
        
        
        
        #placeholder between search Server Button and connection Status Label
        self.placeholder5 = tkinter.Frame(self.serverFrame, bg = 'black', height = 12, width = 10)
        self.placeholder5.grid(row = 2, column = 5)
        
        #connection Status Label
        self.connectionStatLabel = tkinter.Label(self.serverFrame,
                                                 bg = 'black',
                                                 fg = 'red',
                                                 font = ('Comic Sans MS', 15),
                                                 text = 'Connection status:')
        self.connectionStatLabel.grid(row = 2, column = 6)

        #Label to show the actual connection Status
        self.vconnectionStatLabel = tkinter.Label(self.serverFrame,
                                              bg = 'black',
                                              fg = 'red',
                                              font = ('Comic Sans MS', 15),
                                              width = 15,
                                              text = 'no connection')
        self.vconnectionStatLabel.grid(row = 2, column = 7)
        
        """ LOBBYTABLE """
        
        self.lobbyTableFrame = tkinter.Frame(self.serverFrame, bg = 'black')
        
        
        #placeholder between Server Frame and Table Frame
        self.placeholder6 = tkinter.Frame(self.serverFrame, bg = 'black', height = 30, bd = 10)
        self.placeholder6.grid(row = 3, column = 1, columnspan = 3)
        

        self.lobbyTableFrame = tkinter.Frame(self.serverFrame, bg = 'black')
        
        headlineColor = 'gray25'
        
        #available Games Headrow
        self.lobbyHeadRowLabel1 = tkinter.Label(self.lobbyTableFrame, 
                                           bg = headlineColor,
                                           fg = 'white',
                                           width = 15,
                                           font = ('Comic Sans MS', 12),
                                           text = 'Lobby IP')
        self.lobbyHeadRowLabel1.grid(row = 1, column = 1)
        
        #Features Headrow
        self.lobbyHeadRowLabel2 = tkinter.Label(self.lobbyTableFrame, 
                                           bg = headlineColor,
                                           fg = 'white',
                                           width = 20,
                                           font = ('Comic Sans MS', 12),
                                           text = 'Lobby Port')
        self.lobbyHeadRowLabel2.grid(row = 1, column = 2)
        
        #Matrix of Buttons to appear in the Table
        self.lobbyButtonMatrix = []
        #list of the Colors of the row. 1 index represents 1 row
        self.lobbyColorList = []
        #Matrix of strings on the Buttons (Variable due to Game creation)
        self.lobbyContentMatrix = []

        self.lobbyTableFrame.grid(row = 4, column = 1, columnspan = 10)
        
        """CONNECTBUTTONFRAME"""
        
        self.connectBtnFrame = tkinter.Frame(self.serverFrame, bg = 'black')
        
        self.placeholder7 = tkinter.Frame(self.connectBtnFrame, bg = 'black', height = 10, bd = 10)
        self.placeholder7.grid(row = 1, column = 1)
        
        self.joinLobbyBtn = tkinter.Button(self.connectBtnFrame,
                                           bg = 'gray10',
                                           fg = 'white',
                                           bd = 0,
                                           font = ('Comic Sans MS', 12),
                                           text = 'Join Lobby',
                                           width = 20,
                                           height = 1,
                                           #state = 'disabled',
                                           activeforeground = 'thistle3',
                                           activebackground = 'black',
                                           command = self.join_lobby)
        
        self.joinLobbyBtn.grid(row = 2, column = 1)

        self.placeholder8 = tkinter.Frame(self.connectBtnFrame, bg = 'black', height = 15, bd = 10)
        self.placeholder8.grid(row = 3, column = 1)
        
        self.connectBtnFrame.grid(row = 5, column = 1, columnspan = 10)
        
        
        
        self.serverFrame.grid(row = 2, column = 1)
        

        
        """TABLE FRAME"""
        #mainFrame of the table (size adapts to the game List)
        self.tableFrame = tkinter.Frame(self, bg = 'gray8')
        headlineColor = 'gray25'
        #available Games Headrow
        self.headRowLabel1 = tkinter.Label(self.tableFrame, 
                                           bg = headlineColor,
                                           fg = 'white',
                                           width = 15,
                                           font = ('Comic Sans MS', 12),
                                           text = 'Match name')
        self.headRowLabel1.grid(row = 1, column = 1)
        
        #Features Headrow
        self.headRowLabel2 = tkinter.Label(self.tableFrame, 
                                           bg = headlineColor,
                                           fg = 'white',
                                           width = 20,
                                           font = ('Comic Sans MS', 12),
                                           text = 'Features')
        self.headRowLabel2.grid(row = 1, column = 2)

        #Matrix of Buttons to appear in the Table
        self.buttonMatrix = []
        #list of the Colors of the row. 1 index represents 1 row
        self.colorList = []
        #Matrix of strings on the Buttons (Variable due to Game creation)
        self.contentMatrix = []
        #selected game to join next:
        self.selectedGame = None
        
        
        self.update_table()
        
        
        self.tableFrame.grid(row = 3, column = 1)
        
        """BUTTON FRAME"""
        self.buttonFrame = tkinter.Frame(self, bg = 'black') 
        
        #placeholder between Table and Buttons
        self.placeholder9 = tkinter.Frame(self.buttonFrame, bg = 'black', height = 20, bd = 10)
        self.placeholder9.grid(row = 1, column = 1)
        
        #refresh-Table Button
        self.refreshTableBtn = tkinter.Button(self.buttonFrame,
                                              bg = 'gray10',
                                              fg = 'white',
                                              bd = 0,
                                              width = 12,
                                              font = ('Comic Sans MS', 12),
                                              text = 'Refresh',
                                              activeforeground = 'thistle3',
                                              activebackground = 'black',
                                              state='disabled',
                                              command = self.refresh_table)
        self.refreshTableBtn.grid(row = 2, column = 2)
        
        #placeholder between refresh Table and join Game Button
        self.placeholder10 = tkinter.Frame(self.buttonFrame, bg = 'black', width = 20, bd = 10)
        self.placeholder10.grid(row = 2, column = 3)
        
        #Button that opens the join Game Dialog
        self.joinGameBtn = tkinter.Button(self.buttonFrame,
                                          bg = 'gray10',
                                          fg = 'white',
                                          bd = 0,
                                          width = 12,
                                          font = ('Comic Sans MS', 12),
                                          text = 'Join',
                                          activeforeground = 'thistle3',
                                          activebackground = 'black',
                                          state='disabled',
                                          command = self.join_match)
        self.joinGameBtn.grid(row = 2, column = 6)
        
        #placeholder between join Game and create Game Button
        self.placeholder11 = tkinter.Frame(self.buttonFrame, bg = 'black', width = 20, bd = 10)
        self.placeholder11.grid(row = 2, column = 5)
        
        self.leaveGameBtn = tkinter.Button(self.buttonFrame,
                                           bg = 'gray10',
                                           fg = 'white',
                                           bd = 0,
                                           width = 12,
                                           font = ('Comic Sans MS', 12),
                                           text = 'Leave',
                                           activeforeground = 'thistle3',
                                           activebackground = 'black',
                                           state='disabled',
                                           command = self.leave_game)
        self.leaveGameBtn.grid(row = 2, column = 8)
        
        self.placeholder13 = tkinter.Frame(self.buttonFrame, bg = 'black', width = 20, bd = 10)
        self.placeholder13.grid(row = 2, column = 7)
        
        self.createGameBtn = tkinter.Button(self.buttonFrame,
                                            bg = 'gray10',
                                            fg = 'white',
                                            bd = 0,
                                            width = 12,
                                            font = ('Comic Sans MS', 12),
                                            text = 'Create',
                                            activeforeground = 'thistle3',
                                            activebackground = 'black',
                                            state='disabled',
                                            command = self.create_match)
        self.createGameBtn.grid(row = 2, column = 4)
        
        self.placeholder8 = tkinter.Frame(self.buttonFrame, bg = 'black', height = 20)
        self.placeholder8.grid(row = 3, column = 1)
        
        self.iamreadyBtn = tkinter.Button(self.buttonFrame,
                                          bg = 'gray10',
                                          fg = 'white',
                                          bd = 0,
                                          width = 18,
                                          font = ('Comic Sans MS', 12),
                                          text = 'Ready?',
                                          activeforeground = 'thistle3',
                                          activebackground = 'black',
                                          state='disabled',
                                          command = self.i_am_ready)
        
        self.iamreadyBtn.grid(row = 4, column = 1, columnspan = 8)
        
        self.buttonFrame.grid(row = 4, column = 1)
        
        """"BOTTOM FRAME"""
        
        self.bottomFrame = tkinter.Frame(self, bg = 'black')
        
        self.exitButton = tkinter.Button(self.bottomFrame,
                                         bg = 'gray10',
                                         fg = 'white',
                                         bd = 0,
                                         width = 16,
                                         font = ('Comic Sans MS', 12),
                                         text = 'Exit',
                                         activeforeground = 'thistle3',
                                         activebackground = 'black',
                                         command = self.exit_window)
        self.exitButton.grid(row = 2, column = 1)
        
        self.bottomFrame.grid(row = 6, column = 1)
        
        """CHAT FRAME"""
        
        self.chatFrame = tkinter.Frame(self, bg = 'black')
        
        #Chat Title Label
        self.chatTitle = tkinter.Label(self.chatFrame, 
                                             bg = 'black', 
                                             fg = 'white',
                                             width = 40,
                                             font = ('Comic Sans MS', 15), 
                                             text = "Chat ",
                                             anchor = 'w')
        
        #Chat Textbox to see Mesages
        self.chatTextBox = tkinter.Text(self.chatFrame, 
                                        bg = 'gray39', 
                                        height = 6, 
                                        width = 85, 
                                        font =('Times', 10),
                                        state="disabled")
        
        #Chat scrollbar to scroll through Messages
        self.chatScrollbar = tkinter.Scrollbar(self.chatFrame)
        
        self.chatTextBox.config(yscrollcommand = self.chatScrollbar.set)
        self.chatScrollbar.config(command = self.chatTextBox.yview)
        
        self.placeholder12 = tkinter.Frame(self.chatFrame, bg = 'black', height = 5, bd = 10)
           
        self.chatEntryLabel = tkinter.Label(self.chatFrame, 
                                        bg = 'black', 
                                        fg = 'white',
                                        font = ('Comic Sans MS', 15), 
                                        text = "Entry: ",
                                        anchor = 'w')
 
        self.chatEntry = tkinter.Entry(self.chatFrame,
                                       font = ('Times', 12),
                                       fg = 'black',
                                       bg = 'gray45',
                                       width = 55,
                                       justify = 'center')
        
        self.chatEntry.bind('<Return>', self.send_chat_message)
        
        
    
        self.chatTitle.grid(row = 1, column = 1, columnspan = 3)
        self.chatTextBox.grid(row = 2, column = 1, columnspan = 2)
        self.chatScrollbar.grid(row = 2, column = 3, sticky = 'nse')
        self.placeholder12.grid(row = 3, column = 1)        
        self.chatEntryLabel.grid(row = 4, column = 1)
        self.chatEntry.grid(row = 4, column = 2)

        
        self.chatFrame.grid(row = 5, column = 1)


        self.joinGameBtn.config(state='disabled')
        self.refreshTableBtn.config(state='disabled')
        self.createGameBtn.config(state='disabled')
        self.joinLobbyBtn.config(state='disabled')
        self.createGameBtn.config(state='disabled')
        self.chatEntry.config(state='disabled')

    def find_lobbies(self):
        """
        Invokes UDP broadcast/message and displays current lobby pool
        :return: None
        """
        lobbies = LobbyClient.discover_lobby(True if self.demo_var.get() else False)
        self.remove_all_lobbies()
        if lobbies:
            for ip, port in lobbies:
                self.add_lobby(ip, port)
            self.joinLobbyBtn.config(state='normal')
        else:
            self.joinLobbyBtn.config(state='disabled')
        self.update_lobby_table()

    def set_connection_stat(self, status, addr=None):
        """
        manipulates the connection status Label according to status
        :param status: Integer specifying the connection state
        :param addr: Tuple of (String, Integer) specifying an address pair (IP, port)
        :return: None
        """
        if status == 0 and addr:
            self.connectionStatLabel.config(fg='green')
            self.vconnectionStatLabel.config(fg='green', text=addr[0])
        elif status == 1:
            self.connectionStatLabel.config(fg='yellow')
            self.vconnectionStatLabel.config(fg='yellow', text='Searching...')
        elif status == 2:
            self.connectionStatLabel.config(fg='red')
            self.vconnectionStatLabel.config(fg='red', text='No connection')
        elif status == 3:
            self.connectionStatLabel.config(fg='red')
            self.vconnectionStatLabel.config(fg='red', text='Timeout')
        else:
            raise NotImplementedError("only values between 0 and 3 are valid")
        
    def highlight_row(self, row):
        """
        Button callback of the Buttons inside the Table.
        highlights the buttons inside the clicked row.
        :param row: Integer specifying the row number
        :return: None
        """
        for i in range(len(self.buttonMatrix)):
            if i == row:
                for j in range(2):
                    self.buttonMatrix[i][j].config(bg = 'gray40', activebackground = 'gray40')
            else:
                for j in range(2):
                    self.buttonMatrix[i][j].config(bg = self.colorList[i], activebackground = self.colorList[i])

        self.selectedGame = self.contentMatrix[row]
            
    def add_game(self, name, features ='N/A'):
        """
        Adds a match to the contentMatrix
        :param name: String specifying the name of the match
        :param features: String specifying a comma-separated list of feature parameters
        :return: None
        """
        self.contentMatrix.append([])
        i = len(self.contentMatrix) - 1
        self.contentMatrix[i].append(tkinter.StringVar())
        self.contentMatrix[i][0].set(name)
        self.contentMatrix[i].append(tkinter.StringVar())
        self.contentMatrix[i][1].set(features)

    def remove_match(self, name):
        """
        Checks for the specified name in the content table and removes the whole row
        :param name: String specifying the name of the match
        :return: Boolean which is True if an element was removed
        """
        for i in range(len(self.contentMatrix)):
            if self.contentMatrix[i][0].get() == name:
                self.contentMatrix.pop(i)
                return True
        return False

    def update_table(self):
        """
        Updates the Table strictly according to the contentMatrix
        :return: None
        """
        for i, v in enumerate(self.buttonMatrix):
            for j in range(2):
                self.buttonMatrix[i][j].destroy()
        self.buttonMatrix = []

        color1 = 'gray14'
        color2 = 'gray10'
        size_list = [15,20,15,10]
        
        for i in range(len(self.contentMatrix)):
            self.buttonMatrix.append(list())
            self.colorList.append('')
            self.colorList[i] = color1 if i%2==0 else color2

            for j in range(2):
                self.buttonMatrix[i].append(tkinter.Button(self.tableFrame,
                                                           text = self.contentMatrix[i][j].get(),
                                                           bg = self.colorList[i],
                                                           fg = 'white',
                                                           activebackground = self.colorList[i],
                                                           activeforeground = 'white',
                                                           bd = 0,
                                                           font = ('Comic Sans MS', 12),
                                                           width = size_list[j],
                                                           height = 1,
                                                           command = lambda current_i = i: self.highlight_row(current_i)))
                
                self.buttonMatrix[i][j].grid(row = i + 2, column = j + 1)
        self.tableFrame.grid(row = 3, column = 1)
        
    def refresh_table(self):
        """
        Callback function for the refresh-Button 
        :return: None
        """
        LobbyClient.execute_command('/list_matches pong')
        self.contentMatrix = []
        for i in LobbyClient.get_open_matches():
            LobbyClient.execute_command('/match_features {}'.format(i))
            feature = ",".join(LobbyClient.get_features())
            self.add_game(i, features=feature)
        self.update_table()

    def join_match(self):
        """
        Callback function for the join Game Button
        :return: None
        """
        if self.selectedGame:
            joinDlg = JoinGameDialog(self, self.selectedGame)

    def button_state_joined_match(self):
        """
        Sets the buttons to the correct button state
        :return: None
        """
        self.button_find_lobby.config(state="disabled")
        self.joinLobbyBtn.config(state="disabled")
        self.joinGameBtn.config(state="disabled")
        self.createGameBtn.config(state="normal")
        self.refreshTableBtn.config(state="normal")
        self.iamreadyBtn.config(state="normal")
        self.leaveGameBtn.config(state="normal")

    def create_match(self):
        """
        Callback function for the join Game Button
        :return: None
        """
        createMatchDlg = CreateMatchDialog(self, self.supported_features)
    
    def exit_window(self):
        """
        Stops the chat update loop and closes itself correctly
        :return: None
        """
        if hasattr(self, 'chat_update'):
            self.after_cancel(self.chat_update)
        if __name__ == "__main__":
            self.destroy()
        else:
            if self.menu is not None:
                self.menu.toggle_client()

    def close_window(self):
        LobbyClient.end_client()
        if self.exists:
            self.exists = False
            self.destroy()

    """LOBBY FUNCTIONS"""

    def add_lobby(self, IP, port):
        """
        Adds a lobby to the lobbyContentMatrix
        :param IP: String specifying the IP address
        :param port: Integer specifying the port number
        :return: None
        """
        self.lobbyContentMatrix.append([])
        i = len(self.lobbyContentMatrix) - 1
        self.lobbyContentMatrix[i].append(tkinter.StringVar())
        self.lobbyContentMatrix[i][0].set(IP)
        self.lobbyContentMatrix[i].append(tkinter.IntVar())
        self.lobbyContentMatrix[i][1].set(port)
            
    def remove_all_lobbies(self):
        """
        Empty the lobby content matrix containing the lobby information
        :return: None
        """
        self.lobbyContentMatrix = []

    def update_lobby_table(self):
        """
        Updates the lobby table strictly according to the lobbyContentMatrix
        :return: None
        """
        self.lobbyButtonMatrix.clear()
        
        color1 = 'gray14'
        color2 = 'gray10'
        size_list = [15, 20, 15, 10]
        
        for i in range(len(self.lobbyContentMatrix)):
            self.lobbyButtonMatrix.append(list())
            self.lobbyColorList.append('')
            self.lobbyColorList[i] = color1 if i % 2 == 0 else color2
            for j in range(2):
                self.lobbyButtonMatrix[i].append(tkinter.Button(self.lobbyTableFrame,
                                                                text = self.lobbyContentMatrix[i][j].get(),
                                                                bg = self.lobbyColorList[i],
                                                                fg = 'white',
                                                                activebackground = self.lobbyColorList[i],
                                                                activeforeground = 'white',
                                                                bd = 0,
                                                                font = ('Comic Sans MS', 12),
                                                                width = size_list[j],
                                                                height = 1,
                                                                command = lambda current_i = i: self.highlight_lobby_row(current_i)))
                self.lobbyButtonMatrix[i][j].grid(row = i + 2, column = j + 1)
        self.lobbyTableFrame.grid(row = 4, column = 1, columnspan = 10)
                
    def highlight_lobby_row(self, row):
        """
        Button callback of the Buttons inside the Table.
        highlights the buttons inside the clicked row.
        saves the selected row index into self.selectedLobby
        :param row: Integer specifying the row to highlight
        :return: None
        """
        for i in range(len(self.lobbyButtonMatrix)):
            if i == row:
                for j in range(2):
                    self.lobbyButtonMatrix[i][j].config(bg='gray40', activebackground='gray40')
            else:
                for j in range(2):
                    self.lobbyButtonMatrix[i][j].config(bg=self.lobbyColorList[i], activebackground=self.lobbyColorList[i])
                        
        self.selectedLobby = self.lobbyContentMatrix[row]

    def join_lobby(self):
        """
        Callback function for the 'join Lobby' Button
        :return: None
        """
        if self.selectedLobby:
            self.forbid_name_change()

    def forbid_name_change(self):
        """
        Disables name entry and remote checkbox
        :return: None
        """
        self.nameEntry.config(state='disabled')
        self.demo_checkbox.config(state='disabled')
        self.after(1, self.check_name)

    def check_name(self):
        """
        Checks if name is provided
        :return: None
        """
        if self.nameEntry.get():
            self.insertNameLabel.config(fg='white')
            self.nameEntry.after(1, self.handshake)
        else:
            self.insertNameLabel.config(fg='red')
            self.set_connection_stat(2, '')
            self.nameEntry.config(state='normal')
            self.demo_checkbox.config(state='normal')

    def handshake(self):
        """
        Performs TCP handshake with lobby server
        :return: None
        """
        addr, self.supported_features = LobbyClient.connect_to_lobby(self.nameEntry.get(), tuple([i.get() for i in self.selectedLobby]), self)
        if addr:
            # set Status Label on OK
            self.set_connection_stat(0, addr)
            self.joinGameBtn.config(state='normal')
            self.refreshTableBtn.config(state='normal')
            self.createGameBtn.config(state='normal')
            self.chatEntry.config(state='normal')
            self.after(1, self.update_chat)
        else:
            # set Status Label on NO Connection
            self.set_connection_stat(2, '')
            self.nameEntry.config(state='normal')
            self.demo_checkbox.config(state='normal')

    def send_chat_message(self, event):
        """
        Reads user input from entry box and sends it as chat message to server
        :param event: Event specifying the pressed key (mandatory parameter)
        :return: None
        """
        message = self.chatEntry.get()
        self.chatEntry.delete(0, tkinter.END)
        LobbyClient.execute_command(message)

    def display_chat_message(self, message):
        """
        Write a message to the chat box
        :param message: String specfying the message to write
        :return: None
        """
        self.chatTextBox.config(state="normal")
        self.chatTextBox.insert(tkinter.END, message + '\n')
        self.chatTextBox.see(tkinter.END)
        self.chatTextBox.config(state="disabled")

    def update_chat(self):
        """
        Updates the chat with new messages and starts update loop
        :return: None
        """
        if self.exists:
            new_messages = LobbyClient.get_chat()
            for i in new_messages:
                self.display_chat_message(i)
            self.chat_update = self.after(1000, self.update_chat)
            
    def leave_game(self):
        """
        Leaves the currently joined game and adjusts usable buttons
        :return: None
        """
        LobbyClient.execute_command('/leaving_match User left match')
        self.display_chat_message(create_system_message('You left the match.'))
        self.after(1, self.button_state_left_game)

    def button_state_left_game(self):
        """
        Sets all buttons to the correct button state
        :return: None
        """
        self.button_find_lobby.config(state="normal")
        self.joinLobbyBtn.config(state="normal")
        self.joinGameBtn.config(state="normal")
        self.createGameBtn.config(state="normal")
        self.refreshTableBtn.config(state="normal")
        self.iamreadyBtn.config(state="disabled", text="Ready?")
        self.leaveGameBtn.config(state="disabled")

    def i_am_ready(self):
        """
        Signals the server that the user is ready and adjusts usable buttons
        :return: None
        """
        LobbyClient.execute_command('/i_am_ready')
        self.after(1, self.button_state_ready)

    def button_state_ready(self):
        """
        Sets all buttons to the correct button state
        :return: None
        """
        self.button_find_lobby.config(state="disabled")
        self.joinLobbyBtn.config(state="disabled")
        self.joinGameBtn.config(state="disabled")
        self.createGameBtn.config(state="disabled")
        self.refreshTableBtn.config(state="disabled")
        self.iamreadyBtn.config(state="disabled", text="Ready!")
        self.leaveGameBtn.config(state="normal")


if __name__ == "__main__":

    a = ClientMainWindow()
    a.mainloop()

