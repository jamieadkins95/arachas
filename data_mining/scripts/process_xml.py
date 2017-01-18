#!/usr/bin/python3
import xml.etree.ElementTree as xml

tree = xml.parse('templates3.dat')
root = tree.getroot()

print(root)
