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
import FonctionsPerso
import operator


class Panel(wx.Panel):
    def __init__(self, parent, ID=-1):
        wx.Panel.__init__(self, parent, ID, style=wx.TAB_TRAVERSAL)
        
        self.barreTitre = FonctionsPerso.BarreTitre(self,  _(u"Configuration de la liste"), u"")
        texteIntro = _(u"Vous pouvez ici modifier les options d'affichage de la liste :")
        self.label_introduction = FonctionsPerso.StaticWrapText(self, -1, texteIntro)
        self.listCtrl = ListCtrl(self)
        self.listCtrl.SetMinSize((20, 20)) 
        self.bouton_haut = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Fleche_haut.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_bas = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Fleche_bas.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_reinit = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Actualiser.png"), wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonReinit, self.bouton_reinit)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonHaut, self.bouton_haut)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonBas, self.bouton_bas)
        
        self.bouton_haut.Enable(False)
        self.bouton_bas.Enable(False)

        
    def __set_properties(self):
        self.bouton_reinit.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour réinitialiser les paramètres par défaut de l'affichage")))
        self.bouton_reinit.SetSize(self.bouton_reinit.GetBestSize())
        self.bouton_haut.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour déplacer la colonne sélectionnée vers le haut")))
        self.bouton_haut.SetSize(self.bouton_haut.GetBestSize())
        self.bouton_bas.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour déplacer la colonne sélectionnée vers le bas")))
        self.bouton_bas.SetSize(self.bouton_bas.GetBestSize())
        
    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_base2 = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_boutons = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=10)
        grid_sizer_base.Add(self.barreTitre, 0, wx.EXPAND, 0)
        grid_sizer_base.Add(self.label_introduction, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        grid_sizer_base2.Add(self.listCtrl, 1, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_haut, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_bas, 0, 0, 0)
        grid_sizer_boutons.Add((15, 15), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_reinit, 0, 0, 0)
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


    def OnBoutonReinit(self, event):
        self.Reinit()

    def Reinit(self):
        # Avertissement
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous rétablir l'affichage par défaut ?"), "Confirmation", wx.YES_NO | wx.CANCEL | wx.ICON_EXCLAMATION)
        if dlg.ShowModal() == wx.ID_YES:
            
            OL = self.GetParent().GetGrandParent() 
            listeCols = OL.listeColonnesOriginale
            self.GetGrandParent().listeColonnes = listeCols
            self.listCtrl.Importation()
            self.listCtrl.MAJListeCtrl()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return

    def OnBoutonHaut(self, event):
        index = self.listCtrl.GetFirstSelected()
        ID = self.listCtrl.GetItemData(index)
        position = index + 1

        self.listCtrl.listeColonnes[index-1][8] = position
        self.listCtrl.listeColonnes[index][8] = position-1
        
        self.listCtrl.MAJListeCtrl(select=ID) 
        self.listCtrl.OnItemSelected(None)
        self.listCtrl.SetFocus()

    def OnBoutonBas(self, event):
        index = self.listCtrl.GetFirstSelected()
        ID = self.listCtrl.GetItemData(index)
        position = index + 1
        
        self.listCtrl.listeColonnes[index+1][8] = position
        self.listCtrl.listeColonnes[index][8] = position+1
        
        self.listCtrl.MAJListeCtrl(select=ID) 
        self.listCtrl.OnItemSelected(None)
        self.listCtrl.SetFocus()

    def MAJpanel(self):
        self.listCtrl.MAJListeCtrl() 
        


# -----------------------------------------------------------------------------------------------------------------------------------------------------------------

class ListCtrl(wx.ListCtrl, CheckListCtrlMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        CheckListCtrlMixin.__init__(self)
        self.parent = parent
        
        self.Importation()
        self.Remplissage()
        
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)

    def Remplissage(self, select=None):
        # Création des colonnes
        self.InsertColumn(0, "Ordre")
        self.SetColumnWidth(0, 50)
        self.InsertColumn(1, "Label de la colonne")
        self.SetColumnWidth(1, 180)
        self.InsertColumn(2, "Description")
        self.SetColumnWidth(2, 900)
        
        # Remplissage avec les valeurs
        self.remplissage = True
        self.listeColonnes.sort(key=operator.itemgetter(8))
        for ID, labelCol, alignement, largeur, nomChamp, args, description, affiche, ordre in self.listeColonnes : 
                index = self.InsertStringItem(six.MAXSIZE, str(ordre))
                self.SetStringItem(index, 1, labelCol)
                self.SetStringItem(index, 2, description)
                self.SetItemData(index, ID)
                
                # Check
                if affiche == True :
                    self.CheckItem(index) 
                                
                # Sélection
                if ID == select :
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
            ID = self.GetItemData(index)
            # Enregistre l'affichage True/False du gadget dans la base
            self.listeColonnes[ID][7] = flag
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
        
    def OnItemDeselected(self, event):
        self.parent.bouton_haut.Enable(False)
        self.parent.bouton_bas.Enable(False)

    def Importation(self):
        # Récupération des données
        listeCols = self.GetGrandParent().GetParent().listeColonnes
        self.listeColonnes = []
        x = 0
        for labelCol, alignement, largeur, nomChamp, args, description, affiche, ordre in listeCols : 
            self.listeColonnes.append ([x, labelCol, alignement, largeur, nomChamp, args, description, affiche, ordre] )
            x += 1

    def Exportation(self):
        self.listeColonnes.sort(key=operator.itemgetter(0))
        self.listeColonnesExport = []
        for ID, labelCol, alignement, largeur, nomChamp, args, description, affiche, ordre in self.listeColonnes : 
            self.listeColonnesExport.append ([labelCol, alignement, largeur, nomChamp, args, description, affiche, ordre] )
        return self.listeColonnesExport
    
    
    
class Dialog(wx.Dialog):
    def __init__(self, parent, listeColonnes=[]):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.listeColonnes = listeColonnes
        self.panel_base = wx.Panel(self, -1)
        self.panel_contenu = Panel(self.panel_base)
        self.panel_contenu.barreTitre.Show(False)
        self.bouton_aide = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_ok = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Ok"), cheminImage=Chemins.GetStaticPath("Images/32x32/Valider.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.Onbouton_aide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_ok, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_annuler, self.bouton_annuler)

        self.SetMinSize((450, 350))
        self.SetSize((550, 380))
        self.Centre()

    def __set_properties(self):
        self.SetTitle(_(u"Configuration de la liste de personnes"))
        if 'phoenix' in wx.PlatformInfo:
            _icon = wx.Icon()
        else :
            _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.bouton_aide.SetToolTip(wx.ToolTip("Cliquez ici pour obtenir de l'aide"))
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez pour annuler et fermer")))
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

    def Onbouton_aide(self, event):
        FonctionsPerso.Aide(53)
            
    def Onbouton_annuler(self, event):
        self.EndModal(wx.ID_CANCEL)
        
    def Onbouton_ok(self, event):
        listeColonnes = self.panel_contenu.listCtrl.Exportation()
        # Envoie la nouvelle liste de colonnes au objectlistview personnes
        self.GetParent().SetListeColonnes(listeColonnes)
        self.GetParent().MAJ()
        
        # Fermeture
        self.EndModal(wx.ID_OK)

        
        
        
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dlg = Dialog(None, [])
    dlg.ShowModal()
    dlg.Destroy()
    app.MainLoop()