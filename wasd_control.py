from gpiozero import Motor
import time
import sys
import select

motor_a = Motor(forward=17, backward=27)
motor_b = Motor(forward=23, backward=24)

print("WASD Controls: W=forward, A=left, S=backward, D=right, Q=quit")

try:
    while True:
        if select.select([sys.stdin], [], [], 0)[0]:
            key = sys.stdin.read(1).lower()
            if key == 'w':
                motor_a.forward(0.75)
                motor_b.forward(0.75)
            elif key == 'a':
                motor_a.forward(0.4)
                motor_b.forward(0.75)
            elif key == 's':
                motor_a.backward(0.75)
                motor_b.backward(0.75)
            elif key == 'd':
                motor_a.forward(0.75)
                motor_b.forward(0.4)
            elif key == 'q':
                motor_a.stop()
                motor_b.stop()
                break
            else:
                motor_a.stop()
                motor_b.stop()
        time.sleep(0.05)
finally:
    motor_a.close()
    motor_b.close()
(base) malharlabade@Malhars-MacBook-Air code % 
