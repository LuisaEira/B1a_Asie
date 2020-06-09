# INF tc 3 - Projet d'application WEB
# Base de donnees

import sqlite3
import json
from zipfile import ZipFile
import re

conn = sqlite3.connect('pays2.sqlite')

def get_liste_pays():
    with ZipFile('asia.zip','r') as fichier:
        return fichier.namelist()
    
def get_infobox(pays):
    with ZipFile('asia.zip','r') as fichier:
        return json.loads(fichier.read('{}'.format(pays)))
    
def miseajour_bd(conn,info):
    c = conn.cursor()
    sql = 'INSERT INTO countries VALUES (?,?,?)'
    
    nom = get_nom(info)
    #drapeau = get_drapeau(info)
    capitale = get_capitale(info)
    #coords_capitale = get_coords_capitale(info)
    #dirigeant = get_dirigeant(info)
    #langue = get_langue(info)
    population = get_population(info)
    
    c.execute(sql,(nom,capitale,population))
    conn.commit()
    
    return

def get_nom(info):
    return info['common_name']

def get_drapeau(info):
    return

def get_capitale(info):
    try:
        capitale = info['capital']
        m = re.match("\[\[(\w+)\]\]",capitale)
        if m != None:
            capitale = m.group(1)
        else:
            capitale = 'None'
        return capitale
    
    except KeyError:
        return "Ce pays n'a pas de capitale"

def get_population(info):
    pop = info['area_km2']
    return pop.replace(',',"")

# Tests
liste_pays = get_liste_pays()
for pays in liste_pays[:]: 
    info=get_infobox(pays)	
    miseajour_bd(conn,info)	

