import pyqtgraph as pg
from PyQt6 import QtWidgets, QtCore
import os, sys, time, re
import numpy as np

class LiveHistogramWidget(QtWidgets.QWidget):
  resolutionScales = {"THZ":1, "GHz":1E-3,"MHz":1E-6,"kHz":1E-9}
  def __init__(self, orientation='vertical', label='', maxLength=10000, color='red'):
    super().__init__()
    contents = os.listdir('Scans/')
    scansList=[]
    for name in contents:
      match = re.match(r'^Scan(\d+)$', name)
      if match: scansList+=[int(match.group(1))]
    print("contents:",contents, scansList)
    if scansList: self.scanNumber = max(scansList)+1
    else: self.scanNumber=0

    self.layout = QtWidgets.QVBoxLayout()

    # self.resolution=0.00001
    self.resolutionDisplay=10
    self.resolutionMode="MHz"
    self.inputsLayout=QtWidgets.QHBoxLayout(); self.layout.addLayout(self.inputsLayout)
    self.resolutionTextBox=QtWidgets.QLabel("Resolution: "); self.inputsLayout.addWidget(self.resolutionTextBox)
    self.resolutionLineEdit=QtWidgets.QLineEdit(str(self.resolutionDisplay)); self.inputsLayout.addWidget(self.resolutionLineEdit)
    self.resolutionLineEdit.returnPressed.connect(self.updateResolution)
    self.unitsBox=QtWidgets.QComboBox(); self.inputsLayout.addWidget(self.unitsBox)
    self.unitsBox.addItems(list(LiveHistogramWidget.resolutionScales.keys()))
    self.unitsBox.setCurrentText(self.resolutionMode)
    self.unitsBox.currentTextChanged.connect(self.updateResolution)
    self.updateResolution()
    self.toggleButton=QtWidgets.QPushButton(f"Start Scan {self.scanNumber}"); self.layout.addWidget(self.toggleButton)
    self.toggleButton.clicked.connect(self.start)

    self.scanning=False
    
    # self.minBin,self.maxBin=398.911,398.912
    self.xCurrent=-1
    self.spectrumBins=[self.xCurrent+ii*self.resolution for ii in [-1,0,1]]
    self.integrationTimes=[0 for ii in self.spectrumBins]
    self.signalTotals=[0 for ii in self.spectrumBins]
    self.signalRates=[0 for ii in self.spectrumBins]
    self.plot=pg.PlotWidget(title=label, color='red');self.layout.addWidget(self.plot)
    curve1Kwargs={'pen':color, 'symbolBrush':color, 'symbolPen':None, 'symbolSize':2}
    self.signalCurve = pg.PlotDataItem(**curve1Kwargs); self.plot.addItem(self.signalCurve)

  def updateResolution(self):
    try: 
      temp = float(self.resolutionLineEdit.text())
      scaling = LiveHistogramWidget.resolutionScales[self.unitsBox.currentText()]
      proposedRes = temp*scaling
      if proposedRes>0 and proposedRes<1:
        self.resolution=proposedRes
        self.resolutionDisplay=self.resolution/scaling
        self.resolutionMode=self.unitsBox.currentText()
    except exception as ee: print("exception occured:",ee)
    self.resolutionLineEdit.setText(str(self.resolutionDisplay))
    self.unitsBox.setCurrentText(self.resolutionMode)
    self.resolutionTextBox.setText(f"Resolution:\n{self.resolutionDisplay} {self.resolutionMode}")
    
  def start(self):
    self.spectrumBins=[self.xCurrent-self.resolution/2, self.xCurrent+self.resolution/2]
    self.integrationTimes=[0 for ii in self.spectrumBins]
    self.signalTotals=[0 for ii in self.spectrumBins]
    self.signalRates=[0 for ii in self.spectrumBins]

    self.toggleButton.clicked.disconnect(self.start)
    self.toggleButton.setText(f"Stop Scan {self.scanNumber}")
    self.toggleButton.clicked.connect(self.stop)
    self.directory=f'Scans/Scan{self.scanNumber}/'
    if not os.path.exists(self.directory): os.makedirs(self.directory)
    self.file=open(f'{self.directory}Scan{self.scanNumber}Timestream.csv','w')
    self.scanning=True
    self.resolutionLineEdit.setEnabled(not self.scanning)
    self.unitsBox.setEnabled(not self.scanning)
  def stop(self):
    self.scanning=False
    np.savetxt(f'{self.directory}finalSpectrum{self.scanNumber}.csv',np.c_[self.spectrumBins, self.signalTotals,self.integrationTimes,self.signalRates])
    self.scanNumber+=1
    self.directory=f'Scans/Scan{self.scanNumber}'
    if not os.path.exists: os.makedirs(self.directory)
    self.toggleButton.clicked.disconnect(self.stop)
    self.toggleButton.setText(f"Start Scan {self.scanNumber}")
    self.toggleButton.clicked.connect(self.start)
    self.resolutionLineEdit.setEnabled(not self.scanning)
    self.unitsBox.setEnabled(not self.scanning)

  def update(self, xDat, currentSignal):
    self.xCurrent=xDat
    if self.scanning:
        tt=time.time()
        self.file.write(f'{tt}, {xDat}, {currentSignal}\n'); self.file.flush()
        if xDat-self.spectrumBins[-1]>10*self.resolution: return
        if self.spectrumBins[0]-xDat>10*self.resolution: return
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
        displayMask=np.array(self.signalRates[1:])>0
        self.signalCurve.setData(np.array(self.signalRates[1:])[displayMask], np.array(self.spectrumBins[1:])[displayMask])#TODO: confirm that I shouldn't included first bin

    def exit(self):
      if self.scanning: self.stop()