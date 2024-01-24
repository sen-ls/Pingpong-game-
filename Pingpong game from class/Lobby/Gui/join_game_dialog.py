# -*- coding: utf-8 -*-
import tkinter
import os
from ..PongLobbyClient import LobbyClient


class JoinGameDialog(tkinter.Toplevel):
    def __init__(self, master = None, match = None):
        """
        Builds the Join Game Dialog Gui

        Parameters
        ----------
        gameList : List<string>
            element of the content Matrix to identify the Game.

        Returns
        -------
        None.

        """
        super().__init__(master = master)

        self.match = match
        self.master = master

        #sets window title
        self.title('Pong - join game')
        #sets background color
        self.configure(background = 'black')
        #sets little windowicon
        self.tk.call('wm', 'iconphoto', self._w, tkinter.PhotoImage(file=os.sep.join([os.path.dirname(__file__), 'pong_icon.png']), master=self.master))
        
        
        """Description of the Game"""
        self.descriptionLabel = tkinter.Label(self, 
                                              bg = 'black',
                                              fg = 'white',
                                              width = 12,
                                              font = ('Comic Sans MS', 12),
                                              text = 'Match name: ',
                                              anchor = 'w')
        self.descriptionLabel.grid(row = 1, column = 1)
        
        gameName = self.match[0].get()
        
        self.gameNameLabel = tkinter.Label(self, 
                                   bg = 'black',
                                   fg = 'white',
                                   width = 20,
                                   font = ('Comic Sans MS', 12),
                                   text = gameName)
        self.gameNameLabel.grid(row = 1, column = 2)
        
        #Feature Description
        self.descriptionLabel1 = tkinter.Label(self, 
                                              bg = 'black',
                                              fg = 'white',
                                              width = 16,
                                              font = ('Comic Sans MS', 12),
                                              text = 'Required features: ',
                                              anchor = 'w')
        self.descriptionLabel1.grid(row = 2, column = 1)

        gameFeatures = self.match[1].get()
        self.gameFeatureLabel = tkinter.Label(self, 
                                              bg = 'black',
                                              fg = 'white',
                                              width = 20,
                                              font = ('Comic Sans MS', 12),
                                              text = gameFeatures)
        self.gameFeatureLabel.grid(row = 2, column = 2)
        
        self.selectFramerateLabel = tkinter.Label(self, 
                                                  bg = 'black',
                                                  fg = 'white',
                                                  width = 16,
                                                  font = ('Comic Sans MS', 12),
                                                  text = 'Chosen FPS: ',
                                                  anchor = 'w')
        self.selectFramerateLabel.grid(row = 3, column = 1)
        
        self.selectFramerateEntry = tkinter.Entry(self,
                                                  font = ('Comic Sans MS', 10),
                                                  fg = 'white',
                                                  bg = 'gray12',
                                                  width = 3,
                                                  justify = 'center')
        self.selectFramerateEntry.grid(row = 3, column = 2)
        self.selectFramerateEntry.insert(tkinter.END, '20')
                
        self.placeholder = tkinter.Frame(self, bg = 'black', height = 15, bd = 10)
        self.placeholder.grid(row = 4, column = 1)
        
        """COLOR SELECTION"""
        
        self.colorselectionFrame = tkinter.Frame(self, bg = 'black')
        
        self.selColorLabel = tkinter.Label(self.colorselectionFrame, 
                                           bg = 'black',
                                           fg = 'white',
                                           width = 25,
                                           font = ('Comic Sans MS', 12),
                                           text = 'Color Selection',
                                           anchor = 'n')
        self.selColorLabel.grid(row = 1, column = 1)
        
        self.placeholderblock3 = tkinter.Frame(self.colorselectionFrame, height = 20, bg = 'black')
        self.placeholderblock3.grid(row = 2, column = 1)
        
        self.redScale = tkinter.Scale(self.colorselectionFrame, 
                                      orient = 'horizontal',
                                      bd = 2,
                                      font = ('Comic Sans MS', 8),
                                      length = 200,
                                      from_ = 0,
                                      to_ = 255,
                                      bg = 'red',
                                      troughcolor = 'gray24',
                                      activebackground = 'red2',
                                      command = self.setColorString)
        self.redScale.grid(row = 3, column = 1, columnspan = 2)
        
        self.placeholderblock1 = tkinter.Frame(self.colorselectionFrame, height = 20, bg = 'black')
        self.placeholderblock1.grid(row = 4, column = 1)
        
        self.greenScale = tkinter.Scale(self.colorselectionFrame, 
                                      orient = 'horizontal',
                                      bd = 2,
                                      font = ('Comic Sans MS', 8),
                                      length = 200,
                                      from_ = 0,
                                      to_ = 255,
                                      bg = 'green',
                                      troughcolor = 'gray24',
                                      activebackground = 'green3',
                                      command = self.setColorString)
        self.greenScale.grid(row = 5, column = 1, columnspan = 2)
        
        self.placeholderblock2 = tkinter.Frame(self.colorselectionFrame, height = 20, bg = 'black')
        self.placeholderblock2.grid(row = 6, column = 1)
        
        self.blueScale = tkinter.Scale(self.colorselectionFrame, 
                                      orient = 'horizontal',
                                      bd = 2,
                                      font = ('Comic Sans MS', 8),
                                      length = 200,
                                      from_ = 0,
                                      to_ = 255,
                                      bg = 'RoyalBlue1',
                                      troughcolor = 'gray24',
                                      activebackground = 'mediumblue',
                                      command = self.setColorString)
        self.blueScale.grid(row = 7, column = 1, columnspan = 2)
        
        self.colorstring = 'ffffff'
        
        self.colorexample = tkinter.Frame(self.colorselectionFrame,
                                          bg = '#' + self.colorstring,
                                          height = 160,
                                          width = 10)
        self.colorexample.grid(row = 2, rowspan = 7, column = 2)
        
        self.placeholderblock4 = tkinter.Frame(self.colorselectionFrame, height = 20, bg = 'black')
        self.placeholderblock4.grid(row = 8, column = 1)
        
        
        self.colorselectionFrame.grid(row = 5, column = 1, columnspan = 2)      
        
        
        """SKIN SELECTION"""
        self.skinSelectionFrame = tkinter.Frame(self, bg = 'black')
        
        self.selSkinLabel = tkinter.Label(self.skinSelectionFrame, 
                                           bg = 'black',
                                           fg = 'white',
                                           width = 25,
                                           font = ('Comic Sans MS', 12),
                                           text = 'Skin and Playground Selection',
                                           anchor = 'n')
        self.selSkinLabel.grid(row = 1, column = 1, columnspan = 2)
        
        #placeholder between label and dropdown
        self.placeholderblock6 = tkinter.Frame(self.skinSelectionFrame, height = 12, bg = 'black')
        self.placeholderblock6.grid(row = 2, column = 1)
        
        #dict with skinnamme: colorcode
        self.availableSkins = {'no Skin': '',
                               'Space': '1,2,50',
                               'Wood1': '1,2,51',
                               'pingpong1': '1,2,52',
                               'pingpong2': '1,2,53',
                               'LGBT': '1,2,54',
                               'Metal': '1,2,55',
                               'Random': '1,2,60'}
        
        self.skinVar = tkinter.StringVar()
        self.skinVar.set('no Skin')
        
        self.skinselection = tkinter.OptionMenu(self.skinSelectionFrame, self.skinVar, *self.availableSkins.keys())
        self.skinselection.config(width = 15,
                                  bg = 'gray18',
                                  fg = 'white',
                                  highlightthickness = 0,
                                  activebackground = 'gray8',
                                  activeforeground = 'thistle3',
                                  font = ('Comic Sans MS', 10))
        
        self.skinselection['menu'].config(bg = 'gray18',
                                          fg = 'white',
                                          font = ('Comic Sans MS', 10))
        
        self.skinselection.grid(row = 3, column = 1)
        
        #dict playgroundname:playgroundcode
        self.availablePlaygrounds = {'random playground': '',
                                     'playground 1': '1,2,50',
                                     'playground 2': '1,2,51',
                                     'playground 3': '1,2,52',
                                     'playground 4': '1,2,53',
                                     'playground 5': '1,2,54',
                                     'random playground': '1,2,60'}
        
        self.playgroundVar = tkinter.StringVar()
        self.playgroundVar.set('no plaground selected')
        
        self.playgroundSelection = tkinter.OptionMenu(self.skinSelectionFrame, self.playgroundVar, *self.availablePlaygrounds.keys())
        self.playgroundSelection.config(width = 18,
                                        bg = 'gray18',
                                        fg = 'white',
                                        highlightthickness = 0,
                                        activebackground = 'gray8',
                                        activeforeground = 'thistle3',
                                        font = ('Comic Sans MS', 10))
        
        self.playgroundSelection['menu'].config(bg = 'gray18',
                                                fg = 'white',
                                                font = ('Comic Sans MS', 10))
        
        self.playgroundSelection.grid(row = 3, column = 2)
        
        #placeholder between dropdown and buttons
        self.placeholderblock5 = tkinter.Frame(self.skinSelectionFrame, height = 20, bg = 'black')
        self.placeholderblock5.grid(row = 4, column = 1)
        
        self.skinSelectionFrame.grid(row = 6, column = 1, columnspan = 2)
        
        """ BUTTONS """
        
        self.buttonFrame = tkinter.Frame(self, bg = 'black')
        self.joinNowBtn = tkinter.Button(self.buttonFrame, 
                                         bg = 'gray10', 
                                         fg = 'white',
                                         bd = 0,
                                         width = 16,
                                         font = ('Comic Sans MS', 12), 
                                         text = 'Join',
                                         activeforeground = 'thistle3',
                                         activebackground = 'black',
                                         command = self.joinNow)
        self.joinNowBtn.grid(row = 1, column = 1)
        
        self.placeholder7 = tkinter.Frame(self.buttonFrame, bg = 'black', width = 10, bd = 10)
        self.placeholder7.grid(row = 1, column = 2)
        
        self.abortBtn = tkinter.Button(self.buttonFrame, 
                                 bg = 'gray10', 
                                 fg = 'white',
                                 bd = 0,
                                 width = 16,
                                 font = ('Comic Sans MS', 12), 
                                 text = 'Cancel',
                                 activeforeground = 'thistle3',
                                 activebackground = 'black',
                                 command = self.exitDlg)
        self.abortBtn.grid(row = 1, column = 3)
        
        self.placeholder1 = tkinter.Frame(self.buttonFrame, bg = 'black', height = 20, bd = 10)
        self.placeholder1.grid(row = 3, column = 1)
        
        self.buttonFrame.grid(row = 7, column = 1, columnspan = 2)
        
    def joinNow(self):
        """
        Routine to actually join the game
        """
        
        #TODO: implement Playground and FPS selection

        try:
            fps = int(self.selectFramerateEntry.get())
        except ValueError:
            self.selectFramerateEntry.delete(0, tkinter.END)
            self.selectFramerateEntry.insert(0, '20')
            return

        LobbyClient.message_handler.fps = fps

        if (self.skinVar.get() == 'no Skin'):
        
            LobbyClient.execute_command(" ".join(['/join_match', self.match[0].get(), ",".join([str(self.redScale.get()),
                                                                                                str(self.greenScale.get()),
                                                                                                str(self.blueScale.get())])]))
        else:
            
            LobbyClient.execute_command(" ".join(['/join_match', self.match[0].get(), self.availableSkins[self.skinVar.get()]]))
            
        self.destroy()

    def exitDlg(self):
        
        #TODO: exit Dialog Routine
        self.destroy()
        
    def setColorString(self, scale = None):
        red = self.redScale.get()
        green = self.greenScale.get()
        blue = self.blueScale.get()
        
        redstring = '%.2x' % red
        greenstring = '%.2x' % green
        bluestring = '%.2x' % blue
        
        self.colorstring = redstring + greenstring + bluestring
        self.colorexample.config(bg = '#' + self.colorstring)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
