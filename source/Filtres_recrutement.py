#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
# Copyright:    (c) 2008-09 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------

import wx
import FonctionsPerso
import GestionDB
import datetime
import wx.lib.hyperlink as hl

import Filtre_coches
import Filtre_choice
import Filtre_texte
import Selection_periode


def GetListeChoix_emplois():
    DB = GestionDB.DB()        
    req = """SELECT IDemploi, intitule
    FROM emplois; """
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close()
    listeDonnees.insert(0, (0, u"Candidature spontan�e"))
    return listeDonnees

def GetListeChoix_fonctions():
    DB = GestionDB.DB()        
    req = """SELECT IDfonction, fonction
    FROM fonctions; """
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close()
    return listeDonnees

def GetListeChoix_affectations():
    DB = GestionDB.DB()        
    req = """SELECT IDaffectation, affectation
    FROM affectations; """
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close()
    return listeDonnees

def GetListeChoix_decisions():
    listeDonnees = [ (0, u"D�cision non prise"), (1, u"Oui"), (2, u"Non") ]
    return listeDonnees

def GetListeChoix_reponses():
    listeDonnees = [ (0, u"Non"), (1, u"Oui") ]
    return listeDonnees

def GetListeChoix_civilites():
    listeDonnees = [ (0, u"Mr"), (1, u"Melle"), (2, u"Mme") ]
    return listeDonnees

def GetListeChoix_avis():
    listeDonnees = [ (0, u"Avis inconnu"), (1, u"Pas convaincant"), (2, u"Mitig�"), (3, u"Bien"), (4, u"Tr�s bien") ]
    return listeDonnees

def GetListeChoix_diffuseurs():
    DB = GestionDB.DB()        
    req = """SELECT IDdiffuseur, diffuseur
    FROM diffuseurs; """
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close()
    return listeDonnees

def GetListeChoix_diplomes():
    DB = GestionDB.DB()        
    req = """SELECT IDtype_diplome, nom_diplome
    FROM types_diplomes; """
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close()
    return listeDonnees


