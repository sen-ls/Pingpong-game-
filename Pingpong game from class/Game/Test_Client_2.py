# -*- coding: utf-8 -*-
"""
Created on Sat May 30 16:26:11 2020

@author: Nikolas
"""

import cProfile
import socket
import time
from Game.Client import Client


def test_client():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", 55000))

    Spieler = Client("255,121,255","NIKOLAS",s,2,"121,255,255","Zwei",54010)
    time.sleep(5)
    Spieler.i_am_ready([200,670])
    Spieler.run()


cProfile.run('test_client()')
#test_client()
