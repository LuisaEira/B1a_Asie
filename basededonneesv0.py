# INF tc 3 - Projet d'application WEB
# Base de donnees

import sqlite3
import json
from zipfile import ZipFile
import re

conn = sqlite3.connect('pays_test.sqlite')

def get_liste_pays():
    with ZipFile('asia.zip','r') as fichier:
        return fichier.namelist()
    
def get_infobox(pays):
    with ZipFile('asia.zip','r') as fichier:
        return json.loads(fichier.read('{}'.format(pays)))
    
def miseajour_bd(conn,info):
    c = conn.cursor()
    sql = 'INSERT INTO countries VALUES (?,?,?,?,?,?,?,?)'
    
    nom = get_nom(info)
    long_name = get_long_name(info)
    capitale = get_capitale(info)
    coords_dic=get_coords_dic(info)
    lat=coords_dic['lat']
    lon=coords_dic['lon']
    dirigeant = get_dirigeant(info)
    area = get_area(info)
    pib = get_pib(info)
    
    c.execute(sql,(nom,long_name,capitale,lat,lon,dirigeant,area,pib))
    conn.commit()
    
    return

def get_nom(info):
    return info['common_name']

def get_long_name(info):
    try:
        return info['conventional_long_name']
    except KeyError:
        return "None"

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

def get_coords_dic(info):
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

def get_dirigeant(info):    
    try:
        dirigeant = info['leader_name1']
        m = dirigeant[2:-2]
        if m != None:
            dirigeant = m
        else:
            dirigeant = 'None'
            
        if 'nowrap' in dirigeant:
            dirigeant = m[10:-4]
            
        return dirigeant
    except KeyError:
        return None

def get_area(info):
    pop = info['area_km2']
    return pop.replace(',',"")    
    
def get_pib(info):
    string = info['GDP_PPP']
    if string[0] == '{':
        liste = string.split('|')
        
        for i in liste :
            if i[0]== '$':
                string = i
    
        
    if 'billion' in string :
        
        rendu = ''
        for i in string :
            if i == '.':
                rendu += i
            try :
                nombre = int(i)
                rendu += i    
            except ValueError :
                pass
        try :
            rendu = float(rendu)*1e9
            return int(rendu)
        except ValueError :
            return 0
    
    if 'trillion' in string :
        rendu = ''
        for i in string :
            if i == '.':
                rendu += i
            try :
                nombre = int(i)
                rendu += i    
            except ValueError :
                pass
        try :
            rendu = float(rendu)*1e12
            return int(rendu)
        except ValueError :
            return 0

# Tests
liste_pays = get_liste_pays()
for pays in liste_pays[:]: 
    info=get_infobox(pays)	
    miseajour_bd(conn,info)	

