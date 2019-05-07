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
import six
import wx.lib.mixins.listctrl  as  listmix
import GestionDB
from Dlg import DLG_Saisie_type_piece
import FonctionsPerso
from Utils import UTILS_Adaptations
from Ctrl import CTRL_Bouton_image


def FormatDuree(duree):

    posM = duree.find("m")
    posA = duree.find("a")
    jours = int(duree[1:posM-1])
    mois = int(duree[posM+1:posA-1])
    annees = int(duree[posA+1:])
    
    listItems = []
    if jours == 1:
        textJours = _(u"%d jour") % jours
        listItems.append(textJours)
    if jours > 1:
        textJours = _(u"%d jours") % jours
        listItems.append(textJours)
    if mois > 0:
        textMois = _(u"%d mois") % mois
        listItems.append(textMois)
    if annees == 1:
        textAnnees = _(u"%d ann�e") % annees
        listItems.append(textAnnees)
    if annees > 1:
        textAnnees = _(u"%d ann�es") % annees
        listItems.append(textAnnees)

    nbreItems = len(listItems)
    if nbreItems == 0:
        resultat = _(u"Validit� illimit�e")
    else:
        if nbreItems == 1:
            resultat = listItems[0]
        if nbreItems == 2:
            resultat = listItems[0] + " et " + listItems[1]
        if nbreItems == 3:
            resultat = listItems[0] + ", " + listItems[1] + " et " + listItems[2]

    return resultat
    

