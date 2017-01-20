#!/usr/bin/python3
import xml.etree.ElementTree as xml
import sys
import os
import json
import re

xml_folder = sys.argv[1]

# Add a backslash on the end if it doesn't exist.
if xml_folder[-1] != "/":
    xml_folder = xml_folder + "/"

if not os.path.isdir(xml_folder):
    print(xml_folder + " is not a valid directory")
    exit()

TEMPLATES_PATH = xml_folder + "templates.xml"
if not os.path.isfile(TEMPLATES_PATH):
    print("Couldn't find templates.xml at " + TEMPLATES_PATH)
    exit()

TOOLTIP_STRINGS_PATH = xml_folder + "tooltip_strings.txt"
if not os.path.isfile(TOOLTIP_STRINGS_PATH):
    print("Couldn't find tooltip_strings.txt at " + TOOLTIP_STRINGS_PATH)
    exit()

CARD_NAME_PATH = xml_folder + "card_names.txt"
if not os.path.isfile(CARD_NAME_PATH):
    print("Couldn't find card_names.txt at " + CARD_NAME_PATH)
    exit()

CRAFT_VALUES = {}
CRAFT_VALUES['Common'] = {"standard": 30, "premium": 200}
CRAFT_VALUES['Rare'] = {"standard": 80, "premium": 400}
CRAFT_VALUES['Epic'] = {"standard": 200, "premium": 800}
CRAFT_VALUES['Legendary'] = {"standard": 800, "premium": 1600}

MILL_VALUES = {}
MILL_VALUES['Common'] = {"standard": 5, "premium": 25}
MILL_VALUES['Rare'] = {"standard": 10, "premium": 50}
MILL_VALUES['Epic'] = {"standard": 50, "premium": 200}
MILL_VALUES['Legendary'] = {"standard": 200, "premium": 800}

CATEGORIES = ["Vampire", "Mage", "Elf", "Potion", "Weather", "Special", "Dyrad", "Breedable",
              "Shapeshifter", "Blue_Stripes", "Wild_Hunt", "Permadeath", "Ambush", "Fleeting", 
              "Vodyanoi", "Witcher", "Relentless", "Dwarf", "Dragon"]

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
    info = ""

    tooltipId = "-1"
    if card_template.find('Tooltip') != None:
        tooltipId = card_template.find('Tooltip').attrib['key']

    descriptionId = tooltipId
    while len(descriptionId) < 4:
        descriptionId = "0" + descriptionId

    tooltip_strings = open(TOOLTIP_STRINGS_PATH, "r")
    for tooltip in tooltip_strings:
        split = tooltip.split(";")
        if descriptionId in split[1]:
            # Remove any quotation marks, new lines and html tags.
            info = cleanHtml(split[2].replace("\"", "").replace("\n", ""))

    tooltip_strings.close()
    return info

def getInfoFromNameFile(card_template, suffix = "name"):
    result = ""
    key = card_template.attrib['dbgStr'].lower().replace(" ", "_").replace("'", "")

    # Add an underscore to the end if there isn't already one.
    if not key[-1] == "_":
        key += "_"

    key += suffix

    card_names = open(CARD_NAME_PATH, "r")
    for line in card_names:
        split = line.split(";")
        if key in split[1]:
            # Remove any quotation marks and new lines.
            result = split[2].replace("\"", "").replace("\n", "")

    card_names.close()
    return result

def getCardData(root):
    cardData = {}
    for template in root:
        cardId = template.attrib['id']
        card = {}

        card['ingameId'] = cardId
        card['strength'] = int(template.attrib['power'])
        card['type'] = template.attrib['group']
        card['lane'] = []
        card['loyalty'] = []
        card['faction'] = template.attrib['factionId'].replace("NorthernKingdom", "Northern Realms")

        card['name'] = getInfoFromNameFile(template)
        card['flavor'] = getInfoFromNameFile(template, "fluff")
        card['category'] = []
        card['info'] = getTooltip(template)

        for flag in template.iter('flag'):
            key = flag.attrib['name']

            if key == "Loyal" or key == "Disloyal":
                card['loyalty'].append(key)

            if key == "Melee" or key == "Ranged" or key == "Siege" or key == "Event":
                card['lane'].append(key)

        for flag in template.iter('Category'):
            key = flag.attrib['id']
            if key in CATEGORIES:
                card['category'].append(key.replace("_", " "))

        card['variations'] = {}

        for definition in template.find('CardDefinitions').findall('CardDefinition'):
            variation = {}
            variationId = definition.attrib['id']

            variation['variationId'] = variationId
            variation['avaliability'] = definition.find('Availability').attrib['V']
            variation['collectible'] = variation['avaliability'] != "NonOwnable"
            variation['rarity'] = definition.find('Rarity').attrib['V']

            variation['craft'] = CRAFT_VALUES[variation['rarity']]
            variation['mill'] = MILL_VALUES[variation['rarity']]

            art = {}
            art['fullsizeImageUrl'] = ""
            art['thumbnailImageUrl'] = ""
            art['artist'] = definition.find("UnityLinks").find("StandardArt").attrib['author']
            variation['art'] = art

            card['variations'][variationId] = variation

        cardData[cardId] = card

    return cardData

tree = xml.parse(TEMPLATES_PATH)
templates_root = tree.getroot()
cardData = getCardData(templates_root)
saveJson("latest.json", cardData)