class MyDialog(wx.Dialog):
    """ On r�cup�re les infos de cette bo�te avec GetDates() ou avec GetPersonnesPresentes() """
    def __init__(self, parent, id=-1, categorie="", listeValeursDefaut=[], title=u"S�lection de filtres de liste"):
        wx.Dialog.__init__(self, parent, id, title, size=(-1, -1))
        self.categorie = categorie
        
        self.dictControles = {
        
            "candidats" : [
                    #[ u"Civilit�", "candidats_civilite", "hyperlink_liste", "civilites", "civilite", None],
                    [ u"Nom", "candidats_nom", "hyperlink_texte", None, "nom", None],
                    [ u"Pr�nom", "candidats_prenom", "hyperlink_texte", None, "prenom", None],
                    [ u"Adresse", "candidats_adresse_resid", "hyperlink_texte", None, "adresse_resid", None],
                    [ u"Code postal", "candidats_cp_resid", "hyperlink_texte", None, "cp_resid", None],
                    [ u"Ville", "candidats_ville_resid", "hyperlink_texte", None, "ville_resid", None],
                    [ u"M�mo", "candidats_memo", "hyperlink_texte", None, "memo", None],
                    [ u"Qualifications", "candidats_qualifications", "hyperlink_liste", "diplomes", "IDdiplome", None],
                    ], # Label, nomControle, typeControle, listeChoix, motSQL, valeur
                                    
            "candidatures" : [
                    [ u"Date de d�p�t", "candidature_date", "hyperlink_date", None, "date_depot", None],
                    [ u"Offre d'emploi", "candidature_emploi", "hyperlink_liste", "emplois", "IDemploi", None],
                    [ u"Disponibilites", "candidature_dispo", "hyperlink_date", None, ("date_debut", "date_fin"), None],
                    [ u"Fonctions", "candidature_fonctions", "hyperlink_liste", "fonctions", "IDfonction", None],
                    [ u"Affectations", "candidature_affectations", "hyperlink_liste", "affectations", "IDaffectation", None],
                    [ u"D�cision", "candidature_decision", "hyperlink_liste", "decisions", "IDdecision", None],
                    [ u"R�ponse envoy�e", "candidature_reponse", "hyperlink_liste", "reponses", "reponse", None],
                    [ u"Date de r�ponse", "candidature_date_reponse", "hyperlink_date", None, "date_reponse", None],
                    ], # Label, nomControle, typeControle, listeChoix, motSQL, valeur
            
            "entretiens" : [
                    [ u"Date", "entretiens_date", "hyperlink_date", None, "date", None],
                    [ u"Avis", "entretiens_avis", "hyperlink_liste", "avis", "avis", None],
                    [ u"Commentaire", "entretiens_commentaire", "hyperlink_texte", None, "remarques", None],
                    ], # Label, nomControle, typeControle, listeChoix, motSQL, valeur
        
            "emplois" : [
                    [ u"Date de lancement", "emplois_date_debut", "hyperlink_date", None, "date_debut", None],
                    [ u"Date de cl�ture", "emplois_date_fin", "hyperlink_date", None, "date_fin", None],
                    [ u"Disponibilites", "emplois_dispo", "hyperlink_date", None, ("date_debut", "date_fin"), None],
                    [ u"Fonctions", "emplois_fonctions", "hyperlink_liste", "fonctions", "IDfonction", None],
                    [ u"Affectations", "emplois_affectations", "hyperlink_liste", "affectations", "IDaffectation", None],
                    [ u"Diffuseurs", "emplois_diffuseurs", "hyperlink_liste", "diffuseurs", "IDdiffuseur", None],
                    ], # Label, nomControle, typeControle, listeChoix, motSQL, valeur
                                    
        }
        
        # R�cup�ration des valeurs par d�faut
        if len(listeValeursDefaut) > 0 :
            self.SetValeursDefaut(listeValeursDefaut)

        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)
        
        # Label
        self.label = wx.StaticText(self, -1, u"Veuillez d�finir les filtres de votre choix :")
        grid_sizer_base.Add(self.label, 0, wx.ALL, 10)
        
        # Contr�les       
        self.listeControles = self.dictControles[self.categorie]
        self.staticbox = wx.StaticBox(self, -1, self.categorie.capitalize())
        sizerStaticBox = wx.StaticBoxSizer(self.staticbox, wx.HORIZONTAL)
        grid_sizer_contenu = wx.FlexGridSizer(len(self.listeControles), 2, 5, 5)
        
        for label, nomControle, typeControle, listeChoix, motSQL, valeur in self.listeControles :
            ctrl_label = wx.StaticText(self, -1, u"%s :" % label)
            grid_sizer_contenu.Add(ctrl_label, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
            if listeChoix != None :
                exec("self.ctrl_%s = %s(self, valeur=valeur, nomFiltre=label, listeChoix=listeChoix, motSQL=motSQL)" % (nomControle, typeControle))
            else:
                exec("self.ctrl_%s = %s(self, valeur=valeur, nomFiltre=label, motSQL=motSQL)" % (nomControle, typeControle))
            exec("grid_sizer_contenu.Add(self.ctrl_%s, 0, wx.EXPAND|wx.ALL, 0)" % nomControle)
        
        sizerStaticBox.Add(grid_sizer_contenu, 0, wx.EXPAND|wx.ALL, 10)
        grid_sizer_base.Add(sizerStaticBox, 1, wx.ALL|wx.EXPAND, 10)
        
        # Boutons
        self.bouton_reinitialiser = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Reinitialiser.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, wx.ID_CANCEL, wx.Bitmap("Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))
        
        # Fin Layout
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_reinitialiser, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.SetMinSize((550, -1))
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CentreOnScreen()
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonReinit, self.bouton_reinitialiser)
    
    def OnBoutonOk(self, event):
        self.EndModal(wx.ID_OK)
    
    def OnBoutonReinit(self, event):
        """ R�initialiser les param�tres """
        index = 0
        for item in self.dictControles[self.categorie] :
            nomControle = item[1]
            exec("self.ctrl_%s.valeur = None" % nomControle)
            exec("self.ctrl_%s.SetLabel(self.ctrl_%s.GetLabel())" % (nomControle, nomControle))
            index += 1
            
                    
    def GetListeFiltres(self):
        listeFiltres = []
        for labelTemp, nomControle, typeControle, listeChoix, motSQL, valeurTemp in self.dictControles[self.categorie] :
            exec("valeur = self.ctrl_%s.valeur" % nomControle)
            exec("sql = self.ctrl_%s.GetSQL()" % nomControle)
            exec("label = self.ctrl_%s.GetLabel()" % nomControle)
            exec("labelControle = self.ctrl_%s.nomFiltre" % nomControle)
            if valeur != None : 
                dict = { "nomControle" : nomControle,
                            "label" : label,
                            "labelControle" : labelControle,
                            "valeur" : valeur,
                            "sql" : sql,
                            }
                listeFiltres.append(dict)
        return listeFiltres
    
    def SetValeursDefaut(self, listeFiltres):
        """ R�cup�re les valeurs par d�faut des contr�les """
        for dict in listeFiltres :
            nomControle = dict["nomControle"]
            valeur = dict["valeur"]
            # Int�gre la valeur par d�faut dans le dictionnaire des contr�les
            index = 0
            for item in self.dictControles[self.categorie] :
                if item[1] == nomControle :
                    self.dictControles[self.categorie][index][5] = valeur
                index += 1



class Hyperlink(hl.HyperLinkCtrl):
    def __init__(self, parent, id=-1, label="test", infobulle="test infobulle", URL="", size=(-1, -1)):
        hl.HyperLinkCtrl.__init__(self, parent, id, label, URL=URL, size=size)
        
        # Construit l'hyperlink
        self.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False))
        self.AutoBrowse(False)
        self.SetColours("BLUE", "BLUE", "BLUE")
        self.EnableRollover(True)
        self.SetUnderlines(False, False, True)
        self.SetBold(False)
        self.SetToolTip(wx.ToolTip(infobulle))
        self.UpdateLink()
        self.DoPopup(False)
        self.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLeftLink)
    
    def OnLeftLink(self, event):
        """ S�lectionner les donn�es � importer """        
        self.ChangeValeur()





