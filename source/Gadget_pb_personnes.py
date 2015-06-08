#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
# Copyright:    (c) 2008-09 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------

import wx
import GestionDB
import FonctionsPerso
import wx.lib.agw.customtreectrl as CT
import sys


class Panel(wx.Panel):
    def __init__(self, parent, ID=-1):
        wx.Panel.__init__(self, parent, ID, name="panel_gadget_pb_personnes", style=wx.TAB_TRAVERSAL)
        self.barreTitre = FonctionsPerso.BarreTitre(self,  u"Problèmes des fiches", u"")
        self.treeCtrl = TreeCtrl(self)    

        # Layout
        grid_sizer_principal = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)
        grid_sizer_principal.Add(self.barreTitre, 1, wx.EXPAND, 0)
        grid_sizer_principal.Add(self.treeCtrl, 1, wx.ALL|wx.EXPAND, 0)
        self.SetSizer(grid_sizer_principal)
        grid_sizer_principal.Fit(self)
        grid_sizer_principal.AddGrowableRow(1)
        grid_sizer_principal.AddGrowableCol(0)


class PanelGadget(wx.Panel):
    """ Version spéciale pour Gadget Page d'acccueil """
    def __init__(self, parent, ID=-1):
        wx.Panel.__init__(self, parent, ID, name="panel_gadget_pb_personnes", style=wx.TAB_TRAVERSAL)
        self.treeCtrl = TreeCtrl(self)    

        # Layout
        grid_sizer_principal = wx.FlexGridSizer(rows=1, cols=1, vgap=0, hgap=0)
        grid_sizer_principal.Add(self.treeCtrl, 1, wx.ALL|wx.EXPAND, 0)
        self.SetSizer(grid_sizer_principal)
        grid_sizer_principal.Fit(self)
        grid_sizer_principal.AddGrowableRow(0)
        grid_sizer_principal.AddGrowableCol(0)
        
        
class MyFrame(wx.Frame):
    def __init__(self, parent, title="" ):
        wx.Frame.__init__(self, parent, -1, title=title, name="frm_gadget_pb_personnes", style=wx.DEFAULT_FRAME_STYLE)
        self.panel = Panel(self)
        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_base.Add(self.panel, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        self.Layout()
        self.Centre()
        self.SetSize((550, 450))



# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



class TreeCtrl(CT.CustomTreeCtrl):
    def __init__(self, parent, fichier="", id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.NO_BORDER) :
        CT.CustomTreeCtrl.__init__(self, parent, id, pos, size, style)
        self.parent = parent
        
        # Diminution de la taille de la police sous linux
        if "linux" in sys.platform :
            defaultFont = self.GetFont()
            defaultFont.SetPointSize(8)
            self.SetFont(defaultFont)
        
        self.SetAGWWindowStyleFlag(wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | CT.TR_AUTO_CHECK_CHILD)
        self.EnableSelectionVista(True) 
        
        # Couleurs
        self.couleurFond = (122, 161, 230)
        self.couleurPersonne = (255, 255, 255)
        self.couleurType = (0, 0, 0)
        self.couleurProbleme = (0, 0, 0)
        self.couleurTraits = (179, 185, 231)
        
        # Autres paramètres
        if self.parent.GetName() != "panel_gadget_dossiersincomplets" : 
            self.expandPersonnes = True
            self.expandTypes = True
        else:
            self.expandPersonnes = False
            self.expandTypes = False
        
        # Bind
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeftDown)

        
    def OnLeftDown(self, event):
        self.Unselect()
        event.Skip()
        
    def MAJ_treeCtrl(self):
        self.DeleteAllItems()
        # Init couleurs
        self.SetBackgroundColour(self.couleurFond)
        self.SetHilightFocusColour(self.couleurFond)
        self.SetHilightNonFocusColour(self.couleurFond)
        pen = wx.Pen(self.couleurTraits, 2, style=wx.DOT)
        self.SetConnectionPen(pen)
        # Récupération des données
        self.listeDonnees = self.GetListeProblemes()
        # Racine
        self.root = self.AddRoot("Root")
        self.SetPyData(self.root, None)
        # Branches
        self.AddTreeNodes(self.root, self.listeDonnees)

    def AddTreeNodes(self, parentItem, items, img=None):
        for item in items:
            if type(item) == str or type(item) == unicode:
                # Label problème
                newItem = self.AppendItem(parentItem, item)
                self.SetPyData(newItem, None)
                font = self.GetFont()
                font.SetPointSize(7)
                self.SetItemFont(newItem, font)
                self.SetItemTextColour(newItem, self.couleurProbleme)
            else:
                # Tête de rubrique
                texte = item[0]                
                newItem = self.AppendItem(parentItem, texte)
                self.SetPyData(newItem, None)
                if parentItem == self.root :
                    # Nom de la personne
                    self.SetItemTextColour(newItem, self.couleurPersonne)
                    self.SetItemBold(newItem, True)
                else:
                    pass
                    # Type de problème
                    self.SetItemTextColour(newItem, self.couleurType)
                    # self.SetItemBold(newItem, True)
                    if self.expandPersonnes : self.Expand(parentItem) 
                
                # Autres
                self.AddTreeNodes(newItem, item[1], img)
                if self.expandTypes : self.Expand(newItem) 



    def GetListeProblemes(self):
        dictNoms, dictProblemes = FonctionsPerso.Creation_liste_pb_personnes()
        # Transforme le dict en liste
        listeProblemes = []
        index1 = 0
        for IDpersonne, dictCategories in dictProblemes.iteritems() :
            listeProblemes.append( [dictNoms[IDpersonne], []] )
            for nomCategorie, valeurs in dictCategories.iteritems() :
                listeProblemes[index1][1].append( [nomCategorie, valeurs] )
            index1 += 1
        return listeProblemes
           
            

# ------------------------------------------------------------------------------------------------------------------------------------------------



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
