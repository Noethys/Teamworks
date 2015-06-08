#!/bin/python
# -*- coding: iso-8859-15 -*-

#Origine : Algorithme Phonex de Frédéric BROUARD (31/3/99)
#Source : http://sqlpro.developpez.com/cours/soundex
#Version Python : Christian Pennaforte - 5 avril 2005
#Suite : Florent Carlier

import string
import re

def phonex(chaine):

    #0 On met la chaîne en majuscules, on vire les caractères parasites
##trans = string.maketrans(u'àâäãéèêëìîïòôöõùûüñÀÂÄÃÉÈÊËÌÎÏÒÔÖÕÙÛÜÑ', 'AAAAEEEEIIIOOOOUUUNAAAAEEEEIIIOOOOUUUN');
##print (trans,)
##    chaine = string.translate(chaine," 0123456789-.+*/,:;_'()")
    chaine = chaine.upper()

    #1 remplacer les y par des i
    r = chaine.replace('Y','I')

    #2 supprimer les h qui ne sont pas précédées de c ou de s ou de p
    r = re.sub(r'([^P|C|S])H', r'\1', r)

    #3 remplacement du ph par f
    r = r.replace(r'PH', r'F')

    #4 remplacer les groupes de lettres suivantes :
    r = re.sub(r'G(AI?[N|M])',r'K\1',r)

    #5 remplacer les occurrences suivantes, si elles sont suivies par une lettre a, e, i, o, ou u :
    r = re.sub(r'[A|E]I[N|M]([A|E|I|O|U])',r'YN\1',r)

    #6 remplacement de groupes de 3 lettres (sons 'o', 'oua', 'ein') :
    r = r.replace('EAU','O')
    r = r.replace('OUA','2')
    r = r.replace('EIN','4')
    r = r.replace('AIN','4')
    r = r.replace('EIM','4')
    r = r.replace('AIM','4')

    #7 remplacement du son É:
    r = r.replace(u'É','Y') #CP : déjà fait en étape 0
    r = r.replace(u'È','Y') #CP : déjà fait en étape 0
    r = r.replace(u'Ê','Y') #CP : déjà fait en étape 0
    r = r.replace('AI','Y')
    r = r.replace('EI','Y')
    r = r.replace('ER','YR')
    r = r.replace('ESS','YS')
    r = r.replace('ET','YT') #CP : différence entre la version Delphi et l'algo
    r = r.replace('EZ','YZ')

    #8 remplacer les groupes de 2 lettres suivantes (son â..anâ.. et â..inâ..), sauf sâ..il sont suivi par une lettre a, e, i o, u ou un son 1 Ã  4 :
    r = re.sub(r'AN([^A|E|I|O|U|1|2|3|4])',r'1\1',r)
    r = re.sub(r'ON([^A|E|I|O|U|1|2|3|4])',r'1\1',r)
    r = re.sub(r'AM([^A|E|I|O|U|1|2|3|4])',r'1\1',r)
    r = re.sub(r'EN([^A|E|I|O|U|1|2|3|4])',r'1\1',r)
    r = re.sub(r'EM([^A|E|I|O|U|1|2|3|4])',r'1\1',r)
    r = re.sub(r'IN([^A|E|I|O|U|1|2|3|4])',r'4\1',r)

    #9 remplacer les s par des z sâ..ils sont suivi et prÃ©cÃ©dÃ©s des lettres a, e, i, o,u ou dâ..un son 1 Ã  4
    r = re.sub(r'([A|E|I|O|U|Y|1|2|3|4])S([A|E|I|O|U|Y|1|2|3|4])',r'\1Z\2',r)
    #CP : ajout du Y Ã  la liste

    #10 remplacer les groupes de 2 lettres suivants :
    r = r.replace('OE','E')
    r = r.replace('EU','E')
    r = r.replace('AU','O')
    r = r.replace('OI','2')
    r = r.replace('OY','2')
    r = r.replace('OU','3')  

    #11 remplacer les groupes de lettres suivants
    r = r.replace('CH','5')
    r = r.replace('SCH','5')
    r = r.replace('SH','5')
    r = r.replace('SS','S')
    r = r.replace('SC','S') #CP : problème pour PASCAL, mais pas pour PISCINE ?

    #12 remplacer le c par un s s'il est suivi d'un e ou d'un i
    #CP : à mon avis, il faut inverser 11 et 12 et ne pas faire la dernière ligne du 11
    r = re.sub(r'C([E|I])',r'S\1',r)

    #13 remplacer les lettres ou groupe de lettres suivants :
    r = r.replace('C','K')
    r = r.replace('Q','K')
    r = r.replace('QU','K')
    r = r.replace('GU','K')
    r = r.replace('GA','KA')
    r = r.replace('GO','KO')
    r = r.replace('GY','KY')

    #14 remplacer les lettres suivante :
    r = r.replace('A','O')
    r = r.replace('D','T')
    r = r.replace('P','T')
    r = r.replace('J','G')
    r = r.replace('B','F')
    r = r.replace('V','F')
    r = r.replace('M','N')

    #15 Supprimer les lettres dupliquées
    oldc='#'
    newr=''
    for c in r:
        if oldc != c: newr=newr+c
        oldc=c
    r = newr

    #16 Supprimer les terminaisons suivantes : t, x
    r = re.sub(r'(.*)[T|X]$',r'\1',r)

    #17 Affecter à chaque lettre le code numérique correspondant en partant de la dernière lettre
    num = ['1','2','3','4','5','E','F','G','H','I','K','L','N','O','R','S','T','U','W','X','Y','Z']
    l = []
    for c in r:
        l.append(num.index(c))

    #18 Convertissez les codes numériques ainsi obtenu en un nombre de base 22 exprimé en virgule flottante.
    res=0.
    i=1
    for n in l:
        res = n*22**-i+res
        i=i+1

    return res

if __name__ == '__main__':
    listeTest = (u"Noémie", u"Noemie", "Nomie", "Mathis")
    for texte in listeTest :
        print (texte, phonex(texte))
