#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
# Copyright:    (c) 2008-09 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------

import Chemins
from Utils.UTILS_Traduction import _
import six
import wx
import wx.html as  html
import GestionDB
import datetime
import os
import sys
import shutil
from Utils import UTILS_Config
from Utils import UTILS_Fichiers

if six.PY3:
    import functools


def cmp(x, y):
    if x < y:
        return -1
    elif x > y:
        return 1
    else:
        return 0

def SortItems(items, sorter):
    """ Adaptation py3 pour le tri des wx.listctrl """
    if six.PY3:
        items.sort(key=functools.cmp_to_key(sorter))
    else:
        items = SortItems(items, sorter)
    return items


def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def DateFrEng(textDate):
    text = str(textDate[6:10]) + "/" + str(textDate[3:5]) + "/" + str(textDate[:2])
    return text

# --------------------------------------------------------------------------------------------------------

def BoucleFrameOuverte(nom, WindowEnCours) :
    """ Est utilis�e dans FrameOuverte """
    for children in WindowEnCours.GetChildren():
        if children.GetName() == nom : return children
        if len(children.GetChildren()) > 0 :
            tmp = BoucleFrameOuverte(nom, children)
            if tmp != None : return tmp
    return None

def FrameOuverte(nom) :
    """ Permet de savoir si une frame est ouverte ou pas..."""
    topWindow = wx.GetApp().GetTopWindow() 
    # Analyse le TopWindow
    if topWindow.GetName() == nom : return True
    # Analyse les enfants de topWindow
    reponse = BoucleFrameOuverte(nom, topWindow)
    return reponse

def SetModalFrameParente(frameActuelle):
    """ Rend modale la frame parente """
    try :
        frameActuelle.GetParent().GetTopLevelParent().MakeModal(True)
    except : 
        pass

# -------------------------------------------------------------------------------------------------------
# Fonction qui modifie le wx.StaticText pour g�rer le redimensionnement des StaticText

class StaticWrapText(wx.StaticText):
    """A StaticText-like widget which implements word wrapping."""
    
    def __init__(self, *args, **kwargs):
        wx.StaticText.__init__(self, *args, **kwargs)

        # store the initial label
        self.__label = super(StaticWrapText, self).GetLabel()

        # listen for sizing events
        self.Bind(wx.EVT_SIZE, self.OnSize)
        
    def SetLabel(self, newLabel):
        """Store the new label and recalculate the wrapped version."""
        self.__label = newLabel
        self.__wrap()

    def GetLabel(self):
        """Returns the label (unwrapped)."""
        return self.__label
    
    def __wrap(self):
        """Wraps the words in label."""
        words = self.__label.split()
        lines = []

        # get the maximum width (that of our parent)
        if 'phoenix' in wx.PlatformInfo:
            max_width = self.GetParent().GetVirtualSize()[0]-20
        else:
            max_width = self.GetParent().GetVirtualSizeTuple()[0] - 20
        
        index = 0
        current = []

        for word in words:
            current.append(word)

            if self.GetTextExtent(" ".join(current))[0] > max_width:
                del current[-1]
                lines.append(" ".join(current))

                current = [word]

        # pick up the last line of text
        lines.append(" ".join(current))

        # set the actual label property to the wrapped version
        super(StaticWrapText, self).SetLabel("\n".join(lines))

        # refresh the widget
        self.Refresh()
        
    def OnSize(self, event):
        # dispatch to the wrap method which will 
        # determine if any changes are needed
##        self.__wrap()
##        self.GetParent().Layout()
        pass

# -------------------------------------------------------------------------------------------------------



class TexteHtml(wx.Panel):
    def __init__(self, parent, texte="", Enabled=False, ID=-1):
        wx.Panel.__init__(self, parent, ID, style=wx.TAB_TRAVERSAL)
            
        # Cr�ation du widget HTML
        self.pageHtml = html.HtmlWindow(self, -1)
        self.pageHtml.SetPage(texte)

        # Param�tres du widget HTML
        #self.couleurFond = self.getRGB(win32api.GetSysColor(15)) # Pour archive
        self.couleurFond = wx.SystemSettings.GetColour(30)
        self.pageHtml.SetBackgroundColour(self.couleurFond)
        if Enabled == False : self.pageHtml.Enable(False)

        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_base.Add(self.pageHtml, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)

    def getRGB(self, winColor):
        b = winColor >> 16
        g = winColor >> 8 & 255
        r = winColor & 255
        return (r,g,b)

    def SetText(self, texte ="") :
        self.pageHtml.SetPage(texte)
        self.pageHtml.SetBackgroundColour(self.couleurFond)


# ---------------------------------------------------------------------------------------------------------

##def Recup_liste_pb_personnes(recalc=False):
##    """ R�cup�ration de la liste des probl�mes des personnes """
##    try :
##        topWindow = wx.GetApp().GetTopWindow()
##        nomWindow = topWindow.GetName()
##    except :
##        nomWindow = None
##    if nomWindow == "general" : 
##        # Si la frame 'General' est charg�e, on y r�cup�re la liste des problemes
##        if recalc == True :
##            topWindow.dictNomsPersonnes, topWindow.dictProblemesPersonnes = Creation_liste_pb_personnes()
##        return topWindow.dictNomsPersonnes, topWindow.dictProblemesPersonnes
##    else:
##        # On cr��e la liste
##        dictNomsPersonnes, dictProblemesPersonnes = Creation_liste_pb_personnes()
##        return dictNomsPersonnes, dictProblemesPersonnes


def Recup_liste_pb_personnes(recalc=False):
    """ R�cup�ration de la liste des probl�mes des personnes """
    
    topWindow = wx.GetApp().GetTopWindow()
    nomWindow = topWindow.GetName()
##    print ">>>", nomWindow
    # Si Recalcul des donn�es obligatoire :
    if recalc == True :
        print(_(u"Recalcul obligatoire des donnees"))
        topWindow.dictNomsPersonnes, topWindow.dictProblemesPersonnes = Creation_liste_pb_personnes()
        return topWindow.dictNomsPersonnes, topWindow.dictProblemesPersonnes
    
    # Si ce n'est qu'une r�cup�ration des donn�es :
    try :
        # On essaie de r�cup�rer les dictionnaires dans la topWindow
        dictNomsPersonnes = topWindow.dictNomsPersonnes
        dictProblemesPersonnes = topWindow.dictProblemesPersonnes
##        print _(u"Recuperation dans le topWindow")
        return dictNomsPersonnes, dictProblemesPersonnes
    except :
        topWindow.dictNomsPersonnes, topWindow.dictProblemesPersonnes = Creation_liste_pb_personnes()
##        print _(u"Recuperation dans la topWindow impossible : on calcule les donnees")
        return topWindow.dictNomsPersonnes, topWindow.dictProblemesPersonnes

    
    
def Creation_liste_pb_personnes():
    """ Cr�ation de la liste des probl�mes des personnes """
    listeIDpersonne = Recherche_ContratsEnCoursOuAVenir()
    dictNomsPersonnes, dictProblemesPersonnes = Recherche_problemes_personnes(listeIDpersonnes = tuple(listeIDpersonne))
    return dictNomsPersonnes, dictProblemesPersonnes
                
