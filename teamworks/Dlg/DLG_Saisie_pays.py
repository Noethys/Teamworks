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


class Dialog(wx.Dialog):
    def __init__(self, parent, title="" , IDpays=0):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.panel_base = wx.Panel(self, -1)
        self.sizer_contenu_staticbox = wx.StaticBox(self.panel_base, -1, "")
        self.label_nom = wx.StaticText(self.panel_base, -1, _(u"Nom du pays :"))
        self.text_nom = wx.TextCtrl(self.panel_base, -1, "")
        self.label_nation = wx.StaticText(self.panel_base, -1, _(u"Nationalit� :"))
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

    def __set_properties(self):
        self.SetTitle(_(u"Gestion des pays"))
        if 'phoenix' in wx.PlatformInfo:
            _icon = wx.Icon()
        else :
            _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.text_nom.SetToolTip(wx.ToolTip(_(u"Saisissez ici le nom du pays")))
        self.text_nation.SetToolTip(wx.ToolTip(_(u"Saisissez ici la nationalit� du pays")))
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
        self.CenterOnScreen()


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
        """ Sauvegarde des donn�es dans la base de donn�es """
        
        # R�cup�ration ds valeurs saisies
        varNom = self.text_nom.GetValue()
        varNation = self.text_nation.GetValue()

        DB = GestionDB.DB()       
        if self.IDpays == 0:
            # Enregistrement d'une nouvelle coordonn�e
            listeDonnees = [ ("code_drapeau",   "autre"),  
                                    ("nom",    varNom),
                                    ("nationalite",    varNation), ]
            newID = DB.ReqInsert("pays", listeDonnees)
            ID = newID
        else:
            # Modification de la coordonn�e
            listeDonnees = [("nom",    varNom),
                                    ("nationalite",    varNation), ]
            DB.ReqMAJ("pays", listeDonnees, "IDpays", self.IDpays)
            ID = self.IDpays
        DB.Commit()
        DB.Close()
        return ID

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Lespaysetnationalits")

    def OnBoutonAnnuler(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event):
        """ Validation des donn�es saisies """
        # V�rifie que une valeur a �t� saisie
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
        self.EndModal(wx.ID_OK)

    
    
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dlg = Dialog(None, "", IDpays=0)
    dlg.ShowModal()
    dlg.Destroy()

    app.MainLoop()
