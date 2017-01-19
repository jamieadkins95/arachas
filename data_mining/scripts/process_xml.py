#!/usr/bin/python3
import xml.etree.ElementTree as xml
import sys
import os
import json

def saveJson(filename, cardList):
    filepath = os.path.join("../outputs/" + filename)
    print("Saving %s cards to: %s" % (len(cardList), filepath))
    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
        json.dump(cardList, f, sort_keys=True, indent=2, separators=(',', ': '))


xml_folder = sys.argv[1]

if xml_folder[-1] != "/":
    xml_folder = xml_folder + "/"

if not os.path.isdir(xml_folder):
    print(xml_folder + " is not a valid directory")
    exit()

templates_path = xml_folder + "templates.xml"
if not os.path.isfile(templates_path):
    print("Couldn't find templates.xml at " + templates_path)
    exit()

tree = xml.parse(templates_path)
root = tree.getroot()
cardData = {}

for template in root:
    cardId = template.attrib['id']
    card = {}

    card['ingameId'] = cardId
    card['strength'] = int(template.attrib['power'])
    card['type'] = template.attrib['group']
    card['lane'] = []
    card['loyalty'] = []
    card['faction'] = template.attrib['factionId']

    card['name'] = ""
    card['info'] = ""
    card['flavor'] = ""
    card['category'] = []
    card['craft'] = {}
    card['mill'] = {}

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
        art['artist'] = ""
        variation['art'] = art

        card['variations'][variationId] = variation

    cardData[cardId] = card

saveJson("latest.json", cardData)




