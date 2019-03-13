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
from Ctrl import CTRL_Bouton_image
import FonctionsPerso
from Utils import UTILS_Fichiers
import wx.lib.agw.hyperlink as hl
import GestionDB
from wx.lib.mixins.listctrl import CheckListCtrlMixin
import sys
import datetime

def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def DateFrEng(textDate):
    text = str(textDate[6:10]) + "/" + str(textDate[3:5]) + "/" + str(textDate[:2])
    return text   



class Dialog(wx.Dialog):
    def __init__(self, parent, IDpersonne=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDpersonne = IDpersonne
        
        self.panel_base = wx.Panel(self, -1)
        self.label_intro = wx.StaticText(self.panel_base, -1, _(u"Veuillez cocher les déplacements que vous souhaitez inclure dans la fiche de frais :"))
        
        # ListCtrl
        self.ctrl_deplacements = ListCtrl(self.panel_base,  IDpersonne=IDpersonne)
        
        # Hyperlink cocher les non remboursés
        self.hyperlink_nonRembourses = self.Build_Hyperlink()
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_ok = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Imprimer"), cheminImage=Chemins.GetStaticPath("Images/32x32/Imprimante.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)

    def __set_properties(self):
        self.SetTitle(_(u"Imprimer une fiche de frais de déplacements"))
        if 'phoenix' in wx.PlatformInfo:
            _icon = wx.Icon()
        else :
            _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.bouton_aide.SetToolTip(wx.ToolTip("Cliquez ici pour obtenir de l'aide"))
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetToolTip(wx.ToolTip("Cliquez ici pour valider"))
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetToolTip(wx.ToolTip("Cliquez ici pour annuler la saisie"))
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())
        self.SetMinSize((710, 380))

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=0, hgap=0)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_base.Add(self.label_intro, 1, wx.LEFT|wx.TOP|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_base.Add(self.ctrl_deplacements, 1, wx.EXPAND | wx.LEFT|wx.RIGHT|wx.TOP, 10)
        grid_sizer_base.Add(self.hyperlink_nonRembourses, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM | wx.ALIGN_RIGHT, 10)
        grid_sizer_base.Add((10, 10), 1, wx.EXPAND | wx.ALL, 0)
        
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.panel_base.SetSizer(grid_sizer_base)
        sizer_base.Add(self.panel_base, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()
        self.CenterOnScreen()

    def Build_Hyperlink(self) :
        """ Construit un hyperlien """
        self.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False))
        hyper = hl.HyperLinkCtrl(self.panel_base, -1, _(u"Sélectionner uniquement les déplacements non-remboursés"), URL="")
        hyper.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLeftLink)
        hyper.AutoBrowse(False)
        hyper.SetColours("BLACK", "BLACK", "BLUE")
        hyper.EnableRollover(True)
        hyper.SetUnderlines(False, False, True)
        hyper.SetBold(False)
        hyper.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour sélectionner uniquement \nles déplacements non-remboursés")))
        hyper.UpdateLink()
        hyper.DoPopup(False)
        return hyper
        
    def OnLeftLink(self, event):
        """ Sélectionner les déplacements non remboursés """
        self.ctrl_deplacements.MAJListeCtrl()

    def OnBoutonAide(self, event):
        FonctionsPerso.Aide(22)

    def OnBoutonAnnuler(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event):
        """ Validation des données saisies """
        selections = self.ctrl_deplacements.ListeItemsCoches()
        
        # Validation de la sélection
        if len(selections) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez fait aucune sélection"), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Impression
        ImpressionFicheFrais(self.IDpersonne, selections)






# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class ListCtrl(wx.ListCtrl, CheckListCtrlMixin):
    def __init__(self, parent, IDpersonne=None):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        CheckListCtrlMixin.__init__(self)
        self.parent = parent
        self.IDpersonne = IDpersonne
        
        self.Remplissage()
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)


    def Remplissage(self, select=None):

        self.Importation()

        # Création des colonnes
        self.InsertColumn(0, u"N°")
        self.SetColumnWidth(0, 50)
        self.InsertColumn(1, _(u"Date"))
        self.SetColumnWidth(1, 80)
        self.InsertColumn(2, _(u"Objet"))
        self.SetColumnWidth(2, 80) 
        self.InsertColumn(3, _(u"Trajet"))
        self.SetColumnWidth(3, 170)  
        self.InsertColumn(4, _(u"Distance"))
        self.SetColumnWidth(4, 70)
        self.InsertColumn(5, _(u"Tarif"))
        self.SetColumnWidth(5, 70)  
        self.InsertColumn(6, _(u"Montant"))
        self.SetColumnWidth(6, 70)
        self.InsertColumn(7, _(u"Rmbst"))
        self.SetColumnWidth(7, 50)  
        
        # Remplissage avec les valeurs
        self.remplissage = True
        for IDdeplacement, date, objet, trajet, dist, tarif_km, montantStr, remboursement in self.listeDonnees :
                index = self.InsertStringItem(six.MAXSIZE, str(IDdeplacement))
                self.SetStringItem(index, 1, date)
                self.SetStringItem(index, 2, objet)
                self.SetStringItem(index, 3, trajet)
                self.SetStringItem(index, 4, dist)
                self.SetStringItem(index, 5, tarif_km)
                self.SetStringItem(index, 6, montantStr)
                self.SetStringItem(index, 7, remboursement)
                
                self.SetItemData(index, IDdeplacement)
                
                # Check
                if remboursement == "":
                    self.CheckItem(index) 
                    
                # On sélectionne le dernier
                if index == self.nbreLignes-1 :
                    self.EnsureVisible(index)
        
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

      
    def Importation(self):
        # Récupération des données
        DB = GestionDB.DB()        
        req = """SELECT IDdeplacement, date, objet, ville_depart, ville_arrivee, distance, aller_retour, tarif_km, IDremboursement FROM deplacements WHERE IDpersonne=%d ORDER BY date; """ % self.IDpersonne
        DB.ExecuterReq(req)
        donnees = DB.ResultatReq()
        DB.Close()
        self.nbreLignes = len(donnees)
        # Création du dictionnaire de données
        self.listeDonnees = []
        index = 0
        for IDdeplacement, date, objet, ville_depart, ville_arrivee, distance, aller_retour, tarif_km, IDremboursement in donnees :
            # Formatage date
            dateTmp = str(date[8:10])+"/"+str(date[5:7])+"/"+str(date[0:4])
            # Formatage Trajet
            if aller_retour == "True" :
                trajet = ville_depart + " <--> " + ville_arrivee
            else:
                trajet = ville_depart + " -> " + ville_arrivee
            # Formatage Remboursement
            if IDremboursement != None and IDremboursement != 0 and IDremboursement != "" :
                remboursement = u"N°" + str(IDremboursement)
            else :
                remboursement = ""
            # Formatage distance
            dist = str(distance) + _(u" Km")
            # Formatage montant
            montant = float(distance) * float(tarif_km)
            montantStr = u"%.2f €" % montant
            # Formatage tarif/Km
            tarif_km = str(tarif_km) + _(u" €/km")
            self.listeDonnees.append( (IDdeplacement, dateTmp, objet, trajet, dist, tarif_km, montantStr, remboursement) )
            index += 1

    def ListeItemsCoches(self):
        """ Récupère la liste des IDdeplacements cochés """
        listeIDcoches = []
        nbreItems = self.GetItemCount()
        for index in range(0, nbreItems) :
            ID = int(self.GetItem(index, 0).GetText())
            # Vérifie si l'item est coché
            if self.IsChecked(index) :
                listeIDcoches.append(ID)
        return listeIDcoches
        



# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


class ImpressionFicheFrais():
    def __init__(self, IDpersonne=None, listeSelections=[]):
        """ Imprime une fiche de frais """
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.rl_config import defaultPageSize
        from reportlab.lib.units import inch, cm
        from reportlab.lib import colors
        self.hauteur_page = defaultPageSize[1]
        self.largeur_page = defaultPageSize[0]
        self.inch = inch
        
        if len(listeSelections) == 1 : listeSelectionsTmp = "(%d)" % listeSelections[0]
        else : listeSelectionsTmp = str(tuple(listeSelections))
        
        # Récupération des données
        DB = GestionDB.DB()        
        req = """
        SELECT IDdeplacement, date, objet, ville_depart, ville_arrivee, distance, aller_retour, tarif_km, IDremboursement, nom, prenom
        FROM deplacements LEFT JOIN personnes ON deplacements.IDpersonne = personnes.IDpersonne
        WHERE deplacements.IDpersonne=%d AND IDdeplacement IN %s ORDER BY date; """ % (IDpersonne, listeSelectionsTmp)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        
        if len(listeDonnees) == 0 : 
            print("pas de donnees a imprimer")
            return
        
        # Initialisation du PDF
        PAGE_HEIGHT=defaultPageSize[1]
        PAGE_WIDTH=defaultPageSize[0]
        nomDoc = UTILS_Fichiers.GetRepTemp("fiche_frais.pdf")
        if "win" in sys.platform : nomDoc = nomDoc.replace("/", "\\")
        doc = SimpleDocTemplate(nomDoc)
        story = []

        # Création du titre du document
        dataTableau = []
        largeursColonnes = ( (420, 100) )
        dateDuJour = DateEngFr(str(datetime.date.today()))
        dataTableau.append( (_(u"Frais de déplacement"), _(u"Edité le %s") % dateDuJour )  )
        style = TableStyle([
                            ('BOX', (0,0), (-1,-1), 0.25, colors.black), 
                            ('VALIGN', (0,0), (-1,-1), 'TOP'), 
                            ('ALIGN', (0,0), (0,0), 'LEFT'), 
                            ('FONT',(0,0),(0,0), "Helvetica-Bold", 16), 
                            ('ALIGN', (1,0), (1,0), 'RIGHT'), 
                            ('FONT',(1,0),(1,0), "Helvetica", 6), 
                            ])
        tableau = Table(dataTableau, largeursColonnes)
        tableau.setStyle(style)
        story.append(tableau)
        story.append(Spacer(0,20))       
        
        # Tableau de données
        dataTableau = []
        largeursColonnes = (20, 100, 140, 140, 40, 40, 40)
        
        # Création de l'entete de groupe
        titreGroupe = listeDonnees[0][9] + " " + listeDonnees[0][10]
        valeurs = (titreGroupe, "", "", "", "", "", "")
        dataTableau.append( valeurs )
        
        # Création des labels des colonnes
        valeurs = (_(u"ID"), _(u"Date"), _(u"Objet"), _(u"Trajet"), _(u"Distance"), _(u"Tarif/Km"), _(u"Montant"))
        dataTableau.append( valeurs )
        
        # Création des groupes
        montant_total = 0
        for IDdeplacement, date, objet, ville_depart, ville_arrivee, distance, aller_retour, tarif_km, IDremboursement, nom, prenom in listeDonnees :
            varIDdeplacement = IDdeplacement
            varDate = self.DateComplete(self.RetourneDatetime(date))
            varObjet = objet
            if aller_retour == "True" :
                varTrajet = ville_depart + " <--> " + ville_arrivee
            else:
                varTrajet = ville_depart + " -> " + ville_arrivee
            varDistance = str(distance) + " Km"
            varTarif_km = str(tarif_km) + _(u" €/Km")
