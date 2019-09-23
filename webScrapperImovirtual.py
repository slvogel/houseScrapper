# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 14:34:42 2019

@author: slvogel
"""

import pandas as pd
from lxml import html,etree
from requests import get
import pandas as pd
import geopy.distance
import json
import time
import random as rand


headers = ({'User-Agent':
            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'})
  #define source url
url = 'https://www.imovirtual.com/comprar/apartamento-e-moradia/sintra/?search%5Bfilter_float_price%3Ato%5D=300000&search%5Bfilter_enum_rooms_num%5D%5B0%5D=3&search%5Bfilter_enum_rooms_num%5D%5B1%5D=4&search%5Bfilter_enum_rooms_num%5D%5B2%5D=5&search%5Bfilter_enum_rooms_num%5D%5B3%5D=6&search%5Bfilter_enum_rooms_num%5D%5B4%5D=7&search%5Bsubregion_id%5D=158'


#extract info from imo virtual
title_list, url_list, price_list, size_list, area_list, house_type_list, year_list, certificate_list, state_list, description_list, proximity_list = [],[],[],[],[],[],[],[],[],[],[]

#insert the coordintaes of the locations of interest
location_1 = (38.798525, -9.378356)
location_2 = (38.797805, -9.335724)
locais = [location_1, location_2]

for page in range(0,4):
  page_url = url + '&page=' + str(page)
  r = get(page_url, headers=headers)
  tree = html.fromstring(r.content)
  property_url_list = tree.cssselect('div.offer-item-details h3 a')
  for prop in property_url_list:
    prop_url = prop.get('href')
    r = get(prop_url, headers=headers)
    prop_tree = html.fromstring(r.content)
    
    # url
    url_list.append(prop_url)
    
    # Title
    name = prop_tree.cssselect("h1.css-18igut2")[0].text
    title_list.append(name.strip())
    
    #price css-1vr19r7
    price = prop_tree.cssselect("div.css-1vr19r7")[0].text
    if len(price) != 0:
        price = float(price[:-1].replace(u' ', u'').replace(',', '.'))
    else:
        price = None
    price_list.append(price)
    
    #Details css-2fnk9o
    size,area,house_type,year,certificate,state = None,None,None,None,None,None
    details = prop_tree.cssselect("div.css-2fnk9o ul li")
    for detail in details:
      if detail.text_content().startswith('Área útil (m²):'):
          size = float(detail.text_content()[15:-2].strip().replace(' ', '').replace(',', '.'))
      elif detail.text_content().startswith('Área bruta (m²): '):
          area = float(detail.text_content()[17:-2].strip().replace(' ', '.').replace(',', '.'))
      elif detail.text_content().startswith('Tipologia: '):
          house_type = detail.text_content()[10:].strip()
      elif detail.text_content().startswith('Ano de construção: '):
          year = float(detail.text_content()[19:].strip())
      elif detail.text_content().startswith('Certificado Energético: '):
          certificate =  detail.text_content()[23:].strip()
      elif detail.text_content().startswith('Condição: '):
          state = detail.text_content()[10:].strip()
     
    size_list.append(size)
    area_list.append(area)
    house_type_list.append(house_type)
    year_list.append(year)
    certificate_list.append(certificate)
    state_list.append(state)
    
    #description css-fioe1g
    description = prop_tree.cssselect("section.section-description div p")
    if len(description) > 0:
      description = description[0].text_content()
    else:
      description = ""
    description_list.append(description)

    #coordinates
    if len(prop_tree.cssselect("script[type=\"application/ld+json\"]"))>=3:
      geo = prop_tree.cssselect("script[type=\"application/ld+json\"]")[2].text_content()
      location = json.loads(geo)['@graph'][0]['geo']
      latitude = location['latitude']
      longitude = location['longitude']
      coordinates = (latitude,longitude)
      #proximity
      distances = [geopy.distance.geodesic(coordinates, station).km for station in locais]
      proximity = max(distances)
      proximity_list.append(proximity)
    else:
      proximity_list.append(None)    

  time.sleep(rand.randint(1,2))
  
#Create Data Frame
cols = ['Title', 'Price', 'Size', 'Area', 'Type', 'Year', 'Certificate', 'State', 'Proximity', 'Description', 'URL']
pd.options.display.float_format = '{: .2f}'.format
df = pd.DataFrame({'Title': title_list,
                           'Price': price_list,
                           'Size': size_list,
                           'Area': area_list,
                           'Type': house_type_list,
                           'Year': year_list,
                           'Certificate': certificate_list,
                           'State': state_list,
                           'Proximity': proximity_list,
                           'Description': description_list,
                           'URL': url_list})[cols]

