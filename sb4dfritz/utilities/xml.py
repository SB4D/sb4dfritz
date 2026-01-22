import xml
import xml.etree.ElementTree as ET
from datetime import datetime


def prettyprint_xml(xml_in):
    temp = xml.dom.minidom.parseString(xml_in)
    xml_out = temp.toprettyxml(indent="  ")
    print(xml_out)

def process_xml_stats(stats_xml):
    # convert to XML tree object
    stats_tree = ET.fromstring(stats_xml)
    # extract stats into dictionary
    stats = {}
    for stat in stats_tree:
        for idx, data in enumerate(stat):
            key = stat.tag if len(stat) == 1 else stat.tag + str(idx+1)
            val = data.attrib
            val['data'] = data.text
            stats[key] = val
    # convert values to appropriate data types
    for key1 in stats:
        for key2 in stats[key1]:
            str_vals = stats[key1][key2]
            num_vals = [int(val) for val in str_vals.split(",")]
            num_vals = num_vals[0] if len(num_vals) == 1 else tuple(num_vals)
            if key2 == 'datatime':
                num_vals = datetime.fromtimestamp(num_vals)
            stats[key1][key2] = num_vals
    return stats

