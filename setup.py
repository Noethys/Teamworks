#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------
# Auteur:       Ivan LUCAS
# Copyright:    (c) 2008-19 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------

# cd C:\Users\X\Documents\GitHub\Teamworks
# C:\Users\X\Documents\GitHub\Teamworks\venv\Scripts\Activate.bat
# python setup.py build


import sys, os
import glob
import os.path
import shutil
from cx_Freeze import setup, Executable

# Chemins
REP_COURANT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REP_COURANT)
TEAMWORKS_PATH = os.path.join(REP_COURANT, "teamworks")
sys.path.insert(1, TEAMWORKS_PATH)
REP_BUILD = REP_COURANT + "/build/exe.win32-3.7"
PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))

# Supprime le répertoire build
if os.path.isdir(REP_BUILD):
    shutil.rmtree(REP_BUILD)


def GetVersion():
    """ Recherche du numéro de version """
    fichierVersion = open(os.path.join(TEAMWORKS_PATH, "Versions.txt"), "r")
    txtVersion = fichierVersion.readlines()[0]
    fichierVersion.close()
    pos_debut_numVersion = txtVersion.find("n")
    pos_fin_numVersion = txtVersion.find(":")
    numVersion = txtVersion[pos_debut_numVersion+1:pos_fin_numVersion].strip()
    return numVersion

base = 'Console'
if sys.platform == 'win32':
    base = 'Win32GUI'


options = {
    'build_exe': {
        'excludes': [
            'gtk', 'PyQt4', 'PyQt5', 'Tkinter',
            '_gtkagg', '_tkagg', '_agg2', '_cairo', '_cocoaagg',
            '_fltkagg', '_gtk', '_gtkcairo',
            'backend_qt', 'backend_qt4', 'backend_qt4agg',
            'backend_qtagg',
            'backend_cairo', 'backend_cocoaagg',
            'Tkconstants', 'Tkinter', 'tcl', 'numpy.core._dotblas', 'libopenblas',
            "_imagingtk", "PIL._imagingtk", "ImageTk", "PIL.ImageTk", "FixTk",
            ],
        'includes': [
            'Gadget', 'numpy.core._methods', 'numpy.lib.format', 'email.mime.image',
            ],
        'include_files': [
            TEAMWORKS_PATH + '/static', TEAMWORKS_PATH + '/Versions.txt', TEAMWORKS_PATH + '/Licence.txt', TEAMWORKS_PATH + '/Icone.ico',
            os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'libcrypto-1_1.dll'), os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'libssl-1_1.dll'),
            ],
    }
}

executables = [
    Executable('teamworks/Teamworks.py', base=base, icon=TEAMWORKS_PATH + "/icone.ico"),
]

setup(name='Teamworks',
    version=GetVersion(),
    author=u"Ivan LUCAS",
    description=u"Teamworks, le logiciel libre et gratuit de gestion d'équipes",
    executables=executables,
    options=options,
    )


# Suppression des fichiers en double
def listdirectory(path):
    fichier=[]
    l = glob.glob(path+'\\*')
    for i in l:
        if os.path.isdir(i):
            fichier.append(i)
            fichier.extend(listdirectory(i))
        else: fichier.append(i)
    return fichier

def Supprimer(chemin_fichier):
    if os.path.isdir(chemin_fichier):
        shutil.rmtree(chemin_fichier)
    else:
        os.remove(chemin_fichier)

liste_fichiers = listdirectory(REP_BUILD)
dict_fichiers = {}
for chemin_fichier in liste_fichiers:
    nom_rep, nom_fichier = os.path.split(chemin_fichier)
    if nom_fichier in ["python37.dll", "VCRUNTIME140.dll"] and "lib" in nom_rep:
        Supprimer(chemin_fichier)
        print("Suppression de", chemin_fichier)

    if nom_fichier in [".libs", "SelfTest"]:
        Supprimer(chemin_fichier)
        print("Suppression de", chemin_fichier)

    if "wininst-" in nom_fichier:
        Supprimer(chemin_fichier)
        print("Suppression de", chemin_fichier)

shutil.rmtree(REP_BUILD + "/lib/matplotlib/mpl-data")
shutil.rmtree(REP_BUILD + "/mpl-data/sample_data")