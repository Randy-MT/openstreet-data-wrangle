#!/usr/bin/env python
# coding: utf-8

# In[1]:


import xml.etree.ElementTree as ET
from collections import defaultdict
import re
import pprint
import os

import csv
import codecs
import xml.etree.cElementTree as ET
import requests
import cerberus


# ## Data import and sample file creation

# In[2]:



###########################
## Data import and sample file creation
###########################

k = 250 # Parameter: take every k-th top level element

OSM_FILE = "SEA_map.osm" 
OSM_PATH = "sample.osm"
os.chdir(r"C:\Users\randy\OneDrive\Desktop\Udacity\Wrangle_OpenStreet_Submission")
sample_exists = os.path.exists(OSM_PATH) ## Checks to see if a sample file already exists

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

if sample_exists == False:
    with open(OSM_PATH, 'wb') as output:
        output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        output.write('<osm>\n  ')

        # Write every kth top level element
        for i, element in enumerate(get_element(OSM_FILE)):
            if i % k == 0:
                output.write(ET.tostring(element, encoding='utf-8'))

        output.write('</osm>')

    
print 'Filesize is',int(os.stat(OSM_PATH).st_size / 2**20), 'Megabytes'


# ## Data Auditing

# In[3]:



###########################
## Data Auditing 
###########################
street_type_re = re.compile(r'\S+\.?$', re.IGNORECASE)
speed_limit_re = re.compile(r'\S(\w+)$', re.IGNORECASE) # regex to capture last word
street_types = defaultdict(set)
speed_limits = defaultdict(set)
post_codes = defaultdict(set)
name_directions = defaultdict(set)

expected = ["Street","Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons","North","Northeast","Northwest","Southeast","Southwest",
            "South","Way","West","Circle","East","D","Loop","Plaza","Terrace"]

mapping = {"NE": "Northeast","St": "Street","St.": "Street","Blvd.": "Boulevard",'Blvd':"Boulevard","SE": "Southeast",
           "Northest": "Northeast","Dr": "Drive","E": "East","Ave":"Avenue",'avenue':"Avenue","PL":"Place",'N':"North",
           'NW':"Northwest",'S':"South"}

#########################
## Tag locate
#########################
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def is_post_code(elem):
    return (elem.attrib['k'] == "addr:postcode")

def is_speed_limit(elem):
    return (elem.attrib['k'] == "maxspeed")

def is_timestamp(elem):
    return (elem == "timestamp")

##########################
## audits
##########################
def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

def audit_speed_limit(speed_limits,speed_name):
    s = speed_limit_re.search(speed_name)
    if s:
        speed_name = s.group()
        if speed_name != "mph":
            speed_limits[speed_name].add(speed_name)
        
def audit_post_code(post_codes,post_code):
    expected = int(5)
    if len(post_code) != expected:
        post_codes[post_code].add(post_code)
              
def audit(filename):
    for event, elem in ET.iterparse(filename):
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
                if is_speed_limit(tag):
                    audit_speed_limit(speed_limits, tag.attrib['v'])
                if is_post_code(tag):
                    audit_post_code(post_codes, tag.attrib['v'])
    print "Streets to be corrected"
    pprint.pprint (dict(street_types))
    print 
    print "mph abbreviations to be corrected"
    pprint.pprint (dict(speed_limits))
    print
    print "post codes to be corrected"
    pprint.pprint (dict(post_codes))
    print
        
