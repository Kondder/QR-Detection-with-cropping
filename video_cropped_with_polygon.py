import cv2
from pyzbar.pyzbar import decode
from PIL import Image
from matplotlib import pyplot as plt
from pyzbar import pyzbar
import time
from PIL import Image, ImageDraw
import numpy 



st = time.time()  #tiempo de inicio 

captura = cv2.VideoCapture("VID_20230322_173621.mp4") 

n_qr_total = 0  #numero total de qrs detectados en el video

# We need to set resolutions. 
# so, convert them from float to integer. 
frame_width = int(captura.get(3)) 
frame_height = int(captura.get(4)) 
   
size = (frame_width, frame_height)

# Define the codec and create VideoWriter object.The output is stored in 'outpy.avi' file.
out = cv2.VideoWriter('outpy.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 29.458, (frame_width,frame_height))

while (captura.isOpened()):

  ret, image = captura.read() #image es un frame del video

  if ret == True:


    #Aca va cropped
    h = 160   #dividimos la cropped image en 8 porciones segun el largo (y) 1280/8 = 160. dividir por 2
    w = 180  #dividimos la cropped image en 4 porciones segun el ancho (x) 720/4 = 180. dividir 1

    #h y w q pase usuario - esta re hardcodeado xd
    x = 0
    y = 0

    for i in range(0,4):                            #Se itera 4 veces en x   
        for j in range(0,8):                        #Se itera 8 veces en y
         
            crop_img = image[y:y+h, x:x+w]          #crop image es la imagen recortada (en forma de arreglo de numpy)
            cv2.imshow("cropped", crop_img)         #se muestra en pantalla la imagen recortada

            barcodes = pyzbar.decode(crop_img)      #Reconoce todos los QRs de una imagen. Devuelve una lista

            for k, barcode in enumerate(barcodes, start=1):
                # Extraemos el área del rectángulo que envuelve al código de barra, y lo pintamos en la imagen original.
                x1, y1, width, height = barcode.rect #Buscar otros metodos de barcode...

                # Define the codec and create VideoWriter object.The output is stored in 'outpy.avi' file.

                # Decodificamos el tipo del código, así como la información que contiene.
                data = barcode.data.decode('utf-8')
                type_ = barcode.type
                # Imprimimos los datos del código de barras/QR
                print(f'Información del código de barra #{k}: {data}')
                print(f'Tipo del código de barra #{k}: {type_}')
                n_qr_total = n_qr_total + 1
                print("Cantidad de QRs escaneados: ", n_qr_total)

                # Añadimos la una etiqueta con la información del código de barras/QR a la imagen.
                #f'{data} ({type_})'

                text = f'{data}' 

                #Dibujar texto de info y el cuadrado 
                cv2.putText(crop_img, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 255), 2)
                print(x1+x,y1+y)

                arr= []                                  # ---->REVISAR !!!!!!!!
                for i in range (0,4):
                    arr_sub = []
                    arr_sub.append(barcode.polygon[i][0]) 
                    arr_sub.append(barcode.polygon[i][1])
                    arr.append(arr_sub)
                arr = numpy.array(arr)



                cv2.polylines(crop_img, numpy.int32([arr]), True, (0,0,255), 2)   # ---->REVISAR !!!!!!!!
                
                out.write(image)
                cv2.imshow('video', image)   #muestra un frame del video en pantalla

            cv2.imwrite("VID.jpg", crop_img)
 

            cv2.waitKey(1)
            y = y + h 

        y = 0  #HIJO DE PUTA
        x = x + w
    if cv2.waitKey(30) == ord('s'):
      break
  else: break
  
captura.release()
cv2.destroyAllWindows()

et = time.time()  #tiempo de finalizado

elapsed_time = et - st      #tiempo que tarda el programa
print('Tiempo ejecutado cropped:', elapsed_time, 'seconds')

