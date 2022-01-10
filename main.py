import argparse

from x7 import X7

def mute(var):
    print("MUTED", var)

def toggle_output():
    print("TOGGLED")

parser = argparse.ArgumentParser(description='Control Soundblaster X7 over Bluetooth RFCOMM.')
parser.add_argument('mac', type=str)

sub_parsers = parser.add_subparsers(dest='command')
subcommand_a = sub_parsers.add_parser('mute', help='Mute or unmute the device')
subcommand_a.add_argument('target', type=int, help='???')

args = parser.parse_args()

controller = X7(args.mac, True)
controller.mute(args.target)
