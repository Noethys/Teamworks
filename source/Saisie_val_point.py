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
    def __init__(self, parent, title="" , IDvaleur=0):
        wx.Frame.__init__(self, parent, -1, title=title, style=wx.DEFAULT_FRAME_STYLE)
        self.MakeModal(True)
        self.parent = parent
        self.panel_base = wx.Panel(self, -1)
        self.sizer_contenu_staticbox = wx.StaticBox(self.panel_base, -1, "")
        self.label_valeur = wx.StaticText(self.panel_base, -1, u"Valeur :")
        self.text_valeur = wx.TextCtrl(self.panel_base, -1, "", style=wx.TE_CENTRE)
        self.label_euro = wx.StaticText(self.panel_base, -1, u"€")
        self.label_dateDebut = wx.StaticText(self.panel_base, -1, u"A partir du :")
        self.datepicker_dateDebut = wx.DatePickerCtrl(self.panel_base, -1, style=wx.DP_DROPDOWN)
        self.bouton_aide = wx.BitmapButton(self.panel_base, -1, wx.Bitmap("Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self.panel_base, -1, wx.Bitmap("Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self.panel_base, -1, wx.Bitmap("Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))
        
        self.IDvaleur = IDvaleur
        if IDvaleur != 0 : 
            self.Importation()

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
    def __set_properties(self):
        self.SetTitle(u"Gestion de la valeur du point")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.text_valeur.SetMinSize((60, -1))
        self.text_valeur.SetToolTipString("Saisissez ici une valeur")
        self.bouton_aide.SetToolTipString("Cliquez ici pour obtenir de l'aide")
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetToolTipString("Cliquez ici pour valider")
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetToolTipString("Cliquez ici pour annuler la saisie")
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
        self.Centre()


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

    def OnClose(self, event):
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        event.Skip()
        
    def OnBoutonAide(self, event):
        FonctionsPerso.Aide(13)

    def OnBoutonAnnuler(self, event):
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()

    def OnBoutonOk(self, event):
        """ Validation des données saisies """
        # Vérifie que une valeur a été saisie
        valeur = self.text_valeur.GetValue()
        if valeur == "" :
            dlg = wx.MessageDialog(self, u"Vous devez saisir une valeur de point.", "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            self.text_valeur.SetFocus()
            return
        # Vérifie que la valeur est bien constituée de chiffres uniquement
        incoherences = ""
        for lettre in valeur :
            if lettre not in "0123456789." : incoherences += "'"+ lettre + "', "
        if len(incoherences) != 0 :
            txt = u"Caractères incorrects : " + incoherences[:-2]
            dlg = wx.MessageDialog(self, u"La valeur de point que vous avez saisie n'est pas correcte.\n\n" + txt, "Erreur", wx.OK)  
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
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()

    
    
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, "", IDvaleur=0)
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
