
# coding: utf-8

# In[1]:

import sqlite3
import csv
from pprint import pprint


# In[2]:

sqlite_file = 'bcn_osm.db'    # name of the sqlite database file


# In[3]:

conn = sqlite3.connect(sqlite_file)  # Connect to the database


# In[4]:

cur = conn.cursor() # Get a cursor object


# In[5]:

# create nodes table

cur.execute("CREATE TABLE nodes (id, lat, lon, user, uid, version, changeset, timestamp);")

with open('nodes.csv','rb') as fin:
    dr = csv.DictReader(fin) 
    to_db = [(i['id'].decode("utf-8"), i['lat'].decode("utf-8"), i['lon'].decode("utf-8"), i['user'].decode("utf-8"), 
              i['uid'].decode("utf-8"), i['version'].decode("utf-8"), i['changeset'].decode("utf-8"), 
              i['timestamp'].decode("utf-8")) 
             for i in dr]

cur.executemany("INSERT INTO nodes (id, lat, lon, user, uid, version, changeset, timestamp)                 VALUES (?, ?, ?, ?, ?, ?, ?, ?);", to_db)
conn.commit()


# In[6]:

#create nodes_tags table

cur.execute("CREATE TABLE nodes_tags (id, key, value, type);")

with open('nodes_tags.csv','rb') as fin:
    dr = csv.DictReader(fin) 
    to_db = [(i['id'].decode("utf-8"), i['key'].decode("utf-8"), i['value'].decode('utf-8'), i['type'].decode("utf-8"))
             for i in dr]

cur.executemany("INSERT INTO nodes_tags (id, key, value, type) VALUES (?, ?, ?, ?);", to_db)
conn.commit()


# In[7]:

#create ways table

cur.execute("CREATE TABLE ways (id, user, uid, version, changeset, timestamp);")

with open('ways.csv','rb') as fin:
    dr = csv.DictReader(fin) 
    to_db = [(i['id'].decode("utf-8"), i['user'].decode("utf-8"), i['uid'].decode("utf-8"), 
              i['version'].decode("utf-8"), i['changeset'].decode("utf-8"), i['timestamp'].decode("utf-8")) 
             for i in dr]

cur.executemany("INSERT INTO ways (id, user, uid, version, changeset, timestamp) VALUES (?, ?, ?, ?, ?, ?);", to_db)
conn.commit()


# In[8]:

#create ways_tags table

cur.execute("CREATE TABLE ways_tags (id, key, value, type);")

with open('ways_tags.csv','rb') as fin:
    dr = csv.DictReader(fin) 
    to_db = [(i['id'].decode("utf-8"), i['key'].decode("utf-8"), i['value'].decode("utf-8"), i['type'].decode("utf-8"))
             for i in dr]

cur.executemany("INSERT INTO ways_tags (id, key, value, type) VALUES (?, ?, ?, ?);", to_db)
conn.commit()


# In[14]:

#create ways_nodes table

cur.execute("CREATE TABLE ways_nodes (id, node_id, position);")
with open('ways_nodes.csv','rb') as fin:
    dr = csv.DictReader(fin) 
    to_db = [(i['id'].decode("utf-8"), i['node_id'].decode("utf-8"), i['position'].decode("utf-8") )
             for i in dr]
cur.executemany("INSERT INTO ways_nodes (id, node_id, position) VALUES (?, ?, ?);", to_db)
conn.commit()


# In[ ]:



