"""
Show xinput controller status.
"""

import time
import ctypes
import tkinter as tk
from tkinter import ttk

import xinput


def log(*args):
    print('[XInput]:', *args)


GAMEPAD_FIELDS = [
    'wButtons',
    'bLeftTrigger',
    'bRightTrigger',
    'sThumbLX',
    'sThumbLY',
    'sThumbRX',
    'sThumbRY'
]


class XInputStatusUI:
    GRID_PADY = 2

    def __init__(self, master):
        super().__init__()
        self.master = master
        self._create_widgets()

    def _create_widgets(self):
        self._create_mainframe()
        self._create_statusbar()

    def _create_mainframe(self):
        self.mainframe = ttk.Frame(self.master)
        self.mainframe.pack(fill=tk.BOTH, expand=True)

        # connected
        self.w_connected_users = []
        label_frame = ttk.LabelFrame(self.mainframe, text='Connected')
        label_frame.pack(fill=tk.X)
        for i in range(xinput.XUSER_MAX_COUNT):
            var = tk.IntVar()
            button = tk.Checkbutton(label_frame, variable=var, text='User {}'.format(i), state=tk.DISABLED)
            button.pack(side=tk.LEFT)
            var.set(0)
            self.w_connected_users.append(var)

        # user index
        label_frame = ttk.Labelframe(self.mainframe, text='Index')
        label_frame.pack(fill=tk.X)
        self.var_user_index = tk.StringVar()
        users = [str(i) for i in range(xinput.XUSER_MAX_COUNT)]
        self.w_user_index = ttk.OptionMenu(label_frame, self.var_user_index, users[0], *users)
        self.w_user_index.pack(fill=tk.X)

        # gamepad
        label_frame = ttk.Labelframe(self.mainframe, text='Gamepad')
        label_frame.pack(fill=tk.X)
        label = ttk.Label(label_frame, text='dwPacketNumber')
        row = 0
        label.grid(row=row, column=0, pady=self.GRID_PADY)
        self.w_dwPacketNumber = ttk.Label(label_frame, text='0')
        self.w_dwPacketNumber.grid(row=row, column=1)
        self.w_packet_delta = ttk.Label(label_frame, text='0.0')
        self.w_packet_delta.grid(row=row, column=2)
        self.w_gamepad_fields = []
        self.w_gamepad_counts = []
        for name in GAMEPAD_FIELDS:
            row += 1
            label = ttk.Label(label_frame, text=name)
            label.grid(row=row, column=0, pady=self.GRID_PADY)
            label = ttk.Label(label_frame, text='')
            label.grid(row=row, column=1, pady=self.GRID_PADY)
            self.w_gamepad_fields.append(label)
            label = ttk.Label(label_frame, text='')
            label.grid(row=row, column=2, pady=self.GRID_PADY)
            self.w_gamepad_counts.append(label)

        # vibration
        label_frame = ttk.Labelframe(self.mainframe, text='Vibration')
        label_frame.pack(fill=tk.X)
        label = ttk.Label(label_frame, text='Set value in range 0~65535, then click send.')
        row = 0
        label.grid(row=row, columnspan=2, pady=self.GRID_PADY)
        row += 1
        label = ttk.Label(label_frame, text='LeftMotor')
        label.grid(row=row, column=0, pady=self.GRID_PADY)
        self.var_vibration_left = tk.StringVar(value='0')
        entry = ttk.Entry(label_frame, textvariable=self.var_vibration_left)
        entry.grid(row=row, column=1, pady=self.GRID_PADY)
        row += 1
        label = ttk.Label(label_frame, text='RightMotor')
        label.grid(row=row, column=0, pady=self.GRID_PADY)
        self.var_vibration_right = tk.StringVar(value='0')
        entry = ttk.Entry(label_frame, textvariable=self.var_vibration_right)
        entry.grid(row=row, column=1, pady=self.GRID_PADY)
        row += 1
        self.w_vibration_send = ttk.Button(label_frame, text='Send')
        self.w_vibration_send.grid(row=row, column=0, pady=self.GRID_PADY)
        self.w_vibration_pause = ttk.Button(label_frame, text='Pause')
        self.w_vibration_pause.grid(row=row, column=1, pady=self.GRID_PADY)
        self.w_vibration_clear = ttk.Button(label_frame, text='Clear')
        self.w_vibration_clear.grid(row=row, column=2, pady=self.GRID_PADY)

    def _create_statusbar(self):
        self.w_statusbar = ttk.Label(self.master, relief=tk.SUNKEN)
        self.w_statusbar.pack(side=tk.BOTTOM, fill=tk.X)


