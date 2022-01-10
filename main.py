#!/bin/env python3

import argparse

from x7 import X7, X7HardwareButtons


def mute(var):
    print("MUTED", var)


def toggle_output():
    print("TOGGLED")


parser = argparse.ArgumentParser(
    description="Control Soundblaster X7 over Bluetooth RFCOMM."
)
parser.add_argument("mac", type=str)

sub_parsers = parser.add_subparsers(dest="command")
mute_parser = sub_parsers.add_parser("mute", help="Mute or unmute the device")
mute_parser.add_argument("enabled", type=int, help="1 to mute, 0 to unmute")


hw_button_parser = sub_parsers.add_parser(
    "set_hardware_button", help="Set a hardware button"
)
hw_button_parser.add_argument(
    "button",
    type=X7HardwareButtons.argparse,
    choices=list(X7HardwareButtons),
    help="Button Identifier",
)
hw_button_parser.add_argument(
    "state", type=int, help="State of the button, usually 1 for enabled, 0 for disabled"
)

output_parser = sub_parsers.add_parser(
    "audio_output", help="Change Audio Output Configuration"
)
output_parser.add_argument(
    "output",
    type=str,
    choices=("headphones", "speakers"),
    help="Audio output to be used",
)

args = parser.parse_args()

controller = X7(args.mac, True)
if args.command == "mute":
    controller.mute(args.enabled)
elif args.command == "set_hardware_button":
    controller._set_hardware_button(args.button, args.state)
elif args.command == "audio_output":
    controller.set_audio_output(args.output)
