#!/bin/bash
#
# Prepare a file for processing.

set -e

#######################################
# Print the usage of the program
# Globals:
#   none
# Arguments:
#   None
# Returns:
#   None
#######################################
usage()
{
cat << EOF
usage: $0 options

This script prepares a .dat file for processing to get game data.

OPTIONS:
    --templates          Path to GwentCardTemplates.dat
    --abilities           Path to GwentCardAbilities.dat
    --tooltips           Path to GwentTooltips.dat
    --tooltip-strings    Path to tooltips_en-US.dat
    --card-names         Path to cards_en-US.dat
    
EOF
}

function checkFile {
    if [[ ! -f $1 ]]
        then
        echo "ERROR: A file ($1) doesn't exist."
        usage
        exit 1
    fi
}

function prepareXmlFile {
    OUTPUT="$(dirname $0)/../outputs/$2.xml"
    echo ${OUTPUT}

    # First, make sure everything is in utf-8.
    iconv -f UTF-8 -t UTF-8 -c $1 > "$OUTPUT.tmp"

    # Then remove everything before the first xml tag.
    sed -i 's/.*<?/<?/' "$OUTPUT.tmp"

    # Remove any lines that don't contain a '<'. Legit xml lines will always contain a '<'.
    sed -i '/</!d' "$OUTPUT.tmp"

    # Replace any instances of '&' with '&amp;' since '&' is an illegal character in xml.
    sed -i 's/\&/\&amp\;/' "$OUTPUT.tmp"

    mv "$OUTPUT.tmp" "$OUTPUT"
}

function prepareStringFile {
    OUTPUT="$(dirname $0)/../outputs/$2.txt"
    echo ${OUTPUT}

    # First, make sure everything is in utf-8.
    iconv -f UTF-8 -t UTF-8 -c $1 > "$OUTPUT.tmp"

    # Remove any lines that don't contain relevant information.
    sed -i "/$3/!d" "$OUTPUT.tmp"

    # Replace any instances of '&' with '&amp;' since '&' is an illegal character in xml.
    sed -i 's/\&/\&amp\;/' "$OUTPUT.tmp"

    mv "$OUTPUT.tmp" "$OUTPUT"
}

# Parse user input.
while [[ $# -gt 1 ]]
do
key="$1"

case $key in
    --templates)
    TEMPLATE_FILE="$2"
    shift # past argument
    ;;
    --abilities)
    ABILITIES_FILE="$2"
    shift # past argument
    ;;
    --tooltips)
    TOOLTIPS_FILE="$2"
    shift # past argument
    ;;
    --tooltip-strings)
    TOOLTIP_STRINGS_FILE="$2"
    shift # past argument
    ;;
    --card-names)
    CARD_NAMES_FILE="$2"
    shift # past argument
    ;;
    *)
    # unknown option
    ;;
esac
shift # past argument or value
done

# We need all the files, so if one of them is not set we will print usage.
checkFile ${TEMPLATE_FILE}
checkFile ${ABILITIES_FILE}
checkFile ${TOOLTIPS_FILE}
checkFile ${TOOLTIP_STRINGS_FILE}
checkFile ${CARD_NAMES_FILE}

prepareXmlFile ${TEMPLATE_FILE} "templates"
prepareXmlFile ${ABILITIES_FILE} "abilities"
prepareXmlFile ${TOOLTIPS_FILE} "tooltips"
prepareStringFile ${TOOLTIP_STRINGS_FILE} "tooltip_strings" "tooltips\""
prepareStringFile ${CARD_NAMES_FILE} "card_names" "cards\""

echo "Preparation complete. Result outputted to $OUTPUT"