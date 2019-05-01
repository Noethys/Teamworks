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
import six
from wx.lib.mixins.listctrl import CheckListCtrlMixin
import GestionDB
import FonctionsPerso



class Panel(wx.Panel):
    def __init__(self, parent, ID=-1):
        wx.Panel.__init__(self, parent, ID, style=wx.TAB_TRAVERSAL)
        
        self.barreTitre = FonctionsPerso.BarreTitre(self,  _(u"Gestion des gadgets"), u"")
        texteIntro = _(u"Vous pouvez ici modifier les options des gadgets de la page d'accueil.")
        self.label_introduction = FonctionsPerso.StaticWrapText(self, -1, texteIntro)
        self.listCtrl = ListCtrl(self)
        self.listCtrl.SetMinSize((20, 20)) 
        self.bouton_options = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Outils.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_reinit = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Actualiser.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_haut = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Fleche_haut.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_bas = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Fleche_bas.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Aide.png"), wx.BITMAP_TYPE_ANY))
        if parent.GetName() != "treebook_configuration" :
            self.bouton_aide.Show(False)

        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOptions, self.bouton_options)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonReinit, self.bouton_reinit)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonHaut, self.bouton_haut)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonBas, self.bouton_bas)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)

        self.bouton_options.Enable(False)
        self.bouton_haut.Enable(False)
        self.bouton_bas.Enable(False)

        
    def __set_properties(self):
        self.bouton_options.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier les options du gadget sélectionné")))
        self.bouton_options.SetSize(self.bouton_options.GetBestSize())
        self.bouton_reinit.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour réinitialiser les paramètres par défaut de tous les gadgets")))
        self.bouton_reinit.SetSize(self.bouton_reinit.GetBestSize())
        self.bouton_haut.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour déplacer le gadget sélectionné vers le haut")))
        self.bouton_haut.SetSize(self.bouton_haut.GetBestSize())
        self.bouton_bas.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour déplacer le gadget sélectionné vers le bas")))
        self.bouton_bas.SetSize(self.bouton_bas.GetBestSize())
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_base2 = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_boutons = wx.FlexGridSizer(rows=9, cols=1, vgap=5, hgap=10)
        grid_sizer_base.Add(self.barreTitre, 0, wx.EXPAND, 0)
        grid_sizer_base.Add(self.label_introduction, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        grid_sizer_base2.Add(self.listCtrl, 1, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_options, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_reinit, 0, 0, 0)
        grid_sizer_boutons.Add((15, 15), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_haut, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_bas, 0, 0, 0)
        grid_sizer_boutons.Add((5, 5), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.AddGrowableRow(5)
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

    def OnBoutonOptions(self, event):
        self.Options()

    def Options(self):
        index = self.listCtrl.GetFirstSelected()
        IDgadget = self.listCtrl.GetItemData(index)
        
        if index == -1:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un gadget dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        if IDgadget == 1 : # Dossiers incomplets
            from Dlg import DLG_Parametres_dossiers
            dlg = DLG_Parametres_dossiers.Dialog(None)
            dlg.ShowModal()
            dlg.Destroy()

        if IDgadget == 2 : # Horloge
            from Dlg import DLG_Parametres_horloge
            dlg = DLG_Parametres_horloge.Dialog(None)
            dlg.ShowModal()
            dlg.Destroy()

        if IDgadget == 3 : # Calendrier            
            from Dlg import DLG_Parametres_calendrier
            dlg = DLG_Parametres_calendrier.Dialog(None)
            dlg.ShowModal()
            dlg.Destroy()

        if IDgadget == 5 : # Bloc-notes
            from Dlg import DLG_Parametres_blocnotes
            dlg = DLG_Parametres_blocnotes.Dialog(self)
            dlg.ShowModal()
            dlg.Destroy()

    def OnBoutonReinit(self, event):
        self.Reinit()

    def Reinit(self):
        # Avertissement
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment réinitialiser les paramètres de tous les gadgets de la page d'accueil ?"), "Confirmation", wx.YES_NO | wx.CANCEL | wx.ICON_EXCLAMATION)
        if dlg.ShowModal() == wx.ID_YES:
            print("REINIT !")
            dlg.Destroy()
        else:
            dlg.Destroy()
            return

    def OnBoutonHaut(self, event):
        index = self.listCtrl.GetFirstSelected()
        IDgadget = self.listCtrl.GetItemData(index)
        position = index + 1
        
        DB = GestionDB.DB()
        listeDonnees = [("ordre",  position),]
        DB.ReqMAJ("gadgets", listeDonnees, "ordre", position-1)
        listeDonnees = [("ordre",  position-1),]
        DB.ReqMAJ("gadgets", listeDonnees, "IDgadget", IDgadget)
        DB.Close()
        
        self.listCtrl.MAJListeCtrl(select=IDgadget) 
        self.listCtrl.OnItemSelected(None)
        self.listCtrl.SetFocus()

    def OnBoutonBas(self, event):
        index = self.listCtrl.GetFirstSelected()
        IDgadget = self.listCtrl.GetItemData(index)
        position = index + 1
        
        DB = GestionDB.DB()
        listeDonnees = [("ordre",  position),]
        DB.ReqMAJ("gadgets", listeDonnees, "ordre", position+1)
        listeDonnees = [("ordre",  position+1),]
        DB.ReqMAJ("gadgets", listeDonnees, "IDgadget", IDgadget)
        DB.Close()
        
        self.listCtrl.MAJListeCtrl(select=IDgadget) 
        self.listCtrl.OnItemSelected(None)
        self.listCtrl.SetFocus()

    def MAJpanel(self):
        self.listCtrl.MAJListeCtrl() 
        
    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Lesgadgets")
        
      

class ListCtrl(wx.ListCtrl, CheckListCtrlMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        CheckListCtrlMixin.__init__(self)
        self.parent = parent
        
        self.Remplissage()
        
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
##        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)

    def Remplissage(self, select=None):

        self.Importation()

        # Création des colonnes
        self.InsertColumn(0, "Ordre")
        self.SetColumnWidth(0, 50)
        self.InsertColumn(1, "Nom du gadget")
        self.SetColumnWidth(1, 180)
        self.InsertColumn(2, "Description")
        self.SetColumnWidth(2, 900)
        
        # Remplissage avec les valeurs
        self.remplissage = True
        for IDgadget, nom, label, description, taille, affichage, ordre, config, parametres in self.listeGadgets :
            if 'phoenix' in wx.PlatformInfo:
                index = self.InsertItem(six.MAXSIZE, str(ordre))
                self.SetItem(index, 1, label)
                self.SetItem(index, 2, description)
            else:
                index = self.InsertStringItem(six.MAXSIZE, str(ordre))
                self.SetStringItem(index, 1, label)
                self.SetStringItem(index, 2, description)
            self.SetItemData(index, IDgadget)

            # Check
            if affichage == "True":
                self.CheckItem(index)

            # Sélection
            if IDgadget == select :
                self.Select(index)
        
        self.remplissage = False

    def MAJListeCtrl(self, select=None):
        self.ClearAll()
        self.Remplissage(select)
        
    def OnItemActivated(self, evt):
        self.ToggleItem(evt.m_itemIndex)

    def OnCheckItem(self, index, flag):
        """ Ne fait rien si c'est le remplissage qui coche la case ! """
        if self.remplissage == False :
            IDgadget = self.GetItemData(index)
            # Enregistre l'affichage True/False du gadget dans la base
            DB = GestionDB.DB()
            listeDonnees = [("affichage",  str(flag)),]
            DB.ReqMAJ("gadgets", listeDonnees, "IDgadget", IDgadget)
            DB.Close()
        else:
            pass

    def OnItemSelected(self, event):
        index = self.GetFirstSelected()
        # Règle bouton haut
        if index == 0 :
            self.parent.bouton_haut.Enable(False)
        else:
            self.parent.bouton_haut.Enable(True)
        # Règle bouton bas
        if index == self.GetItemCount()-1 :
            self.parent.bouton_bas.Enable(False)
        else:
            self.parent.bouton_bas.Enable(True)

        if self.listeGadgets[index][7] == "True" :
            self.parent.bouton_options.Enable(True)
        else:
            self.parent.bouton_options.Enable(False)
        
    def OnItemDeselected(self, event):
        self.parent.bouton_options.Enable(False)
        self.parent.bouton_haut.Enable(False)
        self.parent.bouton_bas.Enable(False)

    def Importation(self):
      
        # Récupération des données de la table GADGETS
        DB = GestionDB.DB()     
        req = "SELECT * FROM gadgets ORDER BY ordre;"
        DB.ExecuterReq(req)
        liste = DB.ResultatReq()
        DB.Close()
        self.nbreLignes = len(liste)
        # Création du dictionnaire de données
        self.listeGadgets = liste

    def Menu_Options(self, event):
        self.parent.Options()




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
        self.SetTitle(_(u"Gestion des gadgets de la page d'accueil"))
        self.bouton_aide.SetToolTip(wx.ToolTip("Cliquez ici pour obtenir de l'aide"))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez pour fermer")))
        self.SetMinSize((700, 500))

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
        UTILS_Aide.Aide("Lesgadgets")

    def Onbouton_annuler(self, event):
        self.EndModal(wx.ID_CANCEL)


if __name__ == "__main__":
    app = wx.App(0)
    dlg = Dialog(None)
    dlg.ShowModal()
    dlg.Destroy()
    app.MainLoop()