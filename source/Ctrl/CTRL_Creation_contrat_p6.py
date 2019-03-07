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
import FonctionsPerso
import GestionDB


def getRGB(winColor):
    b = winColor >> 16
    g = winColor >> 8 & 255
    r = winColor & 255
    return (r,g,b)

class Page(wx.Panel):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwds)
        self.parent = self.GetGrandParent()
        
        self.label_titre = wx.StaticText(self, -1, _(u"Fin de l'assistant de création de contrat"))
        
        # Label Html
        txtIntro = u"""
        <FONT face="Arial" color="#000000" size=2>
        <P>Vous avez saisi toutes les données du contrat. Cliquez sur le bouton 'Valider' pour terminer l'assistant.</P>
        <p>Vous pouvez ensuite par exemple imprimer ce contrat ou la déclaration unique d'embauche correspondante.</p>
        </FONT>
        """ 
        self.label_intro = FonctionsPerso.TexteHtml(self, texte=txtIntro, Enabled=False)
        
        self.__set_properties()
        self.__do_layout()
        
    def __set_properties(self):
        self.label_titre.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=6, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_base.Add(self.label_titre, 0, 0, 0)
        grid_sizer_base.Add(self.label_intro, 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 20)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(1)
        

    def Validation(self):
        
        # Enregistrement des données
        dictContrats = self.GetGrandParent().dictContrats
        dictChamps = self.GetGrandParent().dictChamps
        DB = GestionDB.DB()

        # Enregistrement des données du CONTRAT 
        listeDonnees = [    ("IDpersonne",     dictContrats["IDpersonne"]),
                                    ("IDclassification",dictContrats["IDclassification"]),
                                    ("IDtype",    dictContrats["IDtype"]),
                                    ("valeur_point",        dictContrats["valeur_point"]),
                                    ("date_debut",     dictContrats["date_debut"]),
                                    ("date_fin",            dictContrats["date_fin"]),
                                    ("date_rupture",            dictContrats["date_rupture"]),
                                    ("essai",            dictContrats["essai"]),
                                ]
        
        if dictContrats["IDcontrat"] == 0 :
            # Ajout
            listeDonnees.append(("signature", ""))
            listeDonnees.append(("due", ""))
            IDcontrat = DB.ReqInsert("contrats", listeDonnees)
            DB.Commit()
        else:
            # Modification
            DB.ReqMAJ("contrats", listeDonnees, "IDcontrat", dictContrats["IDcontrat"])
            DB.Commit()
            IDcontrat = dictContrats["IDcontrat"]

        # Enregistrement des données des CHAMPS 
        
        # Crée une liste des champs existants déjà pour ce contrat
        req = "SELECT IDval_champ, IDchamp FROM contrats_valchamps WHERE (IDcontrat=%d AND type='contrat')  ;" % IDcontrat
        DB.ExecuterReq(req)
        listeChampsDB = DB.ResultatReq()
        nbreResultats = len(listeChampsDB)
        
        # On regarde chaque champ un par un
        for IDchamp, valeur in dictChamps.iteritems() :
            
            listeDonnees = [ ("IDchamp",     IDchamp),
                                    ("type",            "contrat"),
                                    ("valeur",          valeur),
                                    ("IDcontrat",     IDcontrat),
                                    ("IDmodele",     0),
                                ]
            
            # Recherche si le champ existe déjà dans la base
            modif = False
            for IDval_champDB, IDchampDB in listeChampsDB :
                if IDchampDB == IDchamp :
                    # Le champ existe déjà, alors on le modifie :
                    DB.ReqMAJ("contrats_valchamps", listeDonnees, "IDval_champ", IDval_champDB)
                    DB.Commit()
                    modif = True
                    
            if modif == False :
                # Le champ n'existe pas dans la base, alors on le créée :
                ID = DB.ReqInsert("contrats_valchamps", listeDonnees)
                DB.Commit()
        
        # On efface les champs déjà créés qui ne sont plus utilisés :
        for IDval_champDB, IDchampDB in listeChampsDB :
            
            trouve = False
            for IDchamp, valeur in dictChamps.iteritems() : 
                if IDchampDB == IDchamp : trouve = True
            
            if trouve == False :
                # On l'efface :
                DB.ReqDEL("contrats_valchamps", "IDval_champ", IDval_champDB)
                
        # Fermeture de la DB
        DB.Close()
        
        # Recherche si un parent est à mettre à jour
        if FonctionsPerso.FrameOuverte("FicheIndividuelle") != None :
            self.GetGrandParent().GetParent().list_ctrl_contrats.Remplissage()
            self.GetGrandParent().GetParent().MAJ_barre_problemes() 
           
        return True

