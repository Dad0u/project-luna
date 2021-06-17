from time import sleep
from servo import Servo, TRAVEL

s1 = Servo(4)

while True:
  for i in range(0, TRAVEL, 10):
    print(i)
    s1.angle = i
    sleep(1)
