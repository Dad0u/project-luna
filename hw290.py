from machine import Pin, SoftI2C
from time import sleep

# Calib data from the BMP sensor
# AC1 7727
# AC2 -1054
# AC3 -14254
# AC4 32232
# AC5 25612
# AC6 15397
# B1 6515
# B2 36
# MB -32768
# MC -11786
# MD 2447

ADDR_MPU = 104
ADDR_BMP = 119


def toint16(b):
  # Ne gère pas le signe...
  # return int.from_bytes(b, 'big')
  v = ((b[0] & 0x7f) << 8) + b[1]
  if b[0] >> 7:
    return - ((v ^ 0x7fff) + 1)
  else:
    return v


class HW290:
  def __init__(self, sda, scl):
    self.bus = SoftI2C(sda=Pin(sda), scl=Pin(scl))
    # Enable the sensor
    self.bus.writeto_mem(ADDR_MPU, 0x6b, bytes([1]))
    # Max range for the accelero
    self.bus.writeto_mem(ADDR_MPU, 0x1c, bytes([24]))
    # Max range for the gyro
    self.bus.writeto_mem(ADDR_MPU, 0x1b, bytes([24]))
    # Low-pass filter (2 -> ~100Hz)
    self.bus.writeto_mem(ADDR_MPU, 0x1a, bytes([2]))
    self.gain_gyro = 2000 / 32768 # -> °/s
    self.gain_accel = 16 * 9.81 / 32768 # m.s-2
    self.set_calib_coeffs(self.bus.readfrom_mem(ADDR_BMP, 0xaa, 22))

  def set_calib_coeffs(self, data):
    """
    Sets all the coeffs needed to compute pressure and temp from bmp180
    """
    self.ac = [None] # So that ac[1] corresponds to ac1 in the datasheet
    self.ac += [toint16(data[2 * i:2 * i + 2]) for i in range(3)]
    self.ac += [int.from_bytes(data[2 * i + 6:2 * i + 8], 'big')
        for i in range(3)]
    self.b = [None]
    self.b += [toint16(data[2 * i + 12:2 * i + 14]) for i in range(2)]
    self.mb, self.mc, self.md = [
        toint16(data[2 * i + 16:2 * i + 18]) for i in range(3)]

  def read_bmp(self):
    # Query temp
    self.bus.writeto_mem(ADDR_BMP, 0xf4, bytes([0x2e]))
    sleep(.0045)
    # Read temp
    ut = int.from_bytes((self.bus.readfrom_mem(ADDR_BMP, 0xf6, 2)), 'big')
    # Query pressure
    self.bus.writeto_mem(ADDR_BMP, 0xf4, bytes([0x34]))
    sleep(.0045)
    # Read pressure
    up = int.from_bytes(self.bus.readfrom_mem(ADDR_BMP, 0xf6, 2), 'big')

    # Computing real temperature
    x1 = (ut - self.ac[6]) * self.ac[5] / 32768
    x2 = self.mc * 2048 / (x1 + self.md)
    b5 = x1 + x2
    t = (b5 + 8) / 160
    # Computing real pressure
    b6 = b5 - 4000
    x1 = self.b[2] * (b6 * b6 // 4096) // 2048
    x2 = self.ac[2] * b6 // 2048
    x3 = x1 + x2
    b3 = (self.ac[1] * 4 + x3 + 2) // 4
    x1 = self.ac[3] * b6 // 8192
    x2 = self.b[1] * (b6 * b6 // 4096) // 65536
    x3 = (x1 + x2 + 2) // 4
    b4 = self.ac[4] * (x3 + 32768) // 32768
    b7 = (up - b3) * 50000
    p = b7 / b4 * 2
    x1 = (p // 256) * (p // 256)
    x1 = (x1 * 3038) // 65536
    x2 = (-7357 * p) // 65535
    p = p + (x1 + x2 + 3791) / 16
    return t, p

  @property
  def accel_x(self):
    return self.gain_accel * toint16(self.bus.readfrom_mem(ADDR_MPU, 0x3b, 2))

  @property
  def accel_y(self):
    return self.gain_accel * toint16(self.bus.readfrom_mem(ADDR_MPU, 0x3d, 2))

  @property
  def accel_z(self):
    return self.gain_accel * toint16(self.bus.readfrom_mem(ADDR_MPU, 0x3f, 2))

  @property
  def temp_mpu(self):
    return toint16(self.bus.readfrom_mem(ADDR_MPU, 0x41, 2)) / 340 + 36.53

  @property
  def gyro_x(self):
    return self.gain_gyro * toint16(self.bus.readfrom_mem(ADDR_MPU, 0x43, 2))

  @property
  def gyro_y(self):
    return self.gain_gyro * toint16(self.bus.readfrom_mem(ADDR_MPU, 0x45, 2))

  @property
  def gyro_z(self):
    return self.gain_gyro * toint16(self.bus.readfrom_mem(ADDR_MPU, 0x47, 2))
