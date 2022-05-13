#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import pandas as pd
from pathlib import Path
import sqlite3

os.chdir(r"C:\Users\randy\OneDrive\Desktop\Udacity\Wrangle_OpenStreet_Submission")
Path('sea_map.db').touch()
conn = sqlite3.connect('sea_map.db')
c = conn.cursor()


# In[2]:


## Create individual tables within database
c.execute("""CREATE TABLE if not exists nodes(id INTEGER, lat NUMERIC, lon NUMERIC, user TEXT, uid INTEGER, version INTEGER, changeset INTEGER, timestamp REAL)""")
c.execute("""CREATE TABLE if not exists nodes_tags(id INTEGER, key TEXT, value TEXT, type TEXT)""")
c.execute("""CREATE TABLE if not exists ways(id INTEGER, user TEXT, uid INTEGER, version INTEGER, changeset INTEGER, timestamp REAL)""")
c.execute("""CREATE TABLE if not exists ways_nodes(id INTEGER, node_id INTEGER, position INTEGER)""")
c.execute("""CREATE TABLE if not exists ways_tags(id INTEGER, key TEXT, value TEXT, type TEXT)""")


# In[3]:


## Create pandas dataframes of the csv files
nodes = pd.read_csv('nodes.csv')
nodes_tags = pd.read_csv('nodes_tags.csv')
ways = pd.read_csv('ways.csv')
ways_nodes = pd.read_csv('ways_nodes.csv')
ways_tags = pd.read_csv('ways_tags.csv')


# In[4]:


## Import csv's through use of pandas into database
nodes.to_sql('nodes', conn, if_exists='append', index = False)
nodes_tags.to_sql('nodes_tags', conn, if_exists='append', index = False)
ways.to_sql('ways', conn, if_exists='append', index = False)
ways_nodes.to_sql('ways_nodes', conn, if_exists='append', index = False)
ways_tags.to_sql('ways_tags', conn, if_exists='append', index = False)

