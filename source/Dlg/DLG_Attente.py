#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
# Copyright:    (c) 2008-09 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------

import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import threading
import thread
import time
import FonctionsPerso


class newThread(threading.Thread):
    def __init__(self, parent):
        threading.Thread.__init__(self)
        self.parent = parent
        
    def run(self):
        while 1 :
            
            if self.parent.doExit : 
                thread.exit()
                time.sleep(0.1)
            
            self.parent.gauge.Pulse()
            time.sleep(0.03)


class MyFrame(wx.Frame):
    def __init__(self, parent, label=""):
        wx.Frame.__init__(self, parent, -1, title=_(u"Veuillez patientez"), name="frm_attente", style=wx.CAPTION|wx.CLOSE_BOX|wx.SIMPLE_BORDER|wx.CLIP_CHILDREN)
        self.panel_base = wx.Panel(self, -1)
        self.label_intro = wx.StaticText(self.panel_base, -1, label)
        self.gauge = wx.Gauge(self.panel_base, -1, 50, (110, 95), (250, 25), style=wx.GA_HORIZONTAL|wx.GA_SMOOTH)
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))
        self.doExit = 0
        self.__set_properties()
        self.__do_layout()
    
        self.Bind(wx.EVT_BUTTON, self.Onbouton_annuler, self.bouton_annuler)
        
        thread1 = newThread(self)
        thread1.start()


    def __set_properties(self):
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_base_2 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        sizer_base_2.Add(self.label_intro, 0, wx.LEFT|wx.RIGHT|wx.TOP, 10)
        sizer_base_2.Add(self.gauge, 0, wx.ALL|wx.EXPAND, 10)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        sizer_base_2.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.panel_base.SetSizer(sizer_base_2)
        sizer_base.Add(self.panel_base, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        self.Layout()
        self.Centre()
        self.SetSize((380, 138))

    def Onbouton_annuler(self, event):
        self.stop()
    
    def stop(self):
        self.doExit = 1
        time.sleep(0.1)
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()
    
    

if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_attente = MyFrame(None, _(u"Texte d'intro ici..."))
    app.SetTopWindow(frame_attente)
    frame_attente.Show()
    app.MainLoop()
