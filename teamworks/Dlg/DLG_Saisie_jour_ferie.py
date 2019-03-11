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
if 'phoenix' in wx.PlatformInfo:
    from wx.adv import DatePickerCtrl, DP_DROPDOWN
else :
    from wx import DatePickerCtrl, DP_DROPDOWN



class Dialog(wx.Dialog):
    def __init__(self, parent, title="" , IDferie=0, type=""):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.typeJour = type
        
        self.panel_base = wx.Panel(self, -1)
        self.staticBox_staticbox = wx.StaticBox(self.panel_base, -1, "")
        self.label_nom = wx.StaticText(self.panel_base, -1, "Nom :")
        self.text_ctrl_nom = wx.TextCtrl(self.panel_base, -1, "")
        self.label_jour_fixe = wx.StaticText(self.panel_base, -1, "Jour :")
        choices=[]
        for x in range(1, 32) : choices.append(str(x))
        self.choice_jour_fixe = wx.Choice(self.panel_base, -1, choices=choices)
        self.label_mois_fixe = wx.StaticText(self.panel_base, -1, "Mois :")
        self.choice_mois_fixe = wx.Choice(self.panel_base, -1, choices=["Janvier", _(u"Février"), "Mars", "Avril", "Mai", "Juin", "Juillet", _(u"Août"), "Septembre", "Octobre", "Novembre", _(u"Décembre")])
        self.label_date_variable = wx.StaticText(self.panel_base, -1, "Date :")
        self.datepicker_date_variable = DatePickerCtrl(self.panel_base, -1, style=DP_DROPDOWN)
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_ok = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Ok"), cheminImage=Chemins.GetStaticPath("Images/32x32/Valider.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))
        
        self.IDferie = IDferie
        if IDferie != 0 : 
            self.Importation()

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)

    def __set_properties(self):
        self.SetTitle(_(u"Saisie d'un jour férié"))
        if 'phoenix' in wx.PlatformInfo:
            _icon = wx.Icon()
        else :
            _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.choice_jour_fixe.SetMinSize((50, -1))
        self.choice_mois_fixe.SetMinSize((130, 21))
        self.bouton_aide.SetToolTip(wx.ToolTip("Cliquez ici pour obtenir de l'aide"))
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetToolTip(wx.ToolTip("Cliquez ici pour valider"))
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetToolTip(wx.ToolTip("Cliquez ici pour annuler la saisie"))
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_base_2 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=0, hgap=0)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        staticBox = wx.StaticBoxSizer(self.staticBox_staticbox, wx.VERTICAL)
        grid_sizer_staticBox = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_variable = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_fixe = wx.FlexGridSizer(rows=1, cols=5, vgap=5, hgap=5)
        grid_sizer_nom = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_nom.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_nom.Add(self.text_ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_nom.AddGrowableCol(1)
        grid_sizer_staticBox.Add(grid_sizer_nom, 1, wx.EXPAND, 0)
        grid_sizer_fixe.Add(self.label_jour_fixe, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_fixe.Add(self.choice_jour_fixe, 0, wx.RIGHT, 10)
        grid_sizer_fixe.Add(self.label_mois_fixe, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_fixe.Add(self.choice_mois_fixe, 0, wx.EXPAND, 0)
        grid_sizer_fixe.AddGrowableCol(4)
        grid_sizer_staticBox.Add(grid_sizer_fixe, 1, wx.EXPAND, 0)
        grid_sizer_variable.Add(self.label_date_variable, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_variable.Add(self.datepicker_date_variable, 0, 0, 0)
        grid_sizer_staticBox.Add(grid_sizer_variable, 1, wx.EXPAND, 0)
        grid_sizer_staticBox.AddGrowableCol(0)
        staticBox.Add(grid_sizer_staticBox, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticBox, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        sizer_base_2.Add(grid_sizer_base, 1, wx.EXPAND, 0)
        self.panel_base.SetSizer(sizer_base_2)
        sizer_base.Add(self.panel_base, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        
        # Affiche en fonction du type de de jour férié
        if self.typeJour == "fixe" :
            self.label_date_variable.Show(False)
            self.datepicker_date_variable.Show(False)
        else:
            self.label_jour_fixe.Show(False)
            self.choice_jour_fixe.Show(False)
            self.label_mois_fixe.Show(False)
            self.choice_mois_fixe.Show(False)
        
        sizer_base.Fit(self)
        self.Layout()
        self.Centre()

    def Importation(self):
        DB = GestionDB.DB()
        req = "SELECT * FROM jours_feries WHERE IDferie=%d" % self.IDferie
        DB.ExecuterReq(req)
        donnees = DB.ResultatReq()[0]
        DB.Close()
        if len(donnees) == 0: return
        # Récupération des données
        type = donnees[1]
        nom = donnees[2]
        jour = donnees[3]
        mois = donnees[4]
        annee = donnees[5]
        
        # Place le nom
        self.text_ctrl_nom.SetValue(nom)
        # Place le jour et le mois si c'est un jour fixe
        if type == "fixe" :
            self.choice_jour_fixe.SetSelection(jour-1)
            self.choice_mois_fixe.SetSelection(mois-1)     
                
        # Place la date dans le cdatePicker si c'est une date variable
        else:
            date = wx.DateTime()
            date.Set(jour, mois-1, annee)
            self.datepicker_date_variable.SetValue(date)

    def Sauvegarde(self):
        """ Sauvegarde des données dans la base de données """
        
        # Récupération ds valeurs saisies
        varNom = self.text_ctrl_nom.GetValue()
        if self.typeJour == "fixe" :
            varJour = self.choice_jour_fixe.GetSelection()+1
            varMois = self.choice_mois_fixe.GetSelection()+1
            varAnnee = 0
        else:
            date_tmp = self.datepicker_date_variable.GetValue()
            varJour = date_tmp.GetDay()
            varMois = date_tmp.GetMonth()+1
            varAnnee = date_tmp.GetYear()

        DB = GestionDB.DB()
        # Création de la liste des données
        listeDonnees = [    ("type",   self.typeJour),  
                                    ("nom",   varNom),
                                    ("jour",   varJour),
                                    ("mois",   varMois),
                                    ("annee",    varAnnee), ]
        if self.IDferie == 0:
            # Enregistrement d'une nouvelle valeur
            newID = DB.ReqInsert("jours_feries", listeDonnees)
            ID = newID
        else:
            # Modification de la valeur
            DB.ReqMAJ("jours_feries", listeDonnees, "IDferie", self.IDferie)
            ID = self.IDferie
        DB.Commit()
        DB.Close()
        return ID

    def OnBoutonAide(self, event):
        FonctionsPerso.Aide(39)

    def OnBoutonAnnuler(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event):
        """ Validation des données saisies """
        
        varNom = self.text_ctrl_nom.GetValue()
        if varNom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir un nom pour ce jour férié. Par exemple : 'Lundi de Pâques'..."), "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            self.text_ctrl_nom.SetFocus()
            return
        
        if self.typeJour == "fixe" :
            varJour = self.choice_jour_fixe.GetSelection()
            if varJour == -1 or varJour == None :
                dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner un jour pour ce jour férié !"), "Erreur", wx.OK)  
                dlg.ShowModal()
                dlg.Destroy()
                self.choice_jour_fixe.SetFocus()
                return
            varMois = self.choice_mois_fixe.GetSelection()
            if varMois == -1 or varMois == None :
                dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner un mois pour ce jour férié !"), "Erreur", wx.OK)  
                dlg.ShowModal()
                dlg.Destroy()
                self.choice_mois_fixe.SetFocus()
                return

        # Sauvegarde
        self.Sauvegarde()
        
        # MAJ du listCtrl des valeurs de points
        if FonctionsPerso.FrameOuverte("Config_jours_feries_" + self.typeJour) != None :
            self.GetParent().MAJ_ListCtrl()

        # Fermeture
        self.EndModal(wx.ID_OK)

    
    
if __name__ == "__main__":
    app = wx.App(0)
    dlg = Dialog(None, "", IDferie=1, type="fixe")
    dlg.ShowModal()
    dlg.Destroy()
    app.MainLoop()
