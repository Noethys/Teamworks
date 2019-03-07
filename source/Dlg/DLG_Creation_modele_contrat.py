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

from Ctrl.CTRL_Creation_modele_contrat_p1 import Page as Page1
from Ctrl.CTRL_Creation_modele_contrat_p2 import Page as Page2
from Ctrl.CTRL_Creation_modele_contrat_p3 import Page as Page3


class MyWizard(wx.Frame):
    def __init__(self, parent, title="", IDmodele=0):
        wx.Frame.__init__(self, parent, -1, title=title, name="frm_creation_modele_contrats", style=wx.DEFAULT_FRAME_STYLE)
        self.MakeModal(True)
        
        self.parent = parent
        self.listePages = ("Page1", "Page2", "Page3")
        
        self.panel_base = wx.Panel(self, -1)
        self.static_line = wx.StaticLine(self.panel_base, -1)
        self.bouton_aide = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_retour = wx.BitmapButton(self.panel_base, -1, wx.Bitmap(Chemins.GetStaticPath("Images/BoutonsImages/Retour_L72.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_suite = wx.BitmapButton(self.panel_base, -1, wx.Bitmap(Chemins.GetStaticPath("Images/BoutonsImages/Suite_L72.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))
        self.__set_properties()
        self.__do_layout()
                
        self.Bind(wx.EVT_BUTTON, self.Onbouton_aide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_retour, self.bouton_retour)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_suite, self.bouton_suite)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_annuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        self.bouton_retour.Enable(False)
        self.nbrePages = len(self.listePages)    
        self.pageVisible = 1
                
        # Initialisation de la liste de récupération des données
        self.dictModeles = {
                                            "IDmodele" : IDmodele,
                                            "IDclassification" : None,
                                            "IDtype" : None,
                                            "nom" : "",
                                            "description" : "",
                                    }
                                    
        self.dictChamps = {} 
        
        if IDmodele != 0 : self.Importation(IDmodele)
        
        # Création des pages
        self.Creation_Pages()
        
    def Importation(self, IDmodele=0):
        # Récupération des données
        DB = GestionDB.DB()
        
        # Importe les données MODELES
        req = "SELECT nom, description, IDclassification, IDtype FROM contrats_modeles WHERE IDmodele=%d ;" % IDmodele
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()[0]
        self.dictModeles["nom"] = listeDonnees[0]
        self.dictModeles["description"] = listeDonnees[1]        
        self.dictModeles["IDclassification"] = listeDonnees[2]
        self.dictModeles["IDtype"] = listeDonnees[3]
        
        # Importe les données CHAMPS
        req = "SELECT IDchamp, valeur FROM contrats_valchamps WHERE (IDmodele=%d AND type='modele')  ;" % IDmodele
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()

        for item in listeDonnees :
            self.dictChamps[item[0]] = item[1]
        
    
    def Creation_Pages(self):
        """ Creation des pages """
        for numPage in range(1, self.nbrePages+1) :
            exec( "self.page" + str(numPage) + " = " + self.listePages[numPage-1] + "(self.panel_base)" )
            exec( "self.sizer_pages.Add(self.page" + str(numPage) + ", 1, wx.EXPAND, 0)" )
            self.sizer_pages.Layout()
            exec( "self.page" + str(numPage) + ".Show(False)" )
        self.page1.Show(True)
        self.sizer_pages.Layout()

    def __set_properties(self):
        self.SetTitle(_(u"Création d'un modèle de contrat"))
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.bouton_aide.SetToolTipString("Cliquez ici pour obtenir de l'aide")
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_retour.SetToolTipString(_(u"Cliquez ici pour revenir à la page précédente"))
        self.bouton_retour.SetSize(self.bouton_retour.GetBestSize())
        self.bouton_suite.SetToolTipString(_(u"Cliquez ici pour passer à l'étape suivante"))
        self.bouton_suite.SetSize(self.bouton_suite.GetBestSize())
        self.bouton_annuler.SetToolTipString(_(u"Cliquez pour annuler la création du contrat"))
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())
        self.SetMinSize((470, 380))

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        sizer_pages = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base.Add(sizer_pages, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(self.static_line, 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_retour, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_suite, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, wx.LEFT, 10)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL|wx.EXPAND, 10)
        self.panel_base.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        sizer_base.Add(self.panel_base, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()
        self.Centre()
        self.sizer_pages = sizer_pages

    def OnClose(self, event):
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        event.Skip()
        
    def Onbouton_aide(self, event):
        FonctionsPerso.Aide(31)

    def Onbouton_retour(self, event):
        # rend invisible la page affichée
        pageCible = eval("self.page"+str(self.pageVisible))
        pageCible.Show(False)
        # Fait apparaître nouvelle page
        self.pageVisible -= 1
        pageCible = eval("self.page"+str(self.pageVisible))
        pageCible.Show(True)
        self.sizer_pages.Layout()
        # Si on quitte la dernière page, on active le bouton Suivant
        if self.pageVisible == self.nbrePages-1 :
            self.bouton_suite.Enable(True)
            self.bouton_suite.SetBitmapLabel(wx.Bitmap(Chemins.GetStaticPath("Images/BoutonsImages/Suite_L72.png"), wx.BITMAP_TYPE_ANY))
        # Si on revient à la première page, on désactive le bouton Retour
        if self.pageVisible == 1 :
            self.bouton_retour.Enable(False)

    def Onbouton_suite(self, event):
        # Vérifie que les données de la page en cours sont valides
        validation = self.ValidationPages()
        if validation == False : return
        # Si on est déjà sur la dernière page : on termine
        if self.pageVisible == self.nbrePages :
            self.Terminer()
            return
        # Rend invisible la page affichée
        pageCible = eval("self.page"+str(self.pageVisible))
        pageCible.Show(False)
        # Fait apparaître nouvelle page
        self.pageVisible += 1
        pageCible = eval("self.page"+str(self.pageVisible))
        pageCible.Show(True)
        self.sizer_pages.Layout()
        # Si on arrive à la dernière page, on désactive le bouton Suivant
        if self.pageVisible == self.nbrePages :
            self.bouton_suite.SetBitmapLabel(wx.Bitmap(Chemins.GetStaticPath("Images/BoutonsImages/Valider_L72.png"), wx.BITMAP_TYPE_ANY))
        # Si on quitte la première page, on active le bouton Retour
        if self.pageVisible > 1 :
            self.bouton_retour.Enable(True)
            
    def Onbouton_annuler(self, event):
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()
        
    def ValidationPages(self) :
        """ Validation des données avant changement de pages """
        exec( "validation = self.page" + str(self.pageVisible) + ".Validation()" )
        return validation
    
    def Terminer(self):
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()

        
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyWizard(None, "", IDmodele=4)
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