class hyperlink_date(Hyperlink):
    def __init__(self, parent, valeur=None, nomFiltre="", motSQL="", infobulle=u"Cliquez ici pour s�lectionner un filtre"):
        self.valeur = valeur
        self.nomFiltre = nomFiltre
        self.motSQL = motSQL
        self.label = self.GetLabel()
        Hyperlink.__init__(self, parent, label=self.label, infobulle=infobulle)
    
    def GetLabel(self):
        if self.valeur == None :
            label = u"Sans importance"
        else:
            date_debut, date_fin = self.valeur
            if date_debut == date_fin :
                label = u"Le %s" % date_debut.strftime("%d/%m/%Y")
            else:
                label = u"Entre le %s et le %s" % (date_debut.strftime("%d/%m/%Y"), date_fin.strftime("%d/%m/%Y"))
        return label
    
    def ChangeValeur(self):
        dlg = Selection_periode.SelectionPeriode(self)
        if self.valeur != None :
            dlg.SetDates(date_debut=self.valeur[0], date_fin=self.valeur[1])
        if dlg.ShowModal() == wx.ID_OK:
            date_min, date_max = dlg.GetDates()
            dlg.Destroy()
            self.valeur = (date_min, date_max)
            self.SetLabel(self.GetLabel())
        else:
            dlg.Destroy()
    
    def GetSQL(self):
        # Si aucune importance
        if self.valeur == None : return ""
        date_debut, date_fin = self.valeur
        if type(self.motSQL) == tuple :
            # P�riode
            return "(%s>='%s' AND %s<='%s')" % (self.motSQL[1], date_debut, self.motSQL[0], date_fin)
        else:
            # Dates
            if date_debut == date_fin :
                return "%s='%s'" % (self.motSQL, date_debut)
            else:
                return "%s>='%s' AND %s<='%s'" % (self.motSQL, date_debut, self.motSQL, date_fin) 


