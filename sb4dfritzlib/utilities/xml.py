"""Provides tools to deal with XML strings."""

import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
from datetime import datetime


def pretty_print(xml_string: str) -> str:
    """Properly format an XML string with indentation and line breaks."""
    dom = parseString(xml_string)
    pretty_xml = dom.toprettyxml(indent="  ")
    return pretty_xml

# TODO: NEEDS FIXING!
def xml_to_dict(xml_string:str)->dict:
    """Convert an XML string returned from AHA-HTTP request into a 
    dictionary, including data conversion for timestamps tagged as
    `datatime`. """
    xml_object = ET.fromstring(xml_string)
    xml_dict = {}
    # Include attributes
    xml_dict.update(xml_object.attrib)
    # Include child xml_objectents
    for child in xml_object:
        child_dict = xml_to_dict(child)
        if child.tag in xml_dict:
            # Turn existing entry into a list if multiple same tags exist
            if not isinstance(xml_dict[child.tag], list):
                xml_dict[child.tag] = [xml_dict[child.tag]]
            xml_dict[child.tag].append(child_dict[child.tag])
        else:
            xml_dict.update(child_dict)
    # If xml_objectent has text, include it
    text = xml_object.text.strip() if xml_object.text else None
    if text:
        # Special case: convert datatime values to Python datetime
        if xml_object.tag.lower() == "datatime":
            ts = int(text)
            dt = datetime.fromtimestamp(ts)
            xml_dict[xml_object.tag] = dt
        else:
            xml_dict[xml_object.tag] = text
    return {xml_object.tag: xml_dict}



def xml_to_dict(xml_string: str) -> dict:
    """
    Convert an XML string into a nested Python dictionary.
    """

    def elem_to_dict(elem):
        # Convert attributes and children
        xml_dict = {}
        
        # Include element attributes (if any)
        if elem.attrib:
            xml_dict.update({f"@{k}": v for k, v in elem.attrib.items()})
        
        # Include child elements
        children = list(elem)
        if children:
            child_dict = {}
            for child in children:
                child_as_dict = elem_to_dict(child)
                if child.tag not in child_dict:
                    child_dict[child.tag] = child_as_dict
                else:
                    # Handle multiple same-tag children as a list
                    if not isinstance(child_dict[child.tag], list):
                        child_dict[child.tag] = [child_dict[child.tag]]
                    child_dict[child.tag].append(child_as_dict)
            xml_dict.update(child_dict)
        else:
            # Leaf node → store text content
            xml_dict = elem.text.strip() if elem.text and elem.text.strip() else xml_dict

        return xml_dict

    root = ET.fromstring(xml_string)
    xml_dict = elem_to_dict(root)
    return xml_dict
    # return {root.tag: xml_dict}

import xml.etree.ElementTree as ET

def xml_to_dict(xml_string: str) -> dict:
    """
    Convert an XML string into a nested Python dictionary.
    Attributes are prefixed with '@'.
    Text content is stored as '#text' if attributes are also present,
    otherwise just as the element value.
    """

    def elem_to_dict(elem):
        xml_dict = {}

        # Add attributes
        if elem.attrib:
            xml_dict.update({f"{k}": v for k, v in elem.attrib.items()})

        # Process child elements
        children = list(elem)
        if children:
            child_dict = {}
            for child in children:
                child_as_dict = elem_to_dict(child)
                if child.tag not in child_dict:
                    child_dict[child.tag] = child_as_dict
                else:
                    # If tag already exists, make it a list
                    if not isinstance(child_dict[child.tag], list):
                        child_dict[child.tag] = [child_dict[child.tag]]
                    child_dict[child.tag].append(child_as_dict)
            xml_dict.update(child_dict)
        else:
            # Handle leaf nodes
            text = elem.text.strip() if elem.text and elem.text.strip() else None
            if elem.attrib:
                if text:
                    xml_dict['data'] = text
            else:
                xml_dict = text if text else None

        return xml_dict

    root = ET.fromstring(xml_string)
    return elem_to_dict(root)
    # return {root.tag


def prepare_stats_dict(stats):
    stats['count'] = int(stats['count'])
    stats['grid'] = int(stats['count'])
    timestamp = int(stats['datatime'])
    timestamp = datetime.fromtimestamp(timestamp)
    stats['datatime'] = timestamp
    data = stats['data']
    data = [int(num) for num in data.split(",")]
    stats['data'] = data 
    return stats
    
    