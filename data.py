import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
from collections import defaultdict

import cerberus

import schema


street_type_re = re.compile(r'(^[\w]+).*', re.IGNORECASE)  
street_types = defaultdict (set)

#Find postcodes that begins with 08
postcode_re = re.compile(r'^[0][8]', re.IGNORECASE) 
postcodes = defaultdict (set)

expected = ["Avinguda", "Carrer", "Carretera","Can", "Cami", "Passeig", "Plaza", "Passatge", "Rambla", 
            "Ronda", "Via", "Travessera", "Torrent", "Baixada", "Castell", "Jardins", "Moll", "Poligono"]


mapping = { "AVDA": "Avinguda",
            "AVENIDA": "Avinguda",
            "Av" : "Avinguda",
            "avinguda": "Avinguda",
            "Avenida" : "Avinguda",
            "Avda" : "Avinguda",
            "Ave" : "Avinguda",
            "Avinguida" : "Avinguda",
            "Avnd" : "Avinguda",
            "A-2" : "Autovia A-2",
            "C" : "Carrer",
            "c" : "Carrer",
            "c." : "Carrer",
            "Ca": "Carrer",
            "Carrer." : "Carrer",
            "CALLE" : "Carrer",
            "calle": "Carrer",
            "CL" : "Carrer",
            "carrer" : "Carrer",
            "Caller" : "Carrer",
            "Calle" : "Carrer",
            "Carrar" :"Carrer",
            "Carre" : "Carrer",
            "Carrerl" : "Carrer",
            "Carrier" : "Carrer",
            "CARRETERA" : "Carretera",
            "carretera" : "Carretera",
            "CTRA" : "Carretera",
            "Ctra" : "Carretera",
            "CR" : "Carretera",
            "CRA" : "Carretera",
            "Pl" : "Plaza",
            "pl" : "Plaza",
            "Pla" : "Plaza",
            "pla" : "Plaza",
            "Placa" : "Plaza",
            "PS" : "Passeig",
            "Placeta" : "Plaza", 
            "PLAZA" : "Plaza",
            "passeig" : "Passeig",
            "Paaseig" : "Passeig",
            "P" : "passeig",
            "Pg" : "Passeig",
            "Paseo" : "Passeig",
            "PASEO" :  "Passeig",
            "Passad" : "Passeig",
            "Pseo" : "Passeig",
            "passatge" : "Passatge",
            "Diagonal" : "Avinguda Diagonal",
            "ronda" : "Ronda",
            "RONDA" : "Ronda",
            "rambla" : "Rambla",
            "RAMBLA" : "Rambla",
            "Ramble" : "Rambla",
            "Rembla" : "Rambla",
            "Rbla" : "Rambla",
            "Rambleta" : "Rambla",
            "TRAVESIA" : "Travesia",
            "TRAVESSIA" : "Travesia",
            "Cam" : "Cami",
            "Camino" : "Cami",
            "BV 2002" : "Carretera BV 2002",
            "BV" : "Carretera BV 2002",
            "BP-1417" : "Carretera BP-1417"}


def update_name(name, mapping):

    m = street_type_re.search(name)
    if m:
        street_type = m.group(1)
        if street_type not in expected:
            if street_type in mapping.keys():
                name = re.sub(street_type_re, mapping[street_type], name)

    return name


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


OSM_PATH = "barcelona_spain.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

SCHEMA = schema.schema


LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\?%#$@\,\.\\t\r\n]') 


# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

def load_new_tag(element, secondary, default_tag_type):
    """
    Load a new tag dict to go into the list of dicts for way_tags, node_tags
    """
    new = {}
    new['id'] = element.attrib['id']
    if ":" not in secondary.attrib['k']:
        new['key'] = secondary.attrib['k']
        new['type'] = default_tag_type
    else:
        post_colon = secondary.attrib['k'].index(":") + 1
        new['key'] = secondary.attrib['k'][post_colon:]
        new['type'] = secondary.attrib['k'][:post_colon - 1]
        new['value'] = secondary.attrib['v']
    
    print secondary.attrib['v']
    
    return new


# In[ ]:

def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []
                
        
    if element.tag == 'node':
        for attrib in element.attrib:
            if attrib in NODE_FIELDS:
                node_attribs[attrib] = element.attrib[attrib]

        for node_tag in element:
            node_tags = {}
            if LOWER_COLON.match(node_tag.attrib['k']):
                node_tags['type'] = node_tag.attrib['k'].split(':',1)[0]
                node_tags['key'] = node_tag.attrib['k'].split(':',1)[1]
                node_tags['value'] = node_tag.attrib['v']
                node_tags['id'] = element.attrib['id']
                if node_tag.attrib['k'] == 'addr:street':
                    node_tags['value'] = update_name(node_tag.attrib['v'], mapping)
                if node_tag.attrib['k'] == 'addr:postcode':
                    node_tags["value"] = update_postcode(node_tag.attrib['v'])
                else:
                    node_tags['value'] = node_tag.attrib['v']
                tags.append(node_tags)
                
            elif PROBLEMCHARS.match(node_tag.attrib['k']):
                continue
            else:
                node_tags['type'] = 'regular'
                node_tags['id'] = element.attrib['id']
                node_tags['key'] = node_tag.attrib['k'] 
                node_tags['value'] = node_tag.attrib['v']
                tags.append(node_tags)
                
                
        
        return {'node': node_attribs, 'node_tags': tags}


    elif element.tag == 'way':
        for attrib in element.attrib:
            if attrib in WAY_FIELDS:
                way_attribs[attrib] = element.attrib[attrib]

        position = 0        
        for child in element:
            way_node = {}
            way_tag = {}

            if  child.tag == 'tag':
                if LOWER_COLON.match(child.attrib['k']):
                    way_tag['id'] = element.attrib['id']
                    way_tag['type'] = child.attrib['k'].split(':',1)[0]
                    way_tag['key'] = child.attrib['k'].split(':',1)[1]
                    way_tag['value'] = child.attrib['v']
                    if child.attrib['k'] == 'addr:street':
                        
                        way_tag['value'] = update_name(child.attrib['v'], mapping)
                        print way_tag['value']
                        
                    if child.attrib['k'] == 'addr:postcode':
                        # clean the 'v' attribute (i.e. the value)
                        way_tag["value"] = update_postcode(child.attrib["v"])
                        print way_tag['value']
                    else:
                        way_tag['value'] = child.attrib['v']
                    tags.append(way_tag)
                   
                elif PROBLEMCHARS.match(child.attrib['k']):
                       continue

                else:
                        way_tag['type'] = 'regular'
                        way_tag['id'] = element.attrib['id']
                        way_tag['key'] = child.attrib['k']
                        way_tag['value'] = child.attrib['v']
                        tags.append(way_tag)

            elif  child.tag == 'nd':
                way_node['id'] = element.attrib['id']
                way_node['node_id'] = child.attrib['ref']
                way_node['position'] = position
                position += 1
                way_nodes.append(way_node)
                
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}
                
  


# In[ ]:

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# In[ ]:

def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file,          codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file,          codecs.open(WAYS_PATH, 'w') as ways_file,         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file,          codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()



        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == "__main__":
    data = process_map(OSM_PATH, validate=True)