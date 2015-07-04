#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from UTILS_Traduction import _
import os
import glob
import zipfile
from modulefinder import ModuleFinder


def listdirectory(path):
    listeFichiers = filter(os.path.isfile, glob.glob(path + os.sep + '*'))
    return listeFichiers

def CreationSource(nomZip = "teamworks_source.zip"):
    """ Création du ZIP Source publique """
    # Recherche des modules importés
    print "Recherche des modules..."
    finder = ModuleFinder()
    finder.run_script('Teamworks.py')
    listeModules = []
    for nom, mod in finder.modules.iteritems():
        cheminFichier = mod.__file__
        if cheminFichier != None and "Teamworks" in cheminFichier :
            cheminFichier = cheminFichier.replace(os.getcwd(), "")
            if cheminFichier.startswith("\\") :
                cheminFichier = cheminFichier[1:]
            listeModules.append(cheminFichier)
    listeModules.sort() 

    # Affichage des modules trouvés
    print len(listeModules), "modules trouves."
        
    # Initialisation du ZIP
    if os.path.isfile(nomZip) == True :
        os.remove(nomZip)
    zfile = zipfile.ZipFile(nomZip, 'w', compression=zipfile.ZIP_DEFLATED)

    # Insertion des fichiers
    data_files=[
        
          ('Aide', glob.glob('Aide\\*.*')),
          ('Data', ["Data\\Exemple_TDATA.dat", "Data\\Exemple_TPHOTOS.dat", "Data\\Exemple_TDOCUMENTS.dat"] ),
          
          ('Documents\\Editions', listdirectory('Documents\\Editions')),
          ('Documents\\Modeles', listdirectory('Documents\\Modeles')),
          
          ('Images\\16x16', listdirectory('Images\\16x16')),
          ('Images\\22x22', listdirectory('Images\\22x22')),
          ('Images\\32x32', listdirectory('Images\\32x32')),
          ('Images\\48x48', listdirectory('Images\\48x48')),
          ('Images\\80x80', listdirectory('Images\\80x80')),
          ('Images\\128x128', listdirectory('Images\\128x128')),
          ('Images\\Bandeaux', listdirectory('Images\\Bandeaux')),
          ('Images\\BoutonsImages', listdirectory('Images\\BoutonsImages')),
          ('Images\\Drapeaux', listdirectory('Images\\Drapeaux')),
          ('Images\\Petits boutons', listdirectory('Images\\Petits boutons')),
          ('Images\\Special', listdirectory('Images\\Special')),
          ('Images\\CadresPhotos', listdirectory('Images\\CadresPhotos')),
          ('Images\\Teamword', listdirectory('Images\\Teamword')),
          
          ('Temp', glob.glob('Temp\\*.*')),
          ('Updates', glob.glob('Updates\\*.*')),
          
          # Fichiers à importer :
          ('', ['Licence.txt', 'Versions.txt', 'Defaut.dat', 'Villes.db3', 'twico.ico',
                'msvcm90.dll', 'msvcp90.dll', 'msvcr90.dll',
                'Microsoft.VC90.CRT.manifest',
                'gdiplus.dll', ]), 
           ]

    for rep, listeFichiers in data_files :
        
        if len(listeFichiers) > 0 :
            # Création des fichiers :
            for fichier in listeFichiers :
                zfile.write(fichier, fichier)
        else :
            # Création d'un répertoire vide
            zfi = zipfile.ZipInfo(rep)
            zfi.external_attr = 16
            zfile.writestr(zfi, '')

    print "Insertion fichiers ok."

    # Insertion des modules importés
    for fichier in listeModules :
        zfile.write(fichier, fichier)
        
    zfile.close()
    print "Zip ok."





if __name__ == _(u"__main__"):
    CreationSource()
