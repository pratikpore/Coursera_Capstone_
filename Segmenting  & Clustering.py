#!/usr/bin/env python
# coding: utf-8

# In[1]:


get_ipython().system('pip install beautifulsoup4')
from bs4 import BeautifulSoup # library for scraping from a website

import numpy as np # library to handle data in a vectorized manner

import pandas as pd # library for data analsysis
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

import json # library to handle JSON files

get_ipython().system('pip install geopy')
from geopy.geocoders import Nominatim # convert an address into latitude and longitude values

import requests # library to handle requests
from pandas.io.json import json_normalize # tranform JSON file into a pandas dataframe

# Matplotlib and associated plotting modules
import matplotlib.cm as cm
import matplotlib.colors as colors

# import k-means from clustering stage
from sklearn.cluster import KMeans

get_ipython().system('pip install folium')
import folium # map rendering library

get_ipython().system('pip install geocoder')
import geocoder # to get longitude and latitude


# In[2]:


url = 'https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M'
page = requests.get(url).text

# Extract only the table
soup = BeautifulSoup(page, 'html.parser')
table = soup.find('table', class_='sortable')

# Get the values from the Wikipedia table and store into a dataframe
row = [] # initialize row list

for tr in table.find_all('tr'):                                           # for every row in the original table
    if tr.find_all('th') == []:                                           # unless it's a header
        row.append([td.get_text(strip=True) for td in tr.find_all('td')]) # every item w/i 'td' tag appended to row list

# Assign columns names and turn row into a dataframe of neighborhoods
column_names = ['Postcode', 'Borough', 'Neighborhood']

neighborhoods_raw = pd.DataFrame(row, columns=column_names) # create a raw table of neighborhoods
neighborhoods_raw.head(10)


# In[3]:


# Rows containing 'Not assigned' boroughs are dropped.
drop_index = neighborhoods_raw[neighborhoods_raw['Borough'] == 'Not assigned'].index # get indexes of rows containing 'Not assigned' borough
neighborhoods = neighborhoods_raw.drop(drop_index, axis=0)                           # rows dropped to create neighborhoods table
neighborhoods.reset_index(drop=True, inplace=True)                                   # resets the index after dropping the rows


# In[4]:


# Assign borough names to neighborhoods when neighborhood is 'Not assigned'
nh_na = neighborhoods[neighborhoods['Neighborhood'] == 'Not assigned'].index # index of those rows
neighborhoods.iloc[nh_na, 2] = neighborhoods['Borough'][nh_na]


# In[5]:


# Neighborhoods with a same postcode are merged into a single cell, separated by commas
neighborhoods = neighborhoods.groupby(['Postcode', 'Borough'], as_index=False).agg(lambda x: ', '.join(x))
neighborhoods


# In[6]:


neighborhoods.shape


# In[7]:


# Initialize varialbes
lat = []
lng = []
lat_lng_coords = None

# Get postcodes from neighborhoods table
postal_code = neighborhoods['Postcode']

# Store latitude and longitude values in lat and lng
for pc in postal_code:
    g = geocoder.arcgis('{}, Toronto, Ontario'.format(pc))
    lat_lng_coords = g.latlng
    lat.append(lat_lng_coords[0])
    lng.append(lat_lng_coords[1])


# In[8]:


# Add the lists containing latitude and longitude values to the neighborhood dataframe
nh_complete = neighborhoods
nh_complete['Latitude'] = lat
nh_complete['Longitude'] = lng


# In[9]:


nh_complete


# In[10]:


# New dataframe with only the original city included
toronto = nh_complete[nh_complete['Borough'].str.find('Toronto') != -1].reset_index(drop=True)
toronto.shape


# In[12]:


# Get the latitude and longitude of Toronto
g = geocoder.arcgis('Toronto, Ontario')
lat_tor = g.latlng[0]
lng_tor = g.latlng[1]

# Create a map of Toronto
map_toronto = folium.Map(location=[lat_tor, lng_tor], zoom_start=11)

# Add markers to map
for lat, lng, bor, postcode in zip(toronto['Latitude'], toronto['Longitude'], toronto['Borough'], toronto['Postcode']):
    label = '{}, {}'.format(postcode, bor)        # popup labels with postcode and borough
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker([lat, lng],
                        radius=5,
                        popup=label,
                        color='blue',
                        fill=True,
                        fill_color='#3186cc',
                        fill_opacity=0.7,
                        parse_html=False).add_to(map_toronto)  
    
map_toronto


# In[13]:


def getNearbyVenues(names, latitudes, longitudes, radius=500):    
    venues_list=[]
    for name, lat, lng in zip(names, latitudes, longitudes):        
        # create the API request URL
        url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
                CLIENT_ID, 
                CLIENT_SECRET, 
                VERSION, 
                lat, 
                lng, 
                radius, 
                LIMIT)
            
        # make the GET request
        results = requests.get(url).json()["response"]['groups'][0]['items']
        
        # return only relevant information for each nearby venue
        venues_list.append([(name,
                             lat,
                             lng,
                             v['venue']['name'],
                             v['venue']['location']['lat'],
                             v['venue']['location']['lng'],
                             v['venue']['categories'][0]['name']) for v in results])

    nearby_venues = pd.DataFrame([item for venue_list in venues_list for item in venue_list])
    nearby_venues.columns = ['Postcode', 
                  'Latitude', 
                  'Longitude', 
                  'Venue', 
                  'Venue Latitude', 
                  'Venue Longitude', 
                  'Venue Category']
    
    return(nearby_venues)


# In[14]:


# Set number of clusters
kclusters = 3

toronto_grouped_clustering = toronto_grouped.drop('Postcode', 1)

# Run k-means clustering
kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(toronto_grouped_clustering)

# Check cluster labels generated for each row in the dataframe
kmeans.labels_[0:10]


# In[ ]:




