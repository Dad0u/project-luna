from machine import Pin, PWM

MAXVAL = 240
MINVAL = 50
TRAVEL = 180
FREQ = 100


class Servo:
  def __init__(self, pin_id, limits=(0, TRAVEL)):
    self.pwm = PWM(Pin(pin_id))
    self.pwm.freq(FREQ)
    self._angle = TRAVEL / 2
    assert limits[0] < limits[1], "Incorrect limits"
    self.min = max(min(limits[0], TRAVEL), 0)
    self.max = max(min(limits[1], TRAVEL), 0)

  @property
  def angle(self):
    return self._angle

  @angle.setter
  def angle(self, angle):
    angle = max(min(angle, self.max), self.min)
    self._angle = angle
    duty = int(angle / TRAVEL * (MAXVAL - MINVAL) + MINVAL)
    self.pwm.duty(duty)
