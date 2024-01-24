# -*- coding: utf-8 -*-

import tkinter
import os
from .client_window import ClientMainWindow
from .. import PongLobbyServer


class entryWindow(tkinter.Tk):
    
    def __init__(self):
        super().__init__()

        self.server_thread = None
        self.client = None

        self.protocol('WM_DELETE_WINDOW', self.close_window)

        #sets window title
        self.title('Pong')
        #sets background color
        self.configure(background = 'black')
        #sets little windowicon
        self.call('wm', 'iconphoto', self._w, tkinter.PhotoImage(file=os.sep.join([os.path.dirname(__file__), 'pong_icon.png']), master=self))
        #cant resize the window
        self.resizable(width = False, height = False)
        
        #Title Label
        self.headerLabel = tkinter.Label(self, 
                                         bg = 'black', 
                                         fg = 'white', 
                                         font = ('Comic Sans MS', 15), 
                                         text = "Menu")
        self.headerLabel.grid(row = 1, column = 1)
        
        #just a placeholder
        self.placeholder1 = tkinter.Frame(self, bg = 'black', height = 30, width = 300)
        self.placeholder1.grid(row = 2, column = 1)
        
        
        #Button to start the server
        self.startServerBtn = tkinter.Button(self,
                                             bg = 'black',
                                             fg = 'red',
                                             bd = 2,
                                             font = ('Comic Sans MS', 15),
                                             text = 'Server: off',
                                             activeforeground = 'thistle3',
                                             activebackground = 'black',
                                             command = self.toggle_server)
        self.startServerBtn.grid(row = 3, column = 1)
        
        #just a placeholder
        self.placeholder2 = tkinter.Frame(self, bg = 'black', height = 30, width = 300)
        self.placeholder2.grid(row = 4, column = 1)
        
        #Button to start the client
        self.startClientBtn = tkinter.Button(self,
                                             bg = 'black',
                                             fg = 'red',
                                             bd = 2,
                                             font = ('Comic Sans MS', 15),
                                             text = 'Client: off',
                                             activeforeground = 'thistle3',
                                             activebackground = 'black',
                                             command = self.toggle_client)
        self.startClientBtn.grid(row = 5, column = 1)
        
        #just a placeholder
        self.placeholder2 = tkinter.Frame(self, bg = 'black', height = 30, width = 300)
        self.placeholder2.grid(row = 6, column = 1)

    def close_window(self):
        """
        Closes the current window and all other Tkinter windows
        :return: None
        """
        if self.client:
            self.toggle_client()

        if self.server_thread:
            self.toggle_server()

        self.destroy()

    def toggle_server(self):
        """
        Updates the server button and starts or stops the current server
        :return: None
        """
        if not self.server_thread:
            self.server_thread = PongLobbyServer.ServerThread()
            self.server_thread.start()
            self.startServerBtn.config(text='Server: on', fg='green')
        else:
            self.server_thread.stop()
            self.server_thread = None
            self.startServerBtn.config(text='Server: off', fg='red')

    def toggle_client(self):
        """
        Updates the client button and starts or stops the current client
        :return: None
        """
        if not self.client:
            self.startClientBtn.config(text='Client: on', fg='green')
            self.client = ClientMainWindow(self)
            self.client.mainloop()
        else:
            self.startClientBtn.config(text='Client: off', fg='red')
            self.client.close_window()
            self.client = None


def main():
    window = entryWindow()
    window.mainloop()