def Recherche_problemes_personnes(listeIDpersonnes = (), infosPersonne=[]):
    """ Recherche les probl�mes dans les dossiers des personnes """
    
    dictProblemes = {}
    dictNoms = {}
    
    #
    # Analyse des fiches individuelles
    #
    
    if len(listeIDpersonnes) == 0 : listeIDpersonnesTmp = "(100000)"
    elif len(listeIDpersonnes) == 1 : listeIDpersonnesTmp = "(%d)" % listeIDpersonnes[0]
    else : listeIDpersonnesTmp = str(tuple(listeIDpersonnes))
    
    DB = GestionDB.DB()        
    req = """SELECT IDpersonne, civilite, nom, nom_jfille, prenom, date_naiss, cp_naiss, ville_naiss, pays_naiss, nationalite, num_secu, adresse_resid, cp_resid, ville_resid, IDsituation
    FROM personnes WHERE IDpersonne IN %s ORDER BY nom; """ % listeIDpersonnesTmp
    DB.ExecuterReq(req)
    listePersonnes = DB.ResultatReq()
    
    # R�cup�re ici les infos directement dans les contr�les de la fiche individuelle
    if len(infosPersonne) != 0 :
        listePersonnes = infosPersonne

    for personne in listePersonnes :
        IDpersonne = personne[0]
        civilite = personne[1]
        nom = personne[2]
        nom_jfille = personne[3]
        prenom = personne[4]
        date_naiss = personne[5]
        cp_naiss = personne[6]
        ville_naiss = personne[7]
        pays_naiss = personne[8]
        nationalite = personne[9]
        num_secu = personne[10]
        adresse_resid = personne[11]
        cp_resid = personne[12]
        ville_resid = personne[13]
        IDsituation = personne[14]
        
        dictNoms[IDpersonne] = nom + " " + prenom
        problemesFiche = []
        
        # Civilit�
        if civilite == "" or civilite == None : problemesFiche.append( (_(u"Civilit�")) )
        # Nom
        if nom == "" or nom == None : problemesFiche.append( (_(u"Nom de famille")) )
        # Nom de jeune fille
        if civilite == "Mme" :
            if nom_jfille == "" or nom_jfille == None : problemesFiche.append( (_(u"Nom de jeune fille")) )
        # Pr�nom
        if prenom == "" or prenom == None : problemesFiche.append( (_(u"Pr�nom")) )
        # Date de naissance
        if str(date_naiss).strip(" ") == "" or date_naiss == None : problemesFiche.append( (_(u"Date de naissance")) )
        # CP_naissance
        if str(cp_naiss).strip(" ") == "" or cp_naiss == None : problemesFiche.append( (_(u"Code postal de la ville de naissance")) )
        # Ville de naissance
        if ville_naiss == "" or ville_naiss == None : problemesFiche.append( (_(u"Ville de naissance")) )
        # Pays de naissance
        if pays_naiss == "" or pays_naiss == None or pays_naiss == 0 : problemesFiche.append( (_(u"Pays de naissance")) )
        # Nationalite
        if nationalite == "" or nationalite == None or nationalite == 0 : problemesFiche.append( (_(u"Nationalit�")) )
        # Num S�cu
        if str(num_secu).strip(" ") == "" or num_secu == None : problemesFiche.append( (_(u"Num�ro de s�curit� sociale")) )
        # Adresse r�sidence
        if adresse_resid == "" or adresse_resid == None : problemesFiche.append( (_(u"Adresse de r�sidence")) )
        # Code postal r�sidence
        if str(cp_resid).strip(" ") == "" or cp_resid == None : problemesFiche.append( (_(u"Code postal de r�sidence")) )
        # Ville r�sidence
        if ville_resid == "" or ville_resid == None : problemesFiche.append( (_(u"Ville de r�sidence")) )
        # Situation
        if IDsituation == "" or IDsituation == None or IDsituation == 0 : problemesFiche.append( (_(u"Situation sociale")) )

    
        # Analyse des coordonn�es
        req = """SELECT IDcoord
        FROM coordonnees
        WHERE IDpersonne=%d;
        """ % IDpersonne
        DB.ExecuterReq(req)
        listeCoords = DB.ResultatReq()
        
        if len(listeCoords) == 0 : 
            problemesFiche.append( (_(u"Coordonn�es t�l�phoniques")) )
        
        # Met les donn�es dans le dictionnaire
        if len(problemesFiche) != 0 : 
            if (IDpersonne in dictProblemes) == False : dictProblemes[IDpersonne] = {}
            if len(problemesFiche) == 1 : 
                categorie = _(u"1 information manquante")
            else:
                categorie = str(len(problemesFiche))  + _(u" informations manquantes")
            dictProblemes[IDpersonne][categorie] = problemesFiche
            
    
    #
    # Analyse des pi�ces � fournir
    #
    
    date_jour = datetime.date.today()
    
    for IDpersonne in listeIDpersonnes :
        piecesManquantes = []
        piecesPerimees = []
        DictPieces = {}
        
        # Recherche des pi�ces SPECIFIQUES que la personne doit fournir...
        req = """
        SELECT types_pieces.IDtype_piece, types_pieces.nom_piece
        FROM diplomes INNER JOIN diplomes_pieces ON diplomes.IDtype_diplome = diplomes_pieces.IDtype_diplome INNER JOIN types_pieces ON diplomes_pieces.IDtype_piece = types_pieces.IDtype_piece
        WHERE diplomes.IDpersonne=%d;
        """ % IDpersonne
        DB.ExecuterReq(req)
        listePiecesAFournir = DB.ResultatReq()
        
        if type(listePiecesAFournir) != list :
            listePiecesAFournir = list(listePiecesAFournir)
        
        # Recherche des pi�ces BASIQUES que la personne doit fournir...
        req = """
        SELECT diplomes_pieces.IDtype_piece, types_pieces.nom_piece
        FROM diplomes_pieces INNER JOIN types_pieces ON diplomes_pieces.IDtype_piece = types_pieces.IDtype_piece
        WHERE diplomes_pieces.IDtype_diplome=0;
        """ 
        DB.ExecuterReq(req)
        listePiecesBasiquesAFournir = DB.ResultatReq()
        
        listePiecesAFournir.extend(listePiecesBasiquesAFournir)
        
        # Recherche des pi�ces que la personne poss�de
        req = """
        SELECT types_pieces.IDtype_piece, pieces.date_debut, pieces.date_fin
        FROM types_pieces LEFT JOIN pieces ON types_pieces.IDtype_piece = pieces.IDtype_piece
        WHERE (pieces.IDpersonne=%d AND pieces.date_debut<='%s' AND pieces.date_fin>='%s')
        ORDER BY pieces.date_fin;
        """ % (IDpersonne, date_jour, date_jour)
        DB.ExecuterReq(req)
        listePieces = DB.ResultatReq()
        dictTmpPieces = {}
        for IDtype_piece, date_debut, date_fin in listePieces :
            dictTmpPieces[IDtype_piece] = (date_debut, date_fin)
        
        # Passe en revue toutes les pi�ces � fournir et regarde si la personne poss�de les pi�ces correspondantes
        for IDtype_piece, nom_piece in listePiecesAFournir :
            if (IDtype_piece in dictTmpPieces) == True :
                date_debut = dictTmpPieces[IDtype_piece][0]
                date_fin = dictTmpPieces[IDtype_piece][1]
                # Recherche la validit�
                date_fin = datetime.date(int(date_fin[:4]), int(date_fin[5:7]), int(date_fin[8:10]))
                reste = str(date_fin - date_jour)
                if reste != "0:00:00":
                    jours = int(reste[:reste.index("day")])
                    if jours < 15  and jours > 0:
                        etat = "Attention"
                    elif jours <= 0:
                        etat = "PasOk"
                    else:
                        etat = "Ok"
                else:
                    etat = "Attention"
            else:
                etat = "PasOk"
            DictPieces[IDtype_piece] = (etat, nom_piece)
        

        for IDtype_piece, donnees in DictPieces.items() :
            etat, nom_piece = donnees
            if etat == "Ok": continue
            if etat == "PasOk" :
                piecesManquantes.append(nom_piece)
            if etat == "Attention" :
                piecesPerimees.append(nom_piece)

    
        # Met les listes de probl�mes dans un dictionnaire
        if len(piecesManquantes) != 0 : 
            if (IDpersonne in dictProblemes) == False : dictProblemes[IDpersonne] = {}
            if len(piecesManquantes) == 1 : 
                categorie = _(u"1 pi�ce manquante")
            else:
                categorie = str(len(piecesManquantes))  + _(u" pi�ces manquantes")
            dictProblemes[IDpersonne][categorie] = piecesManquantes

        if len(piecesPerimees) != 0 : 
            if (IDpersonne in dictProblemes) == False : dictProblemes[IDpersonne] = {}
            if len(piecesPerimees) == 1 : 
                categorie = _(u"1 pi�ce bient�t p�rim�e")
            else:
                categorie = str(len(piecesPerimees))  + _(u" pi�ces bient�t p�rim�es")
            dictProblemes[IDpersonne][categorie] = piecesPerimees
        
        
        # Analyse des contrats
        problemesContrats = []
        req = """SELECT IDpersonne, signature, due
        FROM contrats 
        WHERE IDpersonne = %d
        ORDER BY date_debut;""" % IDpersonne
        DB.ExecuterReq(req)
        listeContrats = DB.ResultatReq()
        
        for contrat in listeContrats :
            signature = contrat[1]
            due = contrat[2]
            # Signature
            if signature == "" or signature == "Non" : 
                txt = _(u"Contrat non sign�")
                problemesContrats.append( (txt) )
            # DUE
            if due == "" or due == "Non" : 
                txt = _(u"DUE � faire")
                problemesContrats.append( (txt) )
        
        # Met les donn�es dans le dictionnaire
        if len(problemesContrats) != 0 : 
            if (IDpersonne in dictProblemes) == False : dictProblemes[IDpersonne] = {}
            if len(problemesContrats) == 1 : 
                categorie = _(u"1 contrat � voir")
            else:
                categorie = str(len(problemesContrats))  + _(u" contrats � voir")
            dictProblemes[IDpersonne][categorie] = problemesContrats
    

    # Fin de la fonction    
    DB.Close()

    return dictNoms, dictProblemes


