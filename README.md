# barcelona_data_wrangle

## Summary 
As part of Data Analysis Nanodegree, this project was done in order to evaluated data munging skills learned to clean OpenStreetMap data for an area selected. In this case, I selected barcelona city area in https://www.openstreetmap.org After audit and clean the data, the .csv was imported into a SQL database

## Structure
- Dataset: barcelona_spain.osm.bz2
- audit.py: creates a sample data and audit the sample dataset. This script can be updated adding or modifing expected list which includes valid names of street
- data.py: process data. 
- bcn_osm_p3_db.py: create SQL database using schema.py

## Instalation
Python 3
In order to run data.py you must install cerberus 
$ pip install cerberus

## Setup
- First, you should use audit.py script in order to create a sample and audit the file. 
- Then, process data using audit.py. As output of this script you will get .csv needed for SQL database, following schema.py. I've ran the audit.py script first processing sample data and then, after cleaning the data, testing whole dataset
- Use bcn_osm_p3_db.py to get database named 'bcn_osm.db'
