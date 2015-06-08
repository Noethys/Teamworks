Teamworks
==================
Logiciel libre et gratuit de gestion d'équipes
Pour Windows, Mac OS et Linux.

Plus d'infos sur http://teamworks.forumactif.com/


Procédure d'installation
------------------

Si vous souhaitez installer manuellement Noethys sur
Windows, Mac OS ou Linux, il vous suffit de copier
l'intégralité du répertoire sur votre disque dur et
d'installer toutes les dépendances listées ci-dessous.


Dépendances pour Windows
------------------
Sur Windows, vous devez aller sur les sites des auteurs pour 
rechercher et installer les bibliothèques suivantes.

- Python 2.7 (http://www.python.org/)
- wxPython 3.0 - version unicode (http://www.wxpython.org/)
- dateutil (http://pypi.python.org/pypi/python-dateutil)
- MySQLdb (http://sourceforge.net/projects/mysql-python/)
- NumPy (http://new.scipy.org/download.html)
- PIL (http://www.pythonware.com/products/pil/)
- PyCrypto (https://www.dlitz.net/software/pycrypto/)
- PyCrypt (https://sites.google.com/site/reachmeweb/pycrypt)
- ReportLab (http://www.reportlab.com/software/opensource/rl-toolkit/download/)
- MatPlotLib (http://matplotlib.sourceforge.net/)
- pyExcelerator (http://sourceforge.net/projects/pyexcelerator/)


Dépendances pour Linux
------------------

- python 2.7 (installé en principe par défaut sous ubuntu)
- python-wxgtk3.0 (Bibliothèque graphique)
- python-mysqldb (Pour l'utilisation en mode réseau)
- python-dateutil (Manipulation des dates)
- python-numpy (Calculs avancés)
- python-imaging (Traitement des photos)
- python-reportlab (Création des PDF)
- python-matplotlib (Création de graphes)
- python-xlrd (Traitement de fichiers Excel)
- python-crypto (pour crypter les sauvegardes)
- python-excelerator (pour les exports format excel)
- python-pip (qui permet d'installer icalendar)

Ils s'installent depuis le terminal tout simplement avec la commande:

```
apt-get install python-mysqldb python-dateutil python-numpy python-imaging 
python-reportlab python-matplotlib python-xlrd python-excelerator python-pip 
python-crypto
```

Et pour icalendar il faut avoir installé python-pip et les installer par:

- pip install icalendar


Pour lancer Teamworks, lancez le terminal de Linux, placez-vous 
dans le répertoire d'installation de Noethys, puis saisissez
la commande "python Teamworks.py"
