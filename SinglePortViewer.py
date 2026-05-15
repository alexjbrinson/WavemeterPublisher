import pyqtgraph as pg
import numpy as np
from PyQt6 import QtWidgets, QtCore
import sys, time

class SinglePortViewer(QtWidgets.QWidget):
  def __init__(self, fos_port=-1, label='', maxLength=1000, color='red', data=[[],[]]):
    super().__init__()
    self.layout=QtWidgets.QVBoxLayout();
    self.upperLayout=QtWidgets.QHBoxLayout()
    self.labelBox=QtWidgets.QLabel(str(label)); #self.labelBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
    self.readoutBox=QtWidgets.QLabel('0 nm'); self.readoutBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
    self.pauseButton=QtWidgets.QPushButton("||"); self.pauseButton.clicked.connect(self.togglePausing)
    self.logButton=QtWidgets.QPushButton("Log"); self.logButton.clicked.connect(self.toggleLogging)
    self.closeButton=QtWidgets.QPushButton("Close") #this button is connected in multport viewer
    self.clearDataButton=QtWidgets.QPushButton("Clear"); self.clearDataButton.clicked.connect(self.clearData)
    self.switchModeButton=QtWidgets.QPushButton("Histogram"); self.switchModeButton.clicked.connect(self.switchMode)
    # self.switchModeButton.setMaximumSize(QtCore.QSize(100, 60))
    self.labelBox.setStyleSheet("QLabel { font-size: 16pt; color: "+f'{color}'+"; }")
    self.readoutBox.setStyleSheet("QLabel { font-size: 24pt; color: "+f'{color}'+"; }")
    self.pauseButton.setMaximumSize(     QtCore.QSize(40, 60))
    self.logButton.setMaximumSize( QtCore.QSize(40, 60))
    self.closeButton.setMaximumSize(     QtCore.QSize(80, 60))
    self.clearDataButton.setMaximumSize( QtCore.QSize(80, 60))
    self.switchModeButton.setMaximumSize(QtCore.QSize(80, 60))
    # self.upperLayout.addWidget(self.switchModeButton);
    self.upperLeftLayout=QtWidgets.QVBoxLayout()
    self.upperLeftLayout.addWidget(self.labelBox); self.upperLeftLayout.addWidget(self.switchModeButton);
    self.midLeftLayout=QtWidgets.QVBoxLayout()
    self.midLeftLayout.addWidget(self.logButton); self.midLeftLayout.addWidget(self.pauseButton)
    self.upperRightLayout=QtWidgets.QVBoxLayout()
    self.upperRightLayout.addWidget(self.clearDataButton); self.upperRightLayout.addWidget(self.closeButton)
    self.upperLayout.addLayout(self.upperLeftLayout)
    self.upperLayout.addLayout(self.midLeftLayout)
    self.upperLayout.addWidget(self.readoutBox)
    self.upperLayout.addLayout(self.upperRightLayout)
    self.layout.addLayout(self.upperLayout)
    self.timeStreamMode=True
    self.x=data[0]
    self.wl=data[1]
    self.fos_port=fos_port
    self.label=label
    self.maxLength=maxLength
    self.paused=False
    self.logging=False

    '''Creating timeStreamPlot widgets on left side of GUI'''
    curve1Kwargs={'pen':color, 'symbolBrush':color, 'symbolPen':None, 'symbolSize':2}
    curve2Kwargs={'pen':None, 'symbolBrush':color, 'symbolPen':None, 'symbolSize':2}
    self.leftPenList=[curve1Kwargs, curve2Kwargs]
    self.instantiatePlotGroup(['Wavelength (nm)', 'Frequency (THz)'],self.leftPenList, title=self.label, xLabel='time')
    self.yCurve =self.curveList[0]; self.frequencyCurve=self.curveList[1]
    self.updateViews_current(); self.viewList[0].getViewBox().sigResized.connect(self.updateViews_current)
    # self.updatePlot()

  def instantiatePlotGroup(self, yLabelList, penList, title='', xLabel='', invertRightAxis=False, invertLeftAxis=True):
    if type(yLabelList) == list:
      self.plot=pg.plot(title=title, color='red'); self.plot.setWindowTitle(title)
      self.plot.setLabel('bottom', xLabel, color='red',**{'font-size':'20pt'})
      curveList=[]; viewList=[]
      for i,label in enumerate(yLabelList):
        color=penList[i]['symbolBrush']
        if i==0:
          self.plot.setLabel('left', label, color=color, **{'font-size':'10pt'})
          self.plot.getAxis('left').setPen(pg.mkPen(color=color, width=1))
          curveList += [self.plot.plot(**penList[i])]; viewList += [self.plot]
          if len(yLabelList)>1:
            self.plot.showAxis('right')
            viewList[0].invertY(invertLeftAxis)
        else:

          self.plot.setLabel('right', label, color=color, **{'font-size':'10pt'})
          if len(penList)==2:self.plot.getAxis('right').setPen(pg.mkPen(color=color, width=1))
          viewList+=[pg.ViewBox()]
          self.plot.scene().addItem(viewList[i]); self.plot.getAxis('right').linkToView(viewList[i])
          viewList[i].invertY(invertRightAxis); viewList[i].setXLink(self.plot)
          curveList+=[pg.PlotDataItem(**penList[i])]
          viewList[i].addItem(curveList[i])
    self.viewList=viewList
    self.curveList=curveList
    self.layout.addWidget(self.plot)
    self.yCurve =self.curveList[0]; self.extraCurve=self.curveList[1]
    self.updateViews_current(); self.viewList[0].getViewBox().sigResized.connect(self.updateViews_current)

  def switchMode(self):
    print("switching mode")
    self.timeStreamMode = not self.timeStreamMode
    if self.timeStreamMode:
      self.plot.setLabel('left', 'Wavelength (nm)')
      self.plot.setLabel('right', 'Frequency (THz)')
      self.plot.setLabel('bottom', 'Time')
      self.viewList[0].invertY(True)
      self.switchModeButton.setText("Histogram")
    else:
      self.plot.setLabel('left', 'Counts')
      self.plot.setLabel('right', 'Fraction')
      self.plot.setLabel('bottom', 'Frequency (THz)')
      self.viewList[0].invertY(False)
      self.switchModeButton.setText("Timestream")
    self.updatePlot()
  def clearData(self):
    self.x=[];self.wl=[]

  def updateViews_current(self):
    for i in range(1, len(self.viewList)):
      self.viewList[i].setGeometry(self.viewList[0].getViewBox().sceneBoundingRect())
      self.viewList[i].linkedViewChanged(self.viewList[0].getViewBox(),self.viewList[i].XAxis)
    # self.updatePlot()

  def togglePausing(self):
    self.paused=not self.paused
    if self.paused: self.pauseButton.setText("|>")
    else: self.pauseButton.setText("||")

  def toggleLogging(self):
    self.logging = not self.logging
    if self.logging: self.logButton.setStyleSheet("QPushButton {background:Green}")
    else: self.logButton.setStyleSheet("QPushButton {color: Black; }")

  def updatePlot(self):
    if self.paused: return
    if self.timeStreamMode:
      self.yCurve.setData(x=[x-self.x[-1] for x in self.x], y=self.wl)
      self.viewList[0].autoRange(padding=0)
      self.viewList[1].setYRange(299792.458/np.max(self.wl), 299792.458/np.min(self.wl),padding=0)
    else:
      hist, edges= np.histogram(self.wl,bins=self.maxLength//10)
      edges=299792.458/edges
      # print(hist, edges)
      self.yCurve.setData(x=(edges[:-1]+edges[1:])/2, y=hist)
      self.viewList[0].autoRange(padding=0)
      self.viewList[1].setYRange(np.min(hist)/len(self.wl), np.max(hist)/len(self.wl), padding=0)


  def addData(self, time, measurement):
    if self.logging: print(f'time: {time}; measurement: {measurement}')# temporary functionality until I implement file browser
    self.x+=[time]; self.wl+=[measurement]
    if len(self.x)>self.maxLength: self.x.pop(0); self.wl.pop(0)
    self.readoutBox.setText(f'{measurement} nm')
    self.updatePlot()

def dummyUpdateFunction():
  t = time.time()
  y=np.random.rand()
  return(t,y)

if __name__ == '__main__':
  app = QtWidgets.QApplication(sys.argv)
  x=np.linspace(0,999,1000); y=np.sin(x)
  spv=SinglePortViewer(label="Port -1")#, data=[x,y])
  window = QtWidgets.QMainWindow();  cw=QtWidgets.QWidget()
  window.setCentralWidget(cw); 
  cw.setLayout(spv.layout)

  timer = QtCore.QTimer()
  timer.timeout.connect(lambda: spv.addData(*dummyUpdateFunction()))
  timer.start(1)

  window.show()
  sys.exit(app.exec())