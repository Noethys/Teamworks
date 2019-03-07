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
import wx.lib.mixins.listctrl  as  listmix
import GestionDB
import FonctionsPerso



class Panel_TypesDiplomes(wx.Panel):
    def __init__(self, parent, ID=-1):
        wx.Panel.__init__(self, parent, ID, style=wx.TAB_TRAVERSAL)
        
        self.barreTitre = FonctionsPerso.BarreTitre(self,  _(u"Les types de qualifications"), u"")
        texteIntro = _(u"Vous pouvez ici ajouter, modifier ou supprimer des types de qualifications.\nExemple : 'B.A.F.A', 'A.F.P.S.', etc... N'oubliez pas de créer ensuite créer le\ntype de pièces correspondants.")
        self.label_introduction = FonctionsPerso.StaticWrapText(self, -1, texteIntro)
        
        self.listCtrl_TypesDiplomes = ListCtrlTypesDiplomes(self)
        self.listCtrl_TypesDiplomes.SetMinSize((20, 20)) 
        
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Aide.png"), wx.BITMAP_TYPE_ANY))
##        self.label_conclusion = wx.StaticText(self, -1, "Remarques...")

        self.__set_properties()
        self.__do_layout()
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
              
    def __set_properties(self):
        self.bouton_ajouter.SetToolTipString(_(u"Cliquez ici pour créer un nouveau type de qualification"))
        self.bouton_ajouter.SetSize(self.bouton_ajouter.GetBestSize())
        self.bouton_modifier.SetToolTipString(_(u"Cliquez ici pour modifier un type de qualification sélectionné dans la liste"))
        self.bouton_modifier.SetSize(self.bouton_modifier.GetBestSize())
        self.bouton_supprimer.SetToolTipString(_(u"Cliquez ici pour supprimer un type de qualification sélectionné dans la liste"))
        self.bouton_supprimer.SetSize(self.bouton_supprimer.GetBestSize())
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_base2 = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=10)
        grid_sizer_base.Add(self.barreTitre, 0, wx.EXPAND, 0)
        grid_sizer_base.Add(self.label_introduction, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        grid_sizer_base2.Add(self.listCtrl_TypesDiplomes, 1, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_boutons.Add((5, 5), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.AddGrowableRow(3)
        grid_sizer_base2.Add(grid_sizer_boutons, 1, wx.EXPAND, 0)
        grid_sizer_base2.AddGrowableRow(0)
        grid_sizer_base2.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_base2, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
##        grid_sizer_base.Add(self.label_conclusion, 0, 0, 0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.SetAutoLayout(True)
        
        self.grid_sizer_base = grid_sizer_base
        self.grid_sizer_base2 = grid_sizer_base2
        
                
    def OnBoutonAjouter(self, event):
        self.Ajouter()

    def Ajouter(self):
        """ Créer un nouveau type de pièce """
        dlg = wx.TextEntryDialog(self, _(u"Saisissez le nom du nouveau type de qualification (ex : B.A.F.A.) :"), _(u"Saisie d'un nouveau type de qualification"), u"")
        if dlg.ShowModal() == wx.ID_OK:
            varNom_Diplome = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return

        if varNom_Diplome == "":
            dlg = wx.MessageDialog(self, _(u"Le nom que vous avez saisi n'est pas valide."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Sauvegarde
        listeDonnees = [("nom_diplome",  varNom_Diplome),]
        
        # Initialisation de la connexion avec la Base de données
        DB = GestionDB.DB()
        newID = DB.ReqInsert("types_diplomes", listeDonnees)
        DB.Close()

        # MàJ du ListCtrl
        self.listCtrl_TypesDiplomes.MAJListeCtrl()

        #DB.ReqMAJ("types_pieces", listeDonnees, "IDtype_piece", varIDtype_piece)

    def OnBoutonModifier(self, event):
        self.Modifier()

    def Modifier(self):
        """ Modification d'un type de pièce """
        index = self.listCtrl_TypesDiplomes.GetFirstSelected()
        if index == -1:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un type de qualification à modifier dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Avertissement si ce type de diplome a déjà été attribué à une personne
        nbreTitulaires = int(self.listCtrl_TypesDiplomes.GetItem(index, 2).GetText())
        if nbreTitulaires != 0:
            message =_(u"Avertissement : Ce type de qualification a déjà été attribué a ") + str(nbreTitulaires) + _(u" personne(s). Toute modification sera donc répercutée en cascade sur toutes les fiches des personnes à qui ce type de qualification a été attribué. \n\nSouhaitez-vous quand même modifier ce type de qualification ?")
            dlg = wx.MessageDialog(self, message, "Information", wx.YES_NO|wx.NO_DEFAULT|wx.ICON_INFORMATION)
            reponse = dlg.ShowModal()
            if reponse == wx.ID_NO:
                dlg.Destroy()
                return
            else:
                dlg.Destroy()
                
        varIDtype_diplome = int(self.listCtrl_TypesDiplomes.GetItem(index, 0).GetText())
        varNomType_diplome = self.listCtrl_TypesDiplomes.GetItem(index, 1).GetText()
        
        dlg = wx.TextEntryDialog(self, _(u"Saisissez le nom du nouveau type de qualification :"), _(u"Saisie d'un nouveau type de qualification"), varNomType_diplome)
        if dlg.ShowModal() == wx.ID_OK:
            varNom_Diplome = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return

        if varNom_Diplome == "":
            dlg = wx.MessageDialog(self, _(u"Le nom que vous avez saisi n'est pas valide."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Sauvegarde
        listeDonnees = [("nom_diplome",  varNom_Diplome),]
        
        # Initialisation de la connexion avec la Base de données
        DB = GestionDB.DB()
        DB.ReqMAJ("types_diplomes", listeDonnees, "IDtype_diplome", varIDtype_diplome)
        DB.Close()

        # MàJ du ListCtrl
        self.listCtrl_TypesDiplomes.MAJListeCtrl()

        
    def OnBoutonSupprimer(self, event):
        self.Supprimer()

    def Supprimer(self):
        """ Suppression d'une coordonnée """
        index = self.listCtrl_TypesDiplomes.GetFirstSelected()

        # Vérifie qu'un item a bien été sélectionné
        if index == -1:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un type de qualification à supprimer dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Vérifie que cette pièce n'est attribuée à aucune personne
        nbreTitulaires = int(self.listCtrl_TypesDiplomes.GetItem(index, 2).GetText())
        if nbreTitulaires != 0:
            dlg = wx.MessageDialog(self, _(u"Pour des raisons de sécurité des données, vous ne pouvez pas supprimer un type de qualification qui a déjà été attribué à des personnes.\n\nSi vous voulez vraiment le supprimer, vous devez d'abord supprimer les qualifications ayant ce nom sur chaque fiche individuelle concernée."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Demande de confirmation
        IDtype_diplome = int(self.listCtrl_TypesDiplomes.GetItem(index, 0).GetText())
        NomDiplome = self.listCtrl_TypesDiplomes.GetItem(index, 1).GetText()
        txtMessage = unicode((_(u"Voulez-vous vraiment supprimer ce type de qualification ? \n\n> ") + NomDiplome))
        dlgConfirm = wx.MessageDialog(self, txtMessage, _(u"Confirmation de suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        
        # Suppression du type de pièce
        DB = GestionDB.DB()
        DB.ReqDEL("types_diplomes", "IDtype_diplome", IDtype_diplome)

        # MàJ du ListCtrl
        self.listCtrl_TypesDiplomes.MAJListeCtrl()
    
    def MAJpanel(self):
        self.listCtrl_TypesDiplomes.MAJListeCtrl()
        
    def OnBoutonAide(self, event):
        FonctionsPerso.Aide(48)
        

class ListCtrlTypesDiplomes(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin, listmix.ColumnSorterMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__( self, parent, -1, style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        
        self.criteres = ""
        self.parent = parent

        # Initialisation des images
        tailleIcones = 16
        self.il = wx.ImageList(tailleIcones, tailleIcones)
        self.imgTriAz= self.il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Tri_az.png"), wx.BITMAP_TYPE_PNG))
        self.imgTriZa= self.il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Tri_za.png"), wx.BITMAP_TYPE_PNG))
        self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

        #adding some attributes (colourful background for each item rows)
        self.attr1 = wx.ListItemAttr()
        self.attr1.SetBackgroundColour("#EEF4FB") # Vert = #F0FBED

        # Remplissage du ListCtrl
        if self.GetGrandParent().GetName() != "treebook_configuration" :
            self.Remplissage()

    def OnSize(self, event):
        self.Refresh()
        event.Skip()

    def Remplissage(self):
        
        # Récupération des données dans la base de données
        self.Importation()
        
        # Création des colonnes
        self.nbreColonnes = 3
        self.InsertColumn(0, _(u"     ID"))
        self.SetColumnWidth(0, 0)
        self.InsertColumn(1, _(u"Nom de la qualification"))
        self.SetColumnWidth(1, 250)
        self.InsertColumn(2, _(u"Nb titulaires"))
        self.SetColumnWidth(2, 80)        

        #These two should probably be passed to init more cleanly
        #setting the numbers of items = number of elements in the dictionary
        self.itemDataMap = self.donnees
        self.itemIndexMap = self.donnees.keys()
        self.SetItemCount(self.nbreLignes)
        
        #mixins
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        listmix.ColumnSorterMixin.__init__(self, self.nbreColonnes)

        #sort by genre (column 1), A->Z ascending order (1)
        self.SortListItems(1, 1)

        #events
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        #self.Bind(wx.EVT_SIZE, self.OnSize)

    def Importation(self):
      
        # Récupération des données de la table TYPES_PIECES
        DB = GestionDB.DB()
        req = """SELECT types_diplomes.IDtype_diplome, types_diplomes.nom_diplome, Count(diplomes.IDdiplome) AS CompteDeIDdiplome
        FROM types_diplomes LEFT JOIN diplomes ON types_diplomes.IDtype_diplome = diplomes.IDtype_diplome
        GROUP BY types_diplomes.IDtype_diplome, types_diplomes.nom_diplome %s;
        """ % self.criteres
        DB.ExecuterReq(req)
        listeTypesDiplomes = DB.ResultatReq()
        DB.Close()

        self.nbreLignes = len(listeTypesDiplomes)

        # Création du dictionnaire de données
        self.donnees = self.listeEnDict(listeTypesDiplomes)


    def MAJListeCtrl(self):
        self.ClearAll()
        self.Remplissage()
        self.resizeLastColumn(0)
        listmix.ColumnSorterMixin.__init__(self, self.nbreColonnes)

    def listeEnDict(self, liste):
        dictio = {}
        x = 1
        for ligne in liste:
            index = x # Donne un entier comme clé
            dictio[index] = ligne
            x += 1
        return dictio
           
    def OnItemActivated(self, event):
        self.parent.Modifier()
        
    def getColumnText(self, index, col):
        item = self.GetItem(index, col)
        return item.GetText()


    #---------------------------------------------------
    # These methods are callbacks for implementing the
    # "virtualness" of the list...

    def OnGetItemText(self, item, col):
        """ Affichage des valeurs dans chaque case du ListCtrl """
        index=self.itemIndexMap[item]
        valeur = unicode(self.itemDataMap[index][col])
        return valeur

    def OnGetItemImage(self, item):
        """ Affichage des images en début de ligne """
        return -1

    def OnGetItemAttr(self, item):
        """ Application d'une couleur de fond pour une ligne sur deux """
        # Création d'une ligne de couleur 1 ligne sur 2
        if item % 2 == 1:
            return self.attr1
        else:
            return None
       
    #-----------------------------------------------------------
    # Matt C, 2006/02/22
    # Here's a better SortItems() method --
    # the ColumnSorterMixin.__ColumnSorter() method already handles the ascending/descending,
    # and it knows to sort on another column if the chosen columns have the same value.

    def SortItems(self,sorter=cmp):
        items = list(self.itemDataMap.keys())
        items.sort(sorter)
        self.itemIndexMap = items
        # redraw the list
        self.Refresh()

    # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetListCtrl(self):
        return self

    # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetSortImages(self):
        return (self.imgTriAz, self.imgTriZa)

    # ---------------------------------------------------------

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        
        if self.GetFirstSelected() == -1:
            return False
        index = self.GetFirstSelected()
        key = int(self.getColumnText(index, 0))
        
        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Modifier
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Ajouter, id=10)
        
        menuPop.AppendSeparator()

        # Item Ajouter
        item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Modifier, id=20)

        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Supprimer, id=30)
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Menu_Ajouter(self, event):
        self.parent.Ajouter()
        
    def Menu_Modifier(self, event):
        self.parent.Modifier()

    def Menu_Supprimer(self, event):
        self.parent.Supprimer()




class MyFrame(wx.Frame):
    def __init__(self, parent, ID, title=""):
        wx.Frame.__init__(self, parent, ID, title, style=wx.DEFAULT_FRAME_STYLE)
        
        panel = Panel_TypesDiplomes(self)
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