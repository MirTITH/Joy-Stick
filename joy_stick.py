import time
import pygame

def main():
	pygame.init()
	pygame.joystick.init()
	joystick = pygame.joystick.Joystick(0)
	joystick.init()
	axes_num = joystick.get_numaxes()
	print(axes_num)
	print(joystick.get_name())

	while True:
		# print(joystick.get_axis(2))
		for event in pygame.event.get():
			# Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
			if event.type == pygame.JOYBUTTONDOWN:
				print("JOY BUTTON DOWN")
			if event.type == pygame.JOYBUTTONUP:
				print("JOY BUTTON UP")
			if event.type == pygame.JOYAXISMOTION:
				print("Lx:%6.3f" % joystick.get_axis(0) ,end="    ")
				print("Ly:%6.3f" % joystick.get_axis(1) ,end="    ")
				print("Rx:%6.3f" % joystick.get_axis(2) ,end="    ")
				print("Ry:%6.3f" % joystick.get_axis(3) ,end="    ")
				print("LT:%6.3f" % joystick.get_axis(4) ,end="    ")
				print("RT:%6.3f" % joystick.get_axis(5) ,end="")
				# for i in range(axes_num):
				# 	print("%d: %.3f" % (i, joystick.get_axis(i)), end="")
				print()
			if event.type == pygame.JOYHATMOTION:
				print("JOY HAT MOTION")
			if event.type == pygame.JOYBALLMOTION:
				print("JOY BALL MOTION")

		# time.sleep(0.1)


if __name__ == '__main__':
    main()