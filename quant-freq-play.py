#
# quant-freq-play.py: quantize/resampling & play
# (c) 2017-2024 by taroh (sasaki.taroh@gmail.com)
#
import pyaudio
import wave
import scipy.signal as sg
import sys
import numpy as np
import termios

#KEYINT = .5
CHUNK = 128 * 690

def getkey():
  fd = sys.stdin.fileno()
  old = termios.tcgetattr(fd)
  new = termios.tcgetattr(fd)
# new[3] is lflags: reset ICANON, ECHO
  new[3] &= ~termios.ICANON
  new[3] &= ~termios.ECHO
  new[6][termios.VMIN] = 0
  new[6][termios.VTIME] = 0

  try:
    termios.tcsetattr(fd, termios.TCSANOW, new)
    ch = sys.stdin.read(1)

  finally:
    termios.tcsetattr(fd, termios.TCSANOW, old)

    return ch

if len(sys.argv) < 2 or 4 < len(sys.argv):
  print("usage:", sys.argv[0], "FILENAME.wav [STARTSEC [ENDSEC]]");
  sys.exit(1)
filename = sys.argv[1]

wf = wave.open(filename, 'rb')
nch = wf.getnchannels()
srate = wf.getframerate()

if len(sys.argv) == 3:
  stpos = int(srate * float(sys.argv[2]))
  edpos = -1
elif len(sys.argv) == 4:
  stpos = int(srate * float(sys.argv[2]))
  edpos = int(srate * float(sys.argv[3]))
else:
  stpos = 0
  edpos = -1

print(filename, stpos, edpos)
print("operation:")
print("    123456789abcdefg: # sample bits (1...16)")
print("    !@#$%^&*: time quantize by 1, 2, 4, 8, ..., 128 samples")

p = pyaudio.PyAudio()

stream = p.open(format = p.get_format_from_width(wf.getsampwidth()),
                channels = nch,
                rate = srate,
                output = True)

""" 
   format  : stream data format
   channels: 1: mono, 2: stereo
   rate    : sampling rate
   output  : output mode

"""

# read whole samples
dbyte = wf.readframes(-1)
data = np.frombuffer(dbyte, dtype = "int16")

# cut interesting region
if (edpos == -1):
  data = data[stpos * nch:]
else:
  data = data[stpos * nch:edpos * nch]

# init LPF
num_tap = 256
lpflim = .90
lpf = np.empty((8, num_tap))
for fcb in range(1, 8):
  fcycle = 1 << fcb
  lpf_cutoff_hz = srate / fcycle / 2.
  lpf_cutoff = lpf_cutoff_hz / (srate / 2.0)
  win = "hann"
  lpf[fcb] = sg.firwin(num_tap, lpf_cutoff, window = win)

intvl = CHUNK
maskbit = 16
fcb = 0

for i in range(int((len(data) + intvl - 1) / intvl)):
  pdata = data[i * intvl:i * intvl + intvl]

# bit crasher
  mask = ((1 << maskbit) - 1) << (16 - maskbit)
  pdata = np.array(pdata & mask, dtype = "int16")

# freq crasher
  fcycle = 1 << fcb
  pdata = pdata[:int(len(data) / (fcycle * 2)) * (fcycle * 2)]

  print(" ", srate / fcycle, "Hz, ", maskbit, "bits  ", sep = '', end = '\r')

  if 2 <= fcycle:
    for i in range(2, fcycle * 2, 2):
      pdata[i    ::fcycle * 2] = pdata[0::fcycle * 2]
      pdata[i + 1::fcycle * 2] = pdata[1::fcycle * 2]
    pdata = np.array(pdata * lpflim, dtype = "int16")

    lch = pdata[0::2]
    rch = pdata[1::2]

# LPF
    outlch = sg.lfilter(lpf[fcb], [1.0], lch)
    outrch = sg.lfilter(lpf[fcb], [1.0], rch)
    pdata[0::2] = outlch
    pdata[1::2] = outrch

# output
  dbout = pdata.tobytes()
  stream.write(dbout)
  ch = getkey()
  if (ch == 'q'):
    break
  elif ('1' <= ch and ch <= '9'):
    maskbit = int(ch)
  elif ('a' <= ch and ch <= 'g'):
    maskbit = ord(ch) - ord('a') + 10
  elif (ch == '!'):
    fcb = 0
  elif (ch == '@'):
    fcb = 1
  elif (ch == '#'):
    fcb = 2
  elif (ch == '$'):
    fcb = 3
  elif (ch == '%'):
    fcb = 4
  elif (ch == '^'):
    fcb = 5
  elif (ch == '&'):
    fcb = 6
  elif (ch == '*'):
    fcb = 7
#    dbyte = wf.readframes(CHUNK)

stream.stop_stream()
stream.close()

p.terminate()
