#!/usr/bin/python3
import xml.etree.ElementTree as xml

tree = xml.parse('../outputs/templates.xml')
root = tree.getroot()

print(root)
