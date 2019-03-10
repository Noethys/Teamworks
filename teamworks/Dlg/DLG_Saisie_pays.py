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
import GestionDB
import FonctionsPerso


class MyFrame(wx.Frame):
    def __init__(self, parent, title="" , IDpays=0):
        wx.Frame.__init__(self, parent, -1, title=title, style=wx.DEFAULT_FRAME_STYLE)
        self.MakeModal(True)
        self.parent = parent
        self.panel_base = wx.Panel(self, -1)
        self.sizer_contenu_staticbox = wx.StaticBox(self.panel_base, -1, "")
        self.label_nom = wx.StaticText(self.panel_base, -1, _(u"Nom du pays :"))
        self.text_nom = wx.TextCtrl(self.panel_base, -1, "")
        self.label_nation = wx.StaticText(self.panel_base, -1, _(u"Nationalité :"))
        self.text_nation = wx.TextCtrl(self.panel_base, -1, "")
        self.bouton_aide = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_ok = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Ok"), cheminImage=Chemins.GetStaticPath("Images/32x32/Valider.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))
        
        self.IDpays = IDpays
        if IDpays != 0 : 
            self.Importation()

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
    def __set_properties(self):
        self.SetTitle(_(u"Gestion des pays"))
        if 'phoenix' in wx.PlatformInfo:
            _icon = wx.Icon()
        else :
            _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.text_nom.SetToolTip(wx.ToolTip(_(u"Saisissez ici le nom du pays")))
        self.text_nation.SetToolTip(wx.ToolTip(_(u"Saisissez ici la nationalité du pays")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler la saisie")))
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())
        self.SetMinSize((326, 195))

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        sizer_contenu = wx.StaticBoxSizer(self.sizer_contenu_staticbox, wx.VERTICAL)
        grid_sizer_contenu = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_contenu.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.text_nom, 1, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.label_nation, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.text_nation, 1, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableCol(1)
        sizer_contenu.Add(grid_sizer_contenu, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(sizer_contenu, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.panel_base.SetSizer(grid_sizer_base)
        sizer_base.Add(self.panel_base, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()
        self.Centre()


    def Importation(self):
        DB = GestionDB.DB()
        req = "SELECT nom, nationalite FROM pays WHERE IDpays=%d" % self.IDpays
        DB.ExecuterReq(req)
        donnees = DB.ResultatReq()[0]
        DB.Close()
        if len(donnees) == 0: return
        # Place les valeurs dans les controles
        self.text_nom.SetValue(donnees[0])
        self.text_nation.SetValue(donnees[1])

    def Sauvegarde(self):
        """ Sauvegarde des données dans la base de données """
        
        # Récupération ds valeurs saisies
        varNom = self.text_nom.GetValue()
        varNation = self.text_nation.GetValue()

        DB = GestionDB.DB()       
        if self.IDpays == 0:
            # Enregistrement d'une nouvelle coordonnée
            listeDonnees = [ ("code_drapeau",   "autre"),  
                                    ("nom",    varNom),
                                    ("nationalite",    varNation), ]
            newID = DB.ReqInsert("pays", listeDonnees)
            ID = newID
        else:
            # Modification de la coordonnée
            listeDonnees = [("nom",    varNom),
                                    ("nationalite",    varNation), ]
            DB.ReqMAJ("pays", listeDonnees, "IDpays", self.IDpays)
            ID = self.IDpays
        DB.Commit()
        DB.Close()
        return ID

    def OnClose(self, event):
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        event.Skip()
        
    def OnBoutonAide(self, event):
        FonctionsPerso.Aide(23)

    def OnBoutonAnnuler(self, event):
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()

    def OnBoutonOk(self, event):
        """ Validation des données saisies """
        # Vérifie que une valeur a été saisie
        valeur = self.text_nom.GetValue()
        if valeur == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir au moins un nom de pays !"), "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            self.text_nom.SetFocus()
            return
        
        # Sauvegarde
        self.Sauvegarde()
        # MAJ du listCtrl des valeurs de points
        if FonctionsPerso.FrameOuverte("panel_config_pays") != None :
            self.GetParent().MAJ_ListCtrl()
        # Fermeture
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()

    
    
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, "", IDpays=0)
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
