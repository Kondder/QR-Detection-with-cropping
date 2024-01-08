import cv2
from pyzbar.pyzbar import decode
from PIL import Image
from matplotlib import pyplot as plt
from pyzbar import pyzbar
import time 

i = 0
st = time.time()  #tiempo de inicio 

captura = cv2.VideoCapture("VID_20230322_173621.mp4") 

n_qr_total = 0      #numero total de qrs reconocidos en el video

while (captura.isOpened()):
  
  ret, image = captura.read()   #image 
  if ret == True:

    cv2.imshow('video', image)

    
    barcodes = pyzbar.decode(image)

    for k, barcode in enumerate(barcodes, start=1):
        # Extraemos el área del rectángulo que envuelve al código de barra, y lo pintamos en la imagen original.
        x1, y1, width, height = barcode.rect  #Aca estan las posiciones de x e y
        cv2.rectangle(image, (x1, y1), (x1 + width, y1 + height), (0, 0, 255), 2)

        # Decodificamos el tipo del código, así como la información que contiene.
        data = barcode.data.decode('utf-8')
        #print(type(data))
        type_ = barcode.type

        # Imprimimos los datos del código de barras/QR
        print(f'Información del código de barra #{k}: {data}')
        print(f'Tipo del código de barra #{k}: {type_}')
        n_qr_total = n_qr_total + 1
        print("Cantidad de QRs escaneados: ", n_qr_total)

        # Añadimos la una etiqueta con la información del código de barras/QR a la imagen.
        #f'{data} ({type_})'
        text = f'{k}{data}' 
        
    if cv2.waitKey(30) == ord('s'):
      break
  else: break
  
captura.release()
cv2.destroyAllWindows()

et = time.time()  #tiempo de finalizado

elapsed_time = et - st      #tiempo que tarda el programa
print('Tiempo ejecutado no cropped:', elapsed_time, 'seconds')