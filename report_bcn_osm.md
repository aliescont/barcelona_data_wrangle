
# OpenStreetMap Project

## Map Area
I've chosen Barcelona, Spain because is the city where I'm living. Also, I though that would be interesting to evaluate because eventhough it belongs to Spain at the moment, has another local language which is catalan and names of street are usually in that language. Also, I can evaluate if the results I got make sense because I know the city
## Problems encountered in the map
After first audit of a sample of Barcelona dataset, I've found following problems

- Street names are in catalan and spanish and there are some misspelled abbreviations

- There are some street names that don't mention the type of street. For instance, Carrer Sant Antoni Maria Claret appeared just as Sant Antoni Maria Claret 

- Postcode in Barcelona should have this format '08xxx'. However I've found on this dataset postcodes that didn't begin with 08 or have more digits than 5

For this project I've updated street names and postcodes. However, running some queries I found that city name should be updated it too

### Update postcode
First audit (sample) shows that postcodes with errors were
{'08', '28038', 'Barcelona', '08012 Barcelona'}
So, I've created update_postcode function using regular expression that detects this format as expected '08xxx' and remove those errors

Audting complete dataset reveals another issues, such as postcodes with this format '8xxx'. In this case I've assume that first 0 was forgotten and update function adding this rule

```python
def update_postcode(postcode):

    expected = re.match (r'^\d*([0][8]\d{3})', postcode) #Postcode should have '08xxx' format
    search = re.match(r'^\d*([0][8]\d{3})\d', postcode)
    
    #Audit shows that some postcode errors have this format '8xxx'. So, it's possible that 0 was forgotten.
    if expected is None: 
        wrong_pc = re.search (r'^([8]\d{3})', postcode) #For postcode with format '8xxx',this function add 0 before 
        if wrong_pc is None or len(postcode) >4:
            clean_postcode = 'NA'
        else:
            clean_postcode = '0' + wrong_pc.group(1)
            
    elif search is not None:   #Fix error for postcode that begins with '08' but have more than 5 digits
        clean_postcode = 'NA'

    else:
      
         # select the group that is captured
        clean_postcode = expected.group(1)          
    
    return clean_postcode  

```
The format of street type in Barcelona should be: first word refears to street type + name (Ex Avinguda Diagonal). So, auditing sample data shows several errors like misspelled words and abbreviations, type of streets in Spanish and other in Catalan. In order to fix this issues I've used as expected values catalan words and add to mapping most frequent mistakes found on audit.

Another errors found were that some street names don't have the type of street. For instance Bac': {'Bac de Roda'}, were should be Carrer Bac de Roda. Ins this cases I dismissed the value if were not found on expected or mapping.

```python
def update_name(name, mapping):

    m = street_type_re.search(name)
    if m:
        street_type = m.group(1)
        if street_type not in expected:
            if street_type in mapping.keys():
                name = re.sub(street_type_re, mapping[street_type], name)

    return name
```

# Overview of the data

### File sizes
-rw-r--r--@ 1 Alicia  staff  258804451 Sep 24 19:53 barcelona_spain.osm
-rw-r--r--  1 Alicia  staff  183988224 Sep 30 10:31 bcn_osm.db
-rw-r--r--  1 Alicia  staff  94739881 Sep 29 01:14 nodes.csv
-rw-r--r--  1 Alicia  staff  8530844 Sep 29 01:14 nodes_tags.csv
-rw-r--r--  1 Alicia  staff  8909642 Sep 29 01:31 ways.csv
-rw-r--r--  1 Alicia  staff  13955073 Sep 29 01:31 ways_tags.csv
-rw-r--r--  1 Alicia  staff  35568590 Sep 29 01:31 ways_nodes.csv

#### Count nodes
sqlite> SELECT COUNT(*) FROM nodes;
1144437
### Count tags
count_tags ("barcelona_spain.osm")

{'bounds': 1,
 'member': 49560,
 'nd': 1471724,
 'node': 1144437,
 'osm': 1,
 'relation': 3499,
 'tag': 623352,
 'way': 146279}

### Number of unique user
sqlite> SELECT COUNT(DISTINCT(k.uid))
   ...> FROM (SELECT uid FROM nodes UNION ALL SELECT uid FROM ways) as k;
2821
### Count cities 
sqlite> SELECT tags.value, COUNT(*) as count
   ...> FROM (SELECT * FROM nodes_tags UNION ALL SELECT * FROM ways_tags) as tags
   ...> WHERE tags.key = 'city'
   ...> GROUP BY tags.value
   ...> ORDER BY count DESC;
