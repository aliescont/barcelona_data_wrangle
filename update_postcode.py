import re

test = ['08012','28038', '08012 Barcelona', '28239']

def update_postcode(postcode):
    # new regular expression pattern
    search = re.match(r'^\d*(\d{5}).*', postcode)
    # select the group that is captured
    expected = re.match (r'^[0][8]', postcode)
    if expected is None:
        clean_postcode = 'NA'
    else:
         clean_postcode = search.group(1)
    return clean_postcode  

for item in test:
    cleaned = update_postcode(item)
    print cleaned
#Above function shows AttributeError: 'NoneType' object has no attribute 'group' when it runs to complete datase, but works fine with sample

test = ['08012','28038', '08012 Barcelona', '28239']
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

for item in test:
    cleaned = update_postcode(item)
    print cleaned

#Still getting same error


