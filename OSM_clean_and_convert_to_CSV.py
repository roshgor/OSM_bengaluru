
# coding: utf-8

# ### Clean and convert to CSV

# In[3]:


# Clean and convert to CSV

import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET


OSM_PATH = "bengaluru_india.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def audit_and_clean(postcode):   # Auditing and cleaning postcodes that atleast have 6 digits 
    onlydigits = ''.join(re.findall("\d+", postcode))
    if(onlydigits!=''):
        onlydigits = str(int(onlydigits))
        if(len(onlydigits)==6 and onlydigits[:2]=='56'):
            return onlydigits
        
nodes_counter = 0
ways_counter = 0 
node_tags_counter = 0
way_tags_counter = 0
way_nodes_counter = 0

def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""
    global nodes_counter
    global ways_counter
    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements
    
    ## my code
    if element.tag == 'node':    
        node_attribs = {i: element.attrib[i] for i in NODE_FIELDS}
        nodes_counter +=1
        
    if element.tag == 'way':     
        way_attribs = {i: element.attrib[i] for i in WAY_FIELDS}
        ways_counter +=1
        c = 0
        for child in element:
            if(child.tag == 'nd'):
                way_nodes.append({
                    'id' : way_attribs['id'],
                    'node_id' : child.attrib['ref'],
                    'position' : c
                })
                c+=1
        
    
    if (element.tag =='way' or element.tag =='node'):
        for child in element:
            if(child.tag == 'tag'):
                kval = child.attrib['k']
                if(PROBLEMCHARS.match(kval)):  # If any problematic characters in k value for a tag, we skip it
                    continue
                vval = child.attrib['v']
                if(kval == 'addr:city'):   # If tag k value is addr:city we store value as 'Bengaluru'
                    vval = 'Bengaluru'
                    
                if(kval  ==  'addr:postcode'): # Cleaning postcode values. if non-cleanable. skipping postcode tag
                    clean_postcode = audit_and_clean(vval)
                    if(clean_postcode):
                        vval = clean_postcode
                    else:
                        continue

                        
                if(LOWER_COLON.match(kval)): # Splitting tag k values based on the first ':'
                    split_point = kval.find(':')
                    tags.append({
                                'id': node_attribs['id'] if element.tag =='node' else way_attribs['id'], 
                                'key': kval[split_point+1:],
                                'value': vval,
                                'type' : kval[:split_point]                       
                                })
                else:
                    tags.append({
                                'id': node_attribs['id'] if element.tag =='node' else way_attribs['id'], 
                                'key': kval,
                                'value': vval,
                                'type' : 'regular'                       
                                })
                    
    if element.tag == 'node':
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()




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
def process_map(file_in):
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


        for element in get_element(file_in, tags=('node', 'way')):
            c=0
            el = shape_element(element)
            if el:
                c+=1
                
                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    process_map(OSM_PATH)


# In[4]:


print(nodes_counter)
print(ways_counter)

