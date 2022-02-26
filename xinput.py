"""
Simple XInput in python.
https://docs.microsoft.com/en-us/windows/win32/xinput/getting-started-with-xinput
See Xinput.h.
"""

import ctypes
from ctypes import wintypes

# max user count
XUSER_MAX_COUNT = 4

# buttons
XINPUT_GAMEPAD_DPAD_UP = 0x0001
XINPUT_GAMEPAD_DPAD_DOWN = 0x0002
XINPUT_GAMEPAD_DPAD_LEFT = 0x0004
XINPUT_GAMEPAD_DPAD_RIGHT = 0x0008
XINPUT_GAMEPAD_START = 0x0010
XINPUT_GAMEPAD_BACK = 0x0020
XINPUT_GAMEPAD_LEFT_THUMB = 0x0040
XINPUT_GAMEPAD_RIGHT_THUMB = 0x0080
XINPUT_GAMEPAD_LEFT_SHOULDER = 0x0100
XINPUT_GAMEPAD_RIGHT_SHOULDER = 0x0200
XINPUT_GAMEPAD_A = 0x1000
XINPUT_GAMEPAD_B = 0x2000
XINPUT_GAMEPAD_X = 0x4000
XINPUT_GAMEPAD_Y = 0x8000


class XINPUT_GAMEPAD(ctypes.Structure):
    _fields_ = [
        ('wButtons', wintypes.WORD),
        ('bLeftTrigger', ctypes.c_ubyte),  # wintypes.BYTE is signed
        ('bRightTrigger', ctypes.c_ubyte),  # wintypes.BYTE is signed
        ('sThumbLX', wintypes.SHORT),
        ('sThumbLY', wintypes.SHORT),
        ('sThumbRX', wintypes.SHORT),
        ('sThumbRY', wintypes.SHORT)
    ]


class XINPUT_STATE(ctypes.Structure):
    _fields_ = [
        ('dwPacketNumber', wintypes.DWORD),
        ('Gamepad', XINPUT_GAMEPAD)
    ]


class XINPUT_VIBRATION(ctypes.Structure):
    _fields_ = [
        ('wLeftMotorSpeed', wintypes.WORD),
        ('wRightMotorSpeed', wintypes.WORD)
    ]


def get_state(user_index):
    xinput = ctypes.windll.XInput1_4
    c_state = XINPUT_STATE()
    ret = xinput.XInputGetState(user_index, ctypes.byref(c_state))
    return ret, c_state


def set_state(user_index, vibration_left, vibration_right):
    xinput = ctypes.windll.XInput1_4
    c_vibration = XINPUT_VIBRATION()
    c_vibration.wLeftMotorSpeed = vibration_left
    c_vibration.wRightMotorSpeed = vibration_right
    ret = xinput.XInputSetState(user_index, ctypes.byref(c_vibration))
    return ret


if __name__ == '__main__':
    print('xinput controller.')
    print('shaking left motor.')
    print(set_state(0, 30000, 0))