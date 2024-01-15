import cv2
from pyzbar.pyzbar import decode
from PIL import Image
from matplotlib import pyplot as plt
from pyzbar import pyzbar
import time
from PIL import Image, ImageDraw
import numpy 
import csv 


st = time.time()  #tiempo de inicio de ejecución

captura = cv2.VideoCapture("VID_20230322_173621.mp4") 

n_frame = 0 #numero de frame
n_qr_total = 0  #numero total de qrs detectados en el video

# Seteamos la resolucion casteando de float a int. 
frame_width = int(captura.get(3)) 
frame_height = int(captura.get(4)) 
size = (frame_width, frame_height)

positions = ["left_top", "left_down", "right_top", "right_down"]

# Define the codec and create VideoWriter object.The output is stored in 'outpy.avi' file.
out = cv2.VideoWriter('outpy.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 29.458, size)

#Abriendo CSV 
file = open('qr_csv.csv', 'w', newline='')
writer = csv.writer(file)
writer.writerow(['frame', 'qr', 'esquina', 'x', 'y'])   #primera fila del CSV

while (captura.isOpened()):
  
  ret, image = captura.read() #image es un frame del video

  if ret == True:

    #Empieza la logica para croppear el frame
    div_h = 4                #divisor de altura
    div_w = int(div_h/2)     #divisor de ancho (siempre es la mitad del divisor de altura)

    h = int(frame_height/div_h)   #divide en altura y ancho segun la resolucion del video
    w = int(frame_width/div_w)  

    x = 0
    y = 0

    for i in range(0,div_w):                            #Se itera tantas veces se dividio el ancho  
        for j in range(0,div_h):                        #Se itera tantas veces se dividio el largo
         
            crop_img = image[y:y+h, x:x+w]          #crop image es la imagen recortada (en forma de arreglo de numpy)
            cv2.imshow("cropped", crop_img)         #se muestra en pantalla la imagen recortada

            barcodes = pyzbar.decode(crop_img)      #Reconoce todos los QRs de una imagen. Devuelve una lista

            for k, barcode in enumerate(barcodes, start=1):
                # Extraemos el área del rectángulo que envuelve al código de barra, y lo pintamos en la imagen original.
                x1, y1, width, height = barcode.rect #Buscar otros metodos de barcode...

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

                #Logica para pasar los puntos devueltos por el poligono a una lista comun de python
                #Modificar para corregir los puntos
                arr= []                                
                for i in range (0,4):       # 0 a 4 porque el poligono tiene 4 puntos
                    arr_sub = []            # arr_sub es la sub lista, con 2 elementos (x e y) que conforma un punto
                    arr_sub.append(barcode.polygon[i][0]) 
                    arr_sub.append(barcode.polygon[i][1])
                    arr.append(arr_sub)
                arr_np = numpy.int32([numpy.array(arr)])        # QUE HACE ACA?? XDXD. Lista de lista pasa a matriz
                arr = arr_np.tolist()                           # pasa la lista de numpy a una lista de python
                
                #Clase que se llama point. clase hija de point 2d y 3d
                cv2.polylines(crop_img, arr_np, True, (0,0,255), 2)  #dibujar poligono que encierra qr - esto es solo para visualizar en el video

                #Dibujar puntos en las esquinas de los poligonos - esto es solo para visualizar en el video
                cv2.circle(crop_img, (arr[0][0][0],arr[0][0][1]), radius=5, color=(0, 255, 255), thickness=-1) #left_top
                cv2.circle(crop_img, (arr[0][1][0],arr[0][1][1]), radius=5, color=(0, 255, 255), thickness=-1) #left_down
                cv2.circle(crop_img, (arr[0][2][0],arr[0][2][1]), radius=5, color=(0, 255, 255), thickness=-1) #right_top
                cv2.circle(crop_img, (arr[0][3][0],arr[0][3][1]), radius=5, color=(0, 255, 255), thickness=-1) #right_down

                #Escribir en CSV
                for m in range(0,4):
                    writer.writerow([n_frame, data, positions[m], arr[0][m][0], arr[0][m][1]]) #'frame', 'qr', 'esquina', 'x', 'y' 
                            
                #Escribir imagen en el video
                out.write(image)
                cv2.imshow('video', image)   #muestra un frame del video en pantalla

            if cv2.waitKey(1) == ord('s'):
                break
            y = y + h   #Se incrementa la posicion base del cropped en altura

        y = 0       #HIJO DE PUTA - Se tiene que resetear a cero la posicion en altura
        x = x + w   #Se incrementa la posicion base del cropped en ancho

    n_frame += 1    #se incrementa el numero de frame

    if cv2.waitKey(1) == ord('s'):
      break
  else: break
  
captura.release()
cv2.destroyAllWindows()
file.close()

et = time.time()  #tiempo de finalizado de ejecución

elapsed_time = et - st      #tiempo total que tarda el programa
print('Tiempo ejecutado cropped:', elapsed_time, 'seconds')



