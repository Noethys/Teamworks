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
import SaisieTypesPieces
import FonctionsPerso


def FormatDuree(duree):

    posM = duree.find("m")
    posA = duree.find("a")
    jours = int(duree[1:posM-1])
    mois = int(duree[posM+1:posA-1])
    annees = int(duree[posA+1:])
    
    listItems = []
    if jours == 1:
        textJours = u"%d jour" % jours
        listItems.append(textJours)
    if jours > 1:
        textJours = u"%d jours" % jours
        listItems.append(textJours)
    if mois > 0:
        textMois = u"%d mois" % mois
        listItems.append(textMois)
    if annees == 1:
        textAnnees = u"%d ann�e" % annees
        listItems.append(textAnnees)
    if annees > 1:
        textAnnees = u"%d ann�es" % annees
        listItems.append(textAnnees)

    nbreItems = len(listItems)
    if nbreItems == 0:
        resultat = u"Validit� illimit�e"
    else:
        if nbreItems == 1:
            resultat = listItems[0]
        if nbreItems == 2:
            resultat = listItems[0] + " et " + listItems[1]
        if nbreItems == 3:
            resultat = listItems[0] + ", " + listItems[1] + " et " + listItems[2]

    return resultat
    

class Panel_TypesPieces(wx.Panel):
    def __init__(self, parent, ID=-1):
        wx.Panel.__init__(self, parent, ID, style=wx.TAB_TRAVERSAL)
        
        self.barreTitre = FonctionsPerso.BarreTitre(self,  u"Les types de pi�ces", u"")
        texteIntro = u"Vous pouvez ici ajouter, modifier ou supprimer des types de pi�ces. Ce sont les documents que les employ�s doivent vous communiquer. Celles-ci peuvent �tre obligatoire pour tous (Exemple : 'Certificat m�dical'...) ou �tre obligatoire en fonction du dipl�me d�tenu par la personne (Exemple, si une personne a le dipl�me 'A.F.P.S.', elle devra donner la pi�ce 'Dipl�me A.F.P.S.'). Vous devez pr�ciser une dur�e de validit� par d�faut pour chaque pi�ce."
        self.label_introduction = FonctionsPerso.StaticWrapText(self, -1, texteIntro)
        
        self.listCtrl_TypesPieces = ListCtrlTypesPieces(self)
        self.listCtrl_TypesPieces.SetMinSize((20, 20)) 
        
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Aide.png", wx.BITMAP_TYPE_ANY))

