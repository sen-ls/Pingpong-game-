# -*- coding: utf-8 -*-
"""
Created on Sat May 30 15:16:44 2020

@author: Nikolas
"""
import socket
from Game.match import Match


def test_server():
    game = Match("PONG", "TEST", [1,2,3] , 54010)

    server_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_tcp.bind(("0.0.0.0", 55000))
    server_tcp.listen(1)


    TCP_C1, addr = server_tcp.accept()

    TCP_C2, addr = server_tcp.accept()

    game.add_player("NIKOLAS",[255,121,255] , TCP_C1)
    game.add_player("Bot",[121,255,255], TCP_C2)

    game.run()


if __name__ == "__main__":
    test_server()


