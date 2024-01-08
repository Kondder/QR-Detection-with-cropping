import cv2
from pyzbar import pyzbar

#Un genio el que hizo este codigo clapclapclap

image = cv2.imread("qrzoom.png")

barcodes = pyzbar.decode(image)

print(barcodes)
for i, barcode in enumerate(barcodes, start=1):
    # Extraemos el área del rectángulo que envuelve al código de barra, y lo pintamos en la imagen original.
    x, y, width, height = barcode.rect
    cv2.rectangle(image, (x, y), (x + width, y + height), (0, 0, 255), 2)

    # Decodificamos el tipo del código, así como la información que contiene.
    data = barcode.data.decode('utf-8')
    type_ = barcode.type

    # Imprimimos los datos del código de barras/QR
    print(f'Información del código de barra #{i}: {data}')
    print(f'Tipo del código de barra #{i}: {type_}')

    # Añadimos la una etiqueta con la información del código de barras/QR a la imagen.
    text = f'{data} ({type_})'
    cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 255), 2)

cv2.imwrite("qrzoom.png", image)