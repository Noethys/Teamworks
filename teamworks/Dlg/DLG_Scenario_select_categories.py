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
import FonctionsPerso
import GestionDB
import wx.lib.agw.customtreectrl as CT


class MyDialog(wx.Dialog):
    """ Sélection de catégories pour un scénario """
    def __init__(self, parent, listeSelections=[], listeDisabledItems = []):
        wx.Dialog.__init__(self, parent, id=-1, title=_(u"Sélection de catégories"), size=(450, 600))
        self.listeSelections = listeSelections
        self.listeDisabledItems = listeDisabledItems

        # Label
        self.label = wx.StaticText(self, -1, _(u"Veuillez cocher les catégories à inclure obligatoirement dans le scénario :"))
        
        # listCtrl vacances
        self.staticbox_treeCtrl = wx.StaticBox(self, -1, _(u"Aucune catégorie sélectionnée"))
        self.ctrl_treeCtrl = TreeCtrl(self, listeSelections, listeDisabledItems)
        
        # Boutons
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage=Chemins.GetStaticPath("Images/32x32/Valider.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)

    def __set_properties(self):
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.label, 0, wx.ALL, 10)
        
        # Vacances
        sizerStaticBox_treeCtrl = wx.StaticBoxSizer(self.staticbox_treeCtrl, wx.HORIZONTAL)
        sizerStaticBox_treeCtrl.Add(self.ctrl_treeCtrl, 1, wx.EXPAND|wx.ALL, 5)
        grid_sizer_base.Add(sizerStaticBox_treeCtrl, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_boutons.Add((20, 20), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(1)
        self.Layout()
        self.CentreOnScreen()

        
    def OnBoutonOk(self, event):
        """ Validation des données saisies """
        listeSelections = self.ctrl_treeCtrl.GetListeItemsCoches()
        if len(listeSelections) == 0 :
            dlg = wx.MessageDialog(self, _(u"Aucune catégorie n'a été sélectionnée.\n\nSouhaitez-vous valider ce choix ?"), "Confirmation", wx.YES_NO|wx.CANCEL|wx.NO_DEFAULT|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            if reponse == wx.ID_YES:
                dlg.Destroy()
            else: 
                dlg.Destroy()
                return
        self.EndModal(wx.ID_OK)
    
    def GetListeSelections(self):
        return self.ctrl_treeCtrl.GetListeItemsCoches()

        
class TreeCtrl(CT.CustomTreeCtrl):
    def __init__(self, parent, listeSelections=[], listeDisabledItems=[], id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.SIMPLE_BORDER) :
        CT.CustomTreeCtrl.__init__(self, parent, id, pos, size, style)
        
        self.SetBackgroundColour(wx.WHITE)
        self.SetAGWWindowStyleFlag(wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT)
        self.EnableSelectionVista(True) 

        self.listeSelections = listeSelections
        self.listeDisabledItems = listeDisabledItems
        self.Remplissage()
        self.OnItemCheck(None)
        self.Bind(CT.EVT_TREE_ITEM_CHECKED, self.OnItemCheck)

    
    def OnItemCheck(self, event):
        nbreSelections = len(self.GetListeItemsCoches())
        if nbreSelections == 0 : texte = _(u"Aucune catégorie sélectionnée")
        if nbreSelections == 1 : texte = _(u"1 catégorie sélectionnée")
        if nbreSelections > 1 : texte = _(u"%d catégories sélectionnées") % nbreSelections
        self.GetParent().staticbox_treeCtrl.SetLabel(texte)
        
    def FormateCouleur(self, texte):
        pos1 = texte.index(",")
        pos2 = texte.index(",", pos1+1)
        r = int(texte[1:pos1])
        v = int(texte[pos1+2:pos2])
        b = int(texte[pos2+2:-1])
        return (r, v, b)

    def CreationImage(self, tailleImages, r, v, b):
        """ Création des images pour le TreeCtrl """
        if 'phoenix' in wx.PlatformInfo:
            bmp = wx.Image(tailleImages[0], tailleImages[1], True)
            bmp.SetRGB((0, 0, 16, 16), 255, 255, 255)
            bmp.SetRGB((6, 4, 8, 8), r, v, b)
        else:
            bmp = wx.EmptyImage(tailleImages[0], tailleImages[1], True)
            bmp.SetRGBRect((0, 0, 16, 16), 255, 255, 255)
            bmp.SetRGBRect((6, 4, 8, 8), r, v, b)
        return bmp.ConvertToBitmap()

    def Remplissage(self):
        self.listeCategories = self.Importation()
        tailleImages = (16,16)
        il = wx.ImageList(tailleImages[0], tailleImages[1])
        if 'phoenix' in wx.PlatformInfo:
            self.imgRoot = il.Add(wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_OTHER, tailleImages))
        else:
            self.imgRoot = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN, wx.ART_OTHER, tailleImages))
        for categorie in self.listeCategories:
            ID = categorie[0]
            couleur = self.FormateCouleur(categorie[4])
            r = couleur[0]
            v = couleur[1]
            b = couleur[2]
            exec("self.img" + str(ID) +  "= il.Add(self.CreationImage(tailleImages, " + str(r) + ", " + str(v) + ", " + str(b) + "))")
        self.SetImageList(il)
        self.il = il
        self.root = self.AddRoot(_(u"Catégories"))
        self.SetPyData(self.root, 0)
        self.SetItemImage(self.root, self.imgRoot, wx.TreeItemIcon_Normal)
        
        self.nbreCategories = len(self.listeCategories)
        if self.nbreCategories == 0:
            return
        self.nbreBranches = 0
        self.Boucle(0, self.root)
        
        self.Expand(self.root)

    def Boucle(self, IDparent, itemParent):
        """ Boucle de remplissage du TreeCtrl """
        for item in self.listeCategories :
            if item[2] == IDparent:
                # Création de la branche
                newItem = self.AppendItem(itemParent, item[1], ct_type=1)
                self.SetPyData(newItem, item[0])
                
                if item[0] not in self.listeDisabledItems :
                    exec("self.SetItemImage(newItem, self.img" + str(item[0]) + ", wx.TreeItemIcon_Normal)")
                
                if item[0] in self.listeSelections :
                    self.CheckItem(newItem, checked=True)
                    
                if item[0] in self.listeDisabledItems :
                    self.EnableItem(newItem, False) 
                
                self.nbreBranches += 1

                # Recherche des branches enfants
                self.Boucle(item[0], newItem)
                self.Expand(newItem)

    def MAJtree(self):
        self.DeleteAllItems()
        self.Remplissage()

    def Importation(self):
        """ Récupération de la liste des catégories dans la base """
        # Initialisation de la connexion avec la Base de données
        DB = GestionDB.DB()
        req = "SELECT * FROM cat_presences ORDER BY IDcat_parent, ordre"
        DB.ExecuterReq(req)
        listeCategories = DB.ResultatReq()
        DB.Close()
        listeCategories.append( (999, _(u"Sans catégorie"), 0, 0, "(255, 255, 255)" ) )
        return listeCategories               

    def GetListeItemsCoches(self):
        """ Obtient la liste des éléments cochés """
        listeSelections = []
        # Parcours les types de sources : (1ère branche)
        nbre = self.GetChildrenCount(self.root)
        item = self.GetFirstChild(self.root)[0]
        for index in range(nbre) :
            if self.IsItemChecked(item) and self.GetItemPyData(item) != None : 
                data = self.GetItemPyData(item)
                listeSelections.append(data)
            item = self.GetNext(item)
        return listeSelections






if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frm = MyDialog(None, listeSelections = [])
    frm.ShowModal()
    app.MainLoop()