Barcelona|9560
Santa Coloma de Cervelló|2969
Cornellà de Llobregat|562
Badalona|547
El Prat de Llobregat|240
L'Hospitalet de Llobregat|167
Sant Cugat del Vallès|114
Sant Boi de Llobregat|92
Sant Fost de Campsentelles|64
Ripollet|58
Sant Feliu de Llobregat|55
Prat de Llobregat|54
Cerdanyola del Vallès|36
Esplugues de Llobregat|32
Santa Coloma de Gramenet|28
Castelldefels|25
Sant Just Desvern|22
l'Hospitalet de Llobregat|22
Sant Adrià de Besòs|18
Sant Vicenç dels Horts|18
Badia del Vallès|16
Bellaterra|14
barcelona|14
Santa Coloma de Gramanet|13
Montcada i Reixac|12
Sabadell|12
Corbera de Llobregat|10
Gavà|9
Sant Andreu de la Barca|9
Sant Joan Despí|7
BARCELONA|6
Rubí|6
Viladecans|6
la Palma de Cervelló|6
Hospitalet de Llobregat|5
Barberà del Vallès|4
Martorell|4
Molins de Rei|4
Pallejà|4
Sant Cugat de Vallés|4
Torrelles de Llobregat|4
cerdanyola del vallès|4
Alella|3
Bacelona|3
Castellbisbal|3
L'Hospitalet de Llobregat, Barcelona|3
Sant Quirze del Vallès|3
Santa Perpètua de Mogoda|3
Santa coloma de Cervelló|3
Abrera|2
Barelcona|2
Cerdanyola del Valles|2
La Palma de Cervelló|2
Montgat|2
Sant Adrià del Besós|2
Valldoreix, Sant Cugat del Vallès|2
Vallromanes|2
santa Coloma de Cervelló|2
08005|1
08027|1
Barcelana|1
Begues|1
Bellaterra (Cerdanyola del Vallès)|1
Bellvitge|1
Gavà Mar|1
Mira-sol|1
Mira-sol. Sant Cugat del Vallès|1
Montcada i reixac|1
Sant Adrià de Basòs|1
Sant Adrià de Besos|1
Sant Adrià del Besòs|1
Sant Adriá del Besós|1
Sant Climent de Llobregat|1
Sant Cugat del Vallés|1
Santa Perpetua de Moguda|1
Tiana|1
cerdanyola del Vallès|1
el Masnou|1
el Prat del Llobregat Barcelona|1
la Llagosta|1
sabadell|1
sant Andreu de la barca|1
sant Feliu de Llobregat|1
sant Feliu de llobregat|1
sant feliu de llobregat|1
sqlite> 
This query shows that there are some mistakes in city data, such as postcode instead of city name or misspelled city names, such as Barelcona|2 or same city written in different ways, such as
sant Feliu de Llobregat|1
sant Feliu de llobregat|1
sant feliu de llobregat|1

Also shows that Barcelona is the name of city and state and Barcelona city is the most frequent city in this dataset 
### Top nodes amenities
sqlite> SELECT value, COUNT(*) as num
   ...> FROM nodes_tags
   ...> WHERE key='amenity'
   ...> GROUP BY value
   ...> ORDER BY num DESC
   ...> LIMIT 10;
restaurant|1835
bench|1246
drinking_water|1117
bar|776
recycling|681
bank|620
parking_entrance|573
pharmacy|569
cafe|568
parking|413I found interesting that amount number of drinking_water in this dataset is bigger than bars
### Type of cuisine
This query shows top 10 type of restaurants in Barcelona

sqlite> SELECT value, COUNT(*) AS count
   ...> FROM nodes_tags 
   ...> WHERE nodes_tags.key = 'cuisine'
   ...> GROUP BY value
   ...> ORDER BY count DESC
   ...> LIMIT 10;
regional|166
spanish|133
burger|70
pizza|67
japanese|62
tapas|60
italian|55
chinese|31
kebab|28
chicken|24

### Number of schools per city
sqlite> SELECT nodes_tags.value, COUNT(*) as num
   ...> FROM nodes_tags 
   ...> JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value='school') i
   ...> ON nodes_tags.id=i.id
   ...> WHERE nodes_tags.key='city'
   ...> GROUP BY nodes_tags.value
   ...> ORDER BY num DESC
   ...> LIMIT 20;
Barcelona|11
Badalona|5
Santa Coloma de Cervelló|2
Alella|1
Ripollet|1
Sant Cugat del Vallès|1
Sant Feliu de Llobregat|1
Santa Coloma de Gramenet|1
This query shows that most of schools are located in Barcelona. However, it seems that there are a lot of schools that are not included in this dataset because total number is not big enough.
### Number of bicycle_rentals
sqlite> SELECT nodes_tags.value, COUNT(*) as num
   ...> FROM nodes_tags 
   ...> JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value='bicycle_rental') i
   ...> ON nodes_tags.id=i.id
   ...> WHERE nodes_tags.key='city'
   ...> GROUP BY nodes_tags.value
   ...> ORDER BY num DESC;
Barcelona|29
barcelona|6
Bacelona|1
This query shows that all bicycle_rentals are in Barcelona. However, shows again that city name should be updated
## Conclusion
In general, I would say that this dataset is not complete and have a lot of things to clean because there are some inputs in Spanish and other in Catalan and there are a lot of misspelled words or abreviations, specially mispelled words in Catalan. This project only cover some of the things to clean, such as update postcode and street name but needs some improvements; such as update city names and remove postcode with city tag.

I found interesting that for some queries it seems that there is a lot of data missing, such as schools by city. However, for other queries it seems that there is a lot of detail; such as amenities which mentioned number of drinking_water.