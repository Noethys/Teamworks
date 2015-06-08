#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
# Copyright:    (c) 2008-09 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------

import wx
import wx.lib.mixins.listctrl  as  listmix
import GestionDB
import FonctionsPerso
import SaisieCatPresences


class Panel_CatPresences(wx.Panel):
    def __init__(self, parent, ID=-1):
        wx.Panel.__init__(self, parent, ID, style=wx.TAB_TRAVERSAL)
        
        self.barreTitre = FonctionsPerso.BarreTitre(self,  u"Les catégories de présence", u"")
        texteIntro = u"Vous pouvez ici ajouter, modifier ou supprimer des catégories\nde présence. Vous pouvez utiliser autant de catégories et\nsous-catégories que vous souhaitez. Exemples : 'Réunion', 'Congés\npayés', 'Formation'..."
        self.label_introduction = FonctionsPerso.StaticWrapText(self, -1, texteIntro)

        self.treeSelection = 0
        self.treeCtrl_categories = TreeCtrlCategories(self, self.treeSelection)
        
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))
        self.bouton_haut = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Fleche_haut.png", wx.BITMAP_TYPE_ANY))
        self.bouton_bas = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Fleche_bas.png", wx.BITMAP_TYPE_ANY))
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Aide.png", wx.BITMAP_TYPE_ANY))
        if parent.GetName() != "treebook_configuration" :
            self.bouton_aide.Show(False)

