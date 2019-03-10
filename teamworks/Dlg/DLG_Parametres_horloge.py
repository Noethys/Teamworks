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
import  wx.lib.colourselect as  csel
import wx.lib.agw.hyperlink as hl


class MyFrame(wx.Frame):
    def __init__(self, parent, title="Configuration du gadget Horloge"):
        wx.Frame.__init__(self, parent, -1, title=title, style=wx.DEFAULT_FRAME_STYLE)
        self.MakeModal(True)
        self.parent = parent
        self.panel_base = wx.Panel(self, -1)
        self.nomGadget = "horloge"
        
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
        
        # Bouton couleur de face
        self.label_couleurFace = wx.StaticText(self.panel_base, -1, _(u"Couleur de face :"))
        self.bouton_couleurFace = csel.ColourSelect(self.panel_base, -1, "", self.val_couleurFace, size = (40, 23))
        
        # Bouton couleur de fond
        self.label_couleurFond = wx.StaticText(self.panel_base, -1, _(u"Couleur de fond :"))
        self.bouton_couleurFond = csel.ColourSelect(self.panel_base, -1, "", self.val_couleurFond, size = (40, 23))
        
        # Hyperlink_reinit
        self.bouton_reinit = self.Build_Hyperlink()
        
        # Boutons de frame
        self.bouton_aide = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_ok = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Ok"), cheminImage=Chemins.GetStaticPath("Images/32x32/Valider.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))

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
        self.bouton_couleurFace.Bind(csel.EVT_COLOURSELECT, self.OnBoutonColFace)
        self.bouton_couleurFond.Bind(csel.EVT_COLOURSELECT, self.OnBoutonColFond)
        
    def __set_properties(self):
        if 'phoenix' in wx.PlatformInfo:
            _icon = wx.Icon()
        else :
            _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.largeur_texte.SetToolTip(wx.ToolTip(_(u"Saisissez ici une valeur pour la largeur du gadget")))
        self.largeur_slider.SetToolTip(wx.ToolTip(_(u"Vous pouvez aussi utiliser cette glissière pour régler la largeur")))
        self.hauteur_texte.SetToolTip(wx.ToolTip(_(u"Saisissez ici une valeur pour la hauteur du gadget")))
        self.hauteur_slider.SetToolTip(wx.ToolTip(_(u"Vous pouvez aussi utiliser cette glissière pour régler la hauteur")))
        self.bouton_couleurFace.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier la couleur de face de l'horloge")))
        self.bouton_couleurFond.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier la couleur de fond de l'horloge")))
        self.bouton_aide.SetToolTip(wx.ToolTip("Cliquez ici pour obtenir de l'aide"))
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetToolTip(wx.ToolTip("Cliquez ici pour valider"))
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetToolTip(wx.ToolTip("Cliquez ici pour annuler la saisie"))
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())
        self.SetMinSize((400, 305))

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
        
        # Bouton couleur de face
        grid_sizer_contenu.Add(self.label_couleurFace, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.bouton_couleurFace, 0, 0, 0)
        
        # Bouton couleur de fond
        grid_sizer_contenu.Add(self.label_couleurFond, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.bouton_couleurFond, 0, 0, 0)
        
        # Spacer
        grid_sizer_contenu.Add((1, 1), 0, 0, 0)
        grid_sizer_contenu.Add((1, 1), 0, 0, 0)
        
        # Hyperlink_reinit
        grid_sizer_contenu.Add((1, 1), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.bouton_reinit, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_contenu.AddGrowableRow(4)
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
        self.bouton_couleurFace.SetValue(self.val_couleurFace)
        self.bouton_couleurFond.SetValue(self.val_couleurFond)
        
        
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

    def OnBoutonColFace(self, event):
        reponse = event.GetValue()
        self.val_couleurFace = (reponse[0], reponse[1], reponse[2])

    def OnBoutonColFond(self, event):
        reponse = event.GetValue()
        self.val_couleurFond = (reponse[0], reponse[1], reponse[2])

        
        
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
        self.val_couleurFace = self.dictParametres["couleur_face"]
        self.val_couleurFond = self.dictParametres["couleur_fond"]
        

    def Sauvegarde(self):
        """ Sauvegarde des données dans la base de données """
        
        # Récupération ds valeurs saisies
        largeur = int(self.largeur_texte.GetValue())
        hauteur = int(self.hauteur_texte.GetValue())
        self.dictParametres["couleur_face"] = self.val_couleurFace
        self.dictParametres["couleur_fond"] = self.val_couleurFond

        DB = GestionDB.DB()       
        listeDonnees = [("taille", str((largeur, hauteur))), ("parametres", str(self.dictParametres)), ]
        DB.ReqMAJ("gadgets", listeDonnees, "nom", "horloge", IDestChaine=True)
        DB.Commit()
        DB.Close()


    def OnClose(self, event):
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        event.Skip()
        
    def OnBoutonAide(self, event):
        print("Aide")

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
