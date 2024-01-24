"""
Argparser for the subprocessing:
"""
import argparse
import time
from Game.Client import Client


def main():

    def type_port(x):
        x = int(x)
        if x < 1 or x > 65535:
            raise argparse.ArgumentTypeError(
                "Port number has to be greater than 1 and less"
                "than 65535.")
        return x

    def type_rgb(rgb):
        rgb = rgb.split(",")
        if not len(rgb) == 3:
            raise argparse.ArgumentTypeError(
                "Color Code needs 3 Values, separated by a ','")
        for elems in rgb:
            elems = int(float(elems))
            if elems > 255 or elems < 0:
                raise argparse.ArgumentTypeError(
                "RGB Value needs to be between 0 and 255")
        return rgb

    def type_pid(id):
        id = int(id)
        if not id == 1 and not id == 2:
                raise argparse.ArgumentTypeError(
                    "ID has to be either 1 or 2")
        return id

    def type_field(size):
        size = size.split(",")
        if not len(size) == 2:
            raise argparse.ArgumentTypeError(
                "Field needs 2 Values, separated by a ','")
#        size[0] = int(float(size[0]))
#        size[1] = int(float(size[1]))
        return list(map(lambda x: int(float(x)), size))

    def type_unsigned(x):
        x = int(x)
        return x if x > 0 else 1

    def type_fps(x):
        x = int(x)
        if x <= 0:
            x = 1
        elif x > 120:
            x = 120
        return x

    def type_features(x):
        feat = x.split(",")
        if feat[-1] == "" and len(feat) > 1:
            feat = feat[:-1]
        return feat

    description = (
        'Starts a Game Client which is supposed to be called from the tkinter subprocess, to decouple it from tkinter')

    parser = argparse.ArgumentParser(description=description)

    parser.add_argument("-pc",
                        "--player-color",
                        help="RGB player color(Default: [0,0,0]).",
                        default=[0,0,0],
                        type=type_rgb)

    parser.add_argument("-n",
                        "--name",
                        help="Player name (Default: 'User 1')",
                        default='User 1',
                        type=str)

    parser.add_argument("-ip",
                        "--ip-address",
                        help="IP address of the server")

    parser.add_argument("-udp",
                        "--host-udp",
                        help="Destination UDP port of the match.",
                        type=type_port)

    parser.add_argument("-pid",
                        "--player-id",
                        help="Player ID of the client(1 or 2)",
                        type=type_pid)

    parser.add_argument("-oc",
                        "--opponent-color",
                        help="RGB opponent color(Default: [0,0,0]).",
                        type=type_rgb,
                        default=[0,0,0])

    parser.add_argument("-dims",
                        "--dimensions",
                        help="Dimensions of the field (Default: [800,600]).",
                        type=type_field,
                        default=[800, 600])


    parser.add_argument("-v",
                        "--moving-speed",
                        help="Moving Speed of the paddel (Default: 5).",
                        type=type_unsigned,
                        default=1)

    parser.add_argument("-f",
                        "--fps",
                        help="Amount of frames per second during the game",
                        type=type_fps,
                        default=20)

    parser.add_argument("-b",
                        "--ball_size",
                        help="Ball Size",
                        type=type_unsigned,
                        default=15)

    args = parser.parse_args()

    print(args)

    """ color, name, host_ip, host_UDP, player_id, opp_color, dims = [800, 600], moving_speed = 5 """
    Player = Client(color=args.player_color,
                    name=args.name,
                    host_ip=args.ip_address,
                    host_UDP=args.host_udp,
                    player_id=args.player_id,
                    opp_color=args.opponent_color,
                    dims=args.dimensions,
                    moving_speed=args.moving_speed,
                    features=args.ball_size,
                    fps=args.fps)

    #time.sleep(4)
    Player.run()

"""
python client_parser.py -pc 23,23,45 -n Nikolas -ip localhost -udp 54010 -pid 1 -oc 54,54,55  

dims=args.dimensions,
"""
