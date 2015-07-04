#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
# Copyright:    (c) 2008-09 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------

from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import FonctionsPerso
import os


class Aide(wx.Dialog):
    """ Aide provisoire """
    def __init__(self, parent, id=-1, title=_(u"Aide")):
        wx.Dialog.__init__(self, parent, id, title, size=(350, 200))

        # Label
        txt = _(u"Le système d'aide n'est pas encore fonctionnel.\n\nVous pouvez tout de même trouver actuellement de l'aide sur le \nsite de TeamWorks.")
        self.label = wx.StaticText(self, -1, txt)
        
        # Boutons
        self.bouton_web = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/acces_site.png", wx.BITMAP_TYPE_ANY))
        self.bouton_web.SetToolTipString(_(u"Cliquez ici pour accéder au site de TeamWorks"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour fermer"))
        
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSite, self.bouton_web)
        
    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.label, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 10)
        grid_sizer_base.Add(self.bouton_web, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 10)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_boutons, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(1)
        self.Layout()
        self.Centre()

        
    def OnBoutonSite(self, event):
        """ Acceder au site de TW """
        adresse_site = "http://teamworks.forumactif.com"
        FonctionsPerso.LanceFichierExterne(adresse_site)
        self.EndModal(wx.ID_OK)
        
        
        

if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frm = Aide(None)
    frm.ShowModal()
    app.MainLoop()