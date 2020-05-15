# CondorUDP2COM

Application to catch Condor UDP data stream, convert it to data frame and send over serial port.

## Installation

Installer is available: https://github.com/kbobrowski/CondorUDP2COM/releases/download/v1.1/install_CondorUDP2COM.exe

Remember to enable UDP.ini in Condor directory (in Condor2 it is located in Settings subdirectory):

```
[General]
Enabled=1
```

## Video

[![video](https://img.youtube.com/vi/KtItH9Yoj_A/0.jpg)](https://www.youtube.com/watch?v=KtItH9Yoj_A)

## Hints

Check decodeFrame method from CondorUDP2COM.py for hints how to decode the frame on the receiver side.
