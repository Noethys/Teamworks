#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
# Copyright:    (c) 2008-09 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------

import wx
import CTRL_Questionnaire
import GestionDB

try: import psyco; psyco.full()
except: pass


class Panel(wx.Panel):
    def __init__(self, parent, id=-1, IDpersonne=0):
        wx.Panel.__init__(self, parent, id, name="panel_pageQuestionnaire", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDpersonne = IDpersonne
        self.majEffectuee = False
        
        # Widgets
        self.staticBox_staticbox = wx.StaticBox(self, -1, u"Questionnaire")
        self.ctrl_questionnaire = CTRL_Questionnaire.CTRL(self, type="individu", IDindividu=self.IDpersonne, 
                                                                                        largeurReponse=335)
        
        self.__do_layout()
        
        # MAJ
        self.MAJ() 


    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        staticBox = wx.StaticBoxSizer(self.staticBox_staticbox, wx.VERTICAL)
        staticBox.Add(self.ctrl_questionnaire, 1, wx.EXPAND|wx.ALL, 5)
        grid_sizer_base.Add(staticBox, 1, wx.EXPAND|wx.ALL, 5)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)

    def MAJ(self):
        """ MAJ integrale du controle avec MAJ des donnees """
        if self.majEffectuee == True :
            return
        self.ctrl_questionnaire.MAJ() 
        self.majEffectuee = True
        
    def ValidationData(self):
        """ Return True si les données sont valides et pretes à être sauvegardées """
        return True
    
    def Sauvegarde(self):
        valeurs = self.ctrl_questionnaire.GetValeurs() 
        dictReponses = self.ctrl_questionnaire.GetDictReponses() 
        dictValeursInitiales = self.ctrl_questionnaire.GetDictValeursInitiales()
        
        # Sauvegarde
        DB = GestionDB.DB()
        for IDquestion, reponse in valeurs.iteritems() :            
            # Si la réponse est différente de la réponse initiale
            if reponse != dictValeursInitiales[IDquestion] or reponse == "##DOCUMENTS##" :

                if dictReponses.has_key(IDquestion):
                    IDreponse = dictReponses[IDquestion]["IDreponse"]
                else:
                    IDreponse = None
                
                # Si c'est un document, on regarde s'il y a des docs à sauver
                sauvegarder = True
                if reponse == "##DOCUMENTS##" :
                    nbreDocuments = self.ctrl_questionnaire.GetNbreDocuments(IDquestion)
                    if nbreDocuments == 0 :
                        sauvegarder = False
                
                # Sauvegarde la réponse
                if sauvegarder == True :
                    listeDonnees = [    
                        ("IDquestion", IDquestion),
                        ("IDindividu", self.IDpersonne),
                        ("reponse", reponse),
                        ]
                    if IDreponse == None :
                        IDreponse = DB.ReqInsert("questionnaire_reponses", listeDonnees)
                    else:
                        DB.ReqMAJ("questionnaire_reponses", listeDonnees, "IDreponse", IDreponse)
                
                # Sauvegarde du contrôle Porte-documents
                if reponse == "##DOCUMENTS##" :
                    nbreDocuments = self.ctrl_questionnaire.SauvegardeDocuments(IDquestion, IDreponse)
                    if nbreDocuments == 0 and IDreponse != None :
                        DB.ReqDEL("questionnaire_reponses", "IDreponse", IDreponse)
                
        DB.Close()
