#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
# Copyright:    (c) 2008-09 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------

import wx
import GestionDB
import FonctionsPerso
import  wx.lib.colourselect as  csel
import wx.lib.hyperlink as hl


class MyFrame(wx.Frame):
    def __init__(self, parent, title="Configuration du gadget Calendrier"):
        wx.Frame.__init__(self, parent, -1, title=title, style=wx.DEFAULT_FRAME_STYLE)
        self.MakeModal(True)
        self.parent = parent
        self.panel_base = wx.Panel(self, -1)
        self.nomGadget = "calendrier"
        
        self.sizer_contenu_staticbox = wx.StaticBox(self.panel_base, -1, u"Paramètres")
                
        self.largeur_min = 100
        self.largeur_max = 800
        self.hauteur_min = 100
        self.hauteur_max = 800
        
        self.Importation()
        
        # Largeur
        self.largeur_label = wx.StaticText(self.panel_base, -1, u"Largeur :")
        self.largeur_texte = wx.TextCtrl(self.panel_base, -1, str(self.val_largeur), size=(40, -1))
        self.largeur_slider = wx.Slider(self.panel_base, -1, self.val_largeur, self.largeur_min, self.largeur_max, size=(-1, -1), style=wx.SL_HORIZONTAL)
        
        # Hauteur
        self.hauteur_label = wx.StaticText(self.panel_base, -1, u"Hauteur :")
        self.hauteur_texte = wx.TextCtrl(self.panel_base, -1, str(self.val_hauteur), size=(40, -1))
        self.hauteur_slider = wx.Slider(self.panel_base, -1, self.val_hauteur, self.hauteur_min, self.hauteur_max, size=(-1, -1), style=wx.SL_HORIZONTAL)
        
        
        # Bouton couleur de fond
        self.label_couleurFond = wx.StaticText(self.panel_base, -1, u"Couleur de fond :")
        self.bouton_couleurFond = csel.ColourSelect(self.panel_base, -1, "", self.val_couleurFond, size = (40, 23))
        
        # Bouton couleur de cases
        self.label_couleurCases = wx.StaticText(self.panel_base, -1, u"Couleur des cases (semaine):")
        self.bouton_couleurCases = csel.ColourSelect(self.panel_base, -1, "", self.val_couleurCases, size = (40, 23))
        
        # Bouton couleur des Week-ends
        self.label_couleurWE = wx.StaticText(self.panel_base, -1, u"Couleur des cases (week-end) :")
        self.bouton_couleurWE = csel.ColourSelect(self.panel_base, -1, "", self.val_couleurWE, size = (40, 23))
        
        # Bouton couleur des jours de vacances
        self.label_couleurVacances = wx.StaticText(self.panel_base, -1, u"Couleur des cases (vacances) :")
        self.bouton_couleurVacances = csel.ColourSelect(self.panel_base, -1, "", self.val_couleurVacances, size = (40, 23))
        
        # Bouton couleur des jours fériés
        self.label_couleurFerie = wx.StaticText(self.panel_base, -1, u"Couleur des cases (fériés) :")
        self.bouton_couleurFerie = csel.ColourSelect(self.panel_base, -1, "", self.val_couleurFerie, size = (40, 23))
        
        # Bouton couleur des cases sélectionnées
        self.label_couleurSelect = wx.StaticText(self.panel_base, -1, u"Couleur des cases sélectionnées :")
        self.bouton_couleurSelect = csel.ColourSelect(self.panel_base, -1, "", self.val_couleurSelect, size = (40, 23))

        # Bouton couleur du bord de la case survolée
        self.label_couleurSurvol = wx.StaticText(self.panel_base, -1, u"Couleur des bords des cases survolées :")
        self.bouton_couleurSurvol = csel.ColourSelect(self.panel_base, -1, "", self.val_couleurSurvol, size = (40, 23))
        
        # Bouton couleur de police des numéros de jour
        self.label_couleurFontJours = wx.StaticText(self.panel_base, -1, u"Couleur de police des numéros de jour :")
        self.bouton_couleurFontJours = csel.ColourSelect(self.panel_base, -1, "", self.val_couleurFontJours, size = (40, 23))
        
        # Bouton couleur de police des jours avec des présents
        self.label_couleurFontJoursAvecPresents = wx.StaticText(self.panel_base, -1, u"Couleur de police si présences :")
        self.bouton_couleurFontJoursAvecPresents = csel.ColourSelect(self.panel_base, -1, "", self.val_couleurFontJoursAvecPresents, size = (40, 23))
        
        
        # Hyperlink_reinit
        self.bouton_reinit = self.Build_Hyperlink()
        
        # Boutons de frame
        self.bouton_aide = wx.BitmapButton(self.panel_base, -1, wx.Bitmap("Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self.panel_base, -1, wx.Bitmap("Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self.panel_base, -1, wx.Bitmap("Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_SCROLL, self.OnSliderLargeur, self.largeur_slider)
        self.Bind(wx.EVT_SCROLL, self.OnSliderHauteur, self.hauteur_slider)
        self.largeur_texte.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocusLargeur)
        self.hauteur_texte.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocusHauteur)
        self.bouton_couleurFond.Bind(csel.EVT_COLOURSELECT, self.OnBoutonColFond)
        self.bouton_couleurCases.Bind(csel.EVT_COLOURSELECT, self.OnBoutonColCases)
        self.bouton_couleurWE.Bind(csel.EVT_COLOURSELECT, self.OnBoutonColWE)
        self.bouton_couleurVacances.Bind(csel.EVT_COLOURSELECT, self.OnBoutonColVacances)
        self.bouton_couleurFerie.Bind(csel.EVT_COLOURSELECT, self.OnBoutonColFerie)
        self.bouton_couleurSelect.Bind(csel.EVT_COLOURSELECT, self.OnBoutonColSelect)
        self.bouton_couleurSurvol.Bind(csel.EVT_COLOURSELECT, self.OnBoutonColSurvol)
        self.bouton_couleurFontJours.Bind(csel.EVT_COLOURSELECT, self.OnBoutonColFontJours)
        self.bouton_couleurFontJoursAvecPresents.Bind(csel.EVT_COLOURSELECT, self.OnBoutonColFontJoursAP)

        
    def __set_properties(self):
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.largeur_texte.SetToolTipString(u"Saisissez ici une valeur pour la largeur du gadget")
        self.largeur_slider.SetToolTipString(u"Vous pouvez aussi utiliser cette glissière pour régler la largeur")
        self.hauteur_texte.SetToolTipString(u"Saisissez ici une valeur pour la hauteur du gadget")
        self.hauteur_slider.SetToolTipString(u"Vous pouvez aussi utiliser cette glissière pour régler la hauteur")
        self.bouton_couleurFond.SetToolTipString(u"Cliquez ici pour modifier la couleur de fond du gadget")
        self.bouton_couleurCases.SetToolTipString(u"Cliquez ici pour modifier la couleur des cases (semaine)")
        self.bouton_couleurWE.SetToolTipString(u"Cliquez ici pour modifier la couleur des cases (week-end)")
        self.bouton_couleurVacances.SetToolTipString(u"Cliquez ici pour modifier la couleur des cases (vacances)")
        self.bouton_couleurFerie.SetToolTipString(u"Cliquez ici pour modifier la couleur des cases (fériés)")
        self.bouton_couleurSelect.SetToolTipString(u"Cliquez ici pour modifier la couleur des cases sélectionnées")
        self.bouton_couleurSurvol.SetToolTipString(u"Cliquez ici pour modifier la couleur des bords des cases survolées")
        self.bouton_couleurFontJours.SetToolTipString(u"Cliquez ici pour modifier la couleur du texte des numéros de jours")
        self.bouton_couleurFontJoursAvecPresents.SetToolTipString(u"Cliquez ici pour modifier la couleur du texte des \njours ayant des présences enregistrées")
        
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
        grid_sizer_contenu = wx.FlexGridSizer(rows=13, cols=2, vgap=5, hgap=5)
        
        # Sizer largeur
        sizer_largeur = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        sizer_largeur.Add(self.largeur_texte, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_largeur.Add(self.largeur_slider, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_largeur.AddGrowableCol(1)
        grid_sizer_contenu.Add(self.largeur_label, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(sizer_largeur, 1, wx.EXPAND, 0)
        
        # Sizer hauteur
        sizer_hauteur = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        sizer_hauteur.Add(self.hauteur_texte, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_hauteur.Add(self.hauteur_slider, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_hauteur.AddGrowableCol(1)
        grid_sizer_contenu.Add(self.hauteur_label, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(sizer_hauteur, 1, wx.EXPAND, 0)
        
        # Bouton couleur de fond
        grid_sizer_contenu.Add(self.label_couleurFond, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.bouton_couleurFond, 0, 0, 0)
                
        # Bouton couleur des cases (semaines)
        grid_sizer_contenu.Add(self.label_couleurCases, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.bouton_couleurCases, 0, 0, 0)
        
        # Bouton couleur des cases (we)
        grid_sizer_contenu.Add(self.label_couleurWE, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.bouton_couleurWE, 0, 0, 0)
        
        # Bouton couleur des cases (vacs)
        grid_sizer_contenu.Add(self.label_couleurVacances, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.bouton_couleurVacances, 0, 0, 0)
        
        # Bouton couleur des cases (fériés)
        grid_sizer_contenu.Add(self.label_couleurFerie, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.bouton_couleurFerie, 0, 0, 0)
        
        # Bouton couleur des cases sélectionnées
        grid_sizer_contenu.Add(self.label_couleurSelect, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.bouton_couleurSelect, 0, 0, 0)
        
        # Bouton couleur des cases survolées
        grid_sizer_contenu.Add(self.label_couleurSurvol, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.bouton_couleurSurvol, 0, 0, 0)
        
        # Bouton couleur des FontJours
        grid_sizer_contenu.Add(self.label_couleurFontJours, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.bouton_couleurFontJours, 0, 0, 0)
        
        # Bouton couleur des FontJoursAvecPresents
        grid_sizer_contenu.Add(self.label_couleurFontJoursAvecPresents, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.bouton_couleurFontJoursAvecPresents, 0, 0, 0)


        # Spacer
        grid_sizer_contenu.Add((1, 1), 0, 0, 0)
        grid_sizer_contenu.Add((1, 1), 0, 0, 0)
                
        # Hyperlink_reinit
        grid_sizer_contenu.Add((1, 1), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.bouton_reinit, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_contenu.AddGrowableRow(11)        
        grid_sizer_contenu.AddGrowableCol(1)
        sizer_contenu.Add(grid_sizer_contenu, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(sizer_contenu, 1, wx.RIGHT|wx.LEFT|wx.TOP|wx.EXPAND, 10)
    
        
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
        self.grid_sizer_base = grid_sizer_base
        
        self.SetMinSize((400, 480))
        self.SetSize((400, 480))

    def Build_Hyperlink(self) :
        """ Construit un hyperlien """
        self.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False))
        hyper = hl.HyperLinkCtrl(self.panel_base, -1, u"Réinitialiser les paramètres par défaut", URL="")
        hyper.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLeftLink)
        hyper.AutoBrowse(False)
        hyper.SetColours("BLACK", "BLACK", "BLUE")
        hyper.EnableRollover(True)
        hyper.SetUnderlines(True, True, True)
        hyper.SetBold(False)
        hyper.SetToolTip(wx.ToolTip(u"Cliquez ici pour réinitialiser les paramètres par défaut de ce gadget"))
        hyper.UpdateLink()
        hyper.DoPopup(False)
        return hyper
        
    def OnLeftLink(self, event):
        """ Réinitialiser les paramètres par défaut """
        # Confirmation
        message = u"Souhaitez-vous vraiment réinitialiser les paramètres par défaut de ce gadget ?"
        dlg = wx.MessageDialog(self, message, u"Réinitialisation", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
        if dlg.ShowModal() == wx.ID_YES :
            dlg.Destroy()
        else:
            return
            dlg.Destroy()
        
        # Recherche des paramètres par défaut dans la base DEFAUTS
        DB = GestionDB.DB(nomDB="Defaut.db3")
        req = "SELECT taille, parametres FROM gadgets WHERE nom='%s';" % self.nomGadget
        DB.ExecuterReq(req)
        donnees = DB.ResultatReq()[0]
        DB.Close()
        self.InitValeurs(donnees)
        
        # Place les valeur dans les contrôles
        self.largeur_texte.SetValue(str(self.val_largeur))
        self.largeur_slider.SetValue(self.val_largeur)
        self.hauteur_texte.SetValue(str(self.val_hauteur))
        self.hauteur_slider.SetValue(self.val_hauteur)

        self.bouton_couleurFond.SetValue(self.val_couleurFond)
        self.bouton_couleurCases.SetValue(self.val_couleurCases)
        self.bouton_couleurWE.SetValue(self.val_couleurWE)
        self.bouton_couleurVacances.SetValue(self.val_couleurVacances)
        self.bouton_couleurFerie.SetValue(self.val_couleurFerie)
        self.bouton_couleurSelect.SetValue(self.val_couleurSelect)
        self.bouton_couleurSurvol.SetValue(self.val_couleurSurvol)
        self.bouton_couleurFontJours.SetValue(self.val_couleurFontJours)
        self.bouton_couleurFontJoursAvecPresents.SetValue(self.val_couleurFontJoursAvecPresents)

        
    def OnSliderLargeur(self, event):
        self.largeur_texte.SetValue(str(self.largeur_slider.GetValue()))

    def OnSliderHauteur(self, event):
        self.hauteur_texte.SetValue(str(self.hauteur_slider.GetValue()))

    def OnKillFocusLargeur(self, event):
        valide = True
        try :
            valeur = int(self.largeur_texte.GetValue())
        except : 
            valeur = 0
            valide = False
        if self.largeur_min <= valeur <= self.largeur_max :
            self.largeur_slider.SetValue(valeur)
        else: valide = False
        if valide == False :
            dlg = wx.MessageDialog(self, u"La largeur que vous avez saisi n'est pas valide !", "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.largeur_texte.Undo()
            return

    def OnKillFocusHauteur(self, event):
        valide = True
        try :
            valeur = int(self.hauteur_texte.GetValue())
        except : 
            valeur = 0
            valide = False
        if self.hauteur_min <= valeur <= self.hauteur_max :
            self.hauteur_slider.SetValue(valeur)
        else: valide = False
        if valide == False :
            dlg = wx.MessageDialog(self, u"La hauteur que vous avez saisi n'est pas valide !", "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.hauteur_texte.Undo()
            return        

    def OnBoutonColFond(self, event):
        reponse = event.GetValue()
        self.val_couleurFond = (reponse[0], reponse[1], reponse[2])

    def OnBoutonColCases(self, event):
        reponse = event.GetValue()
        self.val_couleurCases = (reponse[0], reponse[1], reponse[2])

    def OnBoutonColWE(self, event):
        reponse = event.GetValue()
        self.val_couleurWE = (reponse[0], reponse[1], reponse[2])
        
    def OnBoutonColVacances(self, event):
        reponse = event.GetValue()
        self.val_couleurVacances = (reponse[0], reponse[1], reponse[2])

    def OnBoutonColFerie(self, event):
        reponse = event.GetValue()
        self.val_couleurFerie = (reponse[0], reponse[1], reponse[2])
        
    def OnBoutonColSelect(self, event):
        reponse = event.GetValue()
        self.val_couleurSelect = (reponse[0], reponse[1], reponse[2])

    def OnBoutonColSurvol(self, event):
        reponse = event.GetValue()
        self.val_couleurSurvol = (reponse[0], reponse[1], reponse[2])

    def OnBoutonColFontJours(self, event):
        reponse = event.GetValue()
        self.val_couleurFontJours = (reponse[0], reponse[1], reponse[2])
        
    def OnBoutonColFontJoursAP(self, event):
        reponse = event.GetValue()
        self.val_couleurFontJoursAvecPresents = (reponse[0], reponse[1], reponse[2])


    def Importation(self):
        """ Importation des paramètres du gadget """
        DB = GestionDB.DB()
        req = "SELECT taille, parametres FROM gadgets WHERE nom='%s';" % self.nomGadget
        DB.ExecuterReq(req)
        donnees = DB.ResultatReq()[0]
        DB.Close()
        self.InitValeurs(donnees)
    
    def InitValeurs(self, donnees):
        # Place les valeurs dans les controles
        exec("taille = " + donnees[0])
        exec("self.dictParametres = " + donnees[1])
        self.val_largeur = taille[0]
        self.val_hauteur = taille[1]
        self.val_couleurFond = self.dictParametres["colFond"]
        self.val_couleurCases = self.dictParametres["colNormal"]
        self.val_couleurWE = self.dictParametres["colWE"]
        self.val_couleurSelect = self.dictParametres["colSelect"]
        self.val_couleurSurvol = self.dictParametres["colSurvol"]
        self.val_couleurFontJours = self.dictParametres["colFontJours"]
        self.val_couleurVacances = self.dictParametres["colVacs"]
        self.val_couleurFontJoursAvecPresents = self.dictParametres["colFontPresents"]
        self.val_couleurFerie = self.dictParametres["colFeries"]


    def Sauvegarde(self):
        """ Sauvegarde des données dans la base de données """
        
        # Récupération ds valeurs saisies
        largeur = int(self.largeur_texte.GetValue())
        hauteur = int(self.hauteur_texte.GetValue())
        self.dictParametres["colFond"] = self.val_couleurFond
        self.dictParametres["colNormal"] = self.val_couleurCases
        self.dictParametres["colWE"] = self.val_couleurWE
        self.dictParametres["colSelect"] = self.val_couleurSelect
        self.dictParametres["colSurvol"] = self.val_couleurSurvol
        self.dictParametres["colFontJours"] = self.val_couleurFontJours
        self.dictParametres["colVacs"] = self.val_couleurVacances
        self.dictParametres["colFontPresents"] = self.val_couleurFontJoursAvecPresents
        self.dictParametres["colFeries"] = self.val_couleurFerie


        DB = GestionDB.DB()       
        listeDonnees = [("taille", str((largeur, hauteur))), ("parametres", str(self.dictParametres)), ]
        DB.ReqMAJ("gadgets", listeDonnees, "nom", "calendrier", IDestChaine=True)
        DB.Commit()
        DB.Close()


    def OnClose(self, event):
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        event.Skip()
        
    def OnBoutonAide(self, event):
        print "Aide"

    def OnBoutonAnnuler(self, event):
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()

    def OnBoutonOk(self, event):
        """ Validation des données saisies """
        
        # Sauvegarde
        self.Sauvegarde()
        
        # MAJ des parents       
        if self.parent == None and FonctionsPerso.FrameOuverte("panel_accueil") != None :
            # Mise à jour de la page d'accueil
            topWindow = wx.GetApp().GetTopWindow() 
            topWindow.toolBook.GetPage(0).MAJpanel() 
            
        # Fermeture
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()

    
    
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None)
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
