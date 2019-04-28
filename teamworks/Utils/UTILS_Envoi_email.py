#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Teamworks
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from Utils.UTILS_Traduction import _
import wx
import six
import os
import GestionDB
import FonctionsPerso


def GetAdresseExpDefaut():
    """ Retourne les paramètres de l'adresse d'expéditeur par défaut """
    dictAdresse = {}
    # Récupération des données
    DB = GestionDB.DB()        
    req = """SELECT IDadresse, adresse, smtp, port, defaut, connexionssl
    FROM adresses_mail WHERE defaut=1 ORDER BY adresse; """
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close()
    if len(listeDonnees) == 0 : return None
    IDadresse, adresse, smtp, port, defaut, connexionssl = listeDonnees[0]
    dictAdresse = {"adresse":adresse, "smtp":smtp, "port":port, "connexionssl":connexionssl}
    return dictAdresse



def Envoi_mail(adresseExpediteur="", listeDestinataires=[], listeDestinatairesCCI=[], sujetMail="", texteMail="", listeFichiersJoints=[], serveur="localhost", port=None, ssl=False, listeImages=[]):
    """ Envoi d'un mail avec pièce jointe """
    import smtplib
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEBase import MIMEBase
    from email.MIMEText import MIMEText
    from email.MIMEImage import MIMEImage
    from email.MIMEAudio import MIMEAudio
    from email.Utils import COMMASPACE, formatdate
    from email import Encoders
    import mimetypes
    
    assert type(listeDestinataires)==list
    assert type(listeFichiersJoints)==list
    
    # Corrige le pb des images embarquées
    index = 0
    for img in listeImages :
        img = img.replace("\\", "/")
        img = img.replace(":", "%3A")
        texteMail = texteMail.replace("file:/%s" % img, "cid:image%d" % index)
        index += 1
    
    # Création du message
    msg = MIMEMultipart()
    msg['From'] = adresseExpediteur
    msg['To'] = ";".join(listeDestinataires)
    msg['Bcc'] = ";".join(listeDestinatairesCCI)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = sujetMail
##    msg.attach( MIMEText(texteMail, 'html') )
    msg.attach( MIMEText(texteMail.encode('utf-8'), 'html', 'utf-8') )
        
    # Attache des pièces jointes
    for fichier in listeFichiersJoints:
        """Guess the content type based on the file's extension. Encoding
        will be ignored, altough we should check for simple things like
        gzip'd or compressed files."""
        ctype, encoding = mimetypes.guess_type(fichier)
        if ctype is None or encoding is not None:
            # No guess could be made, or the file is encoded (compresses), so
            # use a generic bag-of-bits type.
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        if maintype == 'text':
            fp = open(chemin)
            # Note : we should handle calculating the charset
            part = MIMEText(fp.read(), _subtype=subtype)
            fp.close()
        elif maintype == 'image':
            fp = open(fichier, 'rb')
            part = MIMEImage(fp.read(), _subtype=subtype)
            fp.close()
        elif maintype == 'audio':
            fp = open(fichier, 'rb')
            part = MIMEAudio(fp.read(), _subtype=subtype)
            fp.close()
        else:
            fp = open(fichier, 'rb')
            part = MIMEBase(maintype, subtype)
            part.set_payload(fp.read())
            fp.close()
            # Encode the payload using Base64
            Encoders.encode_base64(part)
        # Set the filename parameter
        nomFichier= os.path.basename(fichier)
        if type(nomFichier) == six.text_type :
            nomFichier = FonctionsPerso.supprime_accent(nomFichier)
        part.add_header('Content-Disposition', 'attachment', filename=nomFichier)
        msg.attach(part)
    
    # Images incluses
    index = 0
    for img in listeImages :
        fp = open(img, 'rb')
        msgImage = MIMEImage(fp.read())
        fp.close()
        msgImage.add_header('Content-ID', '<image%d>' % index)
        msg.attach(msgImage)
        index += 1

    if ssl == False :
        # Envoi standard
        smtp = smtplib.SMTP(serveur)
    else:
        # Si identification SSL nécessaire :
        smtp = smtplib.SMTP(serveur, port)
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(adresseExpediteur, passwd)
        
    smtp.sendmail(adresseExpediteur, listeDestinataires + listeDestinatairesCCI, msg.as_string())
    smtp.close()

    return True





