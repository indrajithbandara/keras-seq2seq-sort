import glob

import os

import bs4

from multiprocessing import Process

import sys

import pickle

import gzip

import re
files = glob.glob('htmls/*')
size = len(files)

def _map(arr):
  index, name = arr
  link_name = 'links/' + name.split('/').pop().replace('/', '_') 
  if os.path.exists(link_name) is True:
    return
  
  if index%100 == 0:
    print('now iter', index, '/', size)
  try:
    soup = bs4.BeautifulSoup( open(name).read(), "lxml" )
  except Exception as ex:
    return
 
  f = open(link_name, 'w')
  for a in soup.find_all('a', href=True):
    url = a['href']
    try:
      if url[0] == '/':
        url = 'http://toyokeizai.net' + url
    except Exception:
      continue
    #print(url)  
    if re.search(r'^http://toyokeizai.net/', url) is None:
      continue

    f.write( url + '\n' ) 

if '--map1' in sys.argv:
  for index, name in enumerate(files):
    p = Process(target=_map, args=((index, name), )) 
    p.start()

if '--fold1' in sys.argv:
  urls = set()
  for index, name in enumerate(glob.glob('links/*')):
    if index%1000 == 0:
      print('now iter', index )
    [urls.add(url) for url in open(name).read().split('\n')]
  open('urls.pkl.gz', 'wb').write( gzip.compress(pickle.dumps(urls)) )
