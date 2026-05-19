import numpy as np
import matplotlib.pyplot as plt
def loadData(path):
  c = 299_792_458_000 #nm*MHz
  data=np.loadtxt(path, delimiter=",")
  times=data[:,0]
  wl=data[:,1]
  f=c/wl
  print(f)
  errors=f-751_526_954
  return(times, wl, f, errors)
maxF=0
fileList=["logFile_399locked","logFile_399unlocked"]#,"logFile_399relocked","logFile5","logFile6"]
dataDic={}
for file in fileList:
  data = loadData(f"{file}.csv")
  dataDic[file] = data
  plt.plot((data[0]-dataDic[fileList[0]][0][0])/3600, data[-1], label=file.removeprefix("logFile_399"))
plt.legend()
plt.xlabel("Time (h)")
plt.ylabel("Error (MHz)")
plt.show()

unlockedF=dataDic["logFile_399unlocked"][-1]
bins = np.linspace(np.min(unlockedF), np.max(unlockedF),100)
pBins = (bins[:-1]+bins[1:])/2

for file in fileList:
  hist=np.histogram(dataDic[file][-1], bins)
  plt.plot(pBins, hist[0]/np.sum(hist[0]), label=file)
plt.legend()
plt.show()