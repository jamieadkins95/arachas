#!/usr/bin/python3

import os

inputDirectory = "./"
output = "../images"

if not os.path.exists(output):
    os.makedirs(output)
    
# Sort all of the cards images into folders named by their card id and variation id.
for filename in os.listdir(inputDirectory):
    if filename.endswith(".png"):
        cardId = filename.split("_")[0]
        cardDirectory = os.path.join(output, cardId)
        if not os.path.exists(cardDirectory):
            os.makedirs(cardDirectory)
            
        variationId = cardId + filename.split(".png")[0][-1] + "0"
        variationDirectory = os.path.join(cardDirectory, variationId)
        if not os.path.exists(variationDirectory):
            os.makedirs(variationDirectory)

        print(os.path.join(inputDirectory, filename), "->", os.path.join(variationDirectory, "fullsize.png"))
        os.rename(os.path.join(inputDirectory, filename), os.path.join(variationDirectory, "fullsize.png"))