#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
# Copyright:    (c) 2008-09 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------

from Utils.UTILS_Traduction import _

import sys
import socket
import os
import time

try :
    import uno
    import unohelper
    from com.sun.star.beans import PropertyValue
except :
    message = u"""
    Teamworks n'arrive pas à communiquer avec OpenOffice.
    
    Si OpenOffice est bien installé sur votre ordinateur, vous pourrez sûrement résoudre le problème  avec la méthode suivante :
    1. Quittez Teamworks
    2. Ouvrez le terminal (Menu Applications > Accessoires > Terminal
    3. Tapez-y le texte suivant :
        sudo ldconfig -v /usr/lib/openoffice/program
    4. Tapez sur la touche Entrée puis saisissez votre mot de passe administrateur
    5. Attendez quelques instants, quittez le terminal puis relancez Teamworks
    Le problème devrait être résolu définitivement. Sinon contactez le créateur de Teamworks.
    """
    dlg = wx.MessageDialog(None, message, _(u"Erreur de communication avec OpenOffice"), wx.OK | wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()


class Pilotage():
    """ Classe pour piloter OOO Writer avec PyUno """
    def __init__(self):
        self.document = None
        print('Lancement du pilotage...')
        try:
            self.ctx = self.start_client()
        except Exception as exc:
            print('... Serveur non actif. Lancement du serveur ...')
            status = os.system("/usr/bin/soffice '-accept=socket,host=localhost,port=2002;urp;StarOffice.ServiceManager' -nodefault -nofirststartwizard") # -noheadless pour rendre invisible, -nologo  pour pas afficher le splash screen de ooo
            time.sleep(2)
            self.ctx = self.start_client()
            
        print('Connexion au serveur ...')
        smgr = self.ctx.ServiceManager
        self.desktop = smgr.createInstanceWithContext( "com.sun.star.frame.Desktop",self.ctx)
        

    def start_client(self):
        print('Demarrage du client ...')
        context = uno.getComponentContext()
        resolver = context.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", context)
        ctx = resolver.resolve("uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext")
        return ctx
    
    def Ouvrir_doc(self, cheminDoc="", visible=True):
        print('Ouvrir un document...')
        url = unohelper.systemPathToFileUrl(cheminDoc)
        self.document = self.desktop.loadComponentFromURL(cheminDoc, "_blank", 0, ())
        self.document.CurrentController.Frame.ContainerWindow.Visible = visible
    
    def Creer_doc(self, visible=True):
        print('Creation document...')
        self.document = self.desktop.loadComponentFromURL("private:factory/swriter", "_blank", 0, ())
        self.document.CurrentController.Frame.ContainerWindow.Visible = visible
        
##        self.document = self.desktop.getCurrentComponent()
        
    def Ecrire_exemple(self, listeValeurs=[]):
        print('Ecrit un texte exemple...')
        texte = u"""Je viens de créer pour vous un nouveau document OpenOffice WRITER. Vous pouvez maintenant y saisir le texte de votre choix. Pour insérer des données pour le publipostage, c'est très simple : tapez son mot-clé ! Exemple : "Je suis {CIVILITE} {NOM}" donnera après le publipostage "Je suis David DUPOND"... \n
Voici la liste des mots-clés du contrat en cours. Elle vous aidera à écrire votre texte : \n\n"""
        for motCle, valeur in listeValeurs :
            texte += "  - {" + motCle + "} \n"
        texte += _(u"\n(Effacez bien-sûr ce petit texte d'introduction après l'avoir lu !!!)")
        
        objText = self.document.Text
        objCursor = objText.createTextCursor()
        objText.insertString(objCursor, texte, 0)
    
    def Fermer_doc(self):
        print('Fermer le document...')
        self.document.dispose()
        self.document = None
    
    def Quitter(self):
        print('Quitter ooo...')
        self.ctx.ServiceManager

    def Remplacer_valeurs(self, listeValeurs=[]):
        print('Publipostage...')
        listeRemplacements = []
        listeNotFind = []
        for motCle, valeur in listeValeurs :
            orempl = self.document.createReplaceDescriptor()
            orempl.SearchString= "{" + motCle + "}"
            orempl.ReplaceString= valeur
            orempl.SearchWords = True  #mots entiers seulement ?
            orempl.SearchCaseSensitive = True    # sensible à la casse ?
            nbre = self.document.replaceAll(orempl)
            
            listeRemplacements.append((motCle, valeur, nbre))
            if nbre == 0 : listeNotFind.append((motCle, valeur))
        
        if len(listeNotFind) == 0 :
            txtPublipostage = _(u"\n\n> Toutes les valeurs ont été placées dans le document.")
        else:
            if len(listeNotFind) == 1 :
                txtPublipostage = _(u"\n\n> Remarque : Un mot-clé n'a pas été dans le document : ")
            else:
                txtPublipostage = _(u"\n\n> Remarque : Certains mot-clés n'ont pas été trouvés dans le document : ")
            for item in listeNotFind :
                txtPublipostage += "{" + item[0] + "}, "
            txtPublipostage = txtPublipostage[:-2] + "."
        
        print("Remplacement valeurs fini...")
        return txtPublipostage
    
    def Sauvegarder_doc(self, cheminDoc=""):
        print('Sauvegarde...')
        dest = "file:///" + cheminDoc.replace("\\", "/")
        args = ()
        self.document.storeAsURL(dest, args)
        txtSave = _(u"\n\n> Document sauvegardé sur votre ordinateur.")
        print("Sauvegarde doc...")
        return txtSave


##                # Choix de l'imprimante
##                nomImprimante = self.combo_box_imprimante.GetStringSelection()
##                warg = []
##                
##                #todo : Choix de l'imprimante pour publipostage de contrat sous ooo
                
    ##            warg = []
    ##            prop = objServiceManager.CreateInstance("com.sun.star.beans.PropertyValue")
    ##            prop.Name = 'Printer'
    ##            prop.Value = nomImprimante
    ##            warg[2]=prop 
                
    ##            def createStruct(nom, objServiceManager):
    ##                objCoreReflection=objServiceManager.createInstance("com.sun.star.reflection.CoreReflection")
    ##                classSize = objCoreReflection.forName(nom)
    ##                aStruct=[1, 2]
    ##                classSize.createObject(aStruct)
    ##                return aStruct 
    ##            
    ##            prop=createStruct("com.sun.star.beans.PropertyValue", objServiceManager)
    ##            prop[2].Name = 'Printer'
    ##            prop[2].Value = nomImprimante
                
            
    ##            warg = []
    ##            warg2 = objServiceManager.Bridge_GetStruct("com.sun.star.beans.PropertyValue")
    ##            warg2[0].Name = 'Printer'
    ##            warg2[0].Value = nomImprimante
    
    def Imprimer_doc(self, nbreExemplaires=1):
        txtImpress = ""
        try :
            args = ()
            for x in range(nbreExemplaires) :
                uno.invoke(self.document, "print", (args, ))
                print("Impression...")
                time.sleep(2) # Attend 2 secondes que le doc soit envoyé à l'imprimante, sinon bug !
            txtImpress = _(u"\n\n> Document imprimé en ") + str(nbreExemplaires) + " exemplaire(s)."
        except :
            txtImpress = _(u"\n\n> Problème d'impression.")
        return txtImpress
    
                       
        

##ooo = Pilotage()
##ooo.Ouvrir_doc("/home/ggamer/TestOOO.odt")
##ooo.Creer_doc()
##ooo.Ecrire_exemple()
##ooo.Fermer_doc()
##ooo.Quitter()
 
