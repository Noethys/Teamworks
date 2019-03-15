#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-19 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import datetime
from Data import DATA_Tables as Tables
import GestionDB



class DB(GestionDB.DB):
    def __init__(self, *args, **kwds):
        GestionDB.DB.__init__(self, *args, **kwds)

    def Upgrade(self, versionFichier=(0, 0, 0, 0) ) :
        """ Adapte un fichier obsolète à la version actuelle du logiciel """

        # Filtres de conversion

        # =============================================================

        # Filtre pour passer de la version 1 à la version 2 de Teamworks
        versionFiltre = (2, 0, 0, 0)
        if versionFichier < versionFiltre:
            try:
                from Utils import UTILS_Procedures
                UTILS_Procedures.A2000(nomFichier=self.nomFichierCourt)
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (2, 0, 0, 1)
        if versionFichier < versionFiltre:
            try:
                if self.IsTableExists("questionnaire_questions") == False: self.CreationTable("questionnaire_questions", Tables.DB_DATA)
                if self.IsTableExists("questionnaire_categories") == False: self.CreationTable("questionnaire_categories", Tables.DB_DATA)
                if self.IsTableExists("questionnaire_choix") == False: self.CreationTable("questionnaire_choix", Tables.DB_DATA)
                if self.IsTableExists("questionnaire_reponses") == False: self.CreationTable("questionnaire_reponses", Tables.DB_DATA)
                from Utils import UTILS_Procedures
                UTILS_Procedures.D1051(nomFichier=self.nomFichierCourt)
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (2, 1, 0, 1)
        if versionFichier < versionFiltre:
            try:
                if self.IsTableExists("profils") == False: self.CreationTable("profils", Tables.DB_DATA)
                if self.IsTableExists("profils_parametres") == False: self.CreationTable("profils_parametres", Tables.DB_DATA)
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================







        return True








if __name__ == "__main__":
    pass