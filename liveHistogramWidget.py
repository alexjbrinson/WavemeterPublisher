import pyqtgraph as pg
from PyQt6 import QtWidgets, QtCore
import os, sys, time
import numpy as np

class LiveHistogramWidget(QtWidgets.QWidget):
  def __init__(self, orientation='vertical', label='', maxLength=10000, color='red'):
    super().__init__()
    self.layout = QtWidgets.QVBoxLayout()
    self.toggleButton=QtWidgets.QPushButton("Start"); self.layout.addWidget(self.toggleButton)
    self.toggleButton.clicked.connect(self.start)

    self.scanning=False
    self.numBins=100
    self.resolution=0.00001
    # self.minBin,self.maxBin=398.911,398.912
    self.spectrumBins=[398.9118+ii*self.resolution for ii in [-1,0,1]]
    self.integrationTimes=[0 for ii in self.spectrumBins]
    self.signalTotals=[0 for ii in self.spectrumBins]
    self.signalRates=[0 for ii in self.spectrumBins]
    self.plot=pg.PlotWidget(title=label, color='red');self.layout.addWidget(self.plot)
    curve1Kwargs={'pen':color, 'symbolBrush':color, 'symbolPen':None, 'symbolSize':2}
    self.signalCurve = pg.PlotDataItem(**curve1Kwargs); self.plot.addItem(self.signalCurve)
  def start(self):
    self.scanning=True
  def stop(self):
    pass
  def update(self, xDat, currentSignal):
    if self.scanning:
        while xDat>self.spectrumBins[-1]:
          print("too high",xDat, self.spectrumBins[-1])
          self.spectrumBins.append(self.spectrumBins[-1]+self.resolution) 
          self.integrationTimes.append(0)
          self.signalTotals.append(0)
          self.signalRates.append(0)
        while xDat<self.spectrumBins[0]:
          print("too low",xDat, self.spectrumBins[0])
          self.spectrumBins.insert(0, self.spectrumBins[0]-self.resolution)
          self.integrationTimes.insert(0,0)
          self.signalTotals.insert(0,0)
          self.signalRates.insert(0,0)
        self.currentBin = np.digitize(xDat, self.spectrumBins)
        # print(currentSignal, self.currentBin)
        self.signalTotals[self.currentBin]+=currentSignal
        self.integrationTimes[self.currentBin]+=1
        self.signalRates[self.currentBin]=self.signalTotals[self.currentBin]/self.integrationTimes[self.currentBin]
        self.signalCurve.setData(self.signalRates, self.spectrumBins)