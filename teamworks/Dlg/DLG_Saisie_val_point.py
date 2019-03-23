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
import datetime
import FonctionsPerso
if 'phoenix' in wx.PlatformInfo:
    from wx.adv import DatePickerCtrl, DP_DROPDOWN
else :
    from wx import DatePickerCtrl, DP_DROPDOWN


class Dialog(wx.Dialog):
    def __init__(self, parent, title="" , IDvaleur=0):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.panel_base = wx.Panel(self, -1)
        self.sizer_contenu_staticbox = wx.StaticBox(self.panel_base, -1, "")
        self.label_valeur = wx.StaticText(self.panel_base, -1, _(u"Valeur :"))
        self.text_valeur = wx.TextCtrl(self.panel_base, -1, "", style=wx.TE_CENTRE)
        self.label_euro = wx.StaticText(self.panel_base, -1, u"€")
        self.label_dateDebut = wx.StaticText(self.panel_base, -1, _(u"A partir du :"))
        self.datepicker_dateDebut = DatePickerCtrl(self.panel_base, -1, style=DP_DROPDOWN)
        self.bouton_aide = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_ok = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Ok"), cheminImage=Chemins.GetStaticPath("Images/32x32/Valider.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))
        
        self.IDvaleur = IDvaleur
        if IDvaleur != 0 : 
            self.Importation()

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)

    def __set_properties(self):
        self.SetTitle(_(u"Gestion de la valeur du point"))
        if 'phoenix' in wx.PlatformInfo:
            _icon = wx.Icon()
        else :
            _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.text_valeur.SetMinSize((60, -1))
        self.text_valeur.SetToolTip(wx.ToolTip("Saisissez ici une valeur"))
        self.bouton_aide.SetToolTip(wx.ToolTip("Cliquez ici pour obtenir de l'aide"))
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetToolTip(wx.ToolTip("Cliquez ici pour valider"))
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetToolTip(wx.ToolTip("Cliquez ici pour annuler la saisie"))
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        sizer_contenu = wx.StaticBoxSizer(self.sizer_contenu_staticbox, wx.VERTICAL)
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        grid_sizer_contenu.Add(self.label_valeur, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.text_valeur, 0, 0, 0)
        grid_sizer_contenu.Add(self.label_euro, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.label_dateDebut, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.datepicker_dateDebut, 0, 0, 0)
        sizer_contenu.Add(grid_sizer_contenu, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(sizer_contenu, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.panel_base.SetSizer(grid_sizer_base)
        sizer_base.Add(self.panel_base, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()
        self.CenterOnScreen()

    def Importation(self):
        DB = GestionDB.DB()
        req = "SELECT * FROM valeurs_point WHERE IDvaleur_point=%d" % self.IDvaleur
        DB.ExecuterReq(req)
        donnees = DB.ResultatReq()[0]
        DB.Close()
        if len(donnees) == 0: return
        # Place la valeur dans le controle
        self.text_valeur.SetValue(str(donnees[1]))
        # Place la date dans le cdatePicker 
        jour = int(donnees[2][8:10])
        mois = int(donnees[2][5:7])-1
        annee = int(donnees[2][:4])
        date = wx.DateTime()
        date.Set(jour, mois, annee)
        self.datepicker_dateDebut.SetValue(date)

    def Sauvegarde(self):
        """ Sauvegarde des données dans la base de données """
        
        # Récupération ds valeurs saisies
        varValeur = self.text_valeur.GetValue()
        date_tmp = self.datepicker_dateDebut.GetValue()
        varDate = str(datetime.date(date_tmp.GetYear(), date_tmp.GetMonth()+1, date_tmp.GetDay()))

        DB = GestionDB.DB()
        # Création de la liste des données
        listeDonnees = [    ("valeur",   varValeur),  
                                    ("date_debut",    varDate), ]
        if self.IDvaleur == 0:
            # Enregistrement d'une nouvelle coordonnée
            newID = DB.ReqInsert("valeurs_point", listeDonnees)
            ID = newID
        else:
            # Modification de la coordonnée
            DB.ReqMAJ("valeurs_point", listeDonnees, "IDvaleur_point", self.IDvaleur)
            ID = self.IDvaleur
        DB.Commit()
        DB.Close()
        return ID

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Lesvaleursdepoints")

    def OnBoutonAnnuler(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event):
        """ Validation des données saisies """
        # Vérifie que une valeur a été saisie
        valeur = self.text_valeur.GetValue()
        if valeur == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir une valeur de point."), "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            self.text_valeur.SetFocus()
            return
        # Vérifie que la valeur est bien constituée de chiffres uniquement
        incoherences = ""
        for lettre in valeur :
            if lettre not in "0123456789." : incoherences += "'"+ lettre + "', "
        if len(incoherences) != 0 :
            txt = _(u"Caractères incorrects : ") + incoherences[:-2]
            dlg = wx.MessageDialog(self, _(u"La valeur de point que vous avez saisie n'est pas correcte.\n\n") + txt, "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            self.text_valeur.SetFocus()
            return
        # Sauvegarde
        self.Sauvegarde()

        # MAJ du listCtrl des valeurs de points
        if FonctionsPerso.FrameOuverte("config_val_point") != None :
            self.GetParent().MAJ_ListCtrl()

        # Fermeture
        self.EndModal(wx.ID_OK)

    
    
if __name__ == "__main__":
    app = wx.App(0)
    dlg = Dialog(None, "", IDvaleur=0)
    dlg.ShowModal()
    dlg.Destroy()
    app.MainLoop()
