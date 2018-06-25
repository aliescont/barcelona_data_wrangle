

import xml.etree.cElementTree as ET
import pprint
import re
from collections import defaultdict


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


street_type_re = re.compile(r'(^[\w]+).*', re.IGNORECASE)  
street_types = defaultdict (set)

#Find postcodes that begins with 08
postcode_re = re.compile(r'^[0][8]', re.IGNORECASE) 
postcodes = defaultdict (set)

#Type of streets expected, most of them in Catalan. 
expected = ["Avinguda", "Carrer", "Carretera","Can", "Cami", "Passeig", "Plaza", "Passatge", "Rambla", 
            "Ronda", "Via", "Travessera", "Torrent", "Baixada", "Castell", "Jardins", "Moll", "Poligono"]

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group(1)
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
   




if __name__ == '__main__':

	audit('barcelona_spain.osm')
