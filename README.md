# X7 Bluetooth Control

 Control and configure your SoundBlaster X7 over Bluetooth RFCOMM 

## Why

This project brings an open source alternative to SoundBlaster X7 Control Panel
and supports Linux.

## Use this project

```
$ virtualenv venv
$ pip install -r requirements.txt
```

### Mute and Unmute

```
# Mute
$ ./main.py <X7_MAC_ADDRESS> mute 0

# UnMute
$ ./main.py <X7_MAC_ADDRESS> mute 0
```

### Switch to Speaker/Headphones

```
$ ./main.py <X7_MAC_ADDRESS> audio_output headphones
$ ./main.py <X7_MAC_ADDRESS> audio_output speakers
```
