#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
# Copyright:    (c) 2008-09 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------

import wx
import FonctionsPerso
import wx.lib.hyperlink as hl

# Import des panels
import Config_TypesPieces
import Config_TypesDiplomes
import Config_Situations
import Config_Cat_Presences
import Config_Classifications
import Config_ChampsContrats
import Config_Modeles_Contrats
import Config_Pays
import Config_TypesContrats
import Config_ValPoint
import Config_Periodes_Vacances
import Config_Jours_Feries
import Config_Password
import Config_Sauvegarde
import Config_Gadgets
import Config_Utilisateurs_Reseau
import Config_Fonctions
import Config_Affectations
import Config_Diffuseurs
import Config_Emplois
import Config_Verrouillage_Entretien
import Config_AdressesMail
import Config_Questionnaire


# Type page, contenu (panel ou texteIntro pour les rubriques), titre, nom image
LISTE_PAGES = [

    ( "rubrique", u"Cliquez sur l'une des rubriques présentées ci-dessous ou dans l'arborescence de gauche pour accéder aux paramétrages correspondants.", u"Affichage", "Outils.png"),
    ( "page", "Config_Gadgets.Panel(self, -1)", u"Les gadgets", "Calendrier_ajout.png"),
    
    ( "rubrique", u"Cliquez sur l'une des rubriques présentées ci-dessous ou dans l'arborescence de gauche pour accéder aux paramétrages correspondants.", u"Fichiers", "Repertoire.png"),
    ( "page", "Config_Sauvegarde.Panel(self, -1)", u"Sauvegarde automatique", "Sauvegarder_param.png"),
    ( "page", "Config_Password.Panel(self, -1)", u"Protection par mot de passe", "Cadenas.png"),
    ( "page", "Config_AdressesMail.Panel(self, -1)", u"Adresses expédition de mails", "Mail.png"),
    ( "page", "Config_Utilisateurs_Reseau.Panel(self, -1)", u"Utilisateurs réseau", "Identite.png"),
    
    ( "rubrique", u"Cliquez sur l'une des rubriques présentées ci-dessous ou dans l'arborescence de gauche pour accéder aux paramétrages correspondants.", u"Données personnes", "Personnes.png"),
    ( "page", "Config_Questionnaire.Panel(self, -1)", u"Le questionnaire", "Questionnaire.png"),
    ( "page", "Config_TypesDiplomes.Panel_TypesDiplomes(self, -1)", u"Les types de qualifications", "Personnes.png"),
    ( "page", "Config_TypesPieces.Panel_TypesPieces(self, -1)", u"Les types de pièces", "Personnes.png"),
    ( "page", "Config_Situations.Panel(self, -1)", u"Les types de situations", "Personnes.png"),
    ( "page", "Config_Pays.Panel(self, -1)", u"Les pays et nationalités", "Drapeau.png"),
    
    ( "rubrique", u"Cliquez sur l'une des rubriques présentées ci-dessous ou dans l'arborescence de gauche pour accéder aux paramétrages correspondants.", u"Données contrats", "Document.png"),
    ( "page", "Config_Classifications.Panel(self, -1)", u"Les classifications", "Document.png"),
    ( "page", "Config_ChampsContrats.Panel(self, -1)", u"Les champs de contrats", "Document.png"),
    ( "page", "Config_Modeles_Contrats.Panel(self, -1)", u"Les modèles de contrats", "Document.png"),
    ( "page", "Config_TypesContrats.Panel(self, -1)", u"Les types de contrats", "Document.png"),
    ( "page", "Config_ValPoint.Panel(self, -1)", u"Les valeurs de points", "Document.png"),
    
    ( "rubrique", u"Cliquez sur l'une des rubriques présentées ci-dessous ou dans l'arborescence de gauche pour accéder aux paramétrages correspondants.", u"Présences", "Presences.png"),
    ( "page", "Config_Cat_Presences.Panel_CatPresences(self, -1)", u"Les catégories de présences", "Presences.png"),
    ( "page", "Config_Periodes_Vacances.Panel(self, -1)", u"Les périodes de vacances", "Calendrier3jours.png"),
    ( "page", "Config_Jours_Feries.Panel(self, -1)", u"Les jours fériés", "Calendrier_jour.png"),
    
    ( "rubrique", u"Cliquez sur l'une des rubriques présentées ci-dessous ou dans l'arborescence de gauche pour accéder aux paramétrages correspondants.", u"Recrutement", "Mail.png"),
    ( "page", "Config_Verrouillage_Entretien.Panel(self, -1)", u"Protection des entretiens", "Cadenas.png"),
    ( "page", "Config_Fonctions.Panel(self, -1)", u"Les fonctions", "Mail.png"),
    ( "page", "Config_Affectations.Panel(self, -1)", u"Les affectations", "Mail.png"),
    ( "page", "Config_Diffuseurs.Panel(self, -1)", u"Les diffuseurs", "Mail.png"),
    ( "page", "Config_Emplois.Panel(self, -1)", u"Les offres d emploi", "Mail.png"),
    
    ]

