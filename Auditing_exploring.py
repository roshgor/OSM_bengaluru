
# coding: utf-8

# ## Auditing and exploring OSM tags

# In[3]:


from collections import defaultdict
import xml.etree.cElementTree as ET
import operator

citynames_count = defaultdict(int)
religions_dict = defaultdict(int)
streets_dict = defaultdict(int)
incorrect_postcodes =[]
amenities_dict = defaultdict(int)
cuisine_dict = defaultdict(int)

def audit_postcode(postcode):  # Auditing post codes, and adding incorrect ones to a list for review
    if(len(postcode)==6 and postcode[:2]=='56'):
        try:
            int(postcode)
        except:
            incorrect_postcodes.append(postcode)
    else:
        incorrect_postcodes.append(postcode)
    

def attribute_explorer(elem):
    k = elem.attrib['k']
    v = elem.attrib['v']
    
    if(k=='addr:city'):
        citynames_count[v]+=1
    
    if(k=='religion'):
        religions_dict[v]+=1
    
    if(k=='addr:postcode'):
        audit_postcode(v)
        if(v == '೫೬೦೦೬೦'):
            pass
    
    if(k=='addr:street'):
        streets_dict[v]+=1
        
    if(k=='amenity'):
        amenities_dict[v]+=1
        
    if(k == 'cuisine'):
        cuisine_dict[v]+=1
        
            
    

def process_map(osm_file):
    for _, elem in ET.iterparse(osm_file):
        if(elem.tag == 'tag'):
            k = elem.attrib['k']
            v = elem.attrib['v']
            attribute_explorer(elem)
            
        elem.clear()
            
        
        
process_map('bengaluru_india.osm')

print(citynames_count)
print(religions_dict)
print(incorrect_postcodes)


# In[7]:


# Top 20 amenities
amenities_dict
sorted(amenities_dict.items(), key=operator.itemgetter(1), reverse = True)[:20]


# In[8]:


# Top 10 cuisines
cuisine_dict
sorted(cuisine_dict.items(), key=operator.itemgetter(1), reverse = True)[:10]


# In[9]:


# Top 50 street names
streets_dict
sorted(streets_dict.items(), key=operator.itemgetter(1), reverse = True)[:50]

