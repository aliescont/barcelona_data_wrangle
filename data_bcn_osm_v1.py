import xml.etree.cElementTree as ET
import pprint
import re
from collections import defaultdict
import csv
import codecs
import pprint
import cerberus
import schema


#create a sample
OSM_FILE = "barcelona_spain.osm"  
SAMPLE_FILE = "sample.osm"

k = 10 # Parameter: take every k-th top level element

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag

    Reference:
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


with open(SAMPLE_FILE, 'wb') as output:
    output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write('<osm>\n  ')

    # Write every kth top level element
    for i, element in enumerate(get_element(OSM_FILE)):
        if i % k == 0:
            output.write(ET.tostring(element, encoding='utf-8'))

    output.write('</osm>')

#Audit data

street_type_re = re.compile(r'^^[\w-]+', re.IGNORECASE)
street_types = defaultdict (set)

postcode_re = re.compile(r'^[0][8]', re.IGNORECASE)
postcodes = defaultdict (set)

expected = ["Avinguda", "Carrer", "Carretera","Can", "Cami", "Passeig", "Plaza", "Passatge", "Rambla", 
            "Ronda", "Via", "Travessera", "Torrent", "Baixada"]

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)
    return street_types

def audit_postcode(postcodes, postcode):
    postcodes[postcode].add(postcode)
    return postcodes


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def is_postcode(elem):
    return (elem.attrib['k'] == "addr:postcode")


def audit(osmfile):
    
    for event, elem in ET.iterparse(osmfile, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
                elif is_postcode(tag):
                    audit_postcode(postcodes, tag.attrib['v'])
    
    return postcodes, street_types


#Updating street name and postcode
#In this data there are streets in Spanish and Catalan. I choose most of expected names to be in Catalan

mapping = { "AVDA": "Avinguda",
            "AVENIDA": "Avinguda",
            "Av" : "Avinguda",
            "avinguda": "Avinguda",
            "Avenida" : "Avinguda",
            "C" : "Carrer",
            "c" : "Carrer",
            "Ca": "Carrer",
            "CALLE" : "Carrer",
            "calle": "Carrer",
            "CL" : "Carrer",
            "carrer" : "Carrer",
            "CARRETERA" : "Carretera",
            "carretera" : "Carretera",
            "CR" : "Carretera",
            "CRA" : "Carretera",
            "Pl" : "Plaza",
            "Pla" : "Plaza",
            "pla" : "Plaza",
            "Placa" : "Plaza",
            "Placeta" : "Plaza", 
            "passeig" : "Passeig",
            "Pg" : "Passeig",
            "Paseo" : "Passeig",
            "ronda" : "Ronda",
            "rambla" : "Rambla",
            "RAMBLA" : "Rambla"
            
            }
def update_name(name, mapping):

    m = street_type_re.search(name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            if street_type in mapping.keys():
                name = re.sub(street_type_re, mapping[street_type], name)

    return name

#Postcode in Barcelona should start with '08' and have 3 more digits. For ex: 08012
def update_postcode(postcode):
    expected = re.match (r'^[0][8]', postcode)
    if expected is None:
        clean_postcode = 'NA'
    else:
         # new regular expression pattern
        search = re.match(r'^\d*(\d{5}).*', postcode)
         # select the group that is captured
        clean_postcode = search.group(1)
    
    return clean_postcode  


#schema


OSM_PATH = "barcelona_spain.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

SCHEMA = schema.schema

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')



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

#clean and shape elements

def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    

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
                
#get element

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

#create CSVs

def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
        codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

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