def Recherche_ContratsEnCoursOuAVenir() :
    """ Renvoie la liste des personnes qui ont ou vont avoir un contrat """
    # Recherche des contrats
    dateDuJour = str(datetime.date.today())
    DB = GestionDB.DB()        
    req = """SELECT contrats.IDpersonne, contrats_class.nom, contrats.date_debut, contrats.date_fin, contrats.date_rupture, contrats_types.duree_indeterminee
    FROM contrats INNER JOIN contrats_class ON contrats.IDclassification = contrats_class.IDclassification INNER JOIN contrats_types ON contrats.IDtype = contrats_types.IDtype
    WHERE (contrats.date_fin>='%s' AND contrats.date_rupture='') OR (contrats.date_rupture<>'' AND contrats.date_rupture>='%s')
    ORDER BY contrats.date_debut;""" % (dateDuJour, dateDuJour)
    DB.ExecuterReq(req)
    listeContrats = DB.ResultatReq()
    DB.Close()
    # Retourne la liste des IDpersonne
    if len(listeContrats) == 0 :
        return []
    else:
        listeIDpersonne = []
        for contrat in listeContrats :
            listeIDpersonne.append(contrat[0])
        return listeIDpersonne



class BarreTitre(wx.Panel):
    def __init__(self, parent, titre=_(u"Titre"), infoBulle="", arrondis=False, couleurFondPanel=None):
        wx.Panel.__init__(self, parent, -1, size=(-1, 20))
        couleurFond = (70, 70, 70)
        # Contr�les
        self.barreTitre = wx.StaticText(self, -1, " " + titre)
        self.barreTitre.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        self.barreTitre.SetBackgroundColour(couleurFond)
        self.barreTitre.SetForegroundColour('White')
        # Panel
        self.SetBackgroundColour(couleurFond)
        self.SetToolTip(wx.ToolTip(infoBulle))
        self.barreTitre.SetToolTip(wx.ToolTip(infoBulle))
        # Positionnement
        sizer_base = wx.BoxSizer(wx.HORIZONTAL)
        sizer_base.Add(self.barreTitre, 0, wx.EXPAND|wx.ALL, 3)
        self.SetSizer(sizer_base)
        
        if arrondis == True :
            # Cr�e des coins arrondis
            self.couleurFondPanel = couleurFondPanel
            self.espaceBord = 0
            self.coinArrondi = 5
            self.hauteurTitre = 40
            self.couleurFondTitre = couleurFond
            # Bind pour dessin
            self.Bind(wx.EVT_PAINT, self.OnPaint)
            self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
   
         
    def OnPaint(self, event):
        dc= wx.PaintDC(self)
        dc= wx.BufferedDC(dc)
        largeurDC, hauteurDC= self.GetSizeTuple()
        dc.SetBackground(wx.Brush(self.couleurFondPanel))
        dc.Clear()       
        dc.SetBrush(wx.Brush(self.couleurFondTitre))
        dc.DrawRoundedRectangle(0+self.espaceBord, 0+self.espaceBord, largeurDC-(self.espaceBord*2), self.hauteurTitre, self.coinArrondi)

    def OnEraseBackground(self, event):
        pass 
        

# ---------------------------------------------------------------------------------------------------------------------------------------------------------


