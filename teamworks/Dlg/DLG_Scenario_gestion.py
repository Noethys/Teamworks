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
import datetime
import wx.gizmos as gizmos
import wx.lib.agw.hypertreelist as HTL
from Dlg import DLG_Scenario
from Utils import UTILS_Adaptations



DICT_PERSONNES = {}

class Panel(wx.Panel):
    def __init__(self, parent, ID=-1, IDpersonne=None):
        wx.Panel.__init__(self, parent, ID, name="gestion_scenarios", style=wx.TAB_TRAVERSAL)
        self.IDpersonne = IDpersonne
        texteIntro = _(u"Vous pouvez ici créer, modifier ou supprimer des scénarios.")
        self.label_introduction = FonctionsPerso.StaticWrapText(self, -1, texteIntro)

        if 'phoenix' in wx.PlatformInfo:
            TR_COLUMN_LINES = HTL.TR_COLUMN_LINES
        else :
            TR_COLUMN_LINES = wx.TR_COLUMN_LINES

        if IDpersonne == None :
            style = wx.BORDER_THEME | wx.TR_FULL_ROW_HIGHLIGHT  | TR_COLUMN_LINES | wx.TR_HAS_BUTTONS | wx.TR_HIDE_ROOT | wx.TR_SINGLE
        else:
            style = wx.BORDER_THEME | wx.TR_FULL_ROW_HIGHLIGHT  | TR_COLUMN_LINES | wx.TR_HIDE_ROOT | wx.TR_SINGLE
        self.listCtrl = TreeListCtrl(self, -1, IDpersonne=IDpersonne, style=style)
        self.listCtrl.SetMinSize((20, 20))        
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_dupliquer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Dupliquer.png"), wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonDupliquer, self.bouton_dupliquer)

        
    def __set_properties(self):
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour créer un nouveau scénario")))
        self.bouton_ajouter.SetSize(self.bouton_ajouter.GetBestSize())
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier le scénario sélectionné dans la liste")))
        self.bouton_modifier.SetSize(self.bouton_modifier.GetBestSize())
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer le scénario sélectionné dans la liste")))
        self.bouton_supprimer.SetSize(self.bouton_supprimer.GetBestSize())
        self.bouton_dupliquer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour dupliquer le scénario sélectionné")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_base2 = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_boutons = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=10)
        grid_sizer_base.Add(self.label_introduction, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        grid_sizer_base2.Add(self.listCtrl, 1, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_boutons.Add((5, 5), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_dupliquer, 0, 0, 0)
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
        dlg = DLG_Scenario.Dialog(self, IDscenario=None, IDpersonne=self.IDpersonne)
        dlg.ShowModal()
        dlg.Destroy()

    def OnBoutonModifier(self, event):
        self.Modifier()

    def Modifier(self):
        item = self.listCtrl.GetSelection()
        IDscenario = self.listCtrl.GetPyData(item)

        # Vérifie qu'un item a bien été sélectionné
        if IDscenario > 100000 or IDscenario == None or IDscenario == -1 :
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un scénario à modifier dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        dlg = DLG_Scenario.Dialog(self, IDscenario=IDscenario, IDpersonne=self.IDpersonne)
        dlg.ShowModal()
        dlg.Destroy()
        
    def OnBoutonSupprimer(self, event):
        self.Supprimer()

    def Supprimer(self):
        item = self.listCtrl.GetSelection()
        IDscenario = self.listCtrl.GetPyData(item)

        # Vérifie qu'un item a bien été sélectionné
        if IDscenario > 100000 or IDscenario == None or IDscenario == -1 :
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un scénario à supprimer dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Vérifie si un report utilise ce scénario
        DB = GestionDB.DB()
        req = "SELECT IDscenario_cat, IDscenario, IDcategorie, prevision, report, date_debut_realise, date_fin_realise FROM scenarios_cat;"
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        nbreReports = 0
        for IDscenario_cat, IDscenarioTmp, IDcategorie, prevision, report, date_debut_realise, date_fin_realise in listeDonnees :
            if report != "" and report != None :
                if report[0] == "A" :
                    IDscenarioReport, IDcategorie = report[1:].split(";")
                    if int(IDscenarioReport) == IDscenario :
                        nbreReports += 1
        
        if nbreReports > 0 :
            if nbreReports == 1 : txtMessage = six.text_type(_(u"Un report utilise ce scénario.\n\nSouhaitez-vous tout de même le supprimer ?"))
            else : txtMessage = six.text_type(_(u"%d reports utilisent ce scénario.\n\nSouhaitez-vous tout de même le supprimer ?") % nbreReports)
            dlgConfirm = wx.MessageDialog(self, txtMessage, _(u"Confirmation de suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
            reponse = dlgConfirm.ShowModal()
            dlgConfirm.Destroy()
            if reponse == wx.ID_NO:
                return
        
        # Demande de confirmation
        Nom = self.listCtrl.GetItemText(item)
        txtMessage = six.text_type((_(u"Voulez-vous vraiment supprimer ce scénario ? \n\n> ") + Nom))
        dlgConfirm = wx.MessageDialog(self, txtMessage, _(u"Confirmation de suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        
        # Suppression du type de pièce
        DB = GestionDB.DB()
        DB.ReqDEL("scenarios", "IDscenario", IDscenario)
        DB.ReqDEL("scenarios_cat", "IDscenario", IDscenario)
        DB.Close()
        
        # MàJ du ListCtrl
        self.listCtrl.MAJ()
    
    def OnBoutonDupliquer(self, event):
        item = self.listCtrl.GetSelection()
        IDscenario = self.listCtrl.GetPyData(item)

        # Vérifie qu'un item a bien été sélectionné
        if IDscenario > 100000 or IDscenario == None or IDscenario == -1 :
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un scénario à dupliquer dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Demande de confirmation
        Nom = self.listCtrl.GetItemText(item)
        txtMessage = six.text_type((_(u"Voulez-vous vraiment dupliquer ce scénario ? \n\n> ") + Nom))
        dlgConfirm = wx.MessageDialog(self, txtMessage, _(u"Confirmation de duplication"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        
        # Récupération des données du scénario à dupliquer
        DB = GestionDB.DB()
        req = "SELECT IDpersonne, nom, description, mode_heure, detail_mois, date_debut, date_fin, toutes_categories FROM scenarios WHERE IDscenario=%d ;" % IDscenario
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        
        # Enregistrement du scénario
        for IDpersonne, nom, description, mode_heure, detail_mois, date_debut, date_fin, toutes_categories in listeDonnees :
            listeDonnees = [ ("IDpersonne",   IDpersonne),  
                                        ("nom",   _(u"Copie de %s") % nom),  
                                        ("description",    description),
                                        ("mode_heure",    mode_heure), 
                                        ("detail_mois",    detail_mois),
                                        ("date_debut",    date_debut), 
                                        ("date_fin",    date_fin),
                                        ("toutes_categories",    toutes_categories),
                                         ]
            newIDscenario = DB.ReqInsert("scenarios", listeDonnees) 
            DB.Commit()

        # Enregistrement des catégories de scénarios
        req = "SELECT IDscenario_cat, IDscenario, IDcategorie, prevision, report, date_debut_realise, date_fin_realise FROM scenarios_cat WHERE IDscenario=%d;" % IDscenario
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        
        for IDscenario_cat, IDscenario, IDcategorie, prevision, report, date_debut_realise, date_fin_realise in listeDonnees :
            listeDonnees = [ ("IDscenario",   newIDscenario),  
                                    ("IDcategorie",   IDcategorie),  
                                    ("prevision",    prevision),
                                    ("report",    report), 
                                    ("date_debut_realise",    date_debut_realise),
                                    ("date_fin_realise",    date_fin_realise), 
                                     ]

            IDscenario_cat = DB.ReqInsert("scenarios_cat", listeDonnees) 
            DB.Commit()
        
        DB.Close()
        
        # Ouverture du scénario dans l'éditeur
        frmSaisie = DLG_Scenario.MyFrame(self, IDscenario=newIDscenario, IDpersonne=self.IDpersonne)
        frmSaisie.Show()
            
        
    def MAJ_ListCtrl(self, IDselection=None):
        self.listCtrl.MAJ(IDselection) 
        self.listCtrl.SetFocus()

    def MAJpanel(self):
        self.listCtrl.MAJ() 






class TreeListCtrl(gizmos.TreeListCtrl):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.IDpersonne = kwds.pop("IDpersonne", None)
        self.selectionID = kwds.pop("selectionID", None)
        # Initialisation du listCtrl
        gizmos.TreeListCtrl.__init__(self, *args, **kwds)
        
        self.InitTreeCtrl()
        
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivated)
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.OnContextMenu)   
    
    def InitTreeCtrl(self):
        self.GetDictPersonnes()
        self.dictScenarios = self.GetDictScenarios()
        
        # Création des colonnes
        if self.IDpersonne == None :
            self.AddColumn(_(u"Nom personne / nom scénario"))
            self.SetColumnWidth(0, 250)
        else:
            self.AddColumn(_(u"Nom du scénario"))
            self.SetColumnWidth(0, 200)
        self.AddColumn(_(u"Période"))
        self.SetColumnWidth(1, 160)
        self.AddColumn(_(u"Description"))
        self.SetColumnWidth(2, 400)
        self.SetMainColumn(0) 
        
        # ImageList
        il = wx.ImageList(16, 16)
        self.img_homme  = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Homme.png"), wx.BITMAP_TYPE_PNG))
        self.img_femme  = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Femme.png"), wx.BITMAP_TYPE_PNG))
        self.img_scenario  = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Scenario.png"), wx.BITMAP_TYPE_PNG))
        self.SetImageList(il)
        self.il = il
        
        # Création de la racine
        self.root = self.AddRoot("Racine")
        self.SetItemText(self.root, u"", 1)
        self.SetItemText(self.root, u"", 2)
        self.SetItemImage(self.root, self.img_scenario, wx.TreeItemIcon_Normal)
        self.SetItemImage(self.root, self.img_scenario, wx.TreeItemIcon_Expanded)
        
        # Création des branches
        
        if self.IDpersonne == None :
            listeIDPersonnes = list(self.dictScenarios.keys())
            listeNomsPersonnes = []
            for IDpersonne in listeIDPersonnes :
                IDpersonne, nom, prenom, civilite = DICT_PERSONNES[IDpersonne]
                listeNomsPersonnes.append( (u"%s %s" % (nom, prenom), civilite, IDpersonne) )
            listeNomsPersonnes.sort()
            
            for nomPersonne, civilite, IDpersonne in listeNomsPersonnes :
                child = self.AppendItem(self.root, nomPersonne)
                self.SetItemBold(child, True)
                self.SetItemText(child, "", 1)
                self.SetItemText(child, "", 2)
                self.SetPyData(child, 100000 + IDpersonne)
                if civilite == "Mr" : 
                    image = self.img_homme
                else:
                    image = self.img_femme
                self.SetItemImage(child, image, which = wx.TreeItemIcon_Normal)
                self.SetItemImage(child, image, which = wx.TreeItemIcon_Expanded)
                
                listeScenarios = self.dictScenarios[IDpersonne]
                
                for IDscenario, nom, description, date_debut, date_fin in listeScenarios :
                    last = self.AppendItem(child, nom)
                    periode = _(u"Du %s au %s") % (self.FormateDate(date_debut), self.FormateDate(date_fin))
                    self.SetItemText(last, periode, 1)
                    if description == "" or description == None : description = _(u"Aucune description")
                    self.SetItemText(last, description, 2)
                    self.SetPyData(last, IDscenario)
                    self.SetItemImage(last, self.img_scenario, which = wx.TreeItemIcon_Normal)
                    self.SetItemImage(last, self.img_scenario, which = wx.TreeItemIcon_Expanded)
                    
                    if self.selectionID == IDscenario : 
                        self.EnsureVisible(last)
                        self.SelectItem(last, last, True)
                
                self.Expand(child)
        
        else:
            
            # Version pour fiche individuelle
            if self.IDpersonne in self.dictScenarios :
                listeScenarios = self.dictScenarios[self.IDpersonne]
                for IDscenario, nom, description, date_debut, date_fin in listeScenarios :
                    last = self.AppendItem(self.root, nom)
                    periode = _(u"Du %s au %s") % (self.FormateDate(date_debut), self.FormateDate(date_fin))
                    self.SetItemText(last, periode, 1)
                    if description == "" or description == None : description = _(u"Aucune description")
                    self.SetItemText(last, description, 2)
                    self.SetPyData(last, IDscenario)
                    self.SetItemImage(last, self.img_scenario, which = wx.TreeItemIcon_Normal)
                    self.SetItemImage(last, self.img_scenario, which = wx.TreeItemIcon_Expanded)
                    
                    if self.selectionID == IDscenario : 
                        self.EnsureVisible(last)
                        self.SelectItem(last, last, True)
            
        self.Expand(self.root)

    def MAJ(self, selectionID=None):
        self.DeleteAllItems()
        self.selectionID = selectionID
        self.InitTreeCtrl()
        
    def FormateDate(self, dateStr):
            if dateStr == "" : return ""
            date = str(datetime.date(year=int(dateStr[:4]), month=int(dateStr[5:7]), day=int(dateStr[8:10])))
            text = str(date[8:10]) + "/" + str(date[5:7]) + "/" + str(date[:4])
            return text

    def GetDictScenarios(self):
        DB = GestionDB.DB()
        if self.IDpersonne == None : 
            req = "SELECT IDscenario, IDpersonne, nom, description, date_debut, date_fin FROM scenarios ORDER BY date_debut DESC;"
        else:
            req = "SELECT IDscenario, IDpersonne, nom, description, date_debut, date_fin FROM scenarios WHERE IDpersonne=%d ORDER BY date_debut DESC;" % self.IDpersonne
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        dictScenarios = {}
        for IDscenario, IDpersonne, nom, description, date_debut, date_fin in listeDonnees :
            if IDpersonne in dictScenarios :
                dictScenarios[IDpersonne].append( (IDscenario, nom, description, date_debut, date_fin) )
            else:
                dictScenarios[IDpersonne] = [ (IDscenario, nom, description, date_debut, date_fin), ]
        return dictScenarios

    def GetDictPersonnes(self):
        global DICT_PERSONNES
        DB = GestionDB.DB()
        req = "SELECT IDpersonne, nom, prenom, civilite FROM personnes;"
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        DICT_PERSONNES = {}
        for valeurs in listeDonnees :
            DICT_PERSONNES[valeurs[0]] = valeurs

    def OnActivated(self,event):
        item = self.GetSelection()
        data = self.GetPyData(item)
        if data < 100000 :
            self.GetParent().Modifier()
        else:
            event.Skip()
    
    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        # Recherche et sélection de l'item pointé avec la souris
        item = event.GetItem()
        data = self.GetPyData(item)
        if data > 100000 :
            return
        self.SelectItem(item, item, True)
        
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Ajouter
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.GetParent().OnBoutonAjouter, id=10)

        # Item Modifier
        item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.GetParent().OnBoutonModifier, id=20)
        
        menuPop.AppendSeparator()

        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.GetParent().OnBoutonSupprimer, id=30)
        
        menuPop.AppendSeparator()
        
        # Item Dupliquer
        item = wx.MenuItem(menuPop, 40, _(u"Dupliquer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Dupliquer.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.GetParent().OnBoutonDupliquer, id=40)
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()


        




class Dialog(wx.Dialog):
    def __init__(self, parent, title=""):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent

        self.panel_base = wx.Panel(self, -1)
        self.panel_contenu = Panel(self.panel_base, IDpersonne=None)

        self.bouton_aide = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Fermer"), cheminImage=Chemins.GetStaticPath("Images/32x32/Fermer.png"))
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.Onbouton_aide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_fermer, self.bouton_fermer)

    def __set_properties(self):
        self.SetTitle(_(u"Gestion des scénarios"))
        if 'phoenix' in wx.PlatformInfo:
            _icon = wx.Icon()
        else :
            _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.bouton_aide.SetToolTip(wx.ToolTip("Cliquez ici pour obtenir de l'aide"))
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
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
        self.SetSize((890, 600))
        
        self.CentreOnScreen()
        self.sizer_pages = sizer_pages

    def Onbouton_aide(self, event):
        FonctionsPerso.Aide(58)
                
    def Onbouton_fermer(self, event):
        self.EndModal(wx.ID_CANCEL)
        



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dlg = Dialog(None, "")
    dlg.ShowModal()
    dlg.Destroy()
    app.MainLoop()
