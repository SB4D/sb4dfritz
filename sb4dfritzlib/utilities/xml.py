"""Provides tools to deal with XML strings."""

import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString


def pretty_print(xml_string: str) -> str:
    """Properly format an XML string with indentation and line breaks."""
    dom = parseString(xml_string)
    pretty_xml = dom.toprettyxml(indent="  ")
    return pretty_xml


def xml_to_dict(xml_string: str) -> dict:
    """Converts an XML string into a nested Python dictionary."""

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
