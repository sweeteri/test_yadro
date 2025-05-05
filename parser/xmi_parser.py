import xml.etree.ElementTree as ET
from xml.dom import minidom
import json


class UMLParser:
    def __init__(self, uml_file):
        self.uml_file = uml_file
        self.classes = {}
        self.aggregations = []
        self.aggregation_map = {}
        self.parse()

    def parse(self):
        tree = ET.parse(self.uml_file)
        root = tree.getroot()

        for cls in root.findall('Class'):
            name = cls.get('name')
            is_root = cls.get('isRoot') == 'true'
            documentation = cls.get('documentation', '')

            attributes = []
            for attr in cls.findall('Attribute'):
                attributes.append({
                    "name": attr.get('name'),
                    "type": attr.get('type')
                })

            self.classes[name] = {
                "isRoot": is_root,
                "documentation": documentation,
                "attributes": attributes,
                "children": []
            }

        for agg in root.findall('Aggregation'):
            src = agg.get('source')
            tgt = agg.get('target')
            source_multiplicity = agg.get('sourceMultiplicity')
            min_ = source_multiplicity.split('..')[0]
            max_ = source_multiplicity.split('..')[-1]

            self.aggregation_map[src] = {'min': min_, 'max': max_}
            self.aggregation_map[tgt] = {'min': '1', 'max': '1'}

            self.classes[tgt]["children"].append((src, min_, max_))

    def generate_meta(self, out_path):
        meta = []
        parent_map = {cls: [] for cls in self.classes}
        for src, tgt, min_, max_ in self.aggregations:
            parent_map[tgt].append((src, min_, max_))

        children = set()
        for info in self.classes.values():
            for child_name, _, _ in info["children"]:
                children.add(child_name)

        ordered = []
        visited = set()

        def visit(cls):
            if cls in visited:
                return
            visited.add(cls)
            for child_name, _, _ in self.classes[cls]["children"]:
                visit(child_name)
            ordered.append(cls)

        for name, info in self.classes.items():
            if info["isRoot"]:
                visit(name)

        for class_name in ordered:
            info = self.classes[class_name]
            entry = {
                "class": class_name,
                "documentation": info["documentation"],
                "isRoot": info["isRoot"]
            }

            if class_name in self.aggregation_map:
                entry["max"] = self.aggregation_map[class_name]["max"]
                entry["min"] = self.aggregation_map[class_name]["min"]

            parameters = info["attributes"].copy()
            for child_name, _, _ in info["children"]:
                parameters.append({
                    "name": child_name,
                    "type": "class"
                })
            entry["parameters"] = parameters

            meta.append(entry)

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=4)

    def generate_config(self, out_path):
        def build_element(class_name):
            cls_info = self.classes[class_name]
            elem = ET.Element(class_name)
            elem.text = "\n"
            for attr in cls_info["attributes"]:
                child = ET.SubElement(elem, attr["name"])
                child.text = attr["type"]
            for child_name, _, _ in cls_info["children"]:
                child_elem = build_element(child_name)
                elem.append(child_elem)
            return elem

        for name, info in self.classes.items():
            if info["isRoot"]:
                root_elem = build_element(name)

                rough_string = ET.tostring(root_elem, encoding="utf-8")
                reparsed = minidom.parseString(rough_string)

                pretty_xml = reparsed.toprettyxml(indent="    ")
                pretty_xml = "\n".join(
                    [line for line in pretty_xml.split("\n") if line.strip() and not line.startswith("<?xml")]
                )

                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(pretty_xml)

                break
