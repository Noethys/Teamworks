#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
# Copyright:    (c) 2008-09 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------

import wx

class GaugePulse(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyGauge.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.THICK_FRAME
        wx.Dialog.__init__(self, *args, **kwds)
        self.label_Intro = wx.StaticText(self, -1, "Veuillez patientez...")
        self.gauge = wx.Gauge(self, -1, 10)
        self.bouton_Annuler = wx.Button(self, -1, "Annuler")
        self.count = 0
        
        self.__set_properties()
        self.__do_layout()
        # end wxGlade

        self.Bind(wx.EVT_TIMER, self.TimerHandler)
        self.timer = wx.Timer(self)
        self.timer.Start(100)

    def __set_properties(self):
        # begin wxGlade: MyGauge.__set_properties
        self.SetTitle("")
        self.SetSize((350, 155))
        self.bouton_Annuler.SetToolTipString(u"Cliquez ici pour interrompre la procédure")
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyGauge.__do_layout
        grid_sizer_gauge = wx.FlexGridSizer(rows=3, cols=1, vgap=15, hgap=0)
        grid_sizer_gauge.Add(self.label_Intro, 0, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        grid_sizer_gauge.Add(self.gauge, 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_gauge.Add(self.bouton_Annuler, 0, wx.RIGHT|wx.BOTTOM|wx.ALIGN_RIGHT, 10)
        self.SetSizer(grid_sizer_gauge)
        grid_sizer_gauge.AddGrowableCol(0)
        self.Layout()
        # end wxGlade

# end of class MyGauge

    def __del__(self):
        self.timer.Stop()

    def TimerHandler(self, event):
        self.count = self.count + 1

        if self.count >= 50:
            self.count = 0

        #self.g1.SetValue(self.count)
        self.gauge.Pulse()


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    GaugeAttente = GaugePulse(None, -1, "")
    app.SetTopWindow(GaugeAttente)
    GaugeAttente.Show()
    app.MainLoop()
