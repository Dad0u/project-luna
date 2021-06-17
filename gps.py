from machine import UART


def get_trame(u):
  print("GET_TRAME")
  r = None
  while not r or b'$' not in r:
    r = u.readline()
  while not r.endswith(b'\r\n'):
    r += u.readline() or b''
  print("NEW TRAME",r)
  return r


def get_tlla(t):
  _,t,lati,N,longi,E,_,n,p,alti,*_ = t.split(b',')
  r = {'h':int(t[:2]),'m':int(t[2:4]),'s':int(t[4:6])}
  r['lati'] = int(lati[:4]+lati[5:])
  if N == b'S':
    r['lati'] = -r['lati']
  r['longi'] = int(longi[:5]+longi[6:])
  if E == b'W':
    r['longi'] = -r['longi']
  r['alti'] = float(alti)
  r['n'] = int(n)
  r['precision'] = p
  return r


def main():
  #while True:
  #  r = u.readline()
  #  if r:
  #    print(r.decode('ASCII').strip())
  u = UART(1)
  u.init(9600, bits=8, parity=None, stop=1,tx=12,rx=14)
  while True:
    t = get_trame(u)
    if not t.startswith(b'$GNGGA'):
      continue
    r = get_tlla(t)
    print("T",r['h'],r['m'],r['s'])
    print("-",r['lati'])
    print("|",r['longi'])
    print(".",r['alti'])
    print(r)