class PanelArrondi(wx.Panel):
    def __init__(self, parent, ID=-1, name="gadget", texteTitre=""):
        wx.Panel.__init__(self, parent, ID, name=name)
        self.texteTitre = texteTitre
        
        self.SetBackgroundColour((122, 161, 230))
        
        # Cr�ation fond
        self.espaceBord = 10
        self.coinArrondi = 5
        self.hauteurTitre = 17
        self.couleurFondDC = self.GetBackgroundColour()
        self.couleurFondCadre = (214, 223, 247)
        self.couleurFondTitre = (70, 70, 70)
        self.couleurBord = (70, 70, 70)
        self.couleurDegrade = (130, 190, 235)
        self.couleurTexteTitre = (255, 255, 255)
        
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)      
        self.Bind(wx.EVT_SIZE, self.OnSize)
         
    def OnPaint(self, event):
        dc= wx.PaintDC(self)
        dc= wx.BufferedDC(dc)
        if 'phoenix' in wx.PlatformInfo:
            largeurDC, hauteurDC= self.GetSize()
        else:
            largeurDC, hauteurDC= self.GetSizeTuple()
        
        # paint le fond
        dc.SetBackground(wx.Brush(self.couleurFondDC))
        dc.Clear()       
        
        # Cadre du groupe
        dc.SetBrush(wx.Brush(self.couleurFondCadre))
        dc.DrawRoundedRectangle(0+self.espaceBord, 0+self.espaceBord, largeurDC-(self.espaceBord*2), hauteurDC-(self.espaceBord*2), self.coinArrondi)
        # Barre de titre
        dc.SetBrush(wx.Brush(self.couleurFondTitre))
        dc.DrawRoundedRectangle(0+self.espaceBord, 0+self.espaceBord, largeurDC-(self.espaceBord*2), self.hauteurTitre+self.coinArrondi, self.coinArrondi)
        # D�grad�
        dc.GradientFillLinear((self.espaceBord+1, self.espaceBord+7, largeurDC-(self.espaceBord*2)-2, self.hauteurTitre-2), (214, 223, 247), (0, 0, 0), wx.NORTH)
        # Cache pour enlever l'arrondi inf�rieur de la barre de titre
        dc.SetBrush(wx.Brush(self.couleurFondCadre))
        dc.SetPen(wx.Pen(self.couleurFondCadre, 0))
        dc.DrawRectangle(self.espaceBord+1, self.espaceBord+self.hauteurTitre+1, largeurDC-(self.espaceBord*2)-2, self.coinArrondi+5)
        # Titre
        font = wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD) 
        dc.SetFont(font)
        dc.SetTextForeground(self.couleurTexteTitre)
        dc.DrawText(self.texteTitre, self.espaceBord+7, self.espaceBord+2)

    def OnEraseBackground(self, event):
        pass   
        
    def OnSize(self, event):
        self.Refresh() 
        event.Skip()
                        
# ----------------------------------------------------------------------------------------------------------------------------------------------------------
        
def sendTextMail():
    """ Envoyer un mail avec smtp """
    import smtplib
    try:
        addressTarget = ("test@wanadoo.fr",)
        smtpServer = 'smtp.orange.fr'
        sourceAddress = 'test@fPython.fr'
        MAIL_SUBJECT="sujet du mail"
        MAIL_CONTENT = _(u"ceci est le contenu du mail")
        
        server = smtplib.SMTP( smtpServer, '25', 'localhost' )
        msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % ( sourceAddress, ", ".join( addressTarget ), MAIL_SUBJECT))
        msg = msg + MAIL_CONTENT
        server.sendmail( sourceAddress, addressTarget, msg )
        server.quit()
        print("Envoi mail Ok")
    except smtplib.SMTPException as msg:
        print(msg)


