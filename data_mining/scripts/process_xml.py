#!/usr/bin/python3
import xml.etree.ElementTree as xml
import sys
import os
import json
import re

def saveJson(filename, cardList):
    filepath = os.path.join("../outputs/" + filename)
    print("Saving %s cards to: %s" % (len(cardList), filepath))
    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
        json.dump(cardList, f, sort_keys=True, indent=2, separators=(',', ': '))

def cleanHtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext

def getTooltip(card_template):
    tooltipId = "-1"
    if template.find('Tooltip') != None:
        tooltipId = template.find('Tooltip').attrib['key']

    descriptionId = tooltipId
    while len(descriptionId) < 4:
        descriptionId = "0" + descriptionId

    tooltip_strings = open(tooltip_strings_path, "r")
    for tooltip in tooltip_strings:
        split = tooltip.split(";")
        if descriptionId in split[1]:
            # Remove any quotation marks, new lines and html tags.
            return cleanHtml(split[2].replace("\"", "").replace("\n", ""))

    tooltip_strings.close()

xml_folder = sys.argv[1]

# Add a backslash on the end if it doesn't exist.
if xml_folder[-1] != "/":
    xml_folder = xml_folder + "/"

if not os.path.isdir(xml_folder):
    print(xml_folder + " is not a valid directory")
    exit()

templates_path = xml_folder + "templates.xml"
if not os.path.isfile(templates_path):
    print("Couldn't find templates.xml at " + templates_path)
    exit()

tooltip_strings_path = xml_folder + "tooltip_strings.txt"
if not os.path.isfile(tooltip_strings_path):
    print("Couldn't find tooltip strings at " + tooltip_strings_path)
    exit()

tree = xml.parse(templates_path)
templates_root = tree.getroot()
cardData = {}

for template in templates_root:
    cardId = template.attrib['id']
    card = {}

    card['ingameId'] = cardId
    card['strength'] = int(template.attrib['power'])
    card['type'] = template.attrib['group']
    card['lane'] = []
    card['loyalty'] = []
    card['faction'] = template.attrib['factionId'].replace("NorthernKingdom", "Northern Realms")

    card['name'] = template.attrib['dbgStr']
    card['info'] = ""
    card['flavor'] = ""
    card['category'] = []
    card['craft'] = {}
    card['mill'] = {}

    card['info'] = getTooltip(template)

    for flag in template.iter('flag'):
        key = flag.attrib['name']

        if key == "Loyal" or key == "Disloyal":
            card['loyalty'].append(key)

        if key == "Melee" or key == "Ranged" or key == "Siege" or key == "Event":
            card['lane'].append(key)

        if key == "Potion" or key == "Vampire" or key == "Mage" or key == "Elf": # Loads more to add.
            card['category'].append(key)

    card['variations'] = {}

    for definition in template.find('CardDefinitions').findall('CardDefinition'):
        variation = {}
        variationId = definition.attrib['id']

        variation['variationId'] = variationId
        variation['avaliability'] = definition.find('Availability').attrib['V']
        variation['collectible'] = variation['avaliability'] != "NonOwnable"
        variation['rarity'] = definition.find('Rarity').attrib['V']

        art = {}
        art['fullsizeImageUrl'] = ""
        art['thumbnailImageUrl'] = ""
        art['artist'] = definition.find("UnityLinks").find("StandardArt").attrib['author']
        variation['art'] = art

        card['variations'][variationId] = variation

    cardData[cardId] = card

saveJson("latest.json", cardData)




