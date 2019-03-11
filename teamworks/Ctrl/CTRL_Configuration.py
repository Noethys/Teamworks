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
import FonctionsPerso
import wx.lib.agw.hyperlink as hl

# Import des panels
from Dlg import DLG_Config_types_pieces
from Dlg import DLG_Config_types_diplomes
from Dlg import DLG_Config_situations
from Dlg import DLG_Config_categories_presences
from Dlg import DLG_Config_classifications
from Dlg import DLG_Config_champs_contrats
from Dlg import DLG_Config_modeles_contrats
from Dlg import DLG_Config_pays
from Dlg import DLG_Config_types_contrats
from Dlg import DLG_Config_val_point
from Dlg import DLG_Config_periodes_vacances
from Dlg import DLG_Config_jours_feries
from Dlg import DLG_Config_password
from Dlg import DLG_Config_sauvegarde
from Dlg import DLG_Config_gadgets
from Dlg import DLG_Config_utilisateurs_reseau
from Dlg import DLG_Config_fonctions
from Dlg import DLG_Config_affectations
from Dlg import DLG_Config_diffuseurs
from Dlg import DLG_Config_emplois
from Dlg import DLG_Config_verrouillage_entretien
from Dlg import DLG_Config_adresses_mail
from Dlg import DLG_Config_questionnaires


# Type page, contenu (panel ou texteIntro pour les rubriques), titre, nom image
LISTE_PAGES = [

    ( "rubrique", _(u"Cliquez sur l'une des rubriques présentées ci-dessous ou dans l'arborescence de gauche pour accéder aux paramétrages correspondants."), _(u"Affichage"), "Outils.png"),
    ( "page", "DLG_Config_gadgets.Panel(self, -1)", _(u"Les gadgets"), "Calendrier_ajout.png"),
    
    ( "rubrique", _(u"Cliquez sur l'une des rubriques présentées ci-dessous ou dans l'arborescence de gauche pour accéder aux paramétrages correspondants."), _(u"Fichiers"), "Repertoire.png"),
    ( "page", "DLG_Config_sauvegarde.Panel(self, -1)", _(u"Sauvegarde automatique"), "Sauvegarder_param.png"),
    ( "page", "DLG_Config_password.Panel(self, -1)", _(u"Protection par mot de passe"), "Cadenas.png"),
    ( "page", "DLG_Config_adresses_mail.Panel(self, -1)", _(u"Adresses expédition de mails"), "Mail.png"),
    ( "page", "DLG_Config_utilisateurs_reseau.Panel(self, -1)", _(u"Utilisateurs réseau"), "Identite.png"),
    
    ( "rubrique", _(u"Cliquez sur l'une des rubriques présentées ci-dessous ou dans l'arborescence de gauche pour accéder aux paramétrages correspondants."), _(u"Données personnes"), "Personnes.png"),
    ( "page", "DLG_Config_questionnaires.Panel(self, -1)", _(u"Le questionnaire"), "Questionnaire.png"),
    ( "page", "DLG_Config_types_diplomes.Panel_TypesDiplomes(self, -1)", _(u"Les types de qualifications"), "Personnes.png"),
    ( "page", "DLG_Config_types_pieces.Panel_TypesPieces(self, -1)", _(u"Les types de pièces"), "Personnes.png"),
    ( "page", "DLG_Config_situations.Panel(self, -1)", _(u"Les types de situations"), "Personnes.png"),
    ( "page", "DLG_Config_pays.Panel(self, -1)", _(u"Les pays et nationalités"), "Drapeau.png"),
    
    ( "rubrique", _(u"Cliquez sur l'une des rubriques présentées ci-dessous ou dans l'arborescence de gauche pour accéder aux paramétrages correspondants."), _(u"Données contrats"), "Document.png"),
    ( "page", "DLG_Config_classifications.Panel(self, -1)", _(u"Les classifications"), "Document.png"),
    ( "page", "DLG_Config_champs_contrats.Panel(self, -1)", _(u"Les champs de contrats"), "Document.png"),
    ( "page", "DLG_Config_modeles_contrats.Panel(self, -1)", _(u"Les modèles de contrats"), "Document.png"),
    ( "page", "DLG_Config_types_contrats.Panel(self, -1)", _(u"Les types de contrats"), "Document.png"),
    ( "page", "DLG_Config_val_point.Panel(self, -1)", _(u"Les valeurs de points"), "Document.png"),
    
    ( "rubrique", _(u"Cliquez sur l'une des rubriques présentées ci-dessous ou dans l'arborescence de gauche pour accéder aux paramétrages correspondants."), _(u"Présences"), "Presences.png"),
    ( "page", "DLG_Config_categories_presences.Panel_CatPresences(self, -1)", _(u"Les catégories de présences"), "Presences.png"),
    ( "page", "DLG_Config_periodes_vacances.Panel(self, -1)", _(u"Les périodes de vacances"), "Calendrier3jours.png"),
    ( "page", "DLG_Config_jours_feries.Panel(self, -1)", _(u"Les jours fériés"), "Calendrier_jour.png"),
    
    ( "rubrique", _(u"Cliquez sur l'une des rubriques présentées ci-dessous ou dans l'arborescence de gauche pour accéder aux paramétrages correspondants."), _(u"Recrutement"), "Mail.png"),
    ( "page", "DLG_Config_verrouillage_entretien.Panel(self, -1)", _(u"Protection des entretiens"), "Cadenas.png"),
    ( "page", "DLG_Config_fonctions.Panel(self, -1)", _(u"Les fonctions"), "Mail.png"),
    ( "page", "DLG_Config_affectations.Panel(self, -1)", _(u"Les affectations"), "Mail.png"),
    ( "page", "DLG_Config_diffuseurs.Panel(self, -1)", _(u"Les diffuseurs"), "Mail.png"),
    ( "page", "DLG_Config_emplois.Panel(self, -1)", _(u"Les offres d'emploi"), "Mail.png"),
    
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
            exec( "self.img_" + str(index) + " = il.Add(wx.Bitmap(Chemins.GetStaticPath('Images/16x16/' + image), wx.BITMAP_TYPE_PNG))" )
            index += 1
        self.AssignImageList(il)
        
        # Création des pages du TreeBook
        index = 0
        for type, contenu, titre, image in LISTE_PAGES :
            if type == "rubrique" :
                panel = Panel_rubrique(self, -1, titre, contenu, index)
                exec( "self.AddPage(panel, u'" + titre + "', imageId=self.img_" + str(index) + ")")
            if type == "page" :
                self.AddSubPage(eval(contenu), titre, imageId=getattr(self, "img_%s" % index))
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
        grid_sizer_hyperlinks.AddGrowableCol(1)
        self.SetAutoLayout(True)
        self.Layout()
        self.grid_sizer_hyperlinks = grid_sizer_hyperlinks
        
        # Recherche des pages enfants
        liste_pages_enfants = self.Recherche_titres_hyperlinks(num_index)
        
        # Création des liens
        for titre, num_page in liste_pages_enfants :
            img = wx.StaticBitmap(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/" + LISTE_PAGES[num_page][3]), wx.BITMAP_TYPE_PNG))
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
        if 'phoenix' in wx.PlatformInfo:
            _icon = wx.Icon()
        else :
            _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1)
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
