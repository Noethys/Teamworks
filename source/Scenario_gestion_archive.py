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
import GestionDB
import FonctionsPerso
import datetime
from ObjectListView import GroupListView, ColumnDefn
import Scenario


try: import psyco; psyco.full()
except: pass

DICT_PERSONNES = {}

class Panel(wx.Panel):
    def __init__(self, parent, ID=-1, IDpersonne=None):
        wx.Panel.__init__(self, parent, ID, name="gestion_scenarios", style=wx.TAB_TRAVERSAL)
        self.IDpersonne = IDpersonne
        texteIntro = _(u"Vous pouvez ici créer, modifier ou supprimer des scénarios.")
        self.label_introduction = FonctionsPerso.StaticWrapText(self, -1, texteIntro)
        
        self.listCtrl = ListView(self, IDpersonne=IDpersonne)
        
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap("Images\\16x16\\Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap("Images\\16x16\\Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap("Images\\16x16\\Supprimer.png", wx.BITMAP_TYPE_ANY))
##        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap("Images\\16x16\\Aide.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
##        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)

        self.bouton_modifier.Enable(False)
        self.bouton_supprimer.Enable(False)
        
    def __set_properties(self):
        self.bouton_ajouter.SetToolTipString(_(u"Cliquez ici pour créer un nouveau scénario"))
        self.bouton_ajouter.SetSize(self.bouton_ajouter.GetBestSize())
        self.bouton_modifier.SetToolTipString(_(u"Cliquez ici pour modifier le scénario sélectionné dans la liste"))
        self.bouton_modifier.SetSize(self.bouton_modifier.GetBestSize())
        self.bouton_supprimer.SetToolTipString(_(u"Cliquez ici pour supprimer le scénario sélectionné dans la liste"))
        self.bouton_supprimer.SetSize(self.bouton_supprimer.GetBestSize())
