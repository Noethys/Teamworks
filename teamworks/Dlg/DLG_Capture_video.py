#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import threading
from PIL import Image
from VideoCapture import Device
from Utils import UTILS_Fichiers
from Ctrl import CTRL_Bandeau
from Utils import UTILS_Adaptations


CAMERA = None
DEFAULT_DEVICE_WIDTH = 0
DEFAULT_DEVICE_HEIGHT = 0

def InitCamera():
    """ Initialisation de la webcam """
    global CAMERA, DEFAULT_DEVICE_WIDTH, DEFAULT_DEVICE_HEIGHT
    for x in range(0, 10) :
        try :
            CAMERA = Device(0)
            #buffer, width, height = CAMERA.getBuffer()
            width, height = 640, 480
            CAMERA.setResolution(width, height)
            DEFAULT_DEVICE_WIDTH  = width
            DEFAULT_DEVICE_HEIGHT = height
            return True
        except :
            pass
    return False


class VideoCaptureThread(threading.Thread):
    def __init__(self, control):
        self.width = DEFAULT_DEVICE_WIDTH
        self.height = DEFAULT_DEVICE_HEIGHT
        self.control = control
        self.isRunning =True
        self.buffer = wx.NullBitmap

        threading.Thread.__init__(self)

    def stop(self):
        self.isRunning = False

    def run(self):
        while self.isRunning:
            buffer, width, height = CAMERA.getBuffer()
            im = Image.frombytes('RGB', (width, height), buffer, 'raw', 'BGR', 0, -1)
            buff = im.tobytes()
            self.buffer = wx.BitmapFromBuffer(width, height, buff)
            x, y = (0, 0)
            try:
                width, height = self.control.GetSize()
                if width > self.width:
                    x = (width - self.width) / 2
                if height > self.height:
                    y = (height - self.height) / 2
                dc = wx.BufferedDC(wx.ClientDC(self.control), wx.NullBitmap, wx.BUFFER_VIRTUAL_AREA)
                dc.SetBackground(wx.Brush(wx.Colour(0, 0, 0)))
                dc.Clear()
                dc.DrawBitmap(self.buffer, x, y)
            except TypeError:
                pass
            except wx.PyDeadObjectError:
                pass
        self.isRunning = False


# -----------------------------------------------------------------------------------------------------------------------------

class CTRL_Video(wx.Panel):
    def __init__(self, parent, id=-1, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.SUNKEN_BORDER):
        wx.Panel.__init__(self, parent, id, pos, size, style)
        self.SetBackgroundColour(wx.Colour(0, 0, 0))
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnClose(self, event):
        try : self.Device.stop()
        except : pass

    def StopVideo(self):
        self.Device.stop()

    def StartVideo(self):
        self.Device = VideoCaptureThread(self)
        self.Device.start()
    
    def IsRunning(self):
        return self.Device.isRunning


# -----------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Depots", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent

        # Bandeau
        intro = _(u"Vous pouvez ici capturer une photo à partir d'une webcam connectée à votre ordinateur. Cliquez sur le bouton 'Prendre une photo' pour capturer l'image puis sur 'Ok' pour valider et ouvrir l'éditeur photo qui vous permettra d'effectuer un recadrage avant l'insertion dans la fiche individuelle.")
        titre = _(u"Capture d'une photo")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage=Chemins.GetStaticPath("Images/32x32/Webcam.png"))
        
        # Vidéo
        self.ctrl_video = CTRL_Video(self, -1)
        self.bouton_capture = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/BoutonsImages/Capturer_photo.png"), wx.BITMAP_TYPE_ANY))
        
        # Boutons
        self.ctrl_ligne = wx.StaticLine(self, -1)
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_options = CTRL_Bouton_image.CTRL(self, texte=_(u"Options"), cheminImage=Chemins.GetStaticPath("Images/32x32/Configuration2.png"))
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage=Chemins.GetStaticPath("Images/32x32/Valider.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))
        
        self.bouton_ok.Enable(False)
        
        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonCapture, self.bouton_capture)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOptions, self.bouton_options)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        # Lancement de la capture vidéo
        wx.CallLater(10, self.Initialisation)
    
    def Initialisation(self):
        etat = InitCamera()
        if etat == True :
            self.ctrl_video.StartVideo()
        else:
            self.bouton_capture.Enable(False)
            self.bouton_options.Enable(False)
            dlg = wx.MessageDialog(self, _(u"Noethys n'a pas réussi à se connecter à la caméra.\nVeuillez vérifier que celle-ci est bien installée..."), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

    def __set_properties(self):
        self.bouton_capture.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour prendre la photo")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_options.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour définir les propriétés de la capture vidéo")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((700, 720))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        grid_sizer_base.Add(self.ctrl_video, 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_base.Add(self.bouton_capture, 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_base.Add(self.ctrl_ligne, 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_options, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(2)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OnBoutonCapture(self, event): 
        """ Capture de la photo """
        if self.ctrl_video.IsRunning() :
            self.ctrl_video.StopVideo()
            CAMERA.saveSnapshot(UTILS_Fichiers.GetRepTemp("capture_video.jpg"), quality=100)
            self.bouton_capture.SetBitmapLabel(wx.Bitmap(Chemins.GetStaticPath("Images/BoutonsImages/Capturer_photo2.png"), wx.BITMAP_TYPE_ANY))
            self.bouton_ok.Enable(True)
        else:
            self.ctrl_video.StartVideo()
            self.bouton_capture.SetBitmapLabel(wx.Bitmap(Chemins.GetStaticPath("Images/BoutonsImages/Capturer_photo.png"), wx.BITMAP_TYPE_ANY))
            self.bouton_ok.Enable(False)

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonOptions(self, event): 
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()
        
        menuPop.AppendItem(wx.MenuItem(menuPop, 10, _(u"Propriétés du flux vidéo")))
        self.Bind(wx.EVT_MENU, self.Menu_proprietes_pin, id=10)
        
        menuPop.AppendItem(wx.MenuItem(menuPop, 20, _(u"Propriétés de la capture vidéo")))
        self.Bind(wx.EVT_MENU, self.Menu_proprietes_filter, id=20)
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()
    
    def Menu_proprietes_pin(self, event):
        CAMERA.displayCapturePinProperties() 
    
    def Menu_proprietes_filter(self, event):
        CAMERA.displayCaptureFilterProperties() 

    def OnBoutonOk(self, event): 
        self.EndModal(wx.ID_OK)

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
