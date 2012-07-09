#Boa:Frame:Frame1

import wx
import NCOA
import pickle, time, threading

wildcard = "NCOA files (*.coa; *.COA)|*.coa;*.COA|" "All files (*.*)|*.*"


def create(parent):
    return Frame1(parent)

[wxID_FRAME1, wxID_FRAME1DMCHOICE, wxID_FRAME1FILENAMETEXT, 
 wxID_FRAME1LOADBUTTON, wxID_FRAME1PROGRESSBAR, wxID_FRAME1SELECTBUTTON, 
 wxID_FRAME1STATICTEXT1, wxID_FRAME1STATICTEXT2, 
] = [wx.NewId() for _init_ctrls in range(8)]

class Frame1(wx.Frame):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_FRAME1, name=u'Frame1', parent=prnt,
              pos=wx.Point(495, 282), size=wx.Size(290, 220),
              style=wx.DEFAULT_FRAME_STYLE, title=u'NCOA Loader')
        self.SetClientSize(wx.Size(282, 186))
        self.Bind(EVT_COUNT, self.updateGauge)

        self.dmChoice = wx.Choice(choices=['DM1', 'DM2', 'DM3'],
              id=wxID_FRAME1DMCHOICE, name=u'dmChoice', parent=self,
              pos=wx.Point(24, 48), size=wx.Size(104, 21), style=0)

        self.staticText1 = wx.StaticText(id=wxID_FRAME1STATICTEXT1,
              label=u'Select a Debtmaster', name='staticText1', parent=self,
              pos=wx.Point(26, 32), size=wx.Size(97, 13), style=0)

        self.fileNameText = wx.TextCtrl(id=wxID_FRAME1FILENAMETEXT,
              name=u'fileNameText', parent=self, pos=wx.Point(152, 48),
              size=wx.Size(104, 21), style=0, value=u'')
        self.fileNameText.SetEditable(False)

        self.staticText2 = wx.StaticText(id=wxID_FRAME1STATICTEXT2,
              label=u'File Name', name='staticText2', parent=self,
              pos=wx.Point(154, 32), size=wx.Size(46, 13), style=0)

        self.selectButton = wx.Button(id=wxID_FRAME1SELECTBUTTON,
              label=u'Select File', name=u'selectButton', parent=self,
              pos=wx.Point(48, 96), size=wx.Size(75, 23), style=0)
        self.selectButton.Bind(wx.EVT_BUTTON, self.OnSelectButtonButton,
              id=wxID_FRAME1SELECTBUTTON)

        self.loadButton = wx.Button(id=wxID_FRAME1LOADBUTTON,
              label=u'Load File', name=u'loadButton', parent=self,
              pos=wx.Point(152, 96), size=wx.Size(75, 23), style=0)
        self.loadButton.Bind(wx.EVT_BUTTON, self.OnLoadButtonButton,
              id=wxID_FRAME1LOADBUTTON)

        self.progressBar = wx.Gauge(id=wxID_FRAME1PROGRESSBAR,
              name=u'progressBar', parent=self, pos=wx.Point(38, 144),
              range=100, size=wx.Size(200, 20), style=wx.GA_HORIZONTAL)
        self.progressBar.SetValue(0)
        self.progressBar.SetLabel(u'Progress')
        self.Bind(EVT_COUNT, self.updateGauge)
        
        

    def __init__(self, parent):
        self._init_ctrls(parent)
        self.Filename = None
        self.fileCount = 0
        
        
        
    def countFile(self, file):
        self.fileCount = 0
        self.readFile = open(file, 'rb')
        for i in self.readFile:
            self.fileCount += 1
        
    
    def OnSelectButtonButton(self, event):
        dlg = wx.FileDialog(self, 'Choose a file', 'f:\\', '', wildcard, wx.OPEN)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPath()
                self.Filename = filename
                self.fileNameText.Value = filename.split('\\')[-1]
        finally:
            self.countFile(filename)
            dlg.Destroy()

    
    def OnLoadButtonButton(self, event):
        DM = self.dmChoice.GetStringSelection()
        if self.validateContinue():
            message = "Load %s accounts into %s" % (str(self.fileCount), DM)
            dlg = wx.MessageDialog(self, message, 'Continue?', wx.OK | wx.CANCEL | wx.ICON_INFORMATION)
            try:
                result = dlg.ShowModal()
                if result == wx.ID_OK:
                    self.dm = self.dmChoice.GetStringSelection()
                    self.loadNCOA(self.Filename, self.dm)
            finally:
                dlg.Destroy()
        
    
    def loadNCOA(self, file, dm):
        worker = ncoaThread(file,dm,self.fileCount)
        worker.start()
##        fileName = self.Filename.split('\\')[-1]
##        message = "%s completed" % (fileName)
##        dlg = wx.MessageDialog(self, message, 'Complete', wx.OK | wx.ICON_INFORMATION)
##        try:
##            result = dlg.ShowModal()
##            self.Filename = None
##        finally:
##            dlg.Destroy()
            
    
    def validateContinue(self):
        if not self.dmChoice.GetStringSelection():
            dlg = wx.MessageDialog(self, 'Please Select a DM', 'Missing Value', wx.OK | wx.ICON_INFORMATION)
            try:
                result = dlg.ShowModal()
            finally:
                dlg.Destroy()
            return False
        elif not self.Filename:
            dlg = wx.MessageDialog(self, 'Please Select a File', 'Missing Value', wx.OK | wx.ICON_INFORMATION)
            try:
                result = dlg.ShowModal()
            finally:
                dlg.Destroy()
            return False
        else:
            return True
        
    
    def updateGauge(self, event):
        progress = event.GetValue()
        self.progressBar.SetValue(progress)
        
        

myEVT_COUNT = wx.NewEventType()
EVT_COUNT = wx.PyEventBinder(myEVT_COUNT,1)

class CountEvent(wx.PyCommandEvent):
    def __init__(self, etype, eid, value=None):
        wx.PyCommandEvent.__init__(self, etype, eid)
        self.value = value
        
    def GetValue(self):
        return self.value
        
        
        
        
class ncoaThread(threading.Thread):
    def __init__(self, parent, file, dm, fileCount):
        threading.Thread.__init__(self)
        self.parent = parent
        self.file = file
        self.dm = dm
        self.fileCount = fileCount
        self.acctsRan = 0
        self.progress = 0
        
    def run(self):
        readFile = open(self.file, 'rb')
        for item in readFile:
            self.ncoa = NCOA.NCOA(item, self.dm)
            self.ncoa.findCodes()
            self.ncoa.updateAddress()
            self.ncoa.updatePhone()
            self.ncoa.updateNotes()
            self.ncoa.mailReturnUpdate()
            self.acctsRan += 1
            progress = (self.acctsRan / self.fileCount) * 100
            self.progress = int(progress)
            evt = CountEvent(myEVT_COUNT,-1,self.progress)
            wx.PostEvent(self.parent, evt)
            
            
            