##        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_base2 = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_boutons = wx.FlexGridSizer(rows=4, cols=1, vgap=5, hgap=10)
        grid_sizer_base.Add(self.label_introduction, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        grid_sizer_base2.Add(self.listCtrl, 1, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_boutons.Add((5, 5), 0, 0, 0)
##        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.AddGrowableRow(3)
        grid_sizer_base2.Add(grid_sizer_boutons, 1, wx.EXPAND, 0)
        grid_sizer_base2.AddGrowableRow(0)
        grid_sizer_base2.AddGrowableCol(0)
        if self.GetGrandParent().GetName() == "frm_gestion_scenarios" :
            grid_sizer_base.Add(grid_sizer_base2, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        else:
            grid_sizer_base.Add(grid_sizer_base2, 1, wx.EXPAND, 0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.SetAutoLayout(True)

    def OnBoutonAjouter(self, event):
        self.Ajouter()

    def Ajouter(self):
        frmSaisie = Scenario.MyFrame(self, IDscenario=None, IDpersonne=self.IDpersonne)
        frmSaisie.Show()

    def OnBoutonModifier(self, event):
        self.Modifier()

    def Modifier(self):
        IDscenario = self.listCtrl.GetSelection()
        if IDscenario == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un scénario à modifier dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        frmSaisie = Scenario.MyFrame(self, IDscenario=IDscenario, IDpersonne=None)
        frmSaisie.Show()
        
    def OnBoutonSupprimer(self, event):
        self.Supprimer()

    def Supprimer(self):
        IDscenario = self.listCtrl.GetSelection()

        # Vérifie qu'un item a bien été sélectionné
        if IDscenario == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un scénario à supprimer dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Demande de confirmation
        Nom = self.listCtrl.GetNomSelection()
        txtMessage = unicode((_(u"Voulez-vous vraiment supprimer ce scénario ? \n\n> ") + Nom))
        dlgConfirm = wx.MessageDialog(self, txtMessage, _(u"Confirmation de suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        
        # Suppression du type de pièce
        DB = GestionDB.DB()
        DB.ReqDEL("scenarios", "IDscenario", IDscenario)
        DB.ReqDEL("scenarios", "IDscenario", IDscenario)
        DB.Close()
        
        # MàJ du ListCtrl
        self.listCtrl.MAJ()
        
    def MAJ_ListCtrl(self, IDselection=None):
        self.listCtrl.MAJ(IDselection) 
        self.listCtrl.SetFocus()

    def MAJpanel(self):
        self.listCtrl.MAJ() 

##    def OnBoutonAide(self, event):
##        FonctionsPerso.Aide(None) # <<<<<<<<< A modifier après rédaction de l'aide





# ---------------------------------------- LISTVIEW DATES -----------------------------------------------------------------------


class Track(object):
    def __init__(self, donnees):
        self.IDscenario = donnees[0]
        self.IDpersonne = donnees[1]
        self.nom = donnees[2]
        self.description = donnees[3]
        self.date_debut = donnees[4]
        self.date_fin = donnees[5]
        self.periode = "%s;%s" % (self.date_debut, self.date_fin)
        
    def FormateDate(self, dateStr):
            if dateStr == "" : return ""
            date = str(datetime.date(year=int(dateStr[:4]), month=int(dateStr[5:7]), day=int(dateStr[8:10])))
            text = str(date[8:10]) + "/" + str(date[5:7]) + "/" + str(date[:4])
            return text
    
                                
class ListView(GroupListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.IDpersonne = kwds.pop("IDpersonne", None)
        selectionID = kwds.pop("selectionID", None)
        # Initialisation du listCtrl
        GroupListView.__init__(self, *args, **kwds)
        self.selectionID = None
        self.selectionTrack = None
        self.desactiveMAJ = False
        self.GetDictPersonnes()
        self.InitModel()
        self.InitObjectListView()
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)
        
    def OnActivated(self,event):
        self.GetParent().Modifier()

    def OnItemSelected(self, event):
        self.GetParent().bouton_modifier.Enable(True)
        self.GetParent().bouton_supprimer.Enable(True)

    def OnItemDeselected(self, event):
        self.GetParent().bouton_modifier.Enable(False)
        self.GetParent().bouton_supprimer.Enable(False)

    def InitModel(self):
        self.donnees = self.GetTracks()
            
    def GetTracks(self):
        DB = GestionDB.DB()
        if self.IDpersonne == None : 
            req = "SELECT IDscenario, IDpersonne, nom, description, date_debut, date_fin FROM scenarios ORDER BY date_debut;"
        else:
            req = "SELECT IDscenario, IDpersonne, nom, description, date_debut, date_fin FROM scenarios WHERE IDpersonne=%d ORDER BY date_debut;" % self.IDpersonne
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeListeView = []
        for item in listeDonnees :
            track = Track(item)
            listeListeView.append(track)
            if self.selectionID == item[0] :
                self.selectionTrack = track
        return listeListeView
    
    def GetDictPersonnes(self):
        global DICT_PERSONNES
        DB = GestionDB.DB()
        req = "SELECT IDpersonne, nom, prenom FROM personnes;"
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        DICT_PERSONNES = {}
        for valeurs in listeDonnees :
            DICT_PERSONNES[valeurs[0]] = valeurs

    def FormateDate(self, dateStr):
            if dateStr == "" : return ""
            date = str(datetime.date(year=int(dateStr[:4]), month=int(dateStr[5:7]), day=int(dateStr[8:10])))
            text = str(date[8:10]) + "/" + str(date[5:7]) + "/" + str(date[:4])
            return text
            
    def InitObjectListView(self):
        
        def FormateNomPersonne(IDpersonne):
            IDpersonne, nom, prenom = DICT_PERSONNES[IDpersonne]
            return u"%s %s" % (nom, prenom)
    
        def FormatePeriode(periode):
            date_debut, date_fin = periode.split(";")
            periode = _(u"Du %s au %s") % (self.FormateDate(date_debut), self.FormateDate(date_fin))
            return periode
            
        def GroupKey(track):
            return track.IDpersonne
        
        def GroupKeyConverter(groupKey):
            IDpersonne, nom, prenom = DICT_PERSONNES[groupKey]
            return u"%s %s" % (nom, prenom)
                
        # Couleur en alternance des lignes
        self.useAlternateBackColors = False
##        self.oddRowsBackColor = wx.Colour(255, 255, 255) #"#EEF4FB" # Bleu
##        self.evenRowsBackColor = wx.Colour(255, 255, 255) #"#F0FBED" # Vert
        
        # Paramètres ListView
        self.useExpansionColumn = True
        self.showItemCounts = False
        if self.IDpersonne == None :
            
            # Utilisation en frame
            self.SetColumns([
                ColumnDefn(_(u"Nom du scénario"), "left", 200, "nom"),
                ColumnDefn(_(u"Période"), "left", 165, "periode", stringConverter=FormatePeriode),
                ColumnDefn(_(u"Description"), "left", 600, "description"),
                ColumnDefn(_(u"Personne"), "left", 0, "IDpersonne", groupKeyGetter=GroupKey, groupKeyConverter=GroupKeyConverter, stringConverter=FormateNomPersonne),
            ])
            self.SetSortColumn(self.columns[4])
            self.SetEmptyListMsg(_(u"Aucun scénario enregistré"))
            self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
            self.SetObjects(self.donnees)
            
            # Tri par période
            self.SetAlwaysGroupByColumn(self.GetGroupByColumn())
            self.SortBy(2)
            
        else:
            
            # Utilisation dans la fiche individuelle
            self.SetColumns([
                ColumnDefn(_(u"IDscenario"), "left", 0, "IDscenario"),
                ColumnDefn(_(u"Nom du scénario"), "left", 200, "nom"),
                ColumnDefn(_(u"Période"), "left", 165, "periode", stringConverter=FormatePeriode),
                ColumnDefn(_(u"Description"), "left", 600, "description"),
                ColumnDefn(_(u"Personne"), "left", 0, "IDpersonne", groupKeyGetter=GroupKey, groupKeyConverter=GroupKeyConverter, stringConverter=FormateNomPersonne),
            ])
            self.SetSortColumn(self.columns[5])
            self.SetEmptyListMsg(_(u"Aucun scénario enregistré"))
            self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
            self.SetObjects(self.donnees)
            
            # Tri par période
            self.SetAlwaysGroupByColumn(self.GetGroupByColumn())
            self.SortBy(3)
        
            # Si utilisation du panel dans la fiche ind.
            self.SetShowGroups(False)
        
        
        
    def MAJ(self, selectionID=None):
        if selectionID != None :
            self.selectionID = selectionID
            self.selectionTrack = None
        else:
            self.selectionID = None
            self.selectionTrack = None
        self.InitModel()
        self.InitObjectListView()
        # Sélection d'un item
        if self.selectionTrack != None :
            self.desactiveMAJ = True
            self.SelectObject(self.selectionTrack, deselectOthers=True, ensureVisible=True)
            self.desactiveMAJ = False
        self.selectionID = None
        self.selectionTrack = None

 
    def GetSelection(self):
        if len(self.GetSelectedObjects()) != 0 :
            IDscenario = self.GetSelectedObjects()[0].IDscenario
        else:
            IDscenario = None
        return IDscenario
    
    def GetNomSelection(self):
        if len(self.GetSelectedObjects()) != 0 :
            nomScenario = self.GetSelectedObjects()[0].nom
        else:
            nomScenario = None
        return nomScenario

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        
        if len(self.GetSelectedObjects()) != 0 :
            IDscenario = self.GetSelectedObjects()[0].IDscenario
        else:
            return
        
        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Ajouter
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
        bmp = wx.Bitmap("Images\\16x16\\Ajouter.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.GetParent().OnBoutonAjouter, id=10)

        # Item Modifier
        item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
        bmp = wx.Bitmap("Images\\16x16\\Modifier.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.GetParent().OnBoutonModifier, id=20)
        
        menuPop.AppendSeparator()

        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
        bmp = wx.Bitmap("Images\\16x16\\Supprimer.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.GetParent().OnBoutonSupprimer, id=30)
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()
        
        





class MyFrame(wx.Frame):
    def __init__(self, parent, title="" ):
        wx.Frame.__init__(self, parent, -1, title=title, name="frm_gestion_scenarios", style=wx.DEFAULT_FRAME_STYLE)
        self.parent = parent
        self.MakeModal(True)
        
        self.panel_base = wx.Panel(self, -1)
        self.panel_contenu = Panel(self.panel_base, IDpersonne=None)

        self.bouton_aide = wx.BitmapButton(self.panel_base, -1, wx.Bitmap("Images\\BoutonsImages\\Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_fermer = wx.BitmapButton(self.panel_base, -1, wx.Bitmap("Images\\BoutonsImages\\Fermer_L72.png", wx.BITMAP_TYPE_ANY))
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.Onbouton_aide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_fermer, self.bouton_fermer)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        

    def __set_properties(self):
        self.SetTitle(_(u"Gestion des scénarios"))
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap("Images\\16x16\\Logo.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.bouton_aide.SetToolTipString("Cliquez ici pour obtenir de l'aide")
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_fermer.SetToolTipString(_(u"Cliquez ici pour fermer"))
        self.bouton_fermer.SetSize(self.bouton_fermer.GetBestSize())        

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        sizer_pages = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base.Add(sizer_pages, 1, wx.ALL|wx.EXPAND, 0)
        sizer_pages.Add(self.panel_contenu, 1, wx.EXPAND | wx.TOP, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND, 10)
        self.panel_base.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        sizer_base.Add(self.panel_base, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        self.Layout()
        
        self.SetMinSize((450, 350))
        self.SetSize((800, 600))
        
        self.CentreOnScreen()
        self.sizer_pages = sizer_pages

    def OnClose(self, event):
        # Si frame Creation_contrats ouverte, on met à jour le listCtrl Valeurs de points
##        self.MAJparents()
        # Fermeture
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        event.Skip()
        
    def Onbouton_aide(self, event):
        FonctionsPerso.Aide(None)
                
    def Onbouton_fermer(self, event):
        # Si frame Creation_contrats ouverte, on met à jour le listCtrl Valeurs de points
##        self.MAJparents()
        # Fermeture
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()     
        
##    def MAJparents(self):
##        if FonctionsPerso.FrameOuverte("frm_creation_contrats") != None :
##            self.GetParent().MAJ_ListCtrl()
##        if FonctionsPerso.FrameOuverte("frm_creation_modele_contrats") != None :
##            self.GetParent().MAJ_ListCtrl()            




if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
