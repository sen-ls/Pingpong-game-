# -*- coding: utf-8 -*-
import tkinter
import os
if __name__ == "__main__":
    from Lobby.PongLobbyClient import LobbyClient
else:
    from ..PongLobbyClient import LobbyClient
    from Lobby.Gui.join_game_dialog import JoinGameDialog


class CreateMatchDialog(tkinter.Toplevel):
    def __init__(self, master=None, features=[]):
        """
        Builds the Create Match Dialog Gui

        Returns
        -------
        None.

        """
        super().__init__(master = master)

        self.features = features

        #sets window title
        self.title('Pong - create Match')
        #sets background color
        self.configure(background = 'black')
        #sets little windowicon
        self.tk.call('wm', 'iconphoto', self._w, tkinter.PhotoImage(file=os.sep.join([os.path.dirname(__file__), 'pong_icon.png']), master=self.master))

        """NAME ENTRY"""
        
        self.placeholder3 = tkinter.Frame(self, bg = 'black', height = 10, bd = 10)
        self.placeholder3.grid(row = 1, column = 1)
        
        self.nameLabel = tkinter.Label(self, 
                                       bg = 'black',
                                       fg = 'white',
                                       width = 12,
                                       font = ('Comic Sans MS', 12),
                                       text = 'Match name: ',
                                       anchor = 'w')
        self.nameLabel.grid(row = 2, column = 1)
        
        self.nameEntry = tkinter.Entry(self,
                                       font = ('Comic Sans MS', 12),
                                       fg = 'white',
                                       bg = 'gray12',
                                       width = 22,
                                       justify = 'center')
        self.nameEntry.grid(row = 2, column = 2, columnspan = 4)
        
        self.placeholder = tkinter.Frame(self, bg = 'black', height = 10, bd = 10)
        self.placeholder.grid(row = 3, column = 1)
        
        
        """FEATURE SELECTION"""
        self.selFeatureLabel = tkinter.Label(self, 
                                       bg = 'black',
                                       fg = 'white',
                                       width = 34,
                                       font = ('Comic Sans MS', 12),
                                       text = 'Feature Selection')
        self.selFeatureLabel.grid(row = 4, column = 1, columnspan = 4)
        
        self.checkbuttonFrame = tkinter.Frame(self, bg = 'black')
        
        #list of lists [[BUTTON][BUTTONSTATS]]
        self.checkbuttonList = [[],[]]        
        #TODO call checkbutton constructor
        end_row = self.placeCheckbuttons()
        
        self.checkbuttonFrame.grid(row = 5, column = 1, columnspan=4)
        
        """BUTTON FRAME"""        
        self.placeholder2 = tkinter.Frame(self, bg = 'black', height = 10)
        self.placeholder2.grid(row = 6, column = 2)

        self.button_create = tkinter.Button(self, text="Create Match",
                                       bg = 'gray10',
                                       fg = 'white',
                                       bd = 0,
                                       font = ('Comic Sans MS', 12),
                                       activeforeground = 'thistle3',
                                       activebackground = 'black',
                                       command=self.create_match)
        self.button_create.grid(row = 7, column = 1)

        self.button_cancel = tkinter.Button(self, text="Cancel",
                                           bg = 'gray10',
                                           fg = 'white',
                                           bd = 0,
                                           width = 10,
                                           font = ('Comic Sans MS', 12),
                                           activeforeground = 'thistle3',
                                           activebackground = 'black',
                                           command=self.destroy)
        self.button_cancel.grid(row = 7, column = 4)
        
        self.placeholder1 = tkinter.Frame(self, bg = 'black', width = 8)
        self.placeholder1.grid(row = 7, column = 3)
        
        self.button_createandjoin = tkinter.Button(self, text="Create and Join",
                                           bg = 'gray10',
                                           fg = 'white',
                                           bd = 0,
                                           font = ('Comic Sans MS', 12),
                                           activeforeground = 'thistle3',
                                           activebackground = 'black',
                                           command=self.create_and_join)
        self.button_createandjoin.grid(row = 7, column = 2)

    def create_match(self):
        
        features = []
        for i, v in zip(self.features, self.checkbuttonList[1]):
            if v.get():
                features.append(i)
        LobbyClient.execute_command(" ".join(['/create_match Pong', self.nameEntry.get(), ",".join(["BASIC"] + features)]))
        self.destroy()

    def placeCheckbuttons(self):
        for index, feature in enumerate(self.features):
            self.checkbuttonList[1].append(tkinter.IntVar())
            self.checkbuttonList[0].append(tkinter.Checkbutton(self.checkbuttonFrame,
                                                            text = feature.title(),
                                                            font = ('Comic Sans MS', 12),
                                                            bg = 'black',
                                                            fg = 'white',
                                                            selectcolor="black",
                                                            variable = self.checkbuttonList[1][index],
                                                            onvalue = 1,
                                                            offvalue = 0))
            
            self.checkbuttonList[0][index].grid(row = index, column = 1)
        return len(self.features)

    def create_and_join(self):
        
        features = []
        for i, v in zip(self.features, self.checkbuttonList[1]):
            if v.get():
                features.append(i)
        LobbyClient.execute_command(" ".join(['/create_match Pong', self.nameEntry.get(), ",".join(["BASIC"] + features)]))
        join_game_gui = JoinGameDialog(self.master, [tkinter.StringVar(value=self.nameEntry.get()), tkinter.StringVar(value=",".join(["BASIC"] + features))])
        self.destroy()


if __name__ == "__main__":
    
    window = CreateMatchDialog(features=["Test", "homo", "noch ein feature"])
    window.mainloop()