##        self.label_conclusion = wx.StaticText(self, -1, "Remarques...")

        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        
    def __set_properties(self):
        self.bouton_ajouter.SetToolTipString(u"Cliquez ici pour cr�er un nouveau type de pi�ce")
        self.bouton_ajouter.SetSize(self.bouton_ajouter.GetBestSize())
        self.bouton_modifier.SetToolTipString(u"Cliquez ici pour modifier un type de pi�ce s�lectionn� dans la liste")
        self.bouton_modifier.SetSize(self.bouton_modifier.GetBestSize())
        self.bouton_supprimer.SetToolTipString(u"Cliquez ici pour supprimer un type de pi�ce s�lectionn� dans la liste")
        self.bouton_supprimer.SetSize(self.bouton_supprimer.GetBestSize())
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        
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

        

    def OnBoutonAjouter(self, event):
        self.Ajouter()

    def Ajouter(self):
        """ Cr�er un nouveau type de pi�ce """
        frame_saisieTypesPieces = SaisieTypesPieces.Frm_SaisieTypesPieces(self, -1, IDtype_piece=0)
        frame_saisieTypesPieces.Show()

    def OnBoutonModifier(self, event):
        self.Modifier()

    def Modifier(self):
        """ Modification d'un type de pi�ce """
        index = self.listCtrl_TypesPieces.GetFirstSelected()
        if index == -1:
            dlg = wx.MessageDialog(self, u"Vous devez d'abord s�lectionner un type de pi�ce � modifier dans la liste.", "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Avertissement si cette pi�ce a d�j� �t� attribu�e � aucune personne
        nbreTitulaires = int(self.listCtrl_TypesPieces.GetItem(index, 3).GetText())
        if nbreTitulaires != 0:
            message =u"Avertissement : Ce type de pi�ce a d�j� �t� attribu� a " + str(nbreTitulaires) + u" personne(s). Toute modification sera donc r�percut�e en cascade sur toutes les fiches des personnes � qui ce type de pi�ce a �t� attribu�. \n\nSouhaitez-vous quand m�me modifier ce type de pi�ce ?"
            dlg = wx.MessageDialog(self, message, "Information", wx.YES_NO|wx.NO_DEFAULT|wx.ICON_INFORMATION)
            reponse = dlg.ShowModal()
            if reponse == wx.ID_NO:
                dlg.Destroy()
                return
            else:
                dlg.Destroy()
        
        varIDtype_piece = int(self.listCtrl_TypesPieces.GetItem(index, 0).GetText())
        frame_saisieTypesPieces = SaisieTypesPieces.Frm_SaisieTypesPieces(self, -1, IDtype_piece=varIDtype_piece)
        frame_saisieTypesPieces.Show()
        
    def OnBoutonSupprimer(self, event):
        self.Supprimer()

    def Supprimer(self):
        """ Suppression d'une coordonn�e """
        index = self.listCtrl_TypesPieces.GetFirstSelected()

        # V�rifie qu'un item a bien �t� s�lectionn�
        if index == -1:
            dlg = wx.MessageDialog(self, u"Vous devez d'abord s�lectionner une pi�ce � supprimer dans la liste.", "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # V�rifie que cette pi�ce n'est attribu�e � aucune personne
        nbreTitulaires = int(self.listCtrl_TypesPieces.GetItem(index, 3).GetText())
        if nbreTitulaires != 0:
            dlg = wx.MessageDialog(self, u"Pour des raisons de s�curit� des donn�es, vous ne pouvez pas supprimer un type de pi�ce qui a d�j� �t� attribu� � des personnes.\n\nSi vous voulez vraiment le supprimer, vous devez d'abord supprimer les pi�ces ayant ce nom sur chaque fiche individuelle concern�e.", "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Demande de confirmation
        IDtype_piece = int(self.listCtrl_TypesPieces.GetItem(index, 0).GetText())
        NomPiece = self.listCtrl_TypesPieces.GetItem(index, 1).GetText()
        txtMessage = unicode((u"Voulez-vous vraiment supprimer ce type de pi�ce ? \n\n> " + NomPiece))
        dlgConfirm = wx.MessageDialog(self, txtMessage, u"Confirmation de suppression", wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        
        # Suppression du type de pi�ce
        DB = GestionDB.DB()
        DB.ReqDEL("types_pieces", "IDtype_piece", IDtype_piece)

        # Suppression des associations avec les dipl�mes
        DB = GestionDB.DB()
        DB.ReqDEL("diplomes_pieces", "IDtype_piece", IDtype_piece)

        # M�J du listCtrl Coords de la fiche individuelle
        self.listCtrl_TypesPieces.MAJListeCtrl()
    
    def MAJpanel(self):
        self.listCtrl_TypesPieces.MAJListeCtrl()
        
    def OnBoutonAide(self, event):
        FonctionsPerso.Aide(16)
        
                

class ListCtrlTypesPieces(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin, listmix.ColumnSorterMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__( self, parent, -1, style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        
        self.criteres = ""
        self.parent = parent

        # Initialisation des images
        tailleIcones = 16
        self.il = wx.ImageList(tailleIcones, tailleIcones)
        self.imgTriAz= self.il.Add(wx.Bitmap("Images/16x16/Tri_az.png", wx.BITMAP_TYPE_PNG))
        self.imgTriZa= self.il.Add(wx.Bitmap("Images/16x16/Tri_za.png", wx.BITMAP_TYPE_PNG))
        self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

        #adding some attributes (colourful background for each item rows)
        self.attr1 = wx.ListItemAttr()
        self.attr1.SetBackgroundColour("#EEF4FB") # Vert = #F0FBED

        # Remplissage du ListCtrl
        if self.GetGrandParent().GetName() != "treebook_configuration" :
            self.Remplissage()

    def OnSize(self, event):
        self.Refresh()
        print "Refresh du ListCtrl"
        event.Skip()

    def Remplissage(self):
        
        # R�cup�ration des donn�es dans la base de donn�es
        self.Importation()
        
        # Cr�ation des colonnes
        self.nbreColonnes = 5
        self.InsertColumn(0, u"     ID")
        self.SetColumnWidth(0, 0)
        self.InsertColumn(1, u"Nom de la pi�ce")
        self.SetColumnWidth(1, 200)
        self.InsertColumn(2, u"Dur�e de validit�")
        self.SetColumnWidth(2, 150)
        self.InsertColumn(3, u"Nb titulaires")
        self.SetColumnWidth(3, 80)
        self.InsertColumn(4, u"Dipl�mes associ�s")
        self.SetColumnWidth(4, 300)
        

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
      
        # R�cup�ration des donn�es de la table TYPES_PIECES
        DB = GestionDB.DB()
        if DB.echec == 1 : 
            self.nbreLignes = 0
            self.donnees = {}
            return
        
        # Le code ci-dessous fonctionne avec SQLITE mais pas avec MySQL :
##        DB.baseDonn.create_function("FormatDuree", 1, FormatDuree)
##        req = """SELECT types_pieces.IDtype_piece, types_pieces.nom_piece, FormatDuree(types_pieces.duree_validite), Count(pieces.IDpiece) AS CompteDeIDpiece
##        FROM types_pieces LEFT JOIN pieces ON types_pieces.IDtype_piece = pieces.IDtype_piece
##        GROUP BY types_pieces.IDtype_piece, types_pieces.nom_piece, types_pieces.duree_validite %s;
##        """ % self.criteres
##        DB.ExecuterReq(req)
##        listeTypesPieces = DB.ResultatReq()
##        DB.Close()

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
                texte = u"Pour tous les employ�s"
            else:
                for index2 in range(nbreValeurs):
                    valeur = valeurs[index2]
                    if valeur == None:
                        texte = u"Pour tous les employ�s - "
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
        valeur = unicode(self.itemDataMap[index][col])
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
        
        # Cr�ation du menu contextuel
        menuPop = wx.Menu()

        # Item Modifier
        item = wx.MenuItem(menuPop, 10, u"Ajouter")
        bmp = wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Ajouter, id=10)
        
        menuPop.AppendSeparator()

        # Item Ajouter
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
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Menu_Ajouter(self, event):
        self.parent.Ajouter()
        
    def Menu_Modifier(self, event):
        self.parent.Modifier()

    def Menu_Supprimer(self, event):
        self.parent.Supprimer()
