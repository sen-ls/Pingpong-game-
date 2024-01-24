# -*- coding: utf-8 -*-
"""
Created on Sat May 30 16:26:11 2020

@author: Nikolas
"""

import cProfile
import socket
from Game.Client import Client


def test_client():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", 55000))

    Spieler = Client("252,121,255","Zwei",s,1,"121,255,255","Eins",54010)
    Spieler.run()


if __name__ == "__main__":
    #cProfile.run('test_client()')
    test_client()
