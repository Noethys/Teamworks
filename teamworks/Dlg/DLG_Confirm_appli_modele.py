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
import sys 
import GestionDB
import datetime
from threading import Thread
from time import sleep
import FonctionsPerso


def DatetimeDateEnStr(date):
    """ Transforme un datetime.date en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = ("Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche")
    listeMois = ("janvier", _(u"février"), "mars", "avril", "mai", "juin", "juillet", _(u"août"), "septembre", "octobre", "novembre", _(u"décembre"))
    dateStr = listeJours[date.weekday()] + " " + str(date.day) + " " + listeMois[date.month-1] + " " + str(date.year)
    return dateStr

class Frm_confirm_appli(wx.Frame):
    def __init__(self, parent, nbreTaches=0, dictTaches={}, listeCreationsTaches=[], inclureFeries=False ):
        wx.Frame.__init__(self, parent, -1, title=_(u"Confirmation d'application des modèles"), name="frm_confirmApplication", style=wx.DEFAULT_FRAME_STYLE)
        
        self.dictTaches = dictTaches
        self.listeCreationsTaches = listeCreationsTaches
        self.inclureFeries = inclureFeries
        
        self.panel_base_1 = wx.Panel(self, -1)
        self.panel_base_2 = wx.Panel(self.panel_base_1, -1)
        if nbreTaches == 1 :
            txt = _(u"Confirmez-vous la création de la tâche suivante ?")
        else:
            txt = _(u"Confirmez-vous la création des ") + str(nbreTaches) + _(u" tâches suivantes ?")
        self.label_confirmation = wx.StaticText(self.panel_base_2, -1, txt)
        self.tree_taches = TreeCtrlTaches(self.panel_base_2)
        self.gauge = wx.Gauge(self.panel_base_2, -1, nbreTaches, size=(-1, 10))
        self.bouton_ok = wx.BitmapButton(self.panel_base_2, -1, wx.Bitmap(Chemins.GetStaticPath("Images/BoutonsImages/Ok_L72.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self.panel_base_2, -1, wx.Bitmap(Chemins.GetStaticPath("Images/BoutonsImages/Annuler_L72.png"), wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def __set_properties(self):
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.MakeModal(True)
        self.SetMinSize((400, 400))
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_base_2 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_1 = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_1.Add(self.label_confirmation, 0, 0, 0)
        grid_sizer_1.Add(self.gauge, 0, wx.EXPAND, 0)
        grid_sizer_1.Add(self.tree_taches, 1, wx.EXPAND, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_1.Add(grid_sizer_boutons, 1, wx.EXPAND, 0)
        self.panel_base_2.SetSizer(grid_sizer_1)
        grid_sizer_1.AddGrowableRow(2)
        grid_sizer_1.AddGrowableCol(0)
        sizer_base_2.Add(self.panel_base_2, 1, wx.ALL|wx.EXPAND, 10)
        self.panel_base_1.SetSizer(sizer_base_2)
        sizer_base.Add(self.panel_base_1, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()
        self.Centre()


    def OnClose(self, event):
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        event.Skip()
        
    def OnBoutonAnnuler(self, event) :
        
        try :
            if self.thread1.isAlive():
                # Arret du processus
                self.thread1.abort()
            else:
                # Fermeture après la fin du processus
                self.MakeModal(False)
                FonctionsPerso.SetModalFrameParente(self)
                if self.GetParent().GetName() == "panel_applicModele" :
                    self.GetParent().Fermer()
                else:
                    self.GetParent().Destroy()
                try :
                    self.GetGrandParent().GetGrandParent().GetGrandParent().MAJpanelPlanning()
                except :
                    pass
                self.Destroy()
        except :
            # Fermeture de la fenêtre avant lancement du processus
            self.MakeModal(False)
            FonctionsPerso.SetModalFrameParente(self)
            self.Destroy()
        
    def OnBoutonOk(self, event):
  
        self.thread1 = threadAction(self, self.listeCreationsTaches)
        self.thread1.start()
        
    def EnregistrementTaches(self, listeCreationsTaches) :
        """ Enregistrement des taches dans la base de données """        
        listeExceptions = []
        
        # Récupération des dates de jours fériés
        self.listeFeriesFixes, self.listeFeriesVariables = self.Importation_Feries()
        
        # Initialisation de la connexion avec la Base de données
        DB = GestionDB.DB()
        
        self.bouton_annuler.SetFocus()
        self.bouton_ok.Hide()
        self.bouton_annuler.SetBitmapLabel(wx.Bitmap(Chemins.GetStaticPath("Images/BoutonsImages/Arreter_L72.png"), wx.BITMAP_TYPE_ANY))
        
        nbreTaches = len(listeCreationsTaches)
        interrompu = False
        
        x = 1
        for tache in listeCreationsTaches :
            
            IDpersonne = tache[0]
            date = tache[1]
            heure_debut = tache[2]
            heure_fin = tache[3]
            IDcategorie = tache[4]
            intitule = tache[5]
            
            valide = True

            # Vérifie qu'aucune tâche n'existe déjà à ce moment dans la base de données
            req = """
            SELECT IDpresence, date, heure_debut, heure_fin
            FROM presences
            WHERE (date='%s' AND IDpersonne=%d)  AND
            (heure_debut<'%s' And heure_fin>'%s');
            """ % (str(date), IDpersonne, heure_fin, heure_debut)
            DB.ExecuterReq(req)
            listePresences = DB.ResultatReq()
            nbreResultats = len(listePresences)
            
            # Récupération de l'itemTache correspondant pour actualiser le treeCtrl
            itemTache = self.tree_taches.dictItemsTree[ (IDpersonne, date, heure_debut, heure_fin) ]

            # Un ou des présences existent à ce moment, donc pas d'enregistrement
            if nbreResultats != 0 :
                valide = False
            
            # Vérifie que ce n'est pas un jour férié
            if self.inclureFeries == False :
                if (date.day, date.month) in self.listeFeriesFixes :
                    valide = False
                else:
                    if date in self.listeFeriesVariables :
                        valide = False
                
            # Enregistrement si la date est bien valide
            if valide == True :
                # Traitement de l'item
                listeDonnees = [    ("IDpersonne",     IDpersonne),
                                            ("date",               str(date)),
                                            ("heure_debut",    heure_debut),
                                            ("heure_fin",        heure_fin),
                                            ("IDcategorie",     IDcategorie),
                                            ("intitule",            intitule),
                                ]
                # Enregistrement dans la base
                ID = DB.ReqInsert("presences", listeDonnees)
                # Affiche "Ok" dans le TreeCtrl
                self.tree_taches.ChangeImage(itemTache, True)
            
            else:
                # Si date non valide : on crée un rapport
                dictPersonnes = self.GetParent().list_ctrl_personnes.dictPersonnes
                nomPersonne = dictPersonnes[IDpersonne][0] + " " + dictPersonnes[IDpersonne][1]
                listeExceptions.append((nomPersonne, DatetimeDateEnStr(date), (heure_debut, heure_fin)))
                
                # Affiche "Ok" dans le TreeCtrl
                self.tree_taches.ChangeImage(itemTache, False)
            
                
            # Avance la gauge de 1
            self.gauge.SetValue(x)
            # Met à jour le label d'information
            pourcentage = (x * 100) / nbreTaches
            message =  str(pourcentage) + _(u" % - Veuillez patienter durant la création des tâches... ")
            self.label_confirmation.SetLabel(message)
            
            if self.thread1.stop == True:
                interrompu = True
                break
            
            x += 1
                
        self.listeExceptions = listeExceptions
        # Fermeture de la base de données
        DB.Close()
        
        # Arrêt du thread
        self.thread1.abort()
        
        if interrompu == True :
            message = _(u"Vous avez interrompu le processus ! Cliquez sur Ok pour quitter.")
            self.label_confirmation.SetLabel(message)
        else:
            self.AffichageExceptions()
        self.bouton_annuler.SetBitmapLabel(wx.Bitmap(Chemins.GetStaticPath("Images/BoutonsImages/Ok_L72.png"), wx.BITMAP_TYPE_ANY))

            
    
    def AffichageExceptions(self) :
        # Lecture de la liste des exceptions
        nbreInvalides =len(self.listeExceptions)
        nbreValides = len(self.listeCreationsTaches) - nbreInvalides
        
        if nbreInvalides != 0 :
            if nbreInvalides == 1 :
                message = _(u"1 tâche n'a pas pu être enregistrée.")
            else:
                message = str(nbreInvalides) + _(u" tâches n'ont pas pu être enregistrées.")
        else:
            message = _(u"Toutes les tâches ont été créées avec succès.")
        self.label_confirmation.SetLabel(message)
        
    def Importation_Feries(self):
        """ Importation des dates des jours fériés """

        req = "SELECT * FROM jours_feries;"
        DB = GestionDB.DB()
        DB.ExecuterReq(req)
        listeFeriesTmp = DB.ResultatReq()
        DB.Close()
        
        listeFeriesFixes = []
        listeFeriesVariables = []
        for ID, type, nom, jour, mois, annee in listeFeriesTmp :
            if type =="fixe" :
                date = (jour, mois)
                listeFeriesFixes.append(date)            
            else:
                date = datetime.date(annee, mois, jour)
                listeFeriesVariables.append(date)
        return listeFeriesFixes, listeFeriesVariables
    
    
##        if nbreInvalides != 0 :
##            message = ""
##            if nbreValides == 0 : message += _(u"Aucune tâche n'a été correctement enregistrée.\n\nL")
##            elif nbreValides == 1 : message += str(nbreValides) + _(u" tâche a été correctement enregistrée.\n\nMais l")
##            else: message += str(nbreValides) + _(u" tâches ont été correctement enregistrées.\n\nMais l")
##            if nbreInvalides == 1 :
##                message += _(u"a tâche de la liste suivante n'a pas pu être saisie car elle chevauchait une ou plusieurs des tâches existantes. ")
##                message += _(u"Vous devrez donc d'abord supprimer ou modifier les horaires de ces tâches existantes avant de pouvoir saisir celle-ci.\n\n")
##            else:
##                message += _(u"es ") + str(nbreInvalides) + _(u" tâches de la liste suivante n'ont pas pu être saisies car elles chevauchaient des tâches existantes. ")
##                message += _(u"Vous devrez donc d'abord supprimer ou modifier les horaires de ces tâches existantes avant de pouvoir saisir celles-ci.\n\n")
##            for exception in self.listeExceptions :
##                message += "   > Le " + exception[1] + " pour " + exception[0] + " de " + exception[2][0] + u" à " + exception[2][1] + ".\n"
##            dlg = wx.lib.dialogs.ScrolledMessageDialog(self, message, _(u"Rapport d'erreurs"))
##            dlg.ShowModal()
        
        
        

class Abort(Exception): 
    pass 

class threadAction(Thread): 

    def __init__(self, parent, listeCreationsTaches): 
        Thread.__init__(self) 
        self.parent = parent
        self.stop = False 
        self.listeCreationsTaches = listeCreationsTaches

    def run(self): 
        try: 
            self.parent.EnregistrementTaches(self.listeCreationsTaches) 
        except Abort, KeyBoardInterrupt: 
            pass
            
        except: 
            self.stop = True 
            raise 
            

    def abort(self): 
        self.stop = True
  


class TreeCtrlTaches(wx.TreeCtrl):
    def __init__(self, parent):
        wx.TreeCtrl.__init__(self, parent, -1, wx.DefaultPosition, wx.DefaultSize, style=wx.TR_NO_BUTTONS | wx.TR_NO_LINES )
        # Autres styles possibles = wx.TR_HAS_BUTTONS|wx.TR_EDIT_LABELS| wx.TR_MULTIPLE|wx.TR_HIDE_ROOT
        self.parent = parent
        self.dictTaches = self.GetGrandParent().GetParent().dictTaches
        
        # ImageList pour le treeCtrl
        self.il = wx.ImageList(16,16)
        self.imgOk = self.il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ok.png"), wx.BITMAP_TYPE_PNG))
        self.imgPasOk = self.il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Interdit.png"), wx.BITMAP_TYPE_PNG))
        self.imgRacine = self.il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Document.png"), wx.BITMAP_TYPE_PNG))
        self.imgPersonne = self.il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Homme.png"), wx.BITMAP_TYPE_PNG))
        self.imgDate = self.il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Calendrier_jour.png"), wx.BITMAP_TYPE_PNG))
        self.SetImageList(self.il)
        
        self.dictItemsTree = {}
        self.dictDatesTree = {}
        
        self.Remplissage() 




    def Remplissage(self):
        self.DeleteAllItems()
        
        # Création de la racine
        self.root = self.AddRoot(_(u"Tâches à créer :"))
        self.SetPyData(self.root, None)
        # Image
        self.SetItemImage(self.root, self.imgRacine, wx.TreeItemIcon_Normal)
        
        # Création des noeux noms de personnes
        for key in self.dictTaches.keys():
            IDpersonne = key[0]
            nomPersonne = key[1]
            itemPersonne = self.AppendItem(self.root, nomPersonne)
            self.SetPyData(itemPersonne, IDpersonne)
            # Image
            self.SetItemImage(itemPersonne, self.imgPersonne, wx.TreeItemIcon_Normal)
            
            
            for date in self.dictTaches[key]:
                itemDate = self.AppendItem(itemPersonne, str(date)) 
                self.SetPyData(itemDate, None)
                # Image
                self.SetItemImage(itemDate, self.imgDate, wx.TreeItemIcon_Normal)
                # Mémorisation de l'item Date du TreeCtrl
                self.dictDatesTree[ (IDpersonne, date) ] = itemDate
                
                index = 0
                for tache in self.dictTaches[key][date]:
                    horaires = tache[0][0][:2] + "h" + tache[0][0][3:] + "-" + tache[0][1][:2] + "h" + tache[0][1][3:]
                    categorie = tache[1]
                    intitule = tache[2]
                    detailTache = horaires + " : " + categorie
                    if intitule != "" :
                        detailTache += " (" + intitule + ")"
                    itemTache = self.AppendItem(itemDate, detailTache)
                    self.SetPyData(itemTache, None)
                    
                    # Mémorisation de l'item TreeCtrl
                    self.dictItemsTree[ (IDpersonne, date, tache[0][0], tache[0][1]) ] = itemTache
                    
                    index += 1
                
                self.SortChildren(itemDate)            
            self.SortChildren(itemPersonne)
            
            # Tri des dates
            for date in self.dictTaches[key]:
                item = self.dictDatesTree[ (IDpersonne, date) ] 
                self.SetItemText(item, DatetimeDateEnStr(date))
        
        # Tri des personnes
        self.SortChildren(self.root)
            
        self.ExpandAll() 
        self.ScrollTo(self.root)
        self.SetMinSize((300, 250))
    
    def ChangeImage(self, itemTache, etat):
        """ Change l'image des tâches dans le TreeCtrl """
        if etat == True : 
            img = self.imgOk
        else:
            img = self.imgPasOk
        self.SetItemImage(itemTache, img, wx.TreeItemIcon_Normal)
        self.EnsureVisible(itemTache)


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = Frm_confirm_appli(None)
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
