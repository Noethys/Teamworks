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
import GestionDB
import FonctionsPerso
import  wx.lib.colourselect as  csel
import wx.lib.hyperlink as hl


class MyFrame(wx.Frame):
    def __init__(self, parent, title="Configuration du gadget Bloc-Notes"):
        wx.Frame.__init__(self, parent, -1, title=title, style=wx.DEFAULT_FRAME_STYLE)
        self.MakeModal(True)
        self.parent = parent
        self.panel_base = wx.Panel(self, -1)
        self.nomGadget = "notes"
        
        self.sizer_contenu_staticbox = wx.StaticBox(self.panel_base, -1, _(u"Paramètres"))
                
        self.largeur_min = 100
        self.largeur_max = 800
        self.hauteur_min = 100
        self.hauteur_max = 800
        
        self.Importation()
        
        
        # Largeur
        self.largeur_label = wx.StaticText(self.panel_base, -1, _(u"Largeur :"))
        self.largeur_texte = wx.TextCtrl(self.panel_base, -1, str(self.val_largeur), size=(40, -1))
        self.largeur_slider = wx.Slider(self.panel_base, -1, self.val_largeur, self.largeur_min, self.largeur_max, size=(-1, -1), style=wx.SL_HORIZONTAL)
        
        # Hauteur
        self.hauteur_label = wx.StaticText(self.panel_base, -1, _(u"Hauteur :"))
        self.hauteur_texte = wx.TextCtrl(self.panel_base, -1, str(self.val_hauteur), size=(40, -1))
        self.hauteur_slider = wx.Slider(self.panel_base, -1, self.val_hauteur, self.hauteur_min, self.hauteur_max, size=(-1, -1), style=wx.SL_HORIZONTAL)
        
        # Bouton couleur de fond
        self.label_couleurFond = wx.StaticText(self.panel_base, -1, _(u"Couleur de fond :"))
        self.bouton_couleurFond = csel.ColourSelect(self.panel_base, -1, "", self.val_couleurFond, size = (40, 23))
        
        # Police
        self.label_police = wx.StaticText(self.panel_base, -1, _(u"Police du texte :"))
        self.bouton_police = wx.Button(self.panel_base, -1, "")
        self.bouton_couleurPolice = csel.ColourSelect(self.panel_base, -1, "", self.val_couleurPolice, size = (40, 23))
        
        # Apercu de la police
        self.label_apercu = wx.StaticText(self.panel_base, -1, _(u"Aperçu de la police :"))
        self.label_exemplePolice = wx.StaticText(self.panel_base, -1, _(u" Exemple "), size=(-1, 30))
        self.MajExemplePolice()
        
        # Multipages
        self.label_multipages = wx.StaticText(self.panel_base, -1, _(u"Multi-pages :"))
        self.checkbox_multipages = wx.CheckBox(self.panel_base, -1, "")
        self.checkbox_multipages.SetValue(self.val_multipages)
        
        # Hyperlink_reinit
        self.bouton_reinit = self.Build_Hyperlink()
        
        # Boutons de frame
        self.bouton_aide = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

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
        self.bouton_couleurPolice.Bind(csel.EVT_COLOURSELECT, self.OnBoutonColPolice)
        self.Bind(wx.EVT_BUTTON, self.OnBouton_Police, self.bouton_police)
        
    def __set_properties(self):
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.largeur_texte.SetToolTipString(_(u"Saisissez ici une valeur pour la largeur du gadget"))
        self.largeur_slider.SetToolTipString(_(u"Vous pouvez aussi utiliser cette glissière pour régler la largeur"))
        self.hauteur_texte.SetToolTipString(_(u"Saisissez ici une valeur pour la hauteur du gadget"))
        self.hauteur_slider.SetToolTipString(_(u"Vous pouvez aussi utiliser cette glissière pour régler la hauteur"))
        self.bouton_couleurFond.SetToolTipString(_(u"Cliquez ici pour modifier la couleur de fond du gadget"))
        self.bouton_couleurPolice.SetToolTipString(_(u"Cliquez ici pour modifier la couleur de police du gadget"))
        self.bouton_police.SetToolTipString(_(u"Cliquez ici pour modifier la police d'affichage"))
        self.checkbox_multipages.SetToolTipString(_(u"Cochez cette case pour permettre la saisie de plusieurs pages de texte dans le bloc-notes"))
        self.bouton_aide.SetToolTipString("Cliquez ici pour obtenir de l'aide")
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetToolTipString("Cliquez ici pour valider")
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetToolTipString("Cliquez ici pour annuler la saisie")
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())
        self.SetMinSize((400, 362))

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        sizer_contenu = wx.StaticBoxSizer(self.sizer_contenu_staticbox, wx.VERTICAL)
        grid_sizer_contenu = wx.FlexGridSizer(rows=10, cols=2, vgap=10, hgap=10)
        
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
                
        # Sizer Police
        sizer_police = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        sizer_police.Add(self.bouton_police, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_police.Add(self.bouton_couleurPolice, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_police.AddGrowableCol(1)
        grid_sizer_contenu.Add(self.label_police, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(sizer_police, 1, wx.EXPAND, 0)
        
        # Aperçu de la police
        grid_sizer_contenu.Add(self.label_apercu, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.label_exemplePolice, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        
        # CheckBox Multipages
        grid_sizer_contenu.Add(self.label_multipages, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.checkbox_multipages, 0, 0, 0)

        # Spacer
        grid_sizer_contenu.Add((1, 1), 0, 0, 0)
        grid_sizer_contenu.Add((1, 1), 0, 0, 0)
                
        # Hyperlink_reinit
        grid_sizer_contenu.Add((1, 1), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.bouton_reinit, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_contenu.AddGrowableRow(6)        
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

    def Build_Hyperlink(self) :
        """ Construit un hyperlien """
        self.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False))
        hyper = hl.HyperLinkCtrl(self.panel_base, -1, _(u"Réinitialiser les paramètres par défaut"), URL="")
        hyper.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLeftLink)
        hyper.AutoBrowse(False)
        hyper.SetColours("BLACK", "BLACK", "BLUE")
        hyper.EnableRollover(True)
        hyper.SetUnderlines(True, True, True)
        hyper.SetBold(False)
        hyper.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour réinitialiser les paramètres par défaut de ce gadget")))
        hyper.UpdateLink()
        hyper.DoPopup(False)
        return hyper
        
    def OnLeftLink(self, event):
        """ Réinitialiser les paramètres par défaut """
        # Confirmation
        message = _(u"Souhaitez-vous vraiment réinitialiser les paramètres par défaut de ce gadget ?")
        dlg = wx.MessageDialog(self, message, _(u"Réinitialisation"), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
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
        self.bouton_couleurPolice.SetValue(self.val_couleurPolice)
        self.MajExemplePolice()
        self.checkbox_multipages.SetValue(self.val_multipages)
        
        
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
            dlg = wx.MessageDialog(self, _(u"La largeur que vous avez saisi n'est pas valide !"), "Information", wx.OK | wx.ICON_INFORMATION)
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
            dlg = wx.MessageDialog(self, _(u"La hauteur que vous avez saisi n'est pas valide !"), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.hauteur_texte.Undo()
            return        

    def OnBoutonColFond(self, event):
        reponse = event.GetValue()
        self.val_couleurFond = (reponse[0], reponse[1], reponse[2])
        self.MajExemplePolice()

    def OnBoutonColPolice(self, event):
        reponse = event.GetValue()
        self.val_couleurPolice = (reponse[0], reponse[1], reponse[2])
        self.MajExemplePolice()
        
    def MajExemplePolice(self):
        taille = self.val_police.GetPointSize()
        nom = self.val_police.GetFaceName()
        self.bouton_police.SetLabel(nom + ", " + str(taille) + " points")
        self.label_exemplePolice.SetFont(self.val_police)
        self.label_exemplePolice.SetForegroundColour(self.val_couleurPolice)
        self.label_exemplePolice.SetBackgroundColour(self.val_couleurFond)
        try :
            self.grid_sizer_base.Layout()
        except : pass

    def OnBouton_Police(self, event):
        font = self.val_police
        data = wx.FontData()
        data.EnableEffects(False)
        data.SetInitialFont(font)

        dlg = wx.FontDialog(self, data)
        
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetFontData()
            font = data.GetChosenFont()
            self.val_police = font
            self.MajExemplePolice()
        
        
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
        self.val_couleurFond = self.dictParametres["couleur_fond"]
        self.val_couleurPolice = self.dictParametres["couleur_police"]
        self.val_police = wx.Font(self.dictParametres["taillePolice"], self.dictParametres["familyPolice"], self.dictParametres["stylePolice"], self.dictParametres["weightPolice"], False, self.dictParametres["nomPolice"])
        self.val_multipages = self.dictParametres["multipages"]
        

    def Sauvegarde(self):
        """ Sauvegarde des données dans la base de données """
        
        # Récupération ds valeurs saisies
        largeur = int(self.largeur_texte.GetValue())
        hauteur = int(self.hauteur_texte.GetValue())
        self.dictParametres["couleur_fond"] = self.val_couleurFond
        self.dictParametres["couleur_police"] = self.val_couleurPolice
        self.dictParametres["multipages"] = self.checkbox_multipages.GetValue()
        
        self.dictParametres["taillePolice"] = self.val_police.GetPointSize()
        self.dictParametres["familyPolice"] = self.val_police.GetFamily()
        self.dictParametres["stylePolice"] = self.val_police.GetStyle()
        self.dictParametres["weightPolice"] = self.val_police.GetWeight()
        self.dictParametres["nomPolice"] = self.val_police.GetFaceName()
        

        DB = GestionDB.DB()       
        listeDonnees = [("taille", str((largeur, hauteur))), ("parametres", str(self.dictParametres)), ]
        DB.ReqMAJ("gadgets", listeDonnees, "nom", "notes", IDestChaine=True)
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
