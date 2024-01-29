import cv2
from pyzbar.pyzbar import decode
from PIL import Image
from matplotlib import pyplot as plt
from pyzbar import pyzbar
import time
from PIL import Image, ImageDraw
import numpy as np
import csv
import random
import matplotlib.pyplot as plt


st = time.time()  #tiempo de inicio de ejecución

n_frame = 0 #numero de frame
n_qr_total = 0  #numero total de qrs detectados en el video



positions = ["left_top", "left_bottom", "right_top", "right_bottom"]
full = []


#Abriendo CSV 
file = open('qr_csv.csv', 'w', newline='')
writer = csv.writer(file)
writer.writerow(['track_id','frame', 'qr', 'esquina', 'x', 'y'])   #primera fila del CSV 

# ------ FUNCIONES ------

def convert_lists(pts):      #recibe coordenadas de las esquinas del poligono
    arr= []                                
    for i in range (0,4):       # 0 a 4 porque el poligono tiene 4 puntos
        arr_sub = []            # arr_sub es la sub lista, con 2 elementos (x e y) que conforma un punto
        arr_sub.append(pts[i][0]) 
        arr_sub.append(pts[i][1])
        arr.append(arr_sub)
    arr_np = np.int32(np.array(arr))        # Lista de lista pasa a matriz
    arr = arr_np.tolist()
                              # pasa la lista de numpy a una lista de python
    return arr_np, arr                              # retorna dupla (lista de numpy, lista comun)

def draw_polygons(imagen, coordenate_np, coordenate_list):   #Dibujar poligonos en los frames de un nuevo video

    #Clase que se llama point. clase hija de point 2d y 3d
    cv2.polylines(imagen, [coordenate_np], True, (0,0,255), 2)  #dibujar poligono que encierra qr - esto es solo para visualizar en el video

    #Dibujar puntos en las esquinas de los poligonos - esto es solo para visualizar en el video
    for i in range(0,4):
        cv2.circle(imagen, (coordenate_list[i][0],coordenate_list[i][1]), radius=5, color=(0, 255, 255), thickness=-1) #left_top, left_down, right_top, right_down

    #Escribir imagen en el video
    out.write(image)
    cv2.imshow('video', image)   #muestra un frame del video en pantalla

def csv_write(frame, data, positions, coordenate_list):     #Escribir en CSV
    global track_id
    for i in range(0,4):
        writer.writerow([track_id, frame, data, positions[i], coordenate_list[i][0], coordenate_list[i][1]]) #'track_id','frame', 'qr', 'esquina', 'x', 'y'
        track_id = track_id + 1

def sort_position(coordenate_list):     #Corregir posiciones de los poligonos
    sorted_list_x = sorted(coordenate_list, key=lambda x: x[0], reverse=False)
    sorted_list_left = sorted(sorted_list_x[0:2], key=lambda x: x[1], reverse=True)
    sorted_list_right = sorted(sorted_list_x[2:4], key=lambda x: x[1], reverse=True)
    sorted_list = sorted_list_left + sorted_list_right

    return sorted_list

def generate_heatmap(data_qr, data_x, data_y):     #data_qr es la cantidad de qr reconocidos por iteracion (con un cropped distinto)

    _y= data_y[::-1]                               #Se da vuelta la lista de y para que se imprima de forma ascendente. Antes era data__y.reverse()
    print(len(_y))

    fig, ax = plt.subplots(figsize = (16,12))
    
    ax.set_xticks(np.arange(len(data_x)), labels=data_x)
    ax.set_yticks(np.arange(len(_y)), labels=_y)

    for i in range(0, len(data_qr)):        #Logica para normalizar los valores de la lista (para que sean entre 0 y 1)
        for j in range(0,len(data_qr[i])):
            data_qr[i][j] = data_qr[i][j]/100


    #Ordenar datos para graficar
    data_qr = np.transpose(np.array(data_qr))  #Cambia columna por fila
    data_qr = data_qr.tolist()     
    data_qr.reverse()                          #Este invierte los elementos de la lista
    print(data_qr)

    ax.imshow(data_qr, cmap = "Blues") 

    plt.xlabel('ancho de recorte')
    plt.ylabel('alto de recorte')
    plt.savefig('heatmap.png')
    plt.show()


