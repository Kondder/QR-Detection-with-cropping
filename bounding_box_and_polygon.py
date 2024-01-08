#!/usr/bin/env python3
"""Writes bounding_box_and_polygon.png that illustrates
"""
from PIL import Image, ImageDraw

from pyzbar.pyzbar import decode

import numpy


image = Image.open('qrcode.png').convert('RGB')
draw = ImageDraw.Draw(image)


for barcode in decode(image):
    rect = barcode.rect #saca el rectangulo que contiene al qr detectado
    draw.rectangle(
        (
            (rect.left, rect.top),
            (rect.left + rect.width, rect.top + rect.height)
        ),
        outline='#0080ff'
    )
    draw.polygon(barcode.polygon, outline='#e945ff')

    # -- HIJO DE PUTA -- 
    arr= []
    for i in range (0,4):
        arr_sub = []
        arr_sub.append(barcode.polygon[i][0]) 
        arr_sub.append(barcode.polygon[i][1])
        arr.append(arr_sub)


    print(type(barcode.polygon))
    print(arr)
    arr = numpy.array(arr)
    print(type(arr))

image.save('qrcode.png')
