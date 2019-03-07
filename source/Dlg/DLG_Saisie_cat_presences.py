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

def FormateCouleur(texte):
    pos1 = texte.index(",")
    pos2 = texte.index(",", pos1+1)
    r = int(texte[1:pos1])
    v = int(texte[pos1+2:pos2])
    b = int(texte[pos2+2:-1])
    return (r, v, b)

class Frm_SaisieCatPresences(wx.Frame):
    def __init__(self, parent, ID, title=_(u"Saisie d'une nouvelle catégorie"), IDcategorie=0, IDcat_parent=0):
        wx.Frame.__init__(self, parent, ID, title=title, style=wx.DEFAULT_FRAME_STYLE, size=(350, 420))
        self.MakeModal(True)
        
        # Valeurs par défaut à appliquer
        self.IDcategorie = IDcategorie
        self.IDcat_parent = IDcat_parent
        self.couleur = (255, 255, 255)
        self.nom_categorie = ""

        # Importation des données
        if self.IDcategorie != 0 :
            self.Importation()
            self.SetTitle(_(u"Modification d'une catégorie"))
        
        self.panel_base = wx.Panel(self, -1)
        self.sizer_nom_staticbox = wx.StaticBox(self.panel_base, -1, _(u"Nom de la catégorie"))
        self.sizer_couleur_staticbox = wx.StaticBox(self.panel_base, -1, _(u"Couleur"))
        self.sizer_tree_staticbox = wx.StaticBox(self.panel_base, -1, _(u"Sélection de la catégorie parente"))
        self.treeCtrl_categories = TreeCtrlCategories(self.panel_base, self.IDcat_parent)
        self.text_nom = wx.TextCtrl(self.panel_base, -1, self.nom_categorie)
        self.bouton_aide = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_ok = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Ok"), cheminImage=Chemins.GetStaticPath("Images/32x32/Valider.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))

        self.bouton_couleur = csel.ColourSelect(self.panel_base, -1, "", self.couleur, size = (40, 22))
        self.bouton_couleur.Bind(csel.EVT_COLOURSELECT, self.OnSelectColour)
        self.Bind(wx.EVT_BUTTON, self.OnBouton_aide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBouton_ok, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBouton_annuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        self.__set_properties()
        self.__do_layout()
        # end wxGlade

        self.text_nom.SetFocus()

    def __set_properties(self):
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.treeCtrl_categories.SetToolTipString(_(u"Sélectionnez une catégorie PARENTE. Votre nouvelle catégorie sera placée comment enfant de cette catégorie."))
        self.bouton_aide.SetToolTipString("Bouton Aide")
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetToolTipString("Bouton Ok")
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetToolTipString("Bouton annuler")
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())
        # end wxGlade

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_contenu1 = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        grid_sizer_contenu2 = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        sizer_couleur = wx.StaticBoxSizer(self.sizer_couleur_staticbox, wx.VERTICAL)
        sizer_nom = wx.StaticBoxSizer(self.sizer_nom_staticbox, wx.VERTICAL)
        sizer_tree = wx.StaticBoxSizer(self.sizer_tree_staticbox, wx.VERTICAL)
        sizer_tree.Add(self.treeCtrl_categories, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_contenu1.Add(sizer_tree, 1, wx.EXPAND, 0)
        sizer_nom.Add(self.text_nom, 0, wx.ALL|wx.EXPAND, 5)
        grid_sizer_contenu2.Add(sizer_nom, 1, wx.EXPAND, 0)
        sizer_couleur.Add(self.bouton_couleur, 0, wx.ALL, 5)
        grid_sizer_contenu2.Add(sizer_couleur, 1, wx.EXPAND, 0)
        grid_sizer_contenu2.AddGrowableCol(0)
        grid_sizer_contenu1.Add(grid_sizer_contenu2, 1, wx.EXPAND, 0)
        grid_sizer_contenu1.AddGrowableRow(0)
        grid_sizer_contenu1.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_contenu1, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((15, 15), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.panel_base.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        sizer_base.Add(self.panel_base, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        self.Layout()
        self.Centre()
        # end wxGlade

# end of class Frm_SaisieCatPresences

    def Importation(self):
        """ Récupération des données à modifier dans la base """

        # Initialisation de la connexion avec la Base de données
        DB = GestionDB.DB()
        req = "SELECT * FROM cat_presences WHERE IDcategorie=%d" % self.IDcategorie
        DB.ExecuterReq(req)
        donnees = DB.ResultatReq()[0]
        DB.Close()

        if len(donnees) == 0:
            return

        # Création des variables
        self.IDcat_parent = donnees[2]
        self.couleur = FormateCouleur(donnees[4])
        self.nom_categorie = donnees[1]

    def Sauvegarde(self):
        """ Sauvegarde des données dans la base de données """

        # Initialisation de la connexion avec la Base de données
        DB = GestionDB.DB()

        # Récupération de l'ordre
        req = """
        SELECT Max(cat_presences.ordre)
        FROM cat_presences
        WHERE cat_presences.IDcat_parent=%d;
        """ % self.IDcat_parent
        DB.ExecuterReq(req)
        ordreMax = DB.ResultatReq()[0][0]

        if ordreMax == None:
            ordreMax = 0

        # Création de la liste des données
        listeDonnees = [    ("nom_categorie",   self.nom_categorie),
                            ("IDcat_parent",    self.IDcat_parent),
                            ("ordre",           ordreMax+1),
                            ("couleur",         unicode(self.couleur)),
                        ]

        if self.IDcategorie == 0:
            # Enregistrement d'une nouvelle coordonnée
            newID = DB.ReqInsert("cat_presences", listeDonnees)
            ID = newID
        else:
            # Modification de la coordonnée
            DB.ReqMAJ("cat_presences", listeDonnees, "IDcategorie", self.IDcategorie)
            ID = self.IDcategorie

        DB.Commit()
        DB.Close()
        return ID
        

    def OnSelectColour(self, event):
        reponse = event.GetValue()
        self.couleur = (reponse[0], reponse[1], reponse[2])

    def OnBouton_aide(self, event):
        FonctionsPerso.Aide(11)

    def OnClose(self, event):
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        event.Skip()
        
    def OnBouton_annuler(self, event):
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()
        event.Skip()

    def OnBouton_ok(self, event):

        # Vérification des données
        if self.couleur == (255, 255, 255):
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une couleur en cliquant sur le bouton couleur."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.bouton_couleur.SetFocus()
            return

        if self.text_nom.GetValue() == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom de catégorie"), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.text_nom.SetFocus()
            return
        else:
            self.nom_categorie = self.text_nom.GetValue()

        # Demande de confirmation de création de catégorie
        """
        if int(self.IDcat_parent) == 0:
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une catégorie parente dans la liste proposée."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return"""
        
        # Lancement de la sauvegarde
        ID = self.Sauvegarde()

        # MAJ du TreeCTrl du panel CONFIG
        self.GetParent().treeCtrl_categories.select2 = ID
        self.GetParent().treeCtrl_categories.MAJtree()
        self.GetParent().treeCtrl_categories.SetFocus()

        # Fermeture de la fenêtre
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()
        

class TreeCtrlCategories(wx.TreeCtrl):
    def __init__(self, parent, IDcat_parent):
        wx.TreeCtrl.__init__(self, parent, -1, wx.DefaultPosition, wx.DefaultSize, style=wx.TR_DEFAULT_STYLE)
        # Autres styles possibles = wx.TR_HAS_BUTTONS|wx.TR_EDIT_LABELS| wx.TR_MULTIPLE|wx.TR_HIDE_ROOT
        self.parent = parent
        self.IDcat_parent = IDcat_parent

        self.listeCategories = self.Importation()

        tailleImages = (16,16)
        il = wx.ImageList(tailleImages[0], tailleImages[1])
        self.imgRoot = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN, wx.ART_OTHER, tailleImages))
        for categorie in self.listeCategories:
            ID = categorie[0]
            couleur = FormateCouleur(categorie[4])
            r = couleur[0]
            v = couleur[1]
            b = couleur[2]
            exec("self.img" + str(ID) +  "= il.Add(self.CreationImage(tailleImages, " + str(r) + ", " + str(v) + ", " + str(b) + "))")

        self.SetImageList(il)
        self.il = il

        self.root = self.AddRoot(_(u"Catégories"))
        self.SetPyData(self.root, 0)
        self.SetItemImage(self.root, self.imgRoot, wx.TreeItemIcon_Normal)

        self.Remplissage()

        self.Expand(self.root)
        
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, self)

    
    def CreationImage(self, tailleImages, r, v, b):
        """ Création des images pour le TreeCtrl """
        bmp = wx.EmptyImage(tailleImages[0], tailleImages[1], True)
        bmp.SetRGBRect((0, 0, 16, 16), 255, 255, 255)
        bmp.SetRGBRect((6, 4, 8, 8), r, v, b)
        return bmp.ConvertToBitmap()

    def Remplissage(self):

        self.nbreCategories = len(self.listeCategories)
        if self.nbreCategories == 0:
            return
        self.nbreBranches = 0
        self.Boucle(0, self.root)

    def Boucle(self, IDparent, itemParent):
        """ Boucle de remplissage du TreeCtrl """
        for item in self.listeCategories :
            if item[2] == IDparent:

                # Création de la branche
                newItem = self.AppendItem(itemParent, item[1])
                self.SetPyData(newItem, item[0])
                exec("self.SetItemImage(newItem, self.img" + str(item[0]) + ", wx.TreeItemIcon_Normal)")

                # Sélection de l'item s'il sélectionné est par défaut
                if int(item[0]) == self.IDcat_parent :
                    self.EnsureVisible(newItem)
                    self.SelectItem(newItem)
                    
                self.nbreBranches += 1

                # Recherche des branches enfants
                self.Boucle(item[0], newItem)

    def Importation(self):
        """ Récupération de la liste des catégories dans la base """

        # Initialisation de la connexion avec la Base de données
        DB = GestionDB.DB()
        req = "SELECT * FROM cat_presences"
        DB.ExecuterReq(req)
        listeCategories = DB.ResultatReq()
        DB.Close()

        return listeCategories               
            

    def OnSelChanged(self, event):
        self.item = event.GetItem()
        textItem = self.GetItemText(self.item)
        data = self.GetPyData(self.item)
        self.IDcat_parent = data
        self.GetGrandParent().IDcat_parent = data
        event.Skip()

            

if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = Frm_SaisieCatPresences(None, -1, IDcategorie=0)
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
