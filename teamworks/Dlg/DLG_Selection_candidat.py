#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
# Copyright:    (c) 2008-09 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------

import Chemins
from Utils.UTILS_Traduction import _
from Utils import UTILS_Adaptations
import wx
from Ctrl import CTRL_Bouton_image
OL_candidats = UTILS_Adaptations.Import("Ol.OL_candidats")
OL_personnes = UTILS_Adaptations.Import("Ol.OL_personnes")


class MyDialog(wx.Dialog):
    """ Sélection d'un candidat """
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=-1, title=_(u"Sélectionner un candidat ou un salarié"), size=(450, 600))

        # Label
        self.label = wx.StaticText(self, -1, _(u"Veuillez sélectionner un candidat ou un salarié :"))
        
        self.noteBook = wx.Notebook(self, -1, size=(-1, 150), style=wx.BK_TOP)
        self.listCtrl_candidats = OL_candidats.ListView(self.noteBook, id=-1, activeDoubleClic=False, name="OL_candidats", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.listCtrl_candidats.MAJ() 
##        self.barreRecherche_candidats = BarreRecherche_candidats(self, listview=self.listCtrl_candidats)
        self.noteBook.AddPage(self.listCtrl_candidats, _(u"Liste des candidats"))
        self.listCtrl_personnes = OL_personnes.ListView(self.noteBook, id=-1, activeDoubleClic=False, name="OL_personnes", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
##        self.barreRecherche_personnes = BarreRecherche_personnes(self, listview=self.listCtrl_personnes)
        self.noteBook.AddPage(self.listCtrl_personnes, _(u"Liste des salariés"))
        
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
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.label, 0, wx.ALL, 10)

        grid_sizer_base.Add(self.noteBook, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 10)
        
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
        self.CenterOnScreen()

        
    def OnBoutonOk(self, event):
        """ Validation des données saisies """
        selection_candidat = self.listCtrl_candidats.Selection()
        selection_personne = self.listCtrl_personnes.Selection()
        numPage = self.noteBook.GetSelection()
        
        if numPage== 0 and len(selection_candidat) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun candidat !"), _(u"Aucune sélection"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        if numPage== 1 and len(selection_personne) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun salarié !"), _(u"Aucune sélection"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        self.EndModal(wx.ID_OK)

    def GetIDcandidat(self):
        if self.noteBook.GetSelection() == 0 :
            IDcandidat = self.listCtrl_candidats.Selection()[0].IDcandidat
        else:
            IDcandidat = 0
        return IDcandidat
    
    def GetIDpersonne(self):
        if self.noteBook.GetSelection() == 1 :
            IDpersonne = self.listCtrl_personnes.Selection()[0].IDpersonne
        else:
            IDpersonne = 0
        return IDpersonne


class BarreRecherche_candidats(wx.SearchCtrl):
    def __init__(self, parent, listview):
        wx.SearchCtrl.__init__(self, parent, size=(-1,-1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent

        self.SetDescriptiveText(_(u"Rechercher un individu"))
        self.ShowSearchButton(True)
        
        self.listView = listview
        nbreColonnes = self.listView.GetColumnCount()
        self.listView.SetFilter(Filter.TextSearch(self.listView, self.listView.columns[0:nbreColonnes]))
        
        self.SetCancelBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Interdit.png"), wx.BITMAP_TYPE_PNG))
        self.SetSearchBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Loupe.png"), wx.BITMAP_TYPE_PNG))
        
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnDoSearch)
        self.Bind(wx.EVT_TEXT, self.OnDoSearch)

    def OnSearch(self, evt):
        self.Recherche(self.GetValue())
            
    def OnCancel(self, evt):
        self.SetValue("")
        self.Recherche(self.GetValue())

    def OnDoSearch(self, evt):
        self.Recherche(self.GetValue())
        
    def Recherche(self, txtSearch):
        self.ShowCancelButton(len(txtSearch))
        self.listView.GetFilter().SetText(txtSearch)
        self.listView.RepopulateList()


class BarreRecherche_personnes(wx.SearchCtrl):
    def __init__(self, parent, listview):
        wx.SearchCtrl.__init__(self, parent, size=(-1,-1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent

        self.SetDescriptiveText(_(u"Rechercher un individu"))
        self.ShowSearchButton(True)
        
        self.listView = listview
        nbreColonnes = self.listView.GetColumnCount()
        self.listView.SetFilter(Filter.TextSearch(self.listView, self.listView.columns[0:nbreColonnes]))
        
        self.SetCancelBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Interdit.png"), wx.BITMAP_TYPE_PNG))
        self.SetSearchBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Loupe.png"), wx.BITMAP_TYPE_PNG))
        
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnDoSearch)
        self.Bind(wx.EVT_TEXT, self.OnDoSearch)

    def OnSearch(self, evt):
        self.Recherche(self.GetValue())
            
    def OnCancel(self, evt):
        self.SetValue("")
        self.Recherche(self.GetValue())

    def OnDoSearch(self, evt):
        self.Recherche(self.GetValue())
        
    def Recherche(self, txtSearch):
        self.ShowCancelButton(len(txtSearch))
        self.listView.GetFilter().SetText(txtSearch)
        self.listView.RepopulateList()

if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frm = MyDialog(None)
    frm.ShowModal()
    app.MainLoop()