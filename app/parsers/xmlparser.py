import json
import os
import xml.etree.ElementTree as ET

def xml_to_json(elem_tree):
    results = []
    for sources in elem_tree:
        if sources:
            source_dict = {}
            for source in sources:
                source_dict.update({source.tag: source.text})
                record = xml_to_json(source) 
                if record:
                    source_dict["Record"] = record
            results.append(source_dict)
    return json.dumps(results)


def screen_xml(subdir_path, xml_file):
    file = os.path.join(subdir_path, xml_file)
    tree = ET.parse(file)
    root = tree.getroot()
    elem_tree = root.findall("./Source")
    return xml_to_json(elem_tree)
