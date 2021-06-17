from machine import Pin, SoftI2C

ADDR = 104


def toint16(b):
  # Ne gère pas le signe...
  # return int.from_bytes(b, 'big')
  v = ((b[0] & 0x7f) << 8) + b[1]
  if b[0] >> 7:
    return - ((v ^ 0x7fff) + 1)
  else:
    return v


class HW270:
  def __init__(self, sda, scl):
    self.bus = SoftI2C(sda=Pin(sda), scl=Pin(scl))
    self.bus.writeto_mem(ADDR, 0x6b, bytes([1]))

  @property
  def accel_x(self):
    return toint16(self.bus.readfrom_mem(ADDR, 0x3b, 2))

  @property
  def accel_y(self):
    return toint16(self.bus.readfrom_mem(ADDR, 0x3d, 2))

  @property
  def accel_z(self):
    return toint16(self.bus.readfrom_mem(ADDR, 0x3f, 2))

  @property
  def temp(self):
    return toint16(self.bus.readfrom_mem(ADDR, 0x41, 2)) / 340 + 36.53

  @property
  def gyro_x(self):
    return toint16(self.bus.readfrom_mem(ADDR, 0x43, 2))

  @property
  def gyro_y(self):
    return toint16(self.bus.readfrom_mem(ADDR, 0x45, 2))

  @property
  def gyro_z(self):
    return toint16(self.bus.readfrom_mem(ADDR, 0x47, 2))
