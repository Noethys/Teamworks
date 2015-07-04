#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
# Copyright:    (c) 2008-09 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------

from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import wx.lib.mixins.listctrl  as  listmix
import GestionDB
import FonctionsPerso
import datetime
import Saisie_jour_ferie
import wx.lib.agw.hyperlink as Hyperlink




class Hyperlien(Hyperlink.HyperLinkCtrl):
    def __init__(self, parent, id=-1, label="", infobulle="", URL="", size=(-1, -1), pos=(0, 0)):
        Hyperlink.HyperLinkCtrl.__init__(self, parent, id, label, URL=URL, size=size, pos=pos)
        self.parent = parent
        self.URL = URL
        self.AutoBrowse(False)
        self.SetColours("BLUE", "BLUE", "BLUE")
        self.SetUnderlines(False, False, True)
        self.SetBold(False)
        self.EnableRollover(True)
        self.SetToolTip(wx.ToolTip(infobulle))
        self.UpdateLink()
        self.DoPopup(False)
        self.Bind(Hyperlink.EVT_HYPERLINK_LEFT, self.OnLeftLink)
    
    def OnLeftLink(self, event):
        if self.URL == "importation" :
            self.parent.panel_variables.listCtrl.ImportationVariables()
        self.UpdateLink()




class Panel_secondaire(wx.Panel):
    def __init__(self, parent, ID=-1, type="", nomPanel=""):
        wx.Panel.__init__(self, parent, ID, name=nomPanel, style=wx.TAB_TRAVERSAL)
        
        self.typeJour = type
        self.listCtrl = ListCtrl(self)
        self.listCtrl.SetMinSize((20, 20)) 
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_modifier= wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Aide.png", wx.BITMAP_TYPE_ANY))
        if parent.GetParent().GetName() != "treebook_configuration" :
            self.bouton_aide.Show(False)

        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)

        self.bouton_modifier.Enable(False)
        self.bouton_supprimer.Enable(False)

        
    def __set_properties(self):
        self.bouton_ajouter.SetToolTipString(_(u"Cliquez ici pour créer un nouveau jour férié"))
        self.bouton_ajouter.SetSize(self.bouton_ajouter.GetBestSize())
        self.bouton_modifier.SetToolTipString(_(u"Cliquez ici pour modifier le jour férié sélectionné dans la liste"))
        self.bouton_modifier.SetSize(self.bouton_modifier.GetBestSize())
        self.bouton_supprimer.SetToolTipString(_(u"Cliquez ici pour supprimer le jour férié sélectionné dans la liste"))
        self.bouton_supprimer.SetSize(self.bouton_supprimer.GetBestSize())
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_base2 = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_boutons = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=10)
        grid_sizer_base2.Add(self.listCtrl, 1, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_boutons.Add((5, 5), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.AddGrowableRow(3)
        grid_sizer_base2.Add(grid_sizer_boutons, 1, wx.EXPAND, 0)
        grid_sizer_base2.AddGrowableRow(0)
        grid_sizer_base2.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_base2, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
##        sizer_legende = wx.BoxSizer(wx.HORIZONTAL)
##        grid_sizer_base.Add(sizer_legende, 0, 0, 0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.SetAutoLayout(True)
        
        
    def OnBoutonAjouter(self, event):
        self.Ajouter()

    def Ajouter(self):
        frmSaisie = Saisie_jour_ferie.MyFrame(self, _(u"Saisie d'un jour férié"), IDferie=0, type=self.typeJour)
        frmSaisie.Show()

    def OnBoutonModifier(self, event):
        self.Modifier()

    def Modifier(self):
        index = self.listCtrl.GetFirstSelected()
        if index == -1:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un jour férié à modifier dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        ID = int(self.listCtrl.GetItem(index, 0).GetText())
        frmSaisie = Saisie_jour_ferie.MyFrame(self, _(u"Modification d'un jour férié"), IDferie=ID, type=self.typeJour)
        frmSaisie.Show()
        
    def OnBoutonSupprimer(self, event):
        self.Supprimer()

    def Supprimer(self):
        index = self.listCtrl.GetFirstSelected()

        # Vérifie qu'un item a bien été sélectionné
        if index == -1:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un jour férié à supprimer dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Demande de confirmation
        ID = int(self.listCtrl.GetItem(index, 0).GetText())
        Nom = self.listCtrl.GetItem(index, 2).GetText() + " (" + self.listCtrl.GetItem(index, 1).GetText() + ")"
        txtMessage = unicode((_(u"Voulez-vous vraiment supprimer ce jour férié ? \n\n> ") + Nom))
        dlgConfirm = wx.MessageDialog(self, txtMessage, _(u"Confirmation de suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        
        # Suppression du type de pièce
        DB = GestionDB.DB()
        DB.ReqDEL("jours_feries", "IDferie", ID)

        # MàJ du ListCtrl
        self.listCtrl.MAJListeCtrl()
        
    def MAJ_ListCtrl(self):
        self.listCtrl.MAJListeCtrl() 

    def OnBoutonAide(self, event):
        FonctionsPerso.Aide(34)



class ListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin, listmix.ColumnSorterMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__( self, parent, -1, style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        
        self.criteres = ""
        self.parent = parent

        # Initialisation des images
        tailleIcones = 16
        self.il = wx.ImageList(tailleIcones, tailleIcones)
        self.imgTriAz= self.il.Add(wx.Bitmap("Images/16x16/Tri_az.png", wx.BITMAP_TYPE_PNG))
        self.imgTriZa= self.il.Add(wx.Bitmap("Images/16x16/Tri_za.png", wx.BITMAP_TYPE_PNG))
        self.imgActuel = self.il.Add(wx.Bitmap("Images/16x16/Ok.png", wx.BITMAP_TYPE_PNG))
        self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

        #adding some attributes (colourful background for each item rows)
        self.attr1 = wx.ListItemAttr()
        self.attr1.SetBackgroundColour("#EEF4FB") # Vert = #F0FBED

        # Remplissage du ListCtrl
        if self.GetGrandParent().GetParent().GetName() != "treebook_configuration" :
            self.Remplissage()
        
        #events
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)
        #self.Bind(wx.EVT_SIZE, self.OnSize)

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
        self.InsertColumn(1, _(u"Nom"))
        self.SetColumnWidth(1, 200)  
        self.InsertColumn(2, _(u"Date"))
        self.SetColumnWidth(2, 100)  

        
        #These two should probably be passed to init more cleanly
        #setting the numbers of items = number of elements in the dictionary
        self.itemDataMap = self.donnees
        self.itemIndexMap = self.donnees.keys()
        self.SetItemCount(self.nbreLignes)
        
        #mixins
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        listmix.ColumnSorterMixin.__init__(self, self.nbreColonnes)

        #sort by genre (column 1), A->Z ascending order (1)
        self.SortListItems(2, 0)

    def OnItemSelected(self, event):
        self.parent.bouton_modifier.Enable(True)
        self.parent.bouton_supprimer.Enable(True)
        
    def OnItemDeselected(self, event):
        self.parent.bouton_modifier.Enable(False)
        self.parent.bouton_supprimer.Enable(False)
        
    def Importation(self):
        # Récupération des données
        DB = GestionDB.DB()        
        req = """SELECT IDferie, nom, jour, mois, annee
        FROM jours_feries WHERE type='%s'; """ % self.parent.typeJour
        DB.ExecuterReq(req)
        liste = DB.ResultatReq()
        DB.Close()
        self.nbreLignes = len(liste)
        # Modification des données
        nouvelleListe = []
        for IDferie, nom, jour, mois, annee in liste :
            if self.parent.typeJour == "fixe" :
                if mois <10 : 
                    mois = str("0") + str(mois)
                else : 
                    mois = str(mois)
                date = mois + "-" + str(jour)
                nouvelleListe.append( (IDferie, nom, date) )
            else:
                date = str(annee) + "-" + str(mois) + "-" + str(jour)
                nouvelleListe.append( (IDferie, nom, date) )
        # Création du dictionnaire de données
        self.donnees = self.listeEnDict(nouvelleListe)
        
    def dateEnDateComplet(self, jour, mois, annee):
        """ Transforme le format "aaaa-mm-jj" en "mercredi 12 septembre 2008" """
        listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
        listeJours = (_(u"lundi"), _(u"mardi"), _(u"mercredi"), _(u"jeudi"), _(u"vendredi"), _(u"samedi"), _(u"dimanche"))
        jourSemaine = int(datetime.date(annee, mois, jour).strftime("%w"))
        texte = listeJours[jourSemaine-1] + " " + str(jour) + " " + listeMois[mois-1] + " " + str(annee)
        return texte
            
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
        if col == 2 :
            # Formate les dates pour l'affichage :
            listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
            if self.parent.typeJour == "fixe" :
                mois, jour = valeur.split("-")
                valeur = "Le " + str(jour) +  " " + listeMois[int(mois)-1]
            else:
                annee, mois, jour = valeur.split("-")
                valeur = "Le " + self.dateEnDateComplet(int(jour), int(mois), int(annee))
        return valeur

    def dateEnStr(self, texteDate):
        """ Transforme le format "aaaa-mm-jj" en "mercredi 12 septembre 2008" """
        listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
        listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
        jour = int(texteDate[8:10])
        mois = int(texteDate[5:7])
        annee = int(texteDate[:4])
        jourSemaine = int(datetime.date(annee, mois, jour).strftime("%w"))
        texte = listeJours[jourSemaine-1] + " " + str(jour) + " " + listeMois[mois-1] + " " + str(annee)

        return texte

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
        bmp = wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Ajouter, id=10)
        
        menuPop.AppendSeparator()

        # Item Ajouter
        item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
        bmp = wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Modifier, id=20)

        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
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
    
    def ImportationVariables(self):
        import DLG_Saisie_feries_auto
        dlg = DLG_Saisie_feries_auto.MyDialog(self)
        if dlg.ShowModal() == wx.ID_OK :
            self.MAJListeCtrl()
        dlg.Destroy()




class Panel(wx.Panel):
    def __init__(self, parent, ID=-1):
        wx.Panel.__init__(self, parent, ID, name="panel_config_jours_feries", style=wx.TAB_TRAVERSAL)
        
        self.barreTitre = FonctionsPerso.BarreTitre(self,  _(u"Les jours fériés"), u"")
        texteIntro = _(u"Vous pouvez ici créer, modifier ou supprimer les jours fériés qui s'affichent dans les calendriers.")
        self.label_introduction = FonctionsPerso.StaticWrapText(self, -1, texteIntro)
        
        self.staticbox_fixes_staticbox = wx.StaticBox(self, -1, _(u"Les jours fériés fixes"))
        self.staticbox_variables_staticbox = wx.StaticBox(self, -1, _(u"Les jours fériés variables"))
        
        self.panel_variables = Panel_secondaire(self, -1, type="variable", nomPanel="Config_jours_feries_variable")
        self.panel_fixes = Panel_secondaire(self, -1, type="fixe", nomPanel="Config_jours_feries_fixe") 

        self.hyper_importation = Hyperlien(self, label=_(u"Calcul automatique des jours variables"), infobulle=_(u"Cliquez ici pour laisser Teamworks calculer les jours fériés variables"), URL="importation")

        # Layout
        grid_sizer_principal = wx.FlexGridSizer(rows=4, cols=1, vgap=0, hgap=0)
        grid_sizer_principal.Add(self.barreTitre, 1, wx.EXPAND, 0)
        grid_sizer_principal.Add(self.label_introduction, 1, wx.ALL|wx.EXPAND, 10)
        
        staticbox_variables = wx.StaticBoxSizer(self.staticbox_variables_staticbox, wx.VERTICAL)
        staticbox_variables.Add(self.panel_variables, 1, wx.EXPAND|wx.TOP, 10)
        staticbox_variables.Add( (3, 3), 0, 0, 0)
        staticbox_variables.Add(self.hyper_importation, 0, wx.LEFT|wx.RIGHT, 10)
        staticbox_variables.Add( (3, 3), 0, 0, 0)
        grid_sizer_principal.Add(staticbox_variables, 1, wx.ALL|wx.EXPAND, 10)
        
        staticbox_fixes = wx.StaticBoxSizer(self.staticbox_fixes_staticbox, wx.VERTICAL)
        staticbox_fixes.Add(self.panel_fixes, 1, wx.EXPAND|wx.TOP|wx.BOTTOM, 10)
        grid_sizer_principal.Add(staticbox_fixes, 1, wx.ALL|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_principal)
        grid_sizer_principal.Fit(self)
        grid_sizer_principal.AddGrowableRow(2)
        grid_sizer_principal.AddGrowableRow(3)
        grid_sizer_principal.AddGrowableCol(0)
        
        self.grid_sizer_principal = grid_sizer_principal
        self.staticbox_fixes = staticbox_fixes
        self.staticbox_variables = staticbox_variables
       

    def MAJpanel(self):
        self.panel_variables.listCtrl.MAJListeCtrl() 
        self.panel_fixes.listCtrl.MAJListeCtrl() 
        self.panel_fixes.Layout()
        self.panel_variables.Layout()
        

class MyFrame(wx.Frame):
    def __init__(self, parent, title="" ):
        wx.Frame.__init__(self, parent, -1, title=title, name="frm_config_jours_feries", style=wx.DEFAULT_FRAME_STYLE)
        self.parent = parent
        self.MakeModal(True)
        
        self.panel_base = wx.Panel(self, -1)
        self.panel_contenu = Panel(self.panel_base)
        self.panel_contenu.barreTitre.Show(False)
        self.bouton_aide = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.Onbouton_aide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_ok, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_annuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        self.SetMinSize((550, 500))
        self.SetSize((550, 500))

    def __set_properties(self):
        self.SetTitle(_(u"Gestion des jours fériés"))
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.bouton_aide.SetToolTipString("Cliquez ici pour obtenir de l'aide")
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetToolTipString(_(u"Cliquez pour annuler et fermer"))
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
        self.Layout()
        self.Centre()
        self.sizer_pages = sizer_pages


        
        
    def OnClose(self, event):
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        event.Skip()
        
    def Onbouton_aide(self, event):
        FonctionsPerso.Aide(34)
            
    def Onbouton_annuler(self, event):
        # Si frame Creation_contrats ouverte, on met à jour le listCtrl Valeurs de points
        self.MAJparents()
        # Fermeture
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()
        
    def Onbouton_ok(self, event):
        # Si frame Creation_contrats ouverte, on met à jour le listCtrl Valeurs de points
        self.MAJparents()
        # Fermeture
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()     
        
    def MAJparents(self):
        if FonctionsPerso.FrameOuverte("frm_creation_contrats") != None :
            self.GetParent().MAJ_ListCtrl()
        if FonctionsPerso.FrameOuverte("frm_creation_modele_contrats") != None :
            self.GetParent().MAJ_ListCtrl()            
            
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