def EnvoyerMail(adresses = [], sujet="", message=""):
    """ Envoyer un Email avec le client de messagerie par d�faut """
    if "linux" in sys.platform :
        dlg = wx.MessageDialog(None, _(u"D�sol�, cette fonction n'est pas encore disponible dans la version LINUX de Teamworks."), _(u"Fonction indisponible"), wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
        return
        
    if len(adresses) == 1 :
        commande = "start mailto:%s" % adresses[0]
    else:
        commande = "start mailto:%s" % adresses[0] + "?"
        if len(adresses) > 1 :
            commande+= "bcc=%s" % adresses[1]
        for adresse in adresses[2:] :
            commande+= "^&bcc=%s" % adresse
    if sujet != "" : 
        if len(adresses) == 1 : 
            commande += "?"
        else :
            commande += "^&"
        commande += "subject=%s" % sujet
    if message != "" : 
        if len(adresses) == 1 and sujet == "" : 
            commande += "?"
        else:
            commande += "^&"
        commande += "body=%s" % message
    #print commande
    os.system(commande)


class FichierConfig():
    def __init__(self, nomFichier="" ):
        self.nomFichier = nomFichier
        
    def GetDictConfig(self):
        """ R�cup�re une copie du dictionnaire du fichier de config """
        import shelve
        db = shelve.open(self.nomFichier, "r")
        dictDonnees = {}
        for key in list(db.keys()):
            dictDonnees[key] = db[key]
        db.close()
        return dictDonnees
    
    def SetDictConfig(self, dictConfig={} ):
        """ Remplace le fichier de config pr�sent sur le disque dur par le dict donn� """
        import shelve
        db = shelve.open(self.nomFichier, "n")
        for key in list(dictConfig.keys()):
            db[key] = dictConfig[key]
        db.close()
        
    def GetItemConfig(self, key ):
        """ R�cup�re une valeur du dictionnaire du fichier de config """
        import shelve
        db = shelve.open(self.nomFichier, "r")
        valeur = db[key]
        db.close()
        return valeur
    
    def SetItemConfig(self, key, valeur ):
        """ Remplace une valeur dans le fichier de config """
        import shelve
        db = shelve.open(self.nomFichier, "w")
        db[key] = valeur
        db.close()

    def DelItemConfig(self, key ):
        """ Supprime une valeur dans le fichier de config """
        import shelve
        db = shelve.open(self.nomFichier, "w")
        del db[key]
        db.close()
        

# -----------------------------------------  Affiche l'aide -----------------------------------------------------------------------------------



def Aide(numItem=None):
    """ Appel du module d'aide de Windows """
    
##    # Demande le nom du fichier
##    import Aide
##    frm = Aide.Aide(None)
##    frm.ShowModal()
##    return
    
##    # ------- TEMPORAIRE : ---------------
##    txtMessage = _(u"Le syst�me d'aide n'est pas encore fonctionnel (actuellement en cours de r�daction).\n\nVous pouvez tout de m�me trouver actuellement de l'aide sur le forum de TeamWorks � l'adresse suivante : \nhttp://teamworks.forumactif.com (ou cliquez dans la barre de menu sur 'Aide' puis 'Acc�der au Forum').")
##    dlg = wx.MessageDialog(None, txtMessage, _(u"Aide"), wx.OK | wx.ICON_INFORMATION)
##    dlg.ShowModal()
##    dlg.Destroy()
##    return

    
    # -----------------------------------------------    
    nomPage = ""
    nomAncre = ""
    
    dictAide = {
        1 : ("Leplanning", "", _(u"planning")),
        2 : ("ImprimeruneDUE", "", _(u"Edition DUE")),
        3 : ("Envoyerunmailgroup", "", _(u"Envoi mail group�")),
        4 : ("Creerunnouveaufichier", "", _(u"Cr�er un nouveau fichier")),
        5 : ("Imprimerunelistedeprsences", "", _(u"Impression d'une liste de pr�sences")),
        6 : ("Lescontrats", "", _(u"Impression d'un contrat ou d'une DUE")),
        7 : ("Laprotectionparmotdepasse", "", _(u"Saisie du mot de passe d'ouverture")),
        8 : ("Lescatgoriesdeprsences", "", _(u"Config Cat�gories de pr�sences")),
        9 : ("Lespriodesdevacances", "", _(u"Saisie d'une p�riode de vacances")),
        10 : ("Lestypesdecontrats", "", _(u"Config types de contrats")),
        11 : ("Lescatgoriesdeprsences", "", _(u"Saisie d'une cat de pr�sences")),
        12 : ("Personnes", "", _(u"Panneau Personnes")),
        13 : ("Lesvaleursdepoints", "", _(u"Saisie val point")),
        14 : ("Appliquerunmodledeprsences", "creer_modele", _(u"Saisie d'un mod�le")),
        15 : ("Lespaysetnationalits", "", _(u"Config pays")),
        16 : ("Lestypesdepices", "", _(u"Config types pi�ces")),
        17 : ("Lasauvegardeautomatique", "", _(u"Panel sauvegarde automatique")),
        18 : ("Creerunesauvegarde", "", _(u"Cr�er une sauvegarde occasionnelle")),
        19 : ("Restaurerunesauvegarde", "", _(u"Restaurer une sauvegarde")),
        20 : ("Leschampsdecontrats", "", _(u"Saisie champs contrats")),
        21 : ("Ladresse", "", _(u"Gestion des villes")),
        22 : ("Imprimerunefichedefrais", "", _(u"Impression frais")),
        23 : ("Lespaysetnationalits", "", _(u"Saisir un pays")),
        24 : ("Lestypesdesituations", "", _(u"Config situations")),
        25 : ("Gestiondesfraisdedplacements", "", _(u"Gestion des frais")),
        26 : ("Laprotectionparmotdepasse", "", _(u"Config Password")),
        27 : ("Lesvaleursdepoints", "", _(u"Config val_point")),
        28 : ("Rechercherdesmisesjour", "", _(u"Updater")),
        29 : ("Crerunepice", "", _(u"Saisie pi�ces")),
        30 : ("Imprimerdesphotosdepersonnes", "", _(u"Impression_photo")),
        31 : ("Lesmodlesdecontrats", "", _(u"wiz cr�ation modele contrat")),
        32 : ("Laprotectionparmotdepasse", "", _(u"Saisie pwd")),
        33 : ("Saisirunetcheunique", "", _(u"Saisie d'une pr�sence")),
        34 : ("Lesjoursfris", "", _(u"Config jours f�ri�s")),
        35 : ("Leschampsdecontrats", "", _(u"Config champs contrats")),
        36 : ("Enregistrerunremboursement", "", _(u"Saisie remboursement")),
        37 : ("Imprimeruncontrat", "", _(u"wiz �dition contrat")),
        38 : ("Lesclassifications", "", _(u"Config classifications")),
        39 : ("Lesjoursfris", "", _(u"Saisie jour f�ri�")),
        40 : ("Appliquerunmodledeprsences", "", _(u"Application mod�le de pr�sences")),
        41 : ("Lestypesdecontrats", "", _(u"Saisie types contrats")),
        42 : ("Attribuerunephoto", "", _(u"Editeur photo")),
        43 : ("Lespriodesdevacances", "", _(u"Config p�riodes vacances")),
        44 : ("Enregistrerundplacement", "", _(u"Saisie d�placement")),
        45 : ("Lesgadgets", "", _(u"Config gadgets")),
        46 : ("ExporterlespersonnesdansMSOutl", "", _(u"Export Outlook")),
        47 : ("Ouvrirunfichier", "", _(u"Ouvrir un fichier")),
        48 : ("Lestypesdequalifications", "", _(u"Config types diplomes")),
        49 : ("Assistantdemarrage", "", _(u"Assistant d�marrage")),
        50 : ("Lestypesdepices", "", _(u"Saisie types pi�ces")),
        51 : ("Lecalendrier", "", _(u"Le calendrier")),
        52 : ("Lesmodlesdecontrats", "", _(u"Config modeles contrats")),
        53 : ("Lalistedespersonnes", "Options", _(u"Config liste personnes")),
        54 : ("Creruncontrat", "", _(u"wiz creation contrats")),
        55 : ("Lalistedespersonnes", "export_liste", _(u"export liste personnes")),
        56 : ("Lalistedespersonnes", "Imprimer_liste", _(u"Imprimer liste Personnes")),
        57 : ("Laficheindividuelle", "", _(u"Fiche individuelle")),
        58 : ("Lagestiondesscnarios", "", _(u"Les sc�narios")),
        59 : ("Lesstatistiques", "", _(u"Les statistiques")),
        60 : ("Lagestiondesutilisateurs", "", _(u"La gestion des utilisateurs r�seau")),
        } # NumItem : nomPage, nomAncre, Description
    
    if numItem != None :
        nomPage, nomAncre, description = dictAide[numItem]
    
    if "linux" in sys.platform :
        
        # Aide LINUX : sur internet
        
        # Pr�paration du fichier chm
        nomFichier = "http://www.clsh-lannilis.com/teamworks/aide/tw.htm"
        # Pr�paration de la page HTML
        if nomPage != "" :
            page = "?" + nomPage + ".html"
        else:
            page = ""
        # Pr�paration de l'ancre
        if nomAncre != "" :
            ancre = "#" + nomAncre
        else:
            ancre = ""
        # Ouverture de la page internet
        LanceFichierExterne(nomFichier + page + ancre)
            
    else:
        # Aide WINDOWS avec le CHM
        
        # Pr�paration du fichier chm
        nomFichier = "Aide/teamworks.chm"
        # Pr�paration de la page HTML
        if nomPage != "" :
            page = "::/" + nomPage + ".html"
        else:
            page = ""
        # Pr�paration de l'ancre
        if nomAncre != "" :
            ancre = "#" + nomAncre
        else:
            ancre = ""
        # Ouverture du module d'aide
        commande = 'hh.exe "'+ nomFichier  + page + ancre + '"'
        from subprocess import Popen
        Popen(commande)


# ----------------------------------------------------------------------------------------------------------------------------------------------------


def Parametres(mode="get", categorie="", nom="", valeur=None):
    """ M�morise ou r�cup�re un param�tre quelconque dans la base de donn�es """
    """ Le param�tre doit �tre str ou unicode obligatoirement """
    """ si mode = 'get' : valeur est la valeur par d�faut | si mode = 'set' : valeur est la valeur � donner au param�tre """
   
    # Pr�paration de la valeur par d�faut
    type_parametre = type(valeur)
    if type_parametre == int : valeurTmp = str(valeur)
    elif type_parametre == float : valeurTmp = str(valeur)
    elif type_parametre == str : valeurTmp = valeur
    elif type_parametre == six.text_type : valeurTmp = valeur
    elif type_parametre == tuple : valeurTmp = str(valeur)
    elif type_parametre == list : valeurTmp = str(valeur)
    elif type_parametre == dict : valeurTmp = str(valeur)
    elif type_parametre == bool : valeurTmp = str(valeur)
    else : valeurTmp = ""
    
    # Recherche du parametre
    DB = GestionDB.DB()
    
    # Si aucun fichier n'est charg� dans Teamworks, on renvoie la valeur par d�faut :
    if DB.echec == 1 :
        return valeur

    req = u"""SELECT IDparametre, parametre FROM parametres WHERE categorie="%s" AND nom="%s" ;""" % (categorie, nom)
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    if len(listeDonnees) != 0 :
        if mode == "get" :
            # Un parametre existe :
            valeurTmp = listeDonnees[0][1]
            # On le formate pour le r�cup�rer sous son vrai format
            if type_parametre == int : valeurTmp = int(valeurTmp)
            if type_parametre == float : valeurTmp = float(valeurTmp)
            if type_parametre == str : valeurTmp = valeurTmp
            if type_parametre == six.text_type : valeurTmp = valeurTmp
            if type_parametre == tuple : valeurTmp = eval(valeurTmp)
            if type_parametre == list : valeurTmp = eval(valeurTmp)
            if type_parametre == dict : valeurTmp = eval(valeurTmp)
            if type_parametre == bool : valeurTmp = True if valeurTmp in ("True", True, 1, "1") else False

        else:
            # On modifie la valeur du param�tre
            IDparametre = listeDonnees[0][0]
            listeDonnees = [("categorie",  categorie), ("nom",  nom), ("parametre",  valeurTmp),]
            DB.ReqMAJ("parametres", listeDonnees, "IDparametre", IDparametre)
            valeurTmp = valeur
    else:
        # Le parametre n'existe pas, on le cr�� :
        listeDonnees = [("categorie",  categorie), ("nom",  nom), ("parametre",  valeurTmp),]
        newID = DB.ReqInsert("parametres", listeDonnees)
        valeurTmp = valeur
    DB.Close()
    return valeurTmp


def CompareVersions(versionApp="", versionMaj=""):
    """ Compare 2 versions de TeamWorks """
    """ Return True si la version MAJ est plus r�cente """
    a,b = [[int(n) for n in version.split(".")] for version in [versionMaj, versionApp]]
    return a>b


def GetListeCadresPhotos():
    """ R�cup�re la liste des noms des cadres photos dispo sur le DD """
    listeNomCadres = []
    listeFichiers = os.listdir(Chemins.GetStaticPath("Images/CadresPhotos"))
    for nomFichier in listeFichiers :
        if nomFichier.endswith(".png"):
            listeNomCadres.append(nomFichier[:-4])
    listeNomCadres.sort()
    listeNomCadres.insert(0, _(u"Aucun"))
    return listeNomCadres

def RecupNomCadrePersonne(IDpersonne):
    """ R�cup�re le nom du cadre de d�coration pour une personne donn�e """
    DB = GestionDB.DB()        
    req = "SELECT cadre_photo FROM personnes WHERE IDpersonne=%d;" % IDpersonne
    DB.ExecuterReq(req)
    donnees = DB.ResultatReq()
    DB.Close()
    if len(donnees) == 0 : return None
    cadre_photo = donnees[0][0]
    if cadre_photo == "" : return None
    return cadre_photo

def RecupTextePhotoPersonne(IDpersonne):
    """ R�cup�re le contenu du texte photo pour une personne donn�e """
    DB = GestionDB.DB()        
    req = "SELECT texte_photo FROM personnes WHERE IDpersonne=%d;" % IDpersonne
    DB.ExecuterReq(req)
    donnees = DB.ResultatReq()
    DB.Close()
    if len(donnees) == 0 : return ""
    texte_photo = donnees[0][0]
    if texte_photo == None : texte_photo = ""
    return texte_photo

def CreationPhotoPersonne(IDpersonne=0, nomFichierPhoto="", tailleFinale = None, qualiteBmp = 50):
    """ Cr�ation des photos avec cadre de d�coration """
    # R�cup�ration de la photo
    if os.path.isfile(nomFichierPhoto) == False : return None
    photo = wx.Bitmap(nomFichierPhoto, wx.BITMAP_TYPE_ANY)
    tailleInitiale = photo.GetSize()
    # Cr�ation du dc temporaire
    bmp = wx.EmptyBitmap(tailleInitiale[0], tailleInitiale[1])
    dc = wx.MemoryDC()
    dc.SelectObject(bmp)
    dc.SetBackground(wx.Brush("black"))
    dc.Clear()
    # Dessin de la photo
    dc.DrawBitmap(photo, 0, 0, 0)
    # Dessin du cadre de d�coration
    nomCadre = RecupNomCadrePersonne(IDpersonne)
    if nomCadre != None :
        masque = wx.Bitmap(Chemins.GetStaticPath("Images/CadresPhotos/" + nomCadre + ".png"), wx.BITMAP_TYPE_PNG)
        dc.DrawBitmap(masque, 0, 0)
    # Redimensionne et retourne l'image bmp
    if tailleFinale != None :
        bmp = bmp.ConvertToImage()
        bmp = bmp.Rescale(width=tailleFinale[0], height=tailleFinale[1], quality=qualiteBmp) 
        bmp = bmp.ConvertToBitmap()
    return bmp


def RecupIDfichier():
    """ R�cup�re le code identifiant unique du fichier """
    DB = GestionDB.DB()        
    req = "SELECT codeIDfichier FROM divers WHERE IDdivers=1;"
    DB.ExecuterReq(req)
    donnees = DB.ResultatReq()
    DB.Close()
    codeIDfichier = donnees[0][0]
    return codeIDfichier

def VideRepertoireTemp():
    """ Supprimer tous les fichiers du r�pertoire TEMP """
    for rep in ("Temp/", UTILS_Fichiers.GetRepTemp()) :
        if os.path.isdir(rep) :
            for nomFichier in os.listdir(rep) :
                nomComplet = os.path.join(rep, nomFichier)
                try :
                    if os.path.isdir(nomComplet) :
                        shutil.rmtree(nomComplet)
                    else :
                        os.remove(nomComplet)
                except Exception as err :
                    print(err)

def VideRepertoireUpdates(forcer=False):
    """ Supprimer les fichiers temporaires du r�pertoire Updates """
    try :
        listeReps = UTILS_Fichiers.GetRepUpdates()
        numVersionActuelle = GetVersionTeamworks()
        for nomRep in os.listdir(listeReps) :
            resultat = CompareVersions(versionApp=numVersionActuelle, versionMaj=nomRep)
            if resultat == False or forcer == True :
                # Le rep est pour une version �gale ou plus ancienne
                if numVersionActuelle != nomRep or forcer == True :
                    # Si la version est ancienne, suppression du r�pertoire
                    shutil.rmtree(UTILS_Fichiers.GetRepUpdates(nomRep))
                else:
                    # La version est �gale : on la laisse pour l'instant
                    pass
    except Exception as err:
        print(err)
        pass
        
def ListeImprimantes():
    """ Recherche les imprimantes install�es """
    if "win" in sys.platform :
        import win32print
        
    listeImprimantesLocales = []
    listeImprimantesReseau = []
    listeToutesImprimantes = []

    try:
        for (Flags,pDescription,pName,pComment) in list(win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL,None,1)):
            listeImprimantesLocales.append(pName)
            listeToutesImprimantes.append(pName)
    except : pass
        
    try:   
        for (Flags,pDescription,pName,pComment) in list(win32print.EnumPrinters(win32print.PRINTER_ENUM_CONNECTIONS,None,1)):
            listeImprimantesReseau.append(pName)
            listeToutesImprimantes.append(pName)
    except : pass
    
    nomImprimanteDefaut = ""
    try :
        nomImprimanteDefaut = win32print.GetDefaultPrinter()
    except : pass

    return nomImprimanteDefaut, listeToutesImprimantes, listeImprimantesLocales, listeImprimantesReseau

