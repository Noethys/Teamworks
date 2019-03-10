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


class Page(wx.Panel):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwds)       

        self.label_titre = wx.StaticText(self, -1, _(u"Cr�ation d'un mod�le de contrat"))
        self.label_intro = wx.StaticText(self, -1, _(u"Saisissez un nom et une description pour ce mod�le :"))
        
        self.label_nom = wx.StaticText(self, -1, "Nom :")
        self.text_nom = wx.TextCtrl(self, -1, "")
        
        self.label_description = wx.StaticText(self, -1, "Description :")
        self.text_description = wx.TextCtrl(self, -1, "", style = wx.TE_MULTILINE)

        self.__set_properties()
        self.__do_layout()
        
        # Importation des donn�es
        self.Importation()

    def __set_properties(self):
        self.label_titre.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.label_titre, 0, 0, 0)
        grid_sizer_base.Add(self.label_intro, 0, wx.LEFT, 20)
        grid_sizer_contenu = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_contenu.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.text_nom, 1, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.label_description, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.text_description, 1, wx.EXPAND, 0)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.EXPAND, 20)
        grid_sizer_contenu.AddGrowableCol(1)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        
    
    def Importation(self):
        """ Remplit les controles avec les donn�es import�es si c'est une modification """
        dictModeles = self.GetGrandParent().dictModeles
        nom = dictModeles["nom"]
        self.text_nom.SetValue(nom)
        description= dictModeles["description"]
        self.text_description.SetValue(description)
                        
    def Validation(self):
        
        # V�rifie qu'un nom a �t� saisi
        if self.text_nom.GetValue() == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom pour ce mod�le !"), "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            self.text_nom.SetFocus()
            return False     
        
        # Enregistrement des donn�es
        dictModeles = self.GetGrandParent().dictModeles
        dictChamps = self.GetGrandParent().dictChamps
        DB = GestionDB.DB()
        
        # Enregistrement des donn�es du MODELE 
        listeDonnees = [    
                                    ("IDclassification",    dictModeles["IDclassification"]),
                                    ("IDtype",                  dictModeles["IDtype"]),
                                    ("nom",                  self.text_nom.GetValue()),
                                    ("description",            self.text_description.GetValue()),
                                   
                                ]
        
        if dictModeles["IDmodele"] == 0 :
            # Ajout
            IDmodele = DB.ReqInsert("contrats_modeles", listeDonnees)
            DB.Commit()
        else:
            # Modification
            DB.ReqMAJ("contrats_modeles", listeDonnees, "IDmodele", dictModeles["IDmodele"])
            DB.Commit()
            IDmodele = dictModeles["IDmodele"]

        # Enregistrement des donn�es des CHAMPS 
        
        # Cr�e une liste des champs existants d�j� pour ce contrat
        req = "SELECT IDval_champ, IDchamp FROM contrats_valchamps WHERE (IDmodele=%d AND type='modele')  ;" % IDmodele
        DB.ExecuterReq(req)
        listeChampsDB = DB.ResultatReq()
        nbreResultats = len(listeChampsDB)
        
        # On regarde chaque champ un par un
        for IDchamp, valeur in dictChamps.items() :
            
            listeDonnees = [ ("IDchamp",     IDchamp),
                                    ("type",            "modele"),
                                    ("valeur",          valeur),
                                    ("IDmodele",     IDmodele),
                                    ("IDcontrat",     0),
                                ]
            
            # Recherche si le champ existe d�j� dans la base
            modif = False
            for IDval_champDB, IDchampDB in listeChampsDB :
                if IDchampDB == IDchamp :
                    # Le champ existe d�j�, alors on le modifie :
                    DB.ReqMAJ("contrats_valchamps", listeDonnees, "IDval_champ", IDval_champDB)
                    DB.Commit()
                    modif = True
                    
            if modif == False :
                # Le champ n'existe pas dans la base, alors on le cr��e :
                ID = DB.ReqInsert("contrats_valchamps", listeDonnees)
                DB.Commit()
        
        # On efface les champs d�j� cr��s qui ne sont plus utilis�s :
        for IDval_champDB, IDchampDB in listeChampsDB :
            
            trouve = False
            for IDchamp, valeur in dictChamps.items() : 
                if IDchampDB == IDchamp : trouve = True
            
            if trouve == False :
                # On l'efface :
                DB.ReqDEL("contrats_valchamps", "IDval_champ", IDval_champDB)
                
        # Fermeture de la DB
        DB.Close()
        
        # Recherche si un parent est � mettre � jour
        if FonctionsPerso.FrameOuverte("panel_config_Modeles_Contrats") != None :
            self.GetGrandParent().GetParent().MAJ_ListCtrl()         
           
        return True