class XInputStatus:
    DELTA_TIME_MS = 1

    def __init__(self, master):
        super().__init__()
        self.master = master
        self.ui = XInputStatusUI(master)
        self._current_user_index = 0
        self._last_gamepad_info = None
        self._last_gamepad_count = {}
        self._last_packet_number = 0
        self._current_time = time.perf_counter()
        self._last_packet_time = self._current_time
        self._tick_count = 0
        self.setup()
        
    def setup(self):
        ui = self.ui
        ui.var_user_index.trace('w', self.on_user_index_updated)
        ui.w_vibration_send.configure(command=self.on_vibration_send)
        ui.w_vibration_pause.configure(command=self.on_vibration_pause)
        ui.w_vibration_clear.configure(command=self.on_vibration_clear)
        self.master.after(self.DELTA_TIME_MS, self.on_after)

    def show_status(self, text, duration=5.0):
        self.ui.w_statusbar.configure(text=text)

    def on_after(self):
        self.master.after(self.DELTA_TIME_MS, self.on_after)
        current_time = time.perf_counter()
        delta_time = current_time - self._current_time
        self._current_time = current_time
        self.tick(delta_time)

    def tick(self, delta_time):
        self._tick_count += 1
        if self._tick_count % 30 == 0:
            self.update_connected()

        user_index = self._current_user_index
        ret, state = xinput.get_state(user_index)
        if ret != 0:
            return

        # packet number
        ui = self.ui
        packet_number = state.dwPacketNumber
        if self._last_packet_number != packet_number:
            packet_delta_time = self._current_time - self._last_packet_time
            self._last_packet_time = self._current_time
            self._last_packet_number = packet_number
            ui.w_packet_delta.configure(text='{:10.5f}'.format(packet_delta_time))
        ui.w_dwPacketNumber.configure(text=str(packet_number))
        # gamepad fields
        gamepad = state.Gamepad
        current_gamepad_info = {}
        for i, name in enumerate(GAMEPAD_FIELDS):
            value = getattr(gamepad, name)
            if name == 'wButtons':
                ui.w_gamepad_fields[i].configure(text='{:016b}'.format(value))
            else:
                ui.w_gamepad_fields[i].configure(text=str(value))
            current_gamepad_info[name] = value
        # gamepad counts
        if self._last_gamepad_info:
            for i, name in enumerate(GAMEPAD_FIELDS):
                last_value = self._last_gamepad_info[name]
                value = current_gamepad_info[name]
                if last_value != value:
                    count = self._last_gamepad_count.get(name, 0)
                    count += 1
                    ui.w_gamepad_counts[i].configure(text=str(count))
                    self._last_gamepad_count[name] = count
        self._last_gamepad_info = current_gamepad_info

    def update_connected(self):
        connected_users = self.ui.w_connected_users
        for i in range(xinput.XUSER_MAX_COUNT):
            ret, _ = xinput.get_state(i)
            if ret == 0:
                connected_users[i].set(1)
            else:
                connected_users[i].set(0)

    def on_user_index_updated(self, *args):
        user_index = int(self.ui.var_user_index.get())
        self.show_status('new user index {}'.format(user_index))
        self._current_user_index = user_index
        self._last_gamepad_info = None
        self._last_gamepad_count = {}

    def on_vibration_send(self, *args):
        vibration_left_str = self.ui.var_vibration_left.get()
        vibration_right_str = self.ui.var_vibration_right.get()
        try:
            vibration_left = int(vibration_left_str) if vibration_left_str else 0
            vibration_right = int(vibration_right_str) if vibration_right_str else 0
        except ValueError:
            self.show_status('ERROR vibration should be a integer in range 0 ~ 65535')
            return
        if vibration_left < 0 or vibration_right > 65535:
            self.show_status('ERROR vibration left not in range 0 ~ 65535')
            return
        if vibration_right < 0 or vibration_right > 65535:
            self.show_status('ERROR vibration right not in range 0 ~ 65535')
            return

        self.show_status('vibration send {} {}'.format(vibration_left, vibration_right))
        ret = xinput.set_state(self._current_user_index, vibration_left, vibration_right)
        self.check_ret(ret)

    def on_vibration_pause(self, *args):
        ret = xinput.set_state(self._current_user_index, 0, 0)
        self.check_ret(ret)
        self.show_status('vibration pause')

    def on_vibration_clear(self, *args):
        self.ui.var_vibration_left.set('0')
        self.ui.var_vibration_right.set('0')
        self.on_vibration_send()
        self.show_status('vibration clear')

    def check_ret(self, ret):
        if ret != 0:
            self.show_status('ERROR xinput error {}: {}'.format(ret, ctypes.FormatError(ret)))

def main():
    root = tk.Tk()
    app = XInputStatus(root)
    root.title('Show XInput')
    root.geometry('500x600')
    root.mainloop()

if __name__ == '__main__':
    main()