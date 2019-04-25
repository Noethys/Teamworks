#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-16 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import FonctionsPerso
import webbrowser
import random
import wx.lib.agw.aui as aui


class Page_documentation(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.image_fond = wx.Bitmap(Chemins.GetStaticPath(u"Images/Special/Annonce_documentation.png"), wx.BITMAP_TYPE_ANY)

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"En savoir plus"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_imprimer = CTRL_Bouton_image.CTRL(self, texte=_(u"Bon de commande"), cheminImage=Chemins.GetStaticPath("Images/32x32/Imprimante.png"))
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage=Chemins.GetStaticPath("Images/32x32/Fermer.png"))

        # Propriétés
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour en savoir plus sur le manuel de référence")))
        self.bouton_imprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour imprimer le bon de commande et les conditions générales de vente")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))

        # Calcule les espaces du sizer
        largeurImage, hauteurImage = self.image_fond.GetSize()
        hauteurBouton = self.bouton_imprimer.GetSize()[1]
        hauteurEspaceBas = 40
        hauteurEspaceHaut = hauteurImage - hauteurBouton - hauteurEspaceBas

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)

        grid_sizer_base.Add((largeurImage, hauteurEspaceHaut), 0, 0, 0)

        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add((10, 10), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_imprimer, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.RIGHT | wx.EXPAND, 30)

        grid_sizer_base.Add((largeurImage, hauteurEspaceBas), 0, 0, 0)

        self.SetSizer(grid_sizer_base)

        # Calcule taille de la fenêtre
        self.SetMinSize(self.image_fond.GetSize())
        self.Layout()

        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)

        # Init
        self.bouton_fermer.SetFocus()

    def OnEraseBackground(self, evt):
        dc = evt.GetDC()
        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)
        dc.Clear()
        dc.DrawBitmap(self.image_fond, 0, 0)

    def OnBoutonFermer(self, event):
        self.GetParent().EndModal(wx.ID_CANCEL)

    def OnBoutonAide(self, event):
        url = "https://teamworks.ovh/index.php/presentation/le-programme-de-financement"
        webbrowser.open(url)

    def OnBoutonImprimer(self, event):
        try:
            FonctionsPerso.LanceFichierExterne("https://teamworks.ovh/public/bon_commande_documentation.pdf")
        except:
            dlg = wx.MessageDialog(None, _(u"Teamworks ne peut pas ouvrir le PDF !\n\nVeuillez vérifier qu'un autre PDF n'est pas déjà ouvert en arrière-plan..."),_(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()









class Dialog(wx.Dialog):
    def __init__(self, parent, code=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.CAPTION)
        self.parent = parent
        self.page = Page_documentation(self)

        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.page, 1, wx.EXPAND, 0)
        self.SetSizer(sizer)
        sizer.Fit(self)
        self.Layout()
        self.CenterOnScreen()




    
if __name__ == "__main__":
    app = wx.App(0)
    dlg = Dialog(None)
    dlg.ShowModal() 
    dlg.Destroy()
    app.MainLoop()
