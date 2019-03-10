#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
# Copyright:    (c) 2008-09 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------

from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB
import FonctionsPerso
import datetime
import wx.lib.agw.customtreectrl as CT
import sys


class Panel(wx.Panel):
    def __init__(self, parent, ID=-1):
        wx.Panel.__init__(self, parent, ID, name="panel_gadget_candidatures", style=wx.TAB_TRAVERSAL)
        self.barreTitre = FonctionsPerso.BarreTitre(self,  _(u"Infos recrutement"), u"")
        self.treeCtrl = TreeCtrl(self)
        self.treeCtrl.MAJ() 

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
        wx.Panel.__init__(self, parent, ID, name="panel_gadget_candidatures", style=wx.TAB_TRAVERSAL)
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
        wx.Frame.__init__(self, parent, -1, title=title, name="frm_gadget_candidatures", style=wx.DEFAULT_FRAME_STYLE)
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
        
        self.SetAGWWindowStyleFlag(wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | CT.TR_AUTO_CHECK_CHILD)
        self.EnableSelectionVista(True) 
        
        # Diminution de la taille de la police sous linux
        if "linux" in sys.platform :
            defaultFont = self.GetFont()
            defaultFont.SetPointSize(8)
            self.SetFont(defaultFont)
        
        # Couleurs
        self.couleurFond = (122, 161, 230)
##        self.couleurPersonne = (255, 255, 255)
##        self.couleurType = (0, 0, 0)
##        self.couleurProbleme = (0, 0, 0)
##        self.couleurTraits = (179, 185, 231)
        
##        # Autres paramètres
##        if self.parent.GetName() != "panel_gadget_candidatures" : 
##            self.expandPersonnes = True
##            self.expandTypes = True
##        else:
##            self.expandPersonnes = False
##            self.expandTypes = False
        
        self.ctrl_vide = wx.StaticText(self, -1, _(u"Aucune information"), size=(200, 30), style=wx.ALIGN_CENTER |wx.FULL_REPAINT_ON_RESIZE)
        self.ctrl_vide.SetForegroundColour(wx.LIGHT_GREY)
        self.ctrl_vide.SetBackgroundColour(self.GetBackgroundColour())
        self.ctrl_vide.SetFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.ctrl_vide.Show(False)
        
        # Bind
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeftDown)
        self.Bind(wx.EVT_SIZE, self.OnSize)
    
    def OnSize(self, event):
        self.ctrl_vide.SetBackgroundColour(self.GetBackgroundColour())
        self.ctrl_vide.SetPosition(((self.GetClientSize()[0]/2)-60, self.GetClientSize()[1]/3))
        event.Skip()
        
    def OnLeftDown(self, event):
        self.Unselect()
        event.Skip()
        
    def MAJ(self):
        self.DeleteAllItems()
        # Init couleurs
##        self.SetBackgroundColour(self.couleurFond)
##        self.SetHilightFocusColour(self.couleurFond)
##        self.SetHilightNonFocusColour(self.couleurFond)
##        pen = wx.Pen(self.couleurTraits, 2, style=wx.DOT)
##        self.SetConnectionPen(pen)
        # Récupération des données
        self.listeDonnees = self.GetListeDonnees()
        if len(self.listeDonnees) > 0 :
            self.ctrl_vide.Show(False)
        else:
            self.ctrl_vide.Show(True)
        # Racine
        self.root = self.AddRoot("Root")
        self.SetPyData(self.root, None)
        # Branches
        self.AddTreeNodes(self.root, self.listeDonnees)

    def AddTreeNodes(self, parentItem, items, img=None):
        for item in items:
            if type(item)  != list :
                # Label
                ID, label = item
                newItem = self.AppendItem(parentItem, label)
                self.SetPyData(newItem, ID)
                font = self.GetFont()
                font.SetPointSize(7)
                self.SetItemFont(newItem, font)
##                self.SetItemTextColour(newItem, self.couleurProbleme)
            else:
                # Tête de rubrique
                texte = item[0][1]                
                newItem = self.AppendItem(parentItem, texte)
                self.SetPyData(newItem, None)
