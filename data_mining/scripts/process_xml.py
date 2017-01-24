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

TOOLTIPS_PATH = xml_folder + "tooltips.xml"
if not os.path.isfile(TOOLTIPS_PATH):
    print("Couldn't find tooltips.xml at " + TOOLTIPS_PATH)
    exit()

CARD_ABILITIES_PATH = xml_folder + "abilities.xml"
if not os.path.isfile(CARD_ABILITIES_PATH):
    print("Couldn't find abilities.xml at " + CARD_ABILITIES_PATH)
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

def getRawTooltip(card_template):
    info = ""

    tooltipId = "-1"
    if card_template.find('Tooltip') != None:
        tooltipId = card_template.find('Tooltip').attrib['key']
        tooltipIdMap[card_template.attrib['id']] = tooltipId
    else:
        # This card has no tooltip, immediately return.
        return None

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

def getAbilityValue(abilityId, paramName):
    abilities_tree = xml.parse(CARD_ABILITIES_PATH)
    abilities_root = abilities_tree.getroot()
   
    for ability in abilities_root.iter('Ability'):
        if ability.attrib['id'] == abilityId:
            if ability.find(paramName) != None:
                return ability.find(paramName).attrib['V']
            else:
                print(abilityId + ":" + paramName)
                return "JAMIEA"

def evaluateInfoData(cardData):
    # Now that we have the raw strings, we have to get any values that are missing.
    for cardId in cardData:
        # Some cards don't have info.
        if cardData[cardId]['info'] == None:
            continue

        result = re.findall(r'.*?\{(.*?)\}.*?', cardData[cardId]['info']) # Regex. Get all strings that lie between a '{' and '}'.

        tooltips_tree = xml.parse(TOOLTIPS_PATH)
        tooltips_root = tooltips_tree.getroot()

        for tooltip in tooltips_root.iter('CardTooltip'):
            if tooltip.attrib['id'] == tooltipIdMap[cardId]:
                for key in result:
                    for variable in tooltip.iter('VariableData'):
                        data = variable.find(key)
                        if data == None:
                            # This is not the right variable for this key, let's check the next one.
                            continue
                        if "crd" in key:
                            # Spawn a specific card.
                            crd = data.attrib['V']
                            if crd != "":
                                cardData[cardId]['info'] = cardData[cardId]['info'].replace("{" + key + "}", cardData[crd]['name'])
                                # We've found a token card! Mark it as released.
                                cardData[crd]['released'] = True
                                # We've dealt with this key, move on.
                                continue
                        if variable.attrib['key'] == key:
                            # The value is sometimes given immediately here.
                            if data.attrib['V'] != "":
                                cardData[cardId]['info'] = cardData[cardId]['info'].replace("{" + key + "}", data.attrib['V'])
                            else: # Otherwise we are going to have to look in the ability data to find the value.
                                abilityId = variable.find(key).attrib['abilityId']
                                paramName = variable.find(key).attrib['paramName']
                                cardData[cardId]['info'] = cardData[cardId]['info'].replace("{" + key + "}", getAbilityValue(abilityId, paramName))

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
        card['released'] = False

        card['name'] = getInfoFromNameFile(template)
        card['flavor'] = getInfoFromNameFile(template, "fluff")
        card['category'] = []
        card['info'] = getRawTooltip(template)

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
            collectible = variation['avaliability'] != "NonOwnable"
            variation['collectible'] = collectible

            # If the card is collectible we definitely know that it has been released.
            if collectible:
                card['released'] = collectible

            variation['rarity'] = definition.find('Rarity').attrib['V']

            variation['craft'] = CRAFT_VALUES[variation['rarity']]
            variation['mill'] = MILL_VALUES[variation['rarity']]

            art = {}
            art['fullsizeImageUrl'] = definition.find("UnityLinks").find("StandardArt").attrib['HighArt']
            art['thumbnailImageUrl'] = definition.find("UnityLinks").find("StandardArt").attrib['LowArt']
            art['artist'] = definition.find("UnityLinks").find("StandardArt").attrib['author']
            variation['art'] = art

            card['variations'][variationId] = variation

        cardData[cardId] = card

    return cardData

tree = xml.parse(TEMPLATES_PATH)
templates_root = tree.getroot()

tooltipIdMap = {}
cardData = getCardData(templates_root)
evaluateInfoData(cardData)

saveJson("latest.json", cardData)




