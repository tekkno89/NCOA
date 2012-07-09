#!/usr/bin/env python
#Boa:App:BoaApp

import wx

import NCOAloader

modules ={u'NCOAloader': [1, 'Main frame of Application', u'NCOAloader.py']}

class BoaApp(wx.App):
    def OnInit(self):
        self.main = NCOAloader.create(None)
        self.main.Show()
        self.SetTopWindow(self.main)
        return True

def main():
    application = BoaApp(0)
    application.MainLoop()

if __name__ == '__main__':
    main()