def EnleveAccents(chaineUnicode):
    """ Enl�ve les accents d'une chaine unicode """
    import unicodedata
    if six.PY2 and type(chaineUnicode) == str :
        chaineUnicode = chaineUnicode.decode("iso-8859-15")
    resultat = unicodedata.normalize('NFKD', chaineUnicode).encode('ascii','ignore')
    return resultat

def AfficheStatsProgramme():
    """ Affiche des stats du programme """
    listeResultats = []
    nbreLignesTotal = 0
    # Recherche les fichiers python
    print("Lancement de l'analyse...")

    listeFichiers = {}
    for rep in ("Dlg", "Ctrl", "Ol", "Utils"):
        if rep not in listeFichiers:
            listeFichiers[rep] = []
        listeFichiers[rep] = os.listdir(os.getcwd() + "/" + rep)

    for rep, liste in listeFichiers.items() :
        for nomFichier in liste:
            if nomFichier.endswith(".py") :
                fichier = open(rep + "/" + nomFichier, 'r')

                nbreLignes = 0
                for line in fichier :
                    nbreLignes += 1
                fichier.close()
                # M�morise les r�sultats
                listeResultats.append((nomFichier, nbreLignes))
                nbreLignesTotal += nbreLignes

    # Affiche les r�sultats
    for nomFichier, nbreLignes in listeResultats :
        print("%s ---> %d lignes" % (nomFichier, nbreLignes))
    print("----------------------------------------")
    print("Nbre total de lignes = %d lignes" % nbreLignesTotal)
    print("Nbre total de modules = %s modules" % len(listeResultats))
    print("----------------------------------------")