class Treebook(wx.Treebook):
    def __init__(self, parent):
        wx.Treebook.__init__(self, parent, -1, name="treebook_configuration", style= wx.BK_LEFT)
        self.CreationPages()
        # Couleur de fond
        treeCtrl = self.GetTreeCtrl()
        treeCtrl.SetBackgroundColour((122, 161, 230))
        
        self.Bind(wx.EVT_TREEBOOK_PAGE_CHANGING, self.OnChanging)
        
    def CreationPages(self):
        nbre_pages = len(LISTE_PAGES) 
        
        # Création des images dans le TreeBook
        il = wx.ImageList(16, 16)
        index = 0
        for type, panel, titre, image in LISTE_PAGES :
            exec( "self.img_" + str(index) + " = il.Add(wx.Bitmap('Images/16x16/' + image, wx.BITMAP_TYPE_PNG))" )
            index += 1
        self.AssignImageList(il)
        
        # Création des pages du TreeBook
        index = 0
        for type, contenu, titre, image in LISTE_PAGES :
            if type == "rubrique" :
                panel = Panel_rubrique(self, -1, titre, contenu, index)
                exec( "self.AddPage(panel, u'" + titre + "', imageId=self.img_" + str(index) + ")")
            if type == "page" :
                exec( "self.AddSubPage(" + contenu + ", u'" + titre + "', imageId=self.img_" + str(index) + ")")
            index += 1    
        
        # Deplie toutes les branches du treeCtrl
        for x in range(0, nbre_pages) :
            self.ExpandNode(x, True)


    def MAJpanels(self):
        """ Actualise tous les panels du treebook """
        #self.DeleteAllPages()
        #self.CreationPages()
        index = 0
        for page in LISTE_PAGES :
            if page[0] =="page" :
                self.GetPage(index).MAJpanel()
            index += 1
    
    def MAJpanel(self, indexPage):
        """ Met à jour un panel donné """
        if LISTE_PAGES[indexPage][0] == "page" :
            self.GetPage(indexPage).MAJpanel()
        
    def OnChanging(self, event):
        numPage = event.GetSelection()
        if LISTE_PAGES[numPage][0] == "page" :
            self.GetPage(numPage).MAJpanel()
                

class Panel_rubrique(wx.Panel):
    def __init__(self, parent, ID=-1, titre = "", texteIntro = "", num_index = 0):
        wx.Panel.__init__(self, parent, ID, name="panel_rubrique", style=wx.TAB_TRAVERSAL)
        self.barreTitre = FonctionsPerso.BarreTitre(self,  titre, u"")
        self.label_introduction = FonctionsPerso.StaticWrapText(self, -1, texteIntro)

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_hyperlinks = wx.FlexGridSizer(rows=10, cols=2, vgap=5, hgap=5)
        grid_sizer_base.Add(self.barreTitre, 0, wx.EXPAND, 0)
        grid_sizer_base.Add(self.label_introduction, 0, wx.EXPAND | wx.LEFT | wx.RIGHT|wx.BOTTOM, 10)
        grid_sizer_base.Add(grid_sizer_hyperlinks, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 20)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_hyperlinks.AddGrowableCol(01)
        self.SetAutoLayout(True)
        self.Layout()
        self.grid_sizer_hyperlinks = grid_sizer_hyperlinks
        
        # Recherche des pages enfants
        liste_pages_enfants = self.Recherche_titres_hyperlinks(num_index)
        
        # Création des liens
        for titre, num_page in liste_pages_enfants :
            img = wx.StaticBitmap(self, -1, wx.Bitmap("Images/16x16/" + LISTE_PAGES[num_page][3], wx.BITMAP_TYPE_PNG))
            self.grid_sizer_hyperlinks.Add(img, 0, wx.ALL, 0)
            hyper = self.Build_Hyperlink(titre, num_page)
            self.grid_sizer_hyperlinks.Add(hyper, 0, wx.ALL, 0)
        
    def Recherche_titres_hyperlinks(self, num_index):
        """ Recherche toutes les pages enfants d'une rubrique pour créer les hyperlinks """
        liste_liens = []
        for index in range(num_index+1, len(LISTE_PAGES)) :
            type = LISTE_PAGES[index][0]
            titre = LISTE_PAGES[index][2]
            if type == "page" : 
                liste_liens.append( (titre, index) )
            else :
                return liste_liens
        return liste_liens
    
    def Build_Hyperlink(self, titre, num_page) :
        """ Construit un hyperlien """
        self.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False))
        hyper = hl.HyperLinkCtrl(self, num_page, titre, URL="")
        hyper.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLeftLink)
        hyper.AutoBrowse(False)
        hyper.SetColours("BLACK", "BLACK", "BLUE")
        hyper.EnableRollover(True)
        hyper.SetUnderlines(False, False, True)
        hyper.SetBold(False)
        hyper.SetToolTip(wx.ToolTip("Cliquez ici pour atteindre la page '" + titre + "'"))
        hyper.UpdateLink()
        hyper.DoPopup(False)
        return hyper
        
    def OnLeftLink(self, event):
        self.GetParent().SetSelection(event.GetId())
        


       
class Panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, name="panel_configuration")
        self.init = False 
        self.InitPage() # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        
    def InitPage(self):
        self.init = True
        self.treeBook = Treebook(self)
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_base.Add(self.treeBook, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        self.Layout()
        
        self.Bind(wx.EVT_SIZE, self.OnSize)
        
        
    def OnSize(self, event):
        #self.treeBook.panelPays.Layout() # Pour bur affichage du wrapText
        event.Skip()          
    
    def MAJpanel(self):
        if self.init == False :
            self.InitPage()
        #self.treeBook.MAJpanels()
        
        # Si une page est ouverte, le met à jour
        indexPage = self.treeBook.GetSelection()
        if indexPage != 0 :
            self.treeBook.MAJpanel(indexPage)
        
        
class MyFrame(wx.Frame):
    def __init__(self, parent, ID, title=""):
        wx.Frame.__init__(self, parent, ID, title, name="frm_configuration", style=wx.DEFAULT_FRAME_STYLE)
        
        panel = Panel(self)
        
        self.SetTitle("Configuration")
        self.SetSize(size=(800, 600))
        self.Centre()
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1)
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