def cropp_frame(imagen, div_h, div_w, h, w):
    x = 0
    y = 0
    global n_qr_total

    
    for i in range(0,div_w):                            #Se itera tantas veces se dividio el ancho  
        for j in range(0,div_h):                        #Se itera tantas veces se dividio el largo
        
            crop_img = imagen[y:y+h, x:x+w]          #crop image es la imagen recortada (en forma de arreglo de numpy)
            #cv2.imshow("cropped", crop_img)         #se muestra en pantalla la imagen recortada

            barcodes = pyzbar.decode(crop_img)      #Reconoce todos los QRs de una imagen. Devuelve una lista

            for k, barcode in enumerate(barcodes, start=1):
        
                # Decodificamos el tipo del código, así como la información que contiene.
                data = barcode.data.decode('utf-8')
                type_ = barcode.type
                coordenate_polygon = barcode.polygon 
                
                # Imprimimos los datos del código de barras/QR
                #print(f'Información del código de barra #{k}: {data}')
                #print(f'Tipo del código de barra #{k}: {type_}')
                n_qr_total = n_qr_total + 1
                #print("Cantidad de QRs escaneados: ", n_qr_total)

                #Logica para pasar los puntos devueltos por el poligono a una lista comun de python
                arr_np, arr = convert_lists(coordenate_polygon)     #Ver funcion

                corrected_arr = sort_position(arr)


                draw_polygons(crop_img, arr_np, corrected_arr)                #Ver funcion
                
                csv_write(n_frame, data, positions, corrected_arr)            #Ver funcion
                #cv2.waitKey(1)
                
            y = y + h   #Se incrementa la posicion base del cropped en altura

        y = 0        #HIJO DE PUTA - Se tiene que resetear a cero la posicion en altura
        x = x + w   #Se incrementa la posicion base del cropped en ancho
# ------------------------

dt_qr = []      #lista de cantidad de QRs reconocidos por iteracion
dt_x = []       #valores en x para crear heatmap
dt_y = []       #valores en y para crear heatmap
dv = []         #Este arreglo recibe los divisores de altura arbitrarios. Ahora va de 1,6
sub_list = []

#Obtener valores random

#Este va a ser una funcion

#for j in range(0, 24):
#        div_h = random.randint(4,24) #divisor de altura
#        while(div_h not in dv):
#            dv.append(div_h)
#            j = j - 1


for i in range(4,5):
    dv.append(i)

    #[1,2,3,4,5,6]
    
print(dv)
print(len(dv))

for i in range(0,len(dv)):
    sub_list = []       #sub_list es la lista que contiene, para un valor de x, todas las combinaciones con valores de y
    
    for j in range(0,len(dv)):

        elapsed_time = 0
        captura = cv2.VideoCapture("VID_20230322_173621.mp4")

        # Seteamos la resolucion casteando de float a int. 
        frame_width = int(captura.get(3)) 
        frame_height = int(captura.get(4)) 
        size = (frame_width, frame_height)

        # Define the codec and create VideoWriter object.The output is stored in 'outpy.avi' file.
        out = cv2.VideoWriter('outpy.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 29.458, size)

        #CUIDADO CON ESTO !!!!!!!
        div_h = dv[i]            # divisor de altura
        div_w = dv[j]            # divisor de ancho

        h = int(frame_height/div_h)   #divide en altura y ancho segun la resolucion del video
        w = int(frame_width/div_w)  

        valores = [div_h, div_w, h, w]
        print(valores)
        
        #Datos divisores
        dt_x.append(str(div_w))     #Se agregan como string para usarlos como labels en el heatmap
        dt_y.append(str(div_h))

        n_qr_total = 0
        track_id = 1000

        while (captura.isOpened()):

            ret, image = captura.read() #image es un frame del video

            if ret == True:
                
                cropp_frame(image, div_h, div_w, h , w)
                n_frame += 1    #se incrementa el numero de frame
                
                cv2.waitKey(1)
            else: break

        et = time.time()  #tiempo de finalizado de ejecución

        elapsed_time = et - st      #tiempo total que tarda el programa
        print('Tiempo ejecutado cropped:', elapsed_time, 'seconds')

        sub_list.append(n_qr_total)  
        
        captura.release()
        cv2.destroyAllWindows()


    dt_qr.append(sub_list)    #dt_qr es el arreglo con la cantidad de QRs reconocidos para combinaciones de x e y


# Heat map
print(dt_qr)
print(dt_x)
print(dt_y)
if(len(dv)> 4):                     #si el tamaño de la lista es menor a 4 entonces no genera heatmap debido a que necesitas mas de 2 colores para pintar
    generate_heatmap(dt_qr, dv, dv)        