class Panel(wx.Panel):
    def __init__(self, parent, ID=-1):
        wx.Panel.__init__(self, parent, ID, style=wx.TAB_TRAVERSAL)
        
        self.barreTitre = FonctionsPerso.BarreTitre(self,  _(u"Les types de pi�ces"), u"")
        texteIntro = _(u"Vous pouvez ici ajouter, modifier ou supprimer des types de pi�ces. Ce sont les documents que les employ�s doivent vous communiquer.\nCelles-ci peuvent �tre obligatoire pour tous (Exemple : 'Certificat m�dical'...) ou �tre obligatoire en fonction du dipl�me d�tenu par la\npersonne (Exemple, si une personne a le dipl�me 'A.F.P.S.', elle devra donner la pi�ce 'Dipl�me A.F.P.S.'). Vous devez pr�ciser une dur�e\nde validit� par d�faut pour chaque pi�ce.")
        self.label_introduction = FonctionsPerso.StaticWrapText(self, -1, texteIntro)
        
        self.listCtrl_TypesPieces = ListCtrlTypesPieces(self)
        self.listCtrl_TypesPieces.SetMinSize((20, 20)) 
        
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)

    def __set_properties(self):
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour cr�er un nouveau type de pi�ce")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier un type de pi�ce s�lectionn� dans la liste")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer un type de pi�ce s�lectionn� dans la liste")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_base2 = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=10)
        grid_sizer_base.Add(self.barreTitre, 0, wx.EXPAND, 0)
        grid_sizer_base.Add(self.label_introduction, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        grid_sizer_base2.Add(self.listCtrl_TypesPieces, 1, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableRow(3)
        grid_sizer_base2.Add(grid_sizer_boutons, 1, wx.EXPAND, 0)
        grid_sizer_base2.AddGrowableRow(0)
        grid_sizer_base2.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_base2, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.SetAutoLayout(True)

    def OnBoutonAjouter(self, event):
        self.Ajouter()

    def Ajouter(self):
        """ Cr�er un nouveau type de pi�ce """
        dlg = DLG_Saisie_type_piece.Dialog(self, -1, IDtype_piece=0)
        dlg.ShowModal()
        dlg.Destroy()

    def OnBoutonModifier(self, event):
        self.Modifier()

    def Modifier(self):
        """ Modification d'un type de pi�ce """
        index = self.listCtrl_TypesPieces.GetFirstSelected()
        if index == -1:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord s�lectionner un type de pi�ce � modifier dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Avertissement si cette pi�ce a d�j� �t� attribu�e � aucune personne
        nbreTitulaires = int(self.listCtrl_TypesPieces.GetItem(index, 3).GetText())
        if nbreTitulaires != 0:
            message =_(u"Avertissement : Ce type de pi�ce a d�j� �t� attribu� a ") + str(nbreTitulaires) + _(u" personne(s). Toute modification sera donc r�percut�e en cascade sur toutes les fiches des personnes � qui ce type de pi�ce a �t� attribu�. \n\nSouhaitez-vous quand m�me modifier ce type de pi�ce ?")
            dlg = wx.MessageDialog(self, message, "Information", wx.YES_NO|wx.NO_DEFAULT|wx.ICON_INFORMATION)
            reponse = dlg.ShowModal()
            if reponse == wx.ID_NO:
                dlg.Destroy()
                return
            else:
                dlg.Destroy()
        
        varIDtype_piece = int(self.listCtrl_TypesPieces.GetItem(index, 0).GetText())
        dlg = DLG_Saisie_type_piece.Dialog(self, -1, IDtype_piece=varIDtype_piece)
        dlg.ShowModal()
        dlg.Destroy()

        
    def OnBoutonSupprimer(self, event):
        self.Supprimer()

    def Supprimer(self):
        """ Suppression d'une coordonn�e """
        index = self.listCtrl_TypesPieces.GetFirstSelected()

        # V�rifie qu'un item a bien �t� s�lectionn�
        if index == -1:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord s�lectionner une pi�ce � supprimer dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # V�rifie que cette pi�ce n'est attribu�e � aucune personne
        nbreTitulaires = int(self.listCtrl_TypesPieces.GetItem(index, 3).GetText())
        if nbreTitulaires != 0:
            dlg = wx.MessageDialog(self, _(u"Pour des raisons de s�curit� des donn�es, vous ne pouvez pas supprimer un type de pi�ce qui a d�j� �t� attribu� � des personnes.\n\nSi vous voulez vraiment le supprimer, vous devez d'abord supprimer les pi�ces ayant ce nom sur chaque fiche individuelle concern�e."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Demande de confirmation
        IDtype_piece = int(self.listCtrl_TypesPieces.GetItem(index, 0).GetText())
        NomPiece = self.listCtrl_TypesPieces.GetItem(index, 1).GetText()
        txtMessage = six.text_type((_(u"Voulez-vous vraiment supprimer ce type de pi�ce ? \n\n> ") + NomPiece))
        dlgConfirm = wx.MessageDialog(self, txtMessage, _(u"Confirmation de suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        
        # Suppression du type de pi�ce
        DB = GestionDB.DB()
        DB.ReqDEL("types_pieces", "IDtype_piece", IDtype_piece)
        DB.ReqDEL("diplomes_pieces", "IDtype_piece", IDtype_piece)
        DB.Close()

        # M�J du listCtrl Coords de la fiche individuelle
        self.listCtrl_TypesPieces.MAJListeCtrl()
    
    def MAJpanel(self):
        self.listCtrl_TypesPieces.MAJListeCtrl()
        


class ListCtrlTypesPieces(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin, listmix.ColumnSorterMixin):
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
        print("Refresh du ListCtrl")
        event.Skip()

    def Remplissage(self):
        
        # R�cup�ration des donn�es dans la base de donn�es
        self.Importation()
        
        # Cr�ation des colonnes
        self.nbreColonnes = 5
        self.InsertColumn(0, _(u"     ID"))
        self.SetColumnWidth(0, 0)
        self.InsertColumn(1, _(u"Nom de la pi�ce"))
        self.SetColumnWidth(1, 200)
        self.InsertColumn(2, _(u"Dur�e de validit�"))
        self.SetColumnWidth(2, 150)
        self.InsertColumn(3, _(u"Nb titulaires"))
        self.SetColumnWidth(3, 80)
        self.InsertColumn(4, _(u"Dipl�mes associ�s"))
        self.SetColumnWidth(4, 300)
        

        #These two should probably be passed to init more cleanly
        #setting the numbers of items = number of elements in the dictionary
        self.itemDataMap = self.donnees
        self.itemIndexMap = list(self.donnees.keys())
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
      
        # R�cup�ration des donn�es de la table TYPES_PIECES
        DB = GestionDB.DB()
        if DB.echec == 1 : 
            self.nbreLignes = 0
            self.donnees = {}
            return

        req = """SELECT types_pieces.IDtype_piece, types_pieces.nom_piece, types_pieces.duree_validite, Count(pieces.IDpiece) AS CompteDeIDpiece
        FROM types_pieces LEFT JOIN pieces ON types_pieces.IDtype_piece = pieces.IDtype_piece
        GROUP BY types_pieces.IDtype_piece, types_pieces.nom_piece, types_pieces.duree_validite %s;
        """ % self.criteres
        DB.ExecuterReq(req)
        listeTypesPiecesTmp = DB.ResultatReq()
        DB.Close()
        
        # Formate la dur�e de validit�
        listeTypesPieces = []
        for IDtype_piece, nom_piece, duree_validite, CompteDeIDpiece in listeTypesPiecesTmp :
            typePiece = (IDtype_piece, nom_piece, FormatDuree(duree_validite), CompteDeIDpiece)
            listeTypesPieces.append(typePiece)
            
        self.nbreLignes = len(listeTypesPieces)

        # Recherche les dipl�mes associ�s
        DB = GestionDB.DB()
        req = """
        SELECT *
        FROM diplomes_pieces LEFT JOIN types_diplomes ON diplomes_pieces.IDtype_diplome = types_diplomes.IDtype_diplome;
        """
        DB.ExecuterReq(req)
        listeDiplomes = DB.ResultatReq()
        DB.Close()

        # Ajoute les diplomes associ�s � la liste des types de pi�ces
        dictAssociations = {} # key = IDtype_diplome | valeur = nom_diplome

        index = 0
        for piece in listeTypesPieces:
            IDtype_piece = piece[0]
            dictAssociations[IDtype_piece] = []

            for diplome in listeDiplomes:
                if diplome[2] == IDtype_piece:
                    listeValeurs = dictAssociations[IDtype_piece]
                    listeValeurs.append(diplome[4])
                    dictAssociations[IDtype_piece] = listeValeurs

            # Formatage du r�sultat
            valeurs = dictAssociations[IDtype_piece]
            nbreValeurs = len(valeurs)

            texte = ""
            if nbreValeurs == 0:
                texte = _(u"Pour tous les employ�s")
            else:
                for index2 in range(nbreValeurs):
                    valeur = valeurs[index2]
                    if valeur == None:
                        texte = _(u"Pour tous les employ�s - ")
                    else:
                        texte = texte + valeur + " - "

                texte = texte[:-3]           
            
            # Int�gration dans la liste de valeurs pour le ListCtrl
            ancListe = listeTypesPieces[index]
            newListe = list(ancListe)
            newListe.append(texte)
            listeTypesPieces[index] = newListe

            index += 1
            


        # Cr�ation du dictionnaire de donn�es
        self.donnees = self.listeEnDict(listeTypesPieces)



    def MAJListeCtrl(self):
        self.ClearAll()
        self.Remplissage()
        self.resizeLastColumn(0)
        listmix.ColumnSorterMixin.__init__(self, self.nbreColonnes)

    def listeEnDict(self, liste):
        dictio = {}
        x = 1
        for ligne in liste:
            index = x # Donne un entier comme cl�
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
        valeur = six.text_type(self.itemDataMap[index][col])
        return valeur

    def OnGetItemImage(self, item):
        """ Affichage des images en d�but de ligne """
        return -1

    def OnGetItemAttr(self, item):
        """ Application d'une couleur de fond pour une ligne sur deux """
        # Cr�ation d'une ligne de couleur 1 ligne sur 2
        if item % 2 == 1:
            return self.attr1
        else:
            return None
       
    #-----------------------------------------------------------
    # Matt C, 2006/02/22
    # Here's a better SortItems() method --
    # the ColumnSorterMixin.__ColumnSorter() method already handles the ascending/descending,
    # and it knows to sort on another column if the chosen columns have the same value.

    def SortItems(self,sorter=FonctionsPerso.cmp):
        items = list(self.itemDataMap.keys())
        items = FonctionsPerso.SortItems(items, sorter)
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
        
        # Cr�ation du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

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


class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX)
        self.parent = parent

        self.panel_base = wx.Panel(self, -1)
        self.panel_contenu = Panel(self.panel_base)
        self.panel_contenu.barreTitre.Show(False)
        self.bouton_aide = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Fermer"), cheminImage=Chemins.GetStaticPath("Images/32x32/Fermer.png"))
        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.Onbouton_aide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_annuler, self.bouton_fermer)

    def __set_properties(self):
        self.SetTitle(_(u"Gestion des types de pi�ces"))
        self.bouton_aide.SetToolTip(wx.ToolTip("Cliquez ici pour obtenir de l'aide"))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez pour annuler et fermer")))
        self.SetMinSize((800, 600))

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)
        sizer_pages = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base.Add(sizer_pages, 1, wx.ALL | wx.EXPAND, 0)
        sizer_pages.Add(self.panel_contenu, 1, wx.EXPAND | wx.TOP, 10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.BOTTOM | wx.RIGHT | wx.EXPAND, 10)
        self.panel_base.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        sizer_base.Add(self.panel_base, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()
        self.CenterOnScreen()
        self.sizer_pages = sizer_pages

    def Onbouton_aide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Lestypesdepices")

    def Onbouton_annuler(self, event):
        self.EndModal(wx.ID_CANCEL)



if __name__ == "__main__":
    app = wx.App(0)
    dlg = Dialog(None)
    dlg.ShowModal()
    dlg.Destroy()
    app.MainLoop()