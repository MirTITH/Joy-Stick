
import serial
import serial.tools.list_ports
from threading import Thread
import sys
print(sys.getdefaultencoding())

target_port = {
	"portx": "COM5",
	"bps": 2000000,
	"timeout": 1,  # 单位为秒
	"encoding": "utf-8"
}


def main():
	port_list()
	with serial.Serial(target_port["portx"], target_port["bps"], timeout=target_port["timeout"]) as ser:
		t_port_readline = Thread(target=port_readline,args=(ser,), daemon=True)
		# t_port_write = Thread(target=port_write,args=(ser,))

		t_port_readline.start()
		# t_port_write.start()
		try:
			while True:
				str_to_write = input()
				ser.write(bytes(str_to_write + "\n", encoding=target_port["encoding"]))
		except KeyboardInterrupt:
			exit()
		# t_port_readline.join()
		# t_port_write.join()


def port_readline(ser):
	while True:
		try:
			print(str(ser.read(), target_port["encoding"]), end="")
		except UnicodeDecodeError:
			print("[UnicodeDecodeError]")
		except:
			pass


def port_write(ser):
	while True:
		try:
			str_to_write = input()
			ser.write(bytes(str_to_write + "\n", encoding=target_port["encoding"]))
		except:
			pass


def port_list():
	print("Available ports:")
	for port, desc, hwid in sorted(serial.tools.list_ports.comports(include_links=False)):
		print("{}: {} [{}]".format(port, desc, hwid))


if __name__ == '__main__':
	main()

