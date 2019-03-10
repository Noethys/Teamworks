#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from Utils.UTILS_Traduction import _
import datetime
import time


def DateEngFr(textDate):
    if textDate in (None, "") : return ""
    if type(textDate) == datetime.date : return DateDDEnFr(textDate)
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def DateDDEnFr(date):
    if date == None : return ""
    return DateEngFr(str(date))
    
def DateComplete(dateDD):
    """ Transforme une date DD en date compl�te : Ex : lundi 15 janvier 2008 """
    if dateDD == None : return u""
    listeJours = (_(_(u"Lundi")), _(_(u"Mardi")), _(_(u"Mercredi")), _(_(u"Jeudi")), _(_(u"Vendredi")), _(_(u"Samedi")), _(_(u"Dimanche")))
    listeMois = (_(_(u"janvier")), _(_(u"f�vrier")), _(_(u"mars")), _(_(u"avril")), _(_(u"mai")), _(_(u"juin")), _(_(u"juillet")), _(_(u"ao�t")), _(_(u"septembre")), _(_(u"octobre")), _(_(u"novembre")), _(_(u"d�cembre")))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    if dateEng == None or dateEng == "" : return None
    if type(dateEng) == datetime.date : return dateEng
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))


def PeriodeComplete(mois, annee):
    listeMois = (_(_(u"Janvier")), _(_(u"F�vrier")), _(_(u"Mars")), _(_(u"Avril")), _(_(u"Mai")), _(_(u"Juin")), _(_(u"Juillet")), _(_(u"Ao�t")), _(_(u"Septembre")), _(_(u"Octobre")), _(_(u"Novembre")), _(_(u"D�cembre")))
    periodeComplete = u"%s %d" % (listeMois[mois-1], annee)
    return periodeComplete

def CalculeAge(dateReference=None, date_naiss=None):
    """ Calcul de l'age de la personne """
    if dateReference == None :
        dateReference = datetime.date.today()
    if date_naiss in (None, "") :
        return None
    age = (dateReference.year - date_naiss.year) - int((dateReference.month, dateReference.day) < (date_naiss.month, date_naiss.day))
    return age

def HeuresEnDecimal(texteHeure="07:00"):
    """ Transforme une heure string ou datetime.time en entier de type 2075"""
    if texteHeure == None :
        return 0
    if type(texteHeure) == datetime.time :
        heures = str(texteHeure.hour)
        minutes = int(texteHeure.minute)
    if type(texteHeure) in (str, six.text_type) :
        posTemp = texteHeure.index(":")
        heures = str(texteHeure[0:posTemp])
        minutes = int(texteHeure[posTemp+1:5])
    minutes = str(minutes * 100 /60)
    if len(minutes) == 1 : minutes = "0" + minutes
    heure = str(heures + minutes)
    return int(heure)

def SoustractionHeures(heure_max, heure_min):
    """ Effectue l'op�ration heure_max - heure_min. Renvoi un timedelta """
    if type(heure_max) != datetime.timedelta : heure_max = datetime.timedelta(hours=heure_max.hour, minutes=heure_max.minute)
    if type(heure_min) != datetime.timedelta : heure_min =  datetime.timedelta(hours=heure_min.hour, minutes=heure_min.minute)
    return heure_max - heure_min

def AdditionHeures(heure1, heure2):
    """ Effectue l'op�ration heure_max - heure_min. Renvoi un timedelta """
    if type(heure1) != datetime.timedelta : heure1 = datetime.timedelta(hours=heure1.hour, minutes=heure1.minute)
    if type(heure2) != datetime.timedelta : heure2 =  datetime.timedelta(hours=heure2.hour, minutes=heure2.minute)
    return heure1 + heure2

def DeltaEnTime(varTimedelta) :
    """ Transforme une variable TIMEDELTA en heure datetime.time """
    heureStr = time.strftime("%H:%M", time.gmtime(varTimedelta.seconds))
    heure = HeureStrEnTime(heureStr)
    return heure

def TimeEnDelta(heureTime):
    hr = heureTime.hour
    mn = heureTime.minute
    return datetime.timedelta(hours=hr, minutes=mn)

def HeureStrEnTime(heureStr):
    if heureStr == None or heureStr == "" : return datetime.time(0, 0)
    if len(heureStr.split(":")) == 2 : heures, minutes = heureStr.split(":")
    if len(heureStr.split(":")) == 3 : heures, minutes, secondes = heureStr.split(":")
    return datetime.time(int(heures), int(minutes))

def DatetimeTimeEnStr(heure, separateur="h"):
    if heure == None : 
        return None
    else :
        return u"%02d%s%02d" % (heure.hour, separateur, heure.minute)

def HorodatageEnDatetime(horodatage, separation=None):
    if separation == None :
        annee = int(horodatage[0:4])
        mois = int(horodatage[4:6])
        jour = int(horodatage[6:8])
        heures = int(horodatage[8:10])
        minutes = int(horodatage[10:12])
        secondes = int(horodatage[12:14])
        horodatage = datetime.datetime(annee, mois, jour, heures, minutes, secondes)
    else :
        annee, mois, jour, heures, minutes, secondes = horodatage.split(separation)
        horodatage = datetime.datetime(int(annee), int(mois), int(jour), int(heures), int(minutes), int(secondes))
    return horodatage



if __name__ == "__main__":
    pass

    