##        self.label_conclusion = wx.StaticText(self, -1, "Remarques...")

        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.treeCtrl_categories.Menu_Haut, self.bouton_haut)
        self.Bind(wx.EVT_BUTTON, self.treeCtrl_categories.Menu_Bas, self.bouton_bas)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        
    def __set_properties(self):
        self.bouton_ajouter.SetToolTipString(u"Cliquez ici pour créer une nouvelle catégorie de présences")
        self.bouton_ajouter.SetSize(self.bouton_ajouter.GetBestSize())
        self.bouton_modifier.SetToolTipString(u"Cliquez ici pour modifier une catégorie de présences")
        self.bouton_modifier.SetSize(self.bouton_modifier.GetBestSize())
        self.bouton_supprimer.SetToolTipString(u"Cliquez ici pour supprimer une catégorie de présences")
        self.bouton_supprimer.SetSize(self.bouton_supprimer.GetBestSize())
        self.bouton_haut.SetToolTipString(u"Cliquez ici pour déplacer la catégorie sélectionnée vers le haut")
        self.bouton_haut.SetSize(self.bouton_haut.GetBestSize())
        self.bouton_bas.SetToolTipString(u"Cliquez ici pour déplacer la catégorie sélectionnée vers le bas")
        self.bouton_bas.SetSize(self.bouton_bas.GetBestSize())
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_base2 = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=8, cols=1, vgap=5, hgap=10)
        grid_sizer_base.Add(self.barreTitre, 0, wx.EXPAND, 0)
        grid_sizer_base.Add(self.label_introduction, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        grid_sizer_base2.Add(self.treeCtrl_categories, 1, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_boutons.Add((15, 15), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_haut, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_bas, 0, 0, 0)
        grid_sizer_boutons.Add((5, 5), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.AddGrowableRow(6)
        grid_sizer_base2.Add(grid_sizer_boutons, 1, wx.EXPAND, 0)
        grid_sizer_base2.AddGrowableRow(0)
        grid_sizer_base2.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_base2, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
##        grid_sizer_base.Add(self.label_conclusion, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.SetAutoLayout(True)
        self.grid_sizer_base = grid_sizer_base
        self.grid_sizer_base2 = grid_sizer_base2
        
    def OnSize(self, event) :
        self.treeCtrl_categories.Layout()
        self.grid_sizer_base.Layout()
        self.grid_sizer_base2.Layout()
        event.Skip()
        
    def OnBoutonAjouter(self, event):
        self.Ajouter()

    def Ajouter(self):
        """ Créer une nouvelle catégorie """
        frame_saisieCategorie = SaisieCatPresences.Frm_SaisieCatPresences(self, -1, IDcat_parent=self.treeSelection)
        frame_saisieCategorie.Show()

    def OnBoutonModifier(self, event):
        self.Modifier()

    def Modifier(self):
        """ Modification d'une catégorie """
        IDcategorie = self.treeSelection

        # Vérifie qu'un item a bien été sélectionné
        if IDcategorie == 0:
            dlg = wx.MessageDialog(self, u"Vous devez d'abord sélectionner une catégorie à modifier dans la liste.", "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Vérifie que cette catégorie n'est pas attribuée à une présence
        DB = GestionDB.DB()
        req = "SELECT IDpresence FROM presences WHERE IDcategorie=%d" % IDcategorie
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) != 0 :
            dlg = wx.MessageDialog(self, u"Cette catégorie a déjà été attribuée à " + str(len(listeDonnees)) + u" présences.\nEtes-vous sûr de vouloir la modifier ?", "Confirmation", wx.YES_NO|wx.NO_DEFAULT|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            if reponse == wx.ID_NO:
                dlg.Destroy()
                return
            else: dlg.Destroy()

        
        # Vérifie que cette catégorie n'est pas attribuée à un modèle de présences
        DB = GestionDB.DB()
        req = "SELECT IDtache FROM modeles_taches WHERE IDcategorie=%d" % IDcategorie
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) != 0 :
            dlg = wx.MessageDialog(self, u"Cette catégorie a déjà été attribuée à " + str(len(listeDonnees)) + u" modèle(s) de présences.\nEtes-vous sûr de vouloir la modifier ?", "Confirmation", wx.YES_NO|wx.NO_DEFAULT|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            if reponse == wx.ID_NO:
                dlg.Destroy()
                return
            else: dlg.Destroy()
                
        frame_saisieCategorie = SaisieCatPresences.Frm_SaisieCatPresences(self, -1, IDcategorie=IDcategorie)
        frame_saisieCategorie.Show()

        
    def OnBoutonSupprimer(self, event):
        self.Supprimer()

    def Supprimer(self):
        """ Suppression d'une coordonnée """
        IDcategorie = self.treeSelection

        # Vérifie qu'un item a bien été sélectionné
        if IDcategorie == 0:
            dlg = wx.MessageDialog(self, u"Vous devez d'abord sélectionner une catégorie à supprimer dans la liste.", "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return


        # Vérifie que cette catégorie n'a pas de sous-catégorie
        DB = GestionDB.DB()
        req = "SELECT IDcategorie FROM cat_presences WHERE IDcat_parent=%d" % IDcategorie
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) != 0 :
            dlg = wx.MessageDialog(self, u"Vous ne pouvez pas supprimer une catégorie sans en avoir supprimé au préalable toutes les sous-catégories.", "Information", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Vérifie que cette catégorie n'est pas attribuée à une présence
        DB = GestionDB.DB()
        req = "SELECT IDpresence FROM presences WHERE IDcategorie=%d" % IDcategorie
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) != 0 :
            dlg = wx.MessageDialog(self, u"Vous avez déjà enregistré " + str(len(listeDonnees)) + u" présences avec cette catégorie. \nVous ne pouvez donc pas la supprimer.", "Information", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Vérifie que cette catégorie n'est pas attribuée à un modèle de présences
        DB = GestionDB.DB()
        req = "SELECT IDtache FROM modeles_taches WHERE IDcategorie=%d" % IDcategorie
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) != 0 :
            dlg = wx.MessageDialog(self, u"Vous avez déjà créé " + str(len(listeDonnees)) + u" modèle(s) de planning avec cette catégorie. \nVous ne pouvez donc pas la supprimer.", "Information", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Demande de confirmation
        NomCategorie = self.treeCtrl_categories.treeSelection[1]
        txtMessage = unicode((u"Voulez-vous vraiment supprimer cette catégorie ? \n\n> " + NomCategorie))
        dlgConfirm = wx.MessageDialog(self, txtMessage, u"Confirmation de suppression", wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        
        # Suppression de la catégorie
        self.DB = GestionDB.DB()
        self.DB.ReqDEL("cat_presences", "IDcategorie", IDcategorie)

        # Suppression des enfants de cette catégorie
        self.boucleSuppression(IDcategorie)
        
        # Fermeture de la DB
        self.DB.Close()


        # MAJ du TreeCTrl du panel CONFIG
        self.treeCtrl_categories.select2 = None
        self.treeCtrl_categories.treeSelection = (0, 0, 0)
        self.treeCtrl_categories.MAJtree()
        self.treeCtrl_categories.SetFocus()


    def boucleSuppression(self, IDcategorie):
        req = """
        SELECT IDcategorie, IDcat_parent
        FROM cat_presences
        WHERE cat_presences.IDcat_parent=%d;
        """ % IDcategorie
        self.DB.ExecuterReq(req)
        listeCategories = self.DB.ResultatReq()

        for categorie in listeCategories:
            self.DB.ReqDEL("cat_presences", "IDcategorie", categorie[0])
            self.boucleSuppression(categorie[0])
            
    def MAJpanel(self):
        self.treeCtrl_categories.MAJtree()

    def OnBoutonAide(self, event):
        FonctionsPerso.Aide(8)



class TreeCtrlCategories(wx.TreeCtrl):
    def __init__(self, parent, treeSelection):
        wx.TreeCtrl.__init__(self, parent, -1, wx.DefaultPosition, wx.DefaultSize, style=wx.TR_DEFAULT_STYLE)
        # Autres styles possibles = wx.TR_HAS_BUTTONS|wx.TR_EDIT_LABELS| wx.TR_MULTIPLE|wx.TR_HIDE_ROOT
        self.parent = parent
        self.treeSelection = (0, 0, treeSelection)
        self.select2 = None

        if self.GetGrandParent().GetName() != "treebook_configuration" :
            self.Remplissage()

        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, self)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnContextMenu)

    def FormateCouleur(self, texte):
        pos1 = texte.index(",")
        pos2 = texte.index(",", pos1+1)
        r = int(texte[1:pos1])
        v = int(texte[pos1+2:pos2])
        b = int(texte[pos2+2:-1])
        return (r, v, b)

    def CreationImage(self, tailleImages, r, v, b):
        """ Création des images pour le TreeCtrl """
        bmp = wx.EmptyImage(tailleImages[0], tailleImages[1], True)
        bmp.SetRGBRect((0, 0, 16, 16), 255, 255, 255)
        bmp.SetRGBRect((6, 4, 8, 8), r, v, b)
        return bmp.ConvertToBitmap()

    def Remplissage(self):

        self.listeCategories = self.Importation()
        tailleImages = (16,16)
        il = wx.ImageList(tailleImages[0], tailleImages[1])
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

        self.root = self.AddRoot(u"Catégories")
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
                newItem = self.AppendItem(itemParent, item[1])
                self.SetPyData(newItem, item[0])
                exec("self.SetItemImage(newItem, self.img" + str(item[0]) + ", wx.TreeItemIcon_Normal)")

                # Sélection de l'item s'il sélectionné est par défaut
                if self.select2 != None:
                    if int(item[0]) == self.select2 :
                        self.EnsureVisible(newItem)
                        self.SelectItem(newItem)
                        self.select2 = None
                else:
                    if int(item[0]) == self.treeSelection[2] :
                        self.EnsureVisible(newItem)
                        self.SelectItem(newItem)
                    
                self.nbreBranches += 1

                # Recherche des branches enfants
                self.Boucle(item[0], newItem)

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
        return listeCategories               
            

    def OnSelChanged(self, event):
        self.item = event.GetItem()
        textItem = self.GetItemText(self.item)
        data = self.GetPyData(self.item)
        self.treeSelection = (self.item, textItem, data)
        self.parent.treeSelection = data
        event.Skip()


    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """

        # Recherche et sélection de l'item pointé avec la souris
        item = self.FindTreeItem(event.GetPosition())
        if item == None:
            return
        self.SelectItem(item, True)
        
        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Ajouter
        item = wx.MenuItem(menuPop, 10, u"Ajouter")
        bmp = wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Ajouter, id=10)
        
        menuPop.AppendSeparator()

        # Item Modifier
        item = wx.MenuItem(menuPop, 20, u"Modifier")
        bmp = wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Modifier, id=20)

        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, u"Supprimer")
        bmp = wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Supprimer, id=30)

        menuPop.AppendSeparator()

        # Item Deplacer vers le haut
        item = wx.MenuItem(menuPop, 40, u"Déplacer vers le haut")
        bmp = wx.Bitmap("Images/16x16/Fleche_haut.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Haut, id=40)

        # Item Déplacer vers le bas
        item = wx.MenuItem(menuPop, 50, u"Déplacer vers le bas")
        bmp = wx.Bitmap("Images/16x16/Fleche_bas.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Bas, id=50)
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def FindTreeItem(self, position):
        """ Permet de retrouver l'item pointé dans le TreeCtrl """
        item, flags = self.HitTest(position)
        if item and flags & (wx.TREE_HITTEST_ONITEMLABEL |
                             wx.TREE_HITTEST_ONITEMICON):
            return item
        return None
    
    def Menu_Ajouter(self, event):
        self.parent.Ajouter()
        
    def Menu_Modifier(self, event):
        self.parent.Modifier()

    def Menu_Supprimer(self, event):
        self.parent.Supprimer()

    def Menu_Haut(self, event):
        
        if self.treeSelection[2] == 0:
            return
        
        # On recherche si c'est n'est pas le seul enfant
        itemParent = self.GetItemParent(self.treeSelection[0])
        IDitemParent = self.GetPyData(itemParent)
        nbreEnfants = self.GetChildrenCount(itemParent, False)
        if nbreEnfants < 2:
            dlg = wx.MessageDialog(self, u"Cet item est la seule dans sa catégorie. Vous ne pouvez donc pas le déplacer.", "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # On le déplace vers le haut
        IDcategorie = self.GetPyData(self.treeSelection[0])        
        DB = GestionDB.DB()

        # Récupération de l'ordre
        req = """
        SELECT IDcategorie, nom_categorie, ordre
        FROM cat_presences
        WHERE cat_presences.IDcat_parent=%d
        ORDER BY cat_presences.ordre DESC;
        """ % IDitemParent
        DB.ExecuterReq(req)
        listeCategories = DB.ResultatReq()

        ordreTemp = None
        for categorie in listeCategories :

            # Si c'est déjà le premier, on laisse tomber
            if categorie[0] == IDcategorie and categorie[2] == 1:
                dlg = wx.MessageDialog(self, u"Cet item est le premier de sa catégorie. Vous ne pouvez donc pas le déplacer vers le haut.", "Information", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return

            # On cherche les places
            if categorie[0] == IDcategorie:
                ordreTemp = categorie[2]
                # On modifie l'enregistrement
                listeDonnees = [("ordre", ordreTemp-1),]
                DB.ReqMAJ("cat_presences", listeDonnees, "IDcategorie", categorie[0])

            if ordreTemp != None:
                if categorie[2] == ordreTemp-1:
                    listeDonnees = [("ordre", ordreTemp),]
                    DB.ReqMAJ("cat_presences", listeDonnees, "IDcategorie", categorie[0])

        # Finalisation
        DB.Commit()
        DB.Close()

        # MàJ du treeCtrl
        self.select2 = IDcategorie
        self.MAJtree()
        self.SetFocus()
       

    def Menu_Bas(self, event):
        
        if self.treeSelection[2] == 0:
            return
        
        # On recherche si c'est n'est pas le seul enfant
        itemParent = self.GetItemParent(self.treeSelection[0])
        IDitemParent = self.GetPyData(itemParent)
        nbreEnfants = self.GetChildrenCount(itemParent, False)
        if nbreEnfants < 2:
            dlg = wx.MessageDialog(self, u"Cet item est la seule dans sa catégorie. Vous ne pouvez donc pas le déplacer.", "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # On le déplace vers le haut
        IDcategorie = self.GetPyData(self.treeSelection[0])        
        DB = GestionDB.DB()

        # Récupération de l'ordre
        req = """
        SELECT IDcategorie, nom_categorie, ordre
        FROM cat_presences
        WHERE cat_presences.IDcat_parent=%d
        ORDER BY cat_presences.ordre;
        """ % IDitemParent
        DB.ExecuterReq(req)
        listeCategories = DB.ResultatReq()

        ordreTemp = None
        for categorie in listeCategories :

            # Si c'est déjà le premier, on laisse tomber
            if categorie[0] == IDcategorie and categorie[2] == len(listeCategories):
                dlg = wx.MessageDialog(self, u"Cet item est le dernier de sa catégorie. Vous ne pouvez donc pas le déplacer vers le bas.", "Information", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return

            # On cherche les places
            if categorie[0] == IDcategorie:
                ordreTemp = categorie[2]
                # On modifie l'enregistrement
                listeDonnees = [("ordre", ordreTemp+1),]
                DB.ReqMAJ("cat_presences", listeDonnees, "IDcategorie", categorie[0])

            if ordreTemp != None:
                if categorie[2] == ordreTemp+1:
                    listeDonnees = [("ordre", ordreTemp),]
                    DB.ReqMAJ("cat_presences", listeDonnees, "IDcategorie", categorie[0])

        # Finalisation
        DB.Commit()
        DB.Close()

        # MàJ du treeCtrl
        self.select2 = IDcategorie
        self.MAJtree()
        self.SetFocus()


        
class MyFrame(wx.Frame):
    def __init__(self, parent, title="" ):
        wx.Frame.__init__(self, parent, -1, title=title, name="frm_gestion_cat_presences", style=wx.DEFAULT_FRAME_STYLE)
        self.parent = parent
        self.MakeModal(True)
        self.panel_base = wx.Panel(self, -1)
        self.panel_contenu = Panel_CatPresences(self.panel_base)
        self.panel_contenu.barreTitre.Show(False)
        self.bouton_aide = wx.BitmapButton(self.panel_base, -1, wx.Bitmap("Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self.panel_base, -1, wx.Bitmap("Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self.panel_base, -1, wx.Bitmap("Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.Onbouton_aide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_ok, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_annuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
       
        

    def __set_properties(self):
        self.SetTitle(u"Gestion des catégories de présences")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.bouton_aide.SetToolTipString("Cliquez ici pour obtenir de l'aide")
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetToolTipString(u"Cliquez ici pour valider")
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetToolTipString(u"Cliquez pour annuler et fermer")
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())
        

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        sizer_pages = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base.Add(sizer_pages, 1, wx.ALL|wx.EXPAND, 0)
        sizer_pages.Add(self.panel_contenu, 1, wx.EXPAND | wx.TOP, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND, 10)
        self.panel_base.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        sizer_base.Add(self.panel_base, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        self.SetMinSize((400, 400))
        self.Layout()
        self.Centre()
        self.sizer_pages = sizer_pages
        
        self.SetSize((350, 500))
        

    def OnClose(self, event):
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        event.Skip()
        
    def Onbouton_aide(self, event):
        FonctionsPerso.Aide(8)
            
    def Onbouton_annuler(self, event):
        # Si frame Creation_contrats ouverte, on met à jour le listCtrl Valeurs de points
##        if FonctionsPerso.FrameOuverte("frm_creation_contrats") != None :
##            self.GetParent().MAJ_choice_ValPoint()
##        # Fermeture
##        self.MakeModal(False)
##        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()
        
    def Onbouton_ok(self, event):
##        # Si frame Creation_contrats ouverte, on met à jour le listCtrl Valeurs de points
##        if FonctionsPerso.FrameOuverte("frm_creation_contrats") != None :
##            self.GetParent().MAJ_choice_ValPoint()
##        # Fermeture
##        self.MakeModal(False)
##        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()     

if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