def GetVersionTeamworks():
    """ Recherche du num�ro de version de TW """
    fichierVersion = open(Chemins.GetMainPath("Versions.txt"), "r")
    txtVersion = fichierVersion.readlines()[0]
    fichierVersion.close() 
    pos_debut_numVersion = txtVersion.find("n")
    if "(" in txtVersion[:50] :
        pos_fin_numVersion = txtVersion.find("(")
    else:
        pos_fin_numVersion = txtVersion.find(":")
    numVersion = txtVersion[pos_debut_numVersion+1:pos_fin_numVersion].strip()
    return numVersion

def LanceFichierExterne(nomFichier) :
    """ Ouvre un fichier externe sous windows ou linux """
    nomSysteme = sys.platform
    if "win" in nomSysteme : 
        nomFichier = nomFichier.replace("/", "\\")
        os.startfile(nomFichier)
    if "linux" in nomSysteme : 
        os.system("xdg-open " + nomFichier)
    

def GetNomDB():
    """ Renvoie le nom simple du fichier """
    nom = ""
    try :
        topWindow = wx.GetApp().GetTopWindow()
        nomWindow = topWindow.GetName()
    except :
        nomWindow = None
    if nomWindow == "general" : 
        # Si la frame 'General' est charg�e, on y r�cup�re le dict de config
        nom = topWindow.userConfig["nomFichier"]
    else:
        # R�cup�ration du nom de la DB directement dans le fichier de config sur le disque dur
        cfg = UTILS_Config.FichierConfig()
        nom = cfg.GetItemConfig("nomFichier")
    return nom


def Supprime_accent(texte):
    liste = [ (u"�", u"e"), (u"�", u"e"), (u"�", u"e"), (u"�", u"e"), (u"�", u"a"), (u"�", u"u"), (u"�", u"o"), (u"�", u"c"), (u"�", u"i"), (u"�", u"i"), (u"/", u""), (u"\\", u""), ]
    for a, b in liste :
        texte = texte.replace(a, b)
        texte = texte.replace(a.upper(), b.upper())
    return texte

def OuvrirCalculatrice():
    if "win" in sys.platform : LanceFichierExterne("calc.exe")
    if "linux" in sys.platform : os.system("gcalctool")

def RemplacerContenuFichier():
    listeRemplacements = [
        ("DB.CreationTable(", "DB.CreationTable("),
        ("db.CreationTable(", "db.CreationTable("),
        ("DB.CreationTables(", "DB.CreationTables("),
        ("db.CreationTables(", "db.CreationTables("),
        ("DB.ExecuterReq(", "DB.ExecuterReq("),
        ("db.ExecuterReq(", "db.ExecuterReq("),
        ("DB.ResultatReq(", "DB.ResultatReq("),
        ("db.ResultatReq(", "db.ResultatReq("),
        ("DB.Commit(", "DB.Commit("),
        ("db.Commit(", "db.Commit("),
        ("DB.Close(", "DB.Close("),
        ("db.Close(", "db.Close("),
        ] 
    listeFichiers = os.listdir("")
    for nomFichier in listeFichiers :
        if nomFichier.endswith(".py") :
            print("%s..." % nomFichier)
            fichier = open(nomFichier, 'r')
            nouveauFichier = open("New/%s" % nomFichier, 'w')
            for line in fichier :
                for old, new in listeRemplacements :
                    if old in line :
                        print("  ->", old)
                        line = line.replace(old, new)
                nouveauFichier.write(line)
                
            fichier.close()
            nouveauFichier.close()

def PreparationFichierDefaut(nomFichier=""):
    """ Pr�pare le fichier de donn�es par d�faut """
    from Data import DATA_Tables as Tables
    import sqlite3
    listeTablesObligatoires = []
    # R�cup�re les tables optionnelles
    for nom, listeTablesTmp, select in Tables.TABLES_IMPORTATION_OPTIONNELLES :
        for table in listeTablesTmp :
            listeTablesObligatoires.append(table)
    # R�cup�re les tables optionnelles
    for table in Tables.TABLES_IMPORTATION_OBLIGATOIRES :
        listeTablesObligatoires.append(table)
    
    # Ouverture du fichier de r�f�rence
    connexion = sqlite3.connect(nomFichier.encode('utf-8'))
    cursor = connexion.cursor()
    
    # Recherche les tables de la base
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    listeTablesBase = cursor.fetchall()
    for nomTable, in listeTablesBase :
        # Supprime les tables non n�cessaires
        if nomTable not in listeTablesObligatoires and nomTable != "sqlite_sequence"  :
            cursor.execute("DROP TABLE %s;" % nomTable)
    connexion.commit()
    # Fermeture base
    connexion.close() 
    print("Procedure terminee.")

##if __name__ == "__main__":
##    RemplacerContenuFichier()


def Formate_taille_octets(size):
    """
    fonction qui prend en argument un nombre d'octets
    et renvoie la taille la plus adapt�
    """
    seuil_Kio = 1024
    seuil_Mio = 1024 * 1024
    seuil_Gio = 1024 * 1024 * 1024

    if size > seuil_Gio:
        return "%.2f Go" % (size/float(seuil_Gio))
    elif size > seuil_Mio:
        return "%.2f Mo" % (size/float(seuil_Mio))
    elif size > seuil_Kio:
        return "%.2f Ko" % (size/float(seuil_Kio))
    else:
        return "%io" % size


def RechercheImports():
    """ Renvoie la liste de tous les modules import�s du logiciel """
    listeImports = []
    listeFichiers = os.listdir(os.getcwd())
    listeExclusions = ("wx", "DLG", "OL", "CTRL", "UTILS", "DATA")
    for nomFichier in listeFichiers :
        if nomFichier.endswith(".py") :
            fichier = open(nomFichier, 'r')
            for line in fichier :
                if line.startswith("import") :
                    nomImport = line[7:-1]
                    if nomImport not in listeImports :
                        valide = True
                        for exclusion in listeExclusions :
                            if nomImport.startswith(exclusion) :
                                valide = False
                        if valide == True :
                            listeImports.append(nomImport)
            fichier.close()
    listeImports.sort()
    return listeImports