##            varIDremboursement = IDremboursement
            montant = distance * tarif_km
            montant_total += montant
            varMontant = u"%.2f €" % montant
            valeurs = (varIDdeplacement, varDate, varObjet, varTrajet, varDistance, varTarif_km, varMontant)
            dataTableau.append( valeurs )
            
        # Création de la ligne de total
        dataTableau.append( ( "", "", "", "", "", "Total :", u"%.2f €" % montant_total ) )
    
        # Style du tableau
        style = TableStyle([
                            ('GRID', (0,0), (-1,-2), 0.25, colors.black), # Crée la bordure noire pour tout le tableau
                            ('GRID', (6,-1), (-1,-1), 0.25, colors.black), # Crée la bordure noire pour tout le tableau
                            ('VALIGN', (0,0), (-1,-1), 'TOP'), # Centre verticalement toutes les cases
##                            ('ALIGN', (0,0), (-1,-1), 'LEFT'), # Titre du groupe à gauche
                            ('ALIGN', (4,2), (-1,-1), 'RIGHT'), # 3 dernières Colonnes alignée à droite
                            ('ALIGN', (0,1), (0,-1), 'CENTRE'), # Colonne ID centrée
                            ('ALIGN', (0,1), (-1,1), 'CENTRE'), # Ligne de labels colonne alignée au centre
##                            ('SPAN',(0,-1),(1,-1)), # Fusionne les 2 lignes du bas pour faire case Total
                            ('SPAN',(0,0),(-1,0)), # Fusionne les lignes du haut pour faire le titre du groupe
                            ('FONT',(0,0),(-1,-1), "Helvetica", 6), # Donne la police de caract. + taille de police 
                            ('FONT',(0,0),(0,0), "Helvetica-Bold", 8), # Donne la police de caract. + taille de police du titre de groupe
                            ('FONT',(0,1),(-1,1), "Helvetica", 5), # Donne la police de caract. + taille de police de la ligne de labels de colonnes
##                            ('FONT',(0,-1),(-1,-1), "Helvetica", 6), # Donne la police de caract. + taille de police de la ligne de total
                            ('BACKGROUND', (0,0), (-1,0), colors.moccasin), # Donne la couleur de fond du titre de groupe
                            ('GRID', (0,0), (-1,-2), 0.25, colors.black),
                            ])
            
           
        # Création du tableau
        tableau = Table(dataTableau, largeursColonnes)
        tableau.setStyle(style)
        story.append(tableau)
        story.append(Spacer(0,20))
        
            
        # Enregistrement du PDF
        doc.build(story)
        
        # Affichage du PDF
        FonctionsPerso.LanceFichierExterne(nomDoc)
        
    def RetourneDatetime(self, dateStr):
        return datetime.date(year=int(dateStr[:4]), month=int(dateStr[5:7]), day=int(dateStr[8:10]))
    
    def DateComplete(self, date):
        listeJours = ("Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche")
        listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), "juillet", _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
        dateStr = listeJours[date.weekday()] + " " + str(date.day) + " " + listeMois[date.month-1] + " " + str(date.year)
        return dateStr
    
    
    
    
if __name__ == "__main__":
    app = wx.App(0)
    dlg = Dialog(None, IDpersonne=1)
    dlg.ShowModal()
    dlg.Destroy()
    app.MainLoop()