class hyperlink_choice(Hyperlink):
    def __init__(self, parent, valeur=None, nomFiltre="", motSQL="", listeChoix=[], infobulle=u"Cliquez ici pour s�lectionner un filtre"):
        self.valeur = valeur
        self.nomFiltre = nomFiltre
        self.listeChoix = listeChoix
        self.motSQL = motSQL
        self.label = self.GetLabel()
        Hyperlink.__init__(self, parent, label=self.label, infobulle=infobulle)
    
    def GetLabel(self):
        if self.valeur == None :
            label = u"Sans importance"
        else:
            ID, label = self.valeur
        return label
    
    def ChangeValeur(self):
        if self.valeur == None :
            selection = None
        else:
            selection = self.valeur[0]
        exec("liste = GetListeChoix_%s()" % self.listeChoix)
        dlg = Filtre_choice.MyDialog(self, nom_filtre=self.nomFiltre, titre_frame = u"Filtre", selection=selection, listeChoix = liste)
        if dlg.ShowModal() == wx.ID_OK:
            ID, label = dlg.GetSelection()
            dlg.Destroy()
            self.valeur = ID, label
            self.SetLabel(self.GetLabel())
        else:
            dlg.Destroy()
    
    def GetSQL(self):
        # Si aucune importance
        if self.valeur == None : 
            return ""
        else:
            return "%s=%s" % (self.motSQL, self.valeur[0])


class hyperlink_liste(Hyperlink):
    def __init__(self, parent, valeur=None, nomFiltre="", motSQL="", listeChoix=[], infobulle=u"Cliquez ici pour s�lectionner un filtre"):
        self.valeur = valeur
        self.nomFiltre = nomFiltre
        self.listeChoix = listeChoix
        self.motSQL = motSQL
        self.label = self.GetLabel()
        Hyperlink.__init__(self, parent, label=self.label, infobulle=infobulle)
    
    def GetLabel(self):
        if self.valeur == None :
            label = u"Sans importance"
        else:
            if len(self.valeur) == 0 :
                label = u"Aucun �l�ment"
            else:
                label = ""
                for ID, texte in self.valeur : 
                    label += texte + ", "
                label = label[:-2]
        return label
    
    def ChangeValeur(self):
        if self.valeur == None :
            listeSelection = None
        else:
            listeSelection = []
            for ID, texte in self.valeur : 
                listeSelection.append(ID)
        exec("liste = GetListeChoix_%s()" % self.listeChoix)
        dlg = Filtre_coches.MyDialog(self, nom_filtre=self.nomFiltre, titre_frame = u"Filtre", listeSelection=listeSelection, listeChoix = liste)
        if dlg.ShowModal() == wx.ID_OK:
            listeSelections = dlg.GetListeSelections()
            dlg.Destroy()
            self.valeur = listeSelections
            self.SetLabel(self.GetLabel())
        else:
            dlg.Destroy()
    
    def GetSQL(self):
        # Si aucune importance
        if self.valeur == None : 
            return ""
        # Autres valeurs
        else:
            if len(self.valeur) == 0 :
                return "%s=Null" % self.motSQL
            elif len(self.valeur) == 1 :
                return "%s=%d" % (self.motSQL, self.valeur[0][0])
            else:
                listeID = []
                for ID, label in self.valeur :
                    listeID.append(ID)
                return "%s IN %s" % (self.motSQL, tuple(listeID))



class hyperlink_texte(Hyperlink):
    def __init__(self, parent, valeur=None, nomFiltre="", motSQL="", infobulle=u"Cliquez ici pour s�lectionner un filtre"):
        self.valeur = valeur
        self.nomFiltre = nomFiltre
        self.motSQL = motSQL
        self.label = self.GetLabel()
        Hyperlink.__init__(self, parent, label=self.label, infobulle=infobulle)
    
    def GetLabel(self):
        if self.valeur == None :
            label = u"Sans importance"
        else:
            label = u"Avec l'expression '%s'" % self.valeur
        return label
    
    def ChangeValeur(self):
        if self.valeur == None :
            selection = None
        else:
            selection = self.valeur
        dlg = Filtre_texte.MyDialog(self, nom_filtre=self.nomFiltre, titre_frame = u"Filtre", texte=selection)
        if dlg.ShowModal() == wx.ID_OK:
            texte = dlg.GetTexte()
            dlg.Destroy()
            self.valeur = texte
            self.SetLabel(self.GetLabel())
        else:
            dlg.Destroy()
    
    def GetSQL(self):
        # Si aucune importance
        if self.valeur == None : 
            return ""
        else:
            return "%s LIKE '%%%s%%'" % (self.motSQL, self.valeur)
        


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frm = MyDialog(None, categorie="emplois")
    frm.ShowModal()
    app.MainLoop()