def RemplacerDeprecatedWxpython():
    listeFichiers = os.listdir(os.getcwd())
    listeFichiersTrouves = []
    for nomFichier in listeFichiers :
        if nomFichier.endswith(".py") and "FonctionsPerso.py" not in nomFichier :
            print("%s..." % nomFichier)
            fichier = open(nomFichier, 'r')
            nouveauFichier = open("New/%s" % nomFichier, 'w')
            numLigne = 1
            try :
                for ligne in fichier :
                    # ----- Remplacement de lignes ------ 
                    
                    # wx.FlexGridSizer
                    for chaine in ("wx.FlexGridSizer(", "wx.GridSizer(") :
                        if chaine in ligne and "rows=" not in ligne :
                            positionDebut = ligne.index(chaine)
                            positionFin = ligne.index(")", positionDebut) + 1
                            valeurs = ligne[positionDebut + len(chaine) : positionFin-1]
                            
                            if len(valeurs.split(", ")) == 4 :
                                newValeurs = "rows=%s, cols=%s, vgap=%s, hgap=%s" % tuple(valeurs.split(", "))
                                ligne = ligne.replace(valeurs, newValeurs)
                                #print nomFichier, ligne
                            else :
                                newValeurs = valeurs
                                print("ERREUR !!!!!!!! ---------> ", nomFichier, numLigne, valeurs, "-->", newValeurs)
                    
                    # wx.PySimpleApp
                    chaine = "wx.PySimpleApp"
                    if chaine in ligne :
                        ligne = ligne.replace(chaine, "wx.App")
                    
                    # wx.InitAllImageHandlers()
                    chaine = " wx.InitAllImageHandlers()"
                    if chaine in ligne :
                        ligne = ligne.replace(chaine, " #wx.InitAllImageHandlers()")
                    
                    # Ecriture
                    nouveauFichier.write(ligne)
                    numLigne += 1
            except Exception as err:
                print(nomFichier, err)
            fichier.close()
            nouveauFichier.close()
            print("fini !!!!!!!!!!!!!!!!!")



def InsertCodeToolTip():
    """ Pour ins�rer  dans tous les fichiers """
    import re
    x = re.compile(r'\.SetToolTipString\((.*?\))')
    #x = re.compile(r'\.SetToolTip\(')

    for repertoire in ("Ctrl", "Dlg", "Ol", "Utils") :
        # Cr�ation du r�pertoire temporaire
        if not os.path.isdir("%s/New" % repertoire):
            os.mkdir("%s/New" % repertoire)

        # Get fichiers
        listeFichiers = os.listdir(os.path.join(os.getcwd(), repertoire))
        indexFichier = 0
        for nomFichier in listeFichiers :
            if nomFichier.endswith("py") :
                #print("%d/%d :  %s..." % (indexFichier, len(listeFichiers), nomFichier))

                # Ouverture des fichiers
                fichier = open(os.path.join(repertoire, nomFichier), "r")
                dirty = False

                # .SetToolTip(wx.ToolTip(_(u"")))

                listeLignes = []
                for ligne in fichier :

                    # Modification chemin Images
                    m = x.search(ligne)
                    if m != None:
                        print(ligne)
                        nouvelle_chaine = u".SetToolTip(wx.ToolTip(%s)" % m.group(1)
                        ligne = ligne.replace(m.group(0), nouvelle_chaine)
                        dirty = True
                        print(("      > ", ligne))

                    listeLignes.append(ligne)

                # Cl�ture des fichiers
                fichier.close()

                # Ecriture du nouveau fichier
                if dirty == True :
                    nouveauFichier = open(os.path.join(repertoire, "New", nomFichier), "w")
                    for ligne in listeLignes :
                        nouveauFichier.write(ligne)
                    nouveauFichier.close()

            indexFichier += 1

    print("Fini !!!!!!!!!!!!!!!!!")


def InsertCode():
    """ Pour ins�rer  dans tous les fichiers """
    import re
    x = re.compile(r'(FonctionsPerso.Aide\()(.*?)\)')

    for repertoire in ("Ctrl", "Dlg", "Ol", "Utils") :
        # Cr�ation du r�pertoire temporaire
        if not os.path.isdir("%s/New" % repertoire):
            os.mkdir("%s/New" % repertoire)

        # Get fichiers
        listeFichiers = os.listdir(os.path.join(os.getcwd(), repertoire))
        indexFichier = 0
        for nomFichier in listeFichiers :
            if nomFichier.endswith("py") :
                #print "%d/%d :  %s..." % (indexFichier, len(listeFichiers), nomFichier)

                # Ouverture des fichiers
                fichier = open(os.path.join(repertoire, nomFichier), "r")
                dirty = False

                listeLignes = []
                for ligne in fichier :

                    # # Insertion de l'import Chemins
                    # if "import Chemins" in ligne :
                    #     ligne = "import Chemins\nfrom Utils import UTILS_Adaptations\n"
                    #     dirty = True

                    # # Remplacement de wx.Menu
                    # if "wx.Menu()" in ligne :
                    #     ligne = ligne.replace("wx.Menu()", "UTILS_Adaptations.Menu()")
                    #     dirty = True

                    # # Modification de UTILS_Traduction
                    # if "UTILS_Traduction" in ligne and repertoire != "Utils" :
                    #     ligne = ligne.replace("UTILS_Traduction", "Utils.UTILS_Traduction")
                    #     dirty = True
                    #     print "Traduction:", ligne
                    #
                    # # Modification from ... import
                    # for rep in ("CTRL", "DATA", "DLG", "OL", "UTILS") :
                    #     chaine = "from %s_" % rep
                    #     if chaine in ligne and rep.capitalize() != repertoire and "UTILS_Traduction" not in ligne :
                    #         ligne = ligne.replace(chaine, "from %s.%s_" % (rep.capitalize(), rep))
                    #         dirty = True
                    #         print "from:", ligne
                    #
                    # # Modification import
                    # for rep in ("CTRL", "DATA", "DLG", "OL", "UTILS") :
                    #     chaine = "import %s_" % rep
                    #     if chaine in ligne and rep.capitalize() != repertoire and "from" not in ligne and "UTILS_Traduction" not in ligne :
                    #         ligne = ligne.replace(chaine, "from %s import %s_" % (rep.capitalize(), rep))
                    #         dirty = True
                    #         print "Import:", ligne

                    # Modification Aide
                    m = x.search(ligne)
                    if m:
                        chaine = m.group(2)
                        numero_aide = int(chaine)
                        code_aide = dictAide[numero_aide][0]
                        listeLignes.append('        from Utils import UTILS_Aide\n')
                        ligne = '        UTILS_Aide.Aide("%s")\n' % code_aide
                        dirty = True
                        print("----------------------------")
                        print(ligne)

                    listeLignes.append(ligne)

                # Cl�ture des fichiers
                fichier.close()

                # Ecriture du nouveau fichier
                if dirty == True :
                    nouveauFichier = open(os.path.join(repertoire, "New", nomFichier), "w")
                    for ligne in listeLignes :
                        nouveauFichier.write(ligne)
                    nouveauFichier.close()

            indexFichier += 1

    print("Fini !!!!!!!!!!!!!!!!!")

def GetIDfichier():
    try :
        DB = GestionDB.DB()
        req = """SELECT IDparametre, nom, parametre 
        FROM parametres WHERE nom='IDfichier';"""
        DB.ExecuterReq(req)
        listeTemp = DB.ResultatReq()
        DB.Close()
        IDfichier = listeTemp[0][2]
    except :
        IDfichier = ""
    return IDfichier



if __name__ == "__main__":
    print(GetIDfichier())
