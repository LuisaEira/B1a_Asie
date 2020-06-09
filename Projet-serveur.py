# Serveur pour le projet; melange de TD3-lieux-insolites.py et TD3-s6.py
# Mettre un do_POST ?

import http.server
import socketserver
import sqlite3
import json

from urllib.parse import urlparse, parse_qs, unquote


#
# Definition du nouveau handler
#
class RequestHandler(http.server.SimpleHTTPRequestHandler):

  # sous-repertoire racine des documents statiques
  static_dir = '/client'

  # version du serveur
  server_version = 'Projet-serveur.py/0.1'

  # On surcharge la methode qui traite les requetes GET
  def do_GET(self):
    # on recupere les parametres
    self.init_params()
    
    # requete location - retourne la liste de lieux et leurs coordonnees geographiques (pour bulle)
    if self.path_info[0] == "location":
      data= self.build_location()
      self.send_json(data)

    # requete description - retourne la description du lieu dont on passe l'id en parametre dans l'URL (pour description en dessous)
    elif self.path_info[0] == "description":
      data= self.build_description()
      for c in data:
        if c['id'] == int(self.path_info[1]):
          self.send_json(c)
          break
    
    # requete generique
    elif self.path_info[0] == "service":
      self.send_html('<p>Path info : <code>{}</p><p>Chaîne de requête : <code>{}</code></p>' \
          .format('/'.join(self.path_info),self.query_string));
    
    else:
      self.send_static()


  # On surcharge la methode qui traite les requetes HEAD
  def do_HEAD(self):
    self.send_static()


  def send_static(self):
    '''envoie le document statique demande'''
    self.path = self.static_dir + self.path
    if (self.command=='HEAD'):
        http.server.SimpleHTTPRequestHandler.do_HEAD(self)
    else:
        http.server.SimpleHTTPRequestHandler.do_GET(self)
        
        
  # on envoie un document html dynamique
  def send_html(self,content):
     headers = [('Content-Type','text/html;charset=utf-8')]
     html = '<!DOCTYPE html><title>{}</title><meta charset="utf-8">{}' \
         .format(self.path_info[0],content)
     self.send(html,headers)


  def init_params(self):
    '''analyse la requete pour initialiser nos parametres'''
    # analyse de l'adresse
    info = urlparse(self.path)
    self.path_info = [unquote(v) for v in info.path.split('/')[1:]]  # info.path.split('/')[1:]
    self.query_string = info.query
    self.params = parse_qs(info.query)

    # recuperation du corps
    length = self.headers.get('Content-Length')
    ctype = self.headers.get('Content-Type')
    if length:
      self.body = str(self.rfile.read(int(length)),'utf-8')
      if ctype == 'application/x-www-form-urlencoded' : 
        self.params = parse_qs(self.body)
    else:
      self.body = ''
   
    # traces
    print('path_info =',self.path_info)
    print('body =',length,ctype,self.body)
    print('params =', self.params)


  def send_json(self,data,headers=[]):
    '''envoie un contenu encode en json'''
    body = bytes(json.dumps(data),'utf-8') # encodage en json et UTF-8
    self.send_response(200)
    self.send_header('Content-Type','application/json')
    self.send_header('Content-Length',int(len(body)))
    [self.send_header(*t) for t in headers]
    self.end_headers()
    self.wfile.write(body) 


  def send(self,body,headers=[]):
    '''envoie les entetes et le corps fourni'''
    encoded = bytes(body, 'UTF-8')
    self.send_response(200)
    [self.send_header(*t) for t in headers]
    self.send_header('Content-Length',int(len(encoded)))
    self.end_headers()
    self.wfile.write(encoded)


  def build_location():
    """Construit la liste des dictionnaires contenant les infos a afficher dans les bulles: id+lat+lon+Nom pays+Capitale"""
    c = conn.cursor()
    
    # recuperation des infos dans la base SQL
    c.execute("SELECT latitude,logitude,name,capital FROM countries")
    r = c.fetchall()  # liste de tuple contenant les donnees demandees, un tuple par pays
    
    # Construction du dictionnaire
    data=[]
    i=0
    dictpays={}
    for a in r:
        i+=1
        dictpays['id']=i
        dictpays['latitude']=a[0]
        dictpays['longitude']=a[1]
        dictpays['name']=a[2]
        dictpays['capital']=a[3]
        data.append(dictpays)
    return data

    
  def build_description():
    """Construit la liste des dictionnaires contenant les infos a afficher hors de la carte"""
    c = conn.cursor()
    c.execute("SELECT name,flag,capital,latitude,longitude,leader,language,population FROM countries")
    r = c.fetchall()  # liste de tuple contenant les donnees demandees, un tuple par pays
    data=[]
    i=0
    for a in r:
        i+=1
        dictpays={}
        dictpays['id']=i
        dictpays['name']=a[0]
        dictpays['flag']=a[1]
        dictpays['capital']=a[2]
        dictpays['latitude']=a[3]
        dictpays['longitude']=a[4]
        dictpays['leader']=a[5]
        dictpays['language']=a[6]
        dictpays['population']=a[7]
        data.append(dictpays)
    return data


 
# Ouverture d'une connexion avec la base de donnees
conn = sqlite3.connect('pays.sqlite')

# Pour acceder au resultat des requetes sous forme d'un dictionnaire
conn.row_factory = sqlite3.Row

# Instanciation et lancement du serveur
httpd = socketserver.TCPServer(("", 8080), RequestHandler)
httpd.serve_forever()