##                if parentItem == self.root :
##                    # Nom de la personne
##                    self.SetItemTextColour(newItem, self.couleurPersonne)
##                    self.SetItemBold(newItem, True)
##                else:
##                    pass
##                    # Type de problème
##                    self.SetItemTextColour(newItem, self.couleurType)
##                    # self.SetItemBold(newItem, True)
##                    self.Expand(parentItem) 
                
                # Autres
                self.AddTreeNodes(newItem, item[1], img)
                self.Expand(newItem) 

    def GetNom(self, IDcandidat=0, IDpersonne=0):
        if IDcandidat != 0 and IDcandidat != None :
            nomID = "IDcandidat"
            ID = IDcandidat
            table = "candidats"
        else:
            nomID = "IDpersonne"
            ID = IDpersonne
            table = "personnes"
        # Recherche d'un nom de CANDIDAT ou de PERSONNES
        DB = GestionDB.DB()
        req = """SELECT %s, civilite, nom, prenom
        FROM %s WHERE %s=%d ORDER BY nom, prenom; """ % (nomID, table, nomID, ID)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) > 0 :
            return u"%s %s" %(listeDonnees[0][2], listeDonnees[0][3])
        else:
            return ""

    def FormateDate(self, dateStr):
        if dateStr == "" or dateStr == None : return ""
        date = str(datetime.date(year=int(dateStr[:4]), month=int(dateStr[5:7]), day=int(dateStr[8:10])))
        text = str(date[8:10]) + "/" + str(date[5:7]) + "/" + str(date[:4])
        return text
    
    def GetListeDonnees(self):
        """ Recup des données """
        listeInfos = []
        
        # Récupération des entretiens sans avis
        DB = GestionDB.DB()
        dateDuJour = datetime.date.today()
        req = """SELECT IDentretien, IDcandidat, date, heure, avis, remarques, IDpersonne 
        FROM entretiens WHERE (date <= '%s' AND avis=0) ORDER BY date, heure; """ % dateDuJour
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) > 0 :
            if len(listeDonnees) == 1 :
                groupe = (0, _(u"1 entretien sans avis"))
            else:
                groupe = (0, _(u"%d entretiens sans avis") % len(listeDonnees))
            listeItems = []
            for IDentretien, IDcandidat, date, heure, avis, remarques, IDpersonne in listeDonnees :
                nom = self.GetNom(IDcandidat, IDpersonne)
                dateStr = self.FormateDate(date)
                label = u"%s : %s" % (dateStr, nom)
                item = (IDentretien, label)
                listeItems.append(item)
            listeInfos.append( [groupe, listeItems] )

        # Récupération des candidatures sans réponse
        DB = GestionDB.DB()
        req = """SELECT IDcandidature, IDcandidat, IDpersonne, date_depot
        FROM candidatures WHERE (reponse_obligatoire=1 AND reponse=0) ORDER BY date_depot; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) > 0 :
            listeItems = []
            if len(listeDonnees) == 1 :
                groupe = (0, _(u"1 candidature sans réponse"))
            else:
                groupe = (0, _(u"%d candidatures sans réponse") % len(listeDonnees))
            for IDcandidature, IDcandidat, IDpersonne, date_depot in listeDonnees :
                nom = self.GetNom(IDcandidat, IDpersonne)
                dateStr = self.FormateDate(date_depot)
                label = u"%s : %s" % (dateStr, nom)
                item = (IDcandidature, label)
                listeItems.append(item)
            listeInfos.append( [groupe, listeItems] )
            
        return listeInfos
        
        # ----------------------------------------------------
        
##        dictNoms, dictProblemes = FonctionsPerso.Creation_liste_pb_personnes()
##        # Transforme le dict en liste
##        listeProblemes = []
##        index1 = 0
##        for IDpersonne, dictCategories in dictProblemes.iteritems() :
##            listeProblemes.append( [dictNoms[IDpersonne], []] )
##            for nomCategorie, valeurs in dictCategories.iteritems() :
##                listeProblemes[index1][1].append( [nomCategorie, valeurs] )
##            index1 += 1
##        return listeProblemes
           
            

# ------------------------------------------------------------------------------------------------------------------------------------------------



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
