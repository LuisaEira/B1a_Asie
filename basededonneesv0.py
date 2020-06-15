# INF tc 3 - Projet d'application WEB
# Base de donnees

import sqlite3
import json
from zipfile import ZipFile
import re

conn = sqlite3.connect('pays_test_html.sqlite')

def get_liste_pays():
    with ZipFile('asia.zip','r') as fichier:
        return fichier.namelist()
    
def get_infobox(pays):
    with ZipFile('asia.zip','r') as fichier:
        return json.loads(fichier.read('{}'.format(pays)))
    
def miseajour_bd(conn,info):
    c = conn.cursor()
    sql = 'INSERT INTO countries VALUES (?,?,?,?,?)'
    
    nom = get_nom(info)
    #drapeau = get_drapeau(info)
    capitale = get_capitale(info)
    coords_dico=get_coords_dico(info)
    lat=coords_dico['lat']
    lon=coords_dico['lon']
    #dirigeant = get_dirigeant(info)
    langue = get_langue(info)
    area = get_area(info)
    
    c.execute(sql,(nom,capitale,lat,lon,area))
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

def get_area(info):
    pop = info['area_km2']
    return pop.replace(',',"")


def cv_coords(str_coords):
    c = str_coords.split('|')[1:-1]
    
    lat = float(c.pop(0))
    if c[0] == 'N':
        c.pop(0)
    elif c[0] == 'S':
        lat = -lat
        c.pop(0)
    elif (len(c) > 1 and c[1] == 'N'):
        lat += float(c.pop(0))/60
        c.pop(0)
    elif (len(c) > 1 and c[1] == 'S'):
        lat += float(c.pop(0))/60
        lat = -lat
        c.pop(0)
    elif (len(c) > 2 and c[2] == 'N'):
        lat += float(c.pop(0))/60
        lat += float(c.pop(0))/3600
        c.pop(0)
    elif (len(c) > 2 and c[2] == 'S'):
        lat += float(c.pop(0))/60
        lat += float(c.pop(0))/3600
        lat = -lat
        c.pop(0)
        
    lon = float(c.pop(0))
    if c[0] == 'W':
        lon = -lon
        c.pop(0)
    elif c[0] == 'E':
        c.pop(0)
    elif (len(c) > 1 and c[1] == 'W'):
        lon += float(c.pop(0))/60
        lon = -lon
        c.pop(0)
    elif (len(c) > 1 and c[1] == 'E'):
        lon += float(c.pop(0))/60
        c.pop(0)
    elif (len(c) > 2 and c[2] == 'W'):
        lon += float(c.pop(0))/60
        lon += float(c.pop(0))/3600
        lon = -lon
        c.pop(0)
    elif (len(c) > 2 and c[2] == 'E'):
        lon += float(c.pop(0))/60
        lon += float(c.pop(0))/3600
        c.pop(0)
    
    return {'lat':lat, 'lon':lon}

def get_coords_dico(info):
    try:
        coords = info['coordinates']
    except KeyError:
        return {'lat':0, 'lon':0}
    return cv_coords(coords)

def get_coords_str(info):
    try:
        coords = info['coordinates']
    except:
        coords = {'lat':0, 'lon':0}
    c = coords.split('|')[1:-1]
    if len(c) == 8:
        return c[0]+'°'+c[1]+"'"+c[2]+"'"+c[3]+" "+c[4]+'°'+c[5]+"'"+c[6]+"'"+c[7]
    elif len(c) == 6:
        return c[0]+'°'+c[1]+"'"+ c[2]+' '+c[3]+'°'+c[4]+"'"+c[5]
    else:
        return None

def get_langue(info):
    try:
        langue = info['official_languages']
        m = re.match("\[\[(\w+)\]\]", langue)  # On enlève les doubles crochets
        if m!=None:
            langue = m.group(1)    
        else:						
            langue ='None'			
        return(langue) 
        
    except KeyError:			# Si le pays n'a pas de langue officielle 
        return "None"    
    
# Tests
liste_pays = get_liste_pays()
for pays in liste_pays[:]: 
    info=get_infobox(pays)	
    miseajour_bd(conn,info)	

