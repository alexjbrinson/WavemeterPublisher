import numpy as np
import matplotlib.pyplot as plt

def plotSpectrum(scanNumber, offset=0):
  data=np.loadtxt(f'Scan{scanNumber}/finalSpectrum{scanNumber}.csv')
  mask=data[:,2]>0
  bins    =data[:,0][mask]
  counts  =data[:,1][mask]
  frames  =data[:,2][mask]
  daqRates=data[:,3][mask]
  print(max(frames))

  
  countErrors=np.sqrt(counts)
  rates=counts/frames
  rateErrors=countErrors/frames
  peakFreq=bins[np.argmax(rates)]
  amplitude=np.max(rates)
  bins=bins-offset
  line, caps, bars=plt.errorbar(x=bins, y=rates, yerr=rateErrors, fmt='.', label=f'scan {scanNumber}')
  plt.plot(bins, rates, color=line.get_color())
  return(peakFreq, amplitude)

peakFreqs=[]
amps=[]
scans=[*range(14,17)]+[18]#[8,9]
scans=[18]#,19]
for i in scans:
  pp,aa=plotSpectrum(i, offset=751)
  peakFreqs+=[pp]; amps+=[aa]
# plt.vlines(751.526533+250E-6*np.linspace(-1,1,3),ymin=0,ymax=amps[-1])
plt.legend()
plt.xlabel("Frequency-751 (THz)")
plt.ylabel("Counts per frame")
# plt.figure()
# plt.plot(scans,peakFreqs)
# plt.figure()
# plt.plot(scans, amps)
print(peakFreqs[-1])
print(amps[-1])
plt.show()