##########################
## Updates
##########################
def update_name(name, mapping):
    m = street_type_re.search(name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            if street_type in mapping:
                name = re.sub(street_type_re, mapping[street_type],name)          
    return name

def update_post_code(post_code):
    expected = int(5)
    if len(post_code) != expected:
        post_code = post_code[:expected]
    return post_code


def update_speed_limit(speed_name):
    expected = 'mph'
    if speed_name[-3:] != 'mph':
        speed_name = speed_name + " " + expected
    return speed_name

###########################
## Audit Call for all conditions 
###########################
audit(OSM_PATH)


# In[4]:



###########################
## Schema 
###########################
schema = {
    'node': {
        'type': 'dict',
        'schema': {
            'id': {'required': True, 'type': 'integer', 'coerce': int},
            'lat': {'required': True, 'type': 'float', 'coerce': float},
            'lon': {'required': True, 'type': 'float', 'coerce': float},
            'user': {'required': True, 'type': 'string'},
            'uid': {'required': True, 'type': 'integer', 'coerce': int},
            'version': {'required': True, 'type': 'string'},
            'changeset': {'required': True, 'type': 'integer', 'coerce': int},
            'timestamp': {'required': True, 'type': 'string'}
        }
    },
    'node_tags': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'id': {'required': True, 'type': 'integer', 'coerce': int},
                'key': {'required': True, 'type': 'string'},
                'value': {'required': True, 'type': 'string'},
                'type': {'required': True, 'type': 'string'}
            }
        }
    },
    'way': {
        'type': 'dict',
        'schema': {
            'id': {'required': True, 'type': 'integer', 'coerce': int},
            'user': {'required': True, 'type': 'string'},
            'uid': {'required': True, 'type': 'integer', 'coerce': int},
            'version': {'required': True, 'type': 'string'},
            'changeset': {'required': True, 'type': 'integer', 'coerce': int},
            'timestamp': {'required': True, 'type': 'string'}
        }
    },
    'way_nodes': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'id': {'required': True, 'type': 'integer', 'coerce': int},
                'node_id': {'required': True, 'type': 'integer', 'coerce': int},
                'position': {'required': True, 'type': 'integer', 'coerce': int}
            }
        }
    },
    'way_tags': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'id': {'required': True, 'type': 'integer', 'coerce': int},
                'key': {'required': True, 'type': 'string'},
                'value': {'required': True, 'type': 'string'},
                'type': {'required': True, 'type': 'string'}
            }
        }
    }
}


# ## Data Shaping

# In[5]:



###########################
## Data Shaping
###########################
NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema

def tag_func(t, element, default_tag_type='regular',problem_chars=PROBLEMCHARS, lower_colon = LOWER_COLON):
    """ Clean and shape way and node tags within shape element function """
    
    if problem_chars.search(t.attrib['k']):
            pass

    else:
        tag ={} 
        tag['id'] = element.attrib['id']
        tag['value'] = t.attrib['v']
        
        if is_street_name(t):#correct the street names
            tag['value'] = update_name(tag['value'],mapping) 
            
        if is_post_code(t):#correct enlongated post codes to unify with majority 
            tag['value'] = update_post_code(tag['value']) 
            
        if is_speed_limit(t):#add mph to all speed limit values
            tag['value'] = update_speed_limit(tag['value'])
                              
        if lower_colon.match(t.attrib['k']):
            k = t.attrib['k'].split(':',1)
            tag['type'] = k[0]
            tag['key'] = k[1]   

        else:
            tag['type'] = default_tag_type
            tag['key'] = t.attrib['k']
        tags.append(tag)

        return tags


# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS):
    """Clean and shape node or way XML element to Python dict"""
    
    global tags
    node_attribs = {}
    way_attribs = {}
    tag = {}
    way_nodes = []
    tags = []  
     
## Node

    if element.tag == 'node':
        for i in node_attr_fields:
            node_attribs[i] = element.attrib[i] 
        # Pass off to tag_func       
        for t in element.iter('tag'):
            value = tag_func(t,element)
            if value == None:
                break
            else: 
                tags = value
            
        return({'node': node_attribs, 'node_tags': tags})
                
## Way   
        
    elif element.tag == 'way':
        for i in way_attr_fields:
            way_attribs[i] = element.attrib[i]
            tag['id'] = element.attrib['id']
            
        ndTagCt = 0 
        for n in element.iter('nd'):
            w_nd = {}
            w_nd['id'] = element.attrib['id'] 
            w_nd['node_id'] = n.attrib['ref']
            w_nd['position'] = ndTagCt
            way_nodes.append(w_nd)
            ndTagCt += 1
            
        for t in element.iter('tag'): 
            # Pass off to tag_func
            value = tag_func(t,element)
            if value == None:
                break
            else: 
                tags = value
            
                
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}  
    
# ================================================== #
#               Helper Functions                     #
# ================================================== #

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


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file,          codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file,          codecs.open(WAYS_PATH, 'w') as ways_file,          codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file,          codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

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
            

if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=True)

