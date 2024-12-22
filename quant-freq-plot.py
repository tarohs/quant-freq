#
# quant-freq-plot.py: quantize/resampling & play
# (c) 2017-2024 by taroh (sasaki.taroh@gmail.com)
#
#import pyaudio
import wave
import scipy.signal as sg
import sys
import numpy as np
import termios
import matplotlib.pyplot as plt

#KEYINT = .5
CHUNK = 128 * 690

if len(sys.argv) != 6 and len(sys.argv) != 7:
  print("usage:", sys.argv[0],
	 "FILENAME.wav StartSec EndSec NBITS FREQ_NDIVBASE [lr]");
  print("    divide time 1, 2, 4, 8, ... when FREQ_NDIVBASE == 0, 1, 2, 3, ...")
  print("    plot L & R ch if lr option (otherwise plot L & L quantized)")
  sys.exit(1)
filename = sys.argv[1]

wf = wave.open(filename, 'rb')
nch = wf.getnchannels()
srate = wf.getframerate()

stsec = float(sys.argv[2])
edsec = float(sys.argv[3])
maskbit = int(sys.argv[4])
fcb = int(sys.argv[5])
if len(sys.argv) == 7 and sys.argv[6] == "lr":
  isplotlr = True
else:
  isplotlr = False

stpos = int(stsec * srate) * nch
if edsec != -1:
  edpos = int(edsec * srate) * nch
else:
  edpos = -1

print(maskbit)
mask = ((1 << maskbit) - 1) << (16 - maskbit)
fcycle = 1 << fcb

print(filename, stpos, edpos)
print(maskbit, "bits,", srate / fcycle, "Hz sampling")

#p = pyaudio.PyAudio()
#
#stream = p.open(format = p.get_format_from_width(wf.getsampwidth()),
#                channels = nch,
#                rate = srate,
#                output = True)
#

# read whole samples
dbyte = wf.readframes(-1)
data = np.frombuffer(dbyte, dtype = "int16")

# cut interesting region
print(fcycle * nch, len(data))
if (edpos == -1):
  data = data[stpos:]
  edpos = len(data)
else:
  data = data[stpos:edpos]
print(fcycle * nch, len(data))
offset = edpos - stpos
offset = int((offset + (fcycle * nch) - 1) / (fcycle * nch)) * (fcycle * nch)
data = np.append(data, np.zeros(fcycle * nch, dtype="int16"))
data = data[:offset]
print(fcycle * nch, len(data))

## init LPF
#num_tap = 256
#lpflim = .95
#lpf = np.empty((8, num_tap))
#for fcb in range(1, 8):
#  fcycle = 1 << fcb
#  lpf_cutoff_hz = srate / fcycle / 2.
#  lpf_cutoff = lpf_cutoff_hz / (srate / 2.0)
#  win = "hann"
#  lpf[fcb] = sg.firwin(num_tap, lpf_cutoff, window = win)

intvl = CHUNK
#maskbit = 16
#fcb = 0
print(maskbit, fcb)

odata = data[:intvl]
pdata = odata.copy()
dummy = pdata & mask

# bit crasher
pdata = np.array(pdata & mask, dtype = "int16")

# freq crasher

#print(" ", srate / fcycle, "Hz, ", maskbit, "bits  ", sep = '', end = '\r')

if 2 <= fcycle:
  for i in range(2, fcycle * 2, 2):
    pdata[i    ::fcycle * 2] = pdata[0::fcycle * 2]
    pdata[i + 1::fcycle * 2] = pdata[1::fcycle * 2]
#  pdata = np.array(pdata * lpflim, dtype = "int16")
#
olch = odata[0::2]
orch = odata[1::2]
plch = pdata[0::2]
prch = pdata[1::2]
#
## LPF
#    outlch = sg.lfilter(lpf[fcb], [1.0], lch)
#    outrch = sg.lfilter(lpf[fcb], [1.0], rch)
#    pdata[0::2] = outlch
#    pdata[1::2] = outrch

# output
x = [i for i in range(len(olch))]
if isplotlr:
  plt.plot(x, olch, color = "b")
  plt.plot(x, orch, color = "r")
else:
  plt.plot(x, olch, color = "k")
  plt.plot(x, plch, color = "r")
#plt.plot(x, prch)

plt.hlines([y for y in range(-(2 ** 15), 2 ** 15 + 1, 1 << (16 - maskbit))],
	0, len(olch), "b", linestyle = ":", lw = 1)
plt.vlines([x for x in range(0, len(olch) + 1, 1 << fcb)], -(2 ** 15), 2 ** 15,
	"b", linestyle = ":", lw = 1)

plt.axis("off")
#ax = plt.gca() # get current axis
#ax.spines["right"].set_color("none")
#ax.spines["left"].set_color("none")
#ax.spines["top"].set_color("none")
#ax.spines["bottom"].set_color("none")

plt.show()

#  dbout = pdata.tobytes()
#  stream.write(dbout)
#stream.stop_stream()
#stream.close()
#
#p.terminate()
