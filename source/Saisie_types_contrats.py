#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
# Copyright:    (c) 2008-09 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------


import wx
import GestionDB
import datetime
import FonctionsPerso



class MyFrame(wx.Frame):
    def __init__(self, parent, title="" , IDtype=0):
        wx.Frame.__init__(self, parent, -1, title=title, style=wx.DEFAULT_FRAME_STYLE)
        self.MakeModal(True)
        self.parent = parent
        self.panel_base = wx.Panel(self, -1)
        self.sizer_contenu_staticbox = wx.StaticBox(self.panel_base, -1, "")
        self.label_nom_abrege = wx.StaticText(self.panel_base, -1, u"Nom abrégé :")
        self.text_nom_abrege = wx.TextCtrl(self.panel_base, -1, "")
        self.label_nom_abrege_aide = wx.StaticText(self.panel_base, -1, "(5 lettres maximum)")
        self.label_nom = wx.StaticText(self.panel_base, -1, "Nom complet :")
        self.text_nom = wx.TextCtrl(self.panel_base, -1, "")
        self.label_duree = wx.StaticText(self.panel_base, -1, u"A durée \nindéterminée ?", style=wx.ALIGN_RIGHT)
        self.radio_oui = wx.RadioButton(self.panel_base, -1, "Oui", style=wx.RB_GROUP)
        self.radio_non = wx.RadioButton(self.panel_base, -1, "Non")
        self.bouton_aide = wx.BitmapButton(self.panel_base, -1, wx.Bitmap("Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self.panel_base, -1, wx.Bitmap("Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self.panel_base, -1, wx.Bitmap("Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))

        self.IDtype = IDtype
        if IDtype != 0 : 
            self.Importation()
            
        self.__set_properties()
        self.__do_layout()
        self.SetMinSize((400, 230))
        self.SetSize((400, 230))
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
    def __set_properties(self):
        self.SetTitle(u"Saisie d'un type de contrat")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.text_nom_abrege.SetMinSize((50, -1))
        self.text_nom_abrege.SetToolTipString(u"Saisissez un nom abrégé. Par ex: 'CDD', 'CDI'...")
        self.label_nom_abrege_aide.SetFont(wx.Font(7, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.text_nom.SetToolTipString(u"Saisissez le nom complet. Par ex: 'Contrat à durée indéterminée'...")
        self.radio_oui.SetToolTipString(u"Cochez 'Oui' si le type de contrat est à durée indéterminée.")
        self.radio_non.SetToolTipString(u"Cochez 'Oui' si le type de contrat est à durée déterminée.")
        self.bouton_aide.SetToolTipString("Cliquez ici pour obtenir de l'aide")
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetToolTipString("Cliquez ici pour valider")
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetToolTipString("Cliquez ici pour annuler la saisie et fermer")
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        sizer_contenu = wx.StaticBoxSizer(self.sizer_contenu_staticbox, wx.VERTICAL)
        grid_sizer_contenu = wx.FlexGridSizer(rows=4, cols=2, vgap=10, hgap=10)
        grid_sizer_duree = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_nom_abrege = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_contenu.Add(self.label_nom_abrege, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_nom_abrege.Add(self.text_nom_abrege, 0, 0, 0)
        grid_sizer_nom_abrege.Add(self.label_nom_abrege_aide, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(grid_sizer_nom_abrege, 1, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.text_nom, 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.label_duree, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_duree.Add(self.radio_oui, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_duree.Add(self.radio_non, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_duree.AddGrowableRow(0)
        grid_sizer_contenu.Add(grid_sizer_duree, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.AddGrowableCol(1)
        sizer_contenu.Add(grid_sizer_contenu, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(sizer_contenu, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.panel_base.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        sizer_base.Add(self.panel_base, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()
        self.Centre()


    def Importation(self):
        DB = GestionDB.DB()
        req = "SELECT * FROM contrats_types WHERE IDtype=%d" % self.IDtype
        DB.ExecuterReq(req)
        donnees = DB.ResultatReq()[0]
        DB.Close()
        if len(donnees) == 0: return
        
        # Place les valeurs dans les controles
        self.text_nom_abrege.SetValue(donnees[2])
        self.text_nom.SetValue(donnees[1])
        if donnees[3] == "oui" :
            self.radio_oui.SetValue(True)
        else:
            self.radio_non.SetValue(True)
        

    def Sauvegarde(self):
        """ Sauvegarde des données dans la base de données """

        # Récupération ds valeurs saisies
        nom_abrege = self.text_nom_abrege.GetValue()
        nom = self.text_nom.GetValue()
        if self.radio_oui.GetValue() == True :
            duree = "oui"
        else:
            duree = "non"

        DB = GestionDB.DB()
        # Création de la liste des données
        listeDonnees = [    ("nom",   nom),  
                                    ("nom_abrege",    nom_abrege), 
                                    ("duree_indeterminee",    duree),
                                    ]
        if self.IDtype == 0:
            # Enregistrement d'une nouvelle coordonnée
            newID = DB.ReqInsert("contrats_types", listeDonnees)
            ID = newID
        else:
            # Modification de la coordonnée
            DB.ReqMAJ("contrats_types", listeDonnees, "IDtype", self.IDtype)
            ID = self.IDtype
        DB.Commit()
        DB.Close()
        return ID

    def OnClose(self, event):
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        event.Skip()
        
    def OnBoutonAide(self, event):
        FonctionsPerso.Aide(41)

    def OnBoutonAnnuler(self, event):
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()

    def OnBoutonOk(self, event):
        """ Validation des données saisies """
        nom_abrege = self.text_nom_abrege.GetValue()
        nom = self.text_nom.GetValue()
        if self.radio_oui.GetValue() == True :
            duree = "oui"
        else:
            duree = "non"
            
        # Vérifie que un nom abrégé a été saisi
        if nom_abrege == "" :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement saisir un nom abrégé.", "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            self.text_nom_abrege.SetFocus()
            return
        
        # Vérifie que un nom abrégé ne dépasse pas 5 caractéres
        if len(nom_abrege) > 5 :
            dlg = wx.MessageDialog(self, u"Le nom abrégé ne doit pas dépasser 5 caractères !", "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            self.text_nom_abrege.SetFocus()
            return
        
        # Vérifie que un nom abrégé a été saisi
        if nom == "" :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement saisir un nom complet.", "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            self.text_nom.SetFocus()
            return
        
        # Sauvegarde
        self.Sauvegarde()
        
        # MAJ du listCtrl des valeurs de points
        if FonctionsPerso.FrameOuverte("config_typeContrat") != None :
            self.GetParent().MAJ_ListCtrl()
            
        # Fermeture
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, "", IDtype=2)
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
