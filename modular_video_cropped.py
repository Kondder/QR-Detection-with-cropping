import cv2
from pyzbar.pyzbar import decode
from matplotlib import pyplot as plt
from pyzbar import pyzbar
import time
import numpy as np
import csv
import time
import matplotlib.pyplot as plt


positions = ["left_top", "left_bottom", "right_top", "right_bottom"]
full = []
array_id = []


#Abriendo CSV 
file = open('qr_csv.csv', 'w', newline='')
writer = csv.writer(file)
writer.writerow(['frame', 'qr', 'esquina', 'x', 'y'])   #primera fila del CSV 

dt_qr = []      #lista de cantidad de QRs reconocidos por iteracion
dt_x = []       #valores en x para crear heatmap
dt_y = []       #valores en y para crear heatmap
dv = []         #Este arreglo recibe los divisores de altura arbitrarios. Ahora va de 1,6

sub_list = []       #sub_list es la lista que contiene, para un valor de x, todas las combinaciones con valores de 
elapsed_time = 0

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
    out.write(imagen)
    #cv2.imshow('video', imagen)   #muestra un frame del video en pantalla

def csv_write(frame, data, positions, coordenate_list, x , y):     #Escribir en CSV
    for i in range(0,4):
        writer.writerow([frame, data, positions[i], coordenate_list[i][0]+x, coordenate_list[i][1]+y]) #'track_id','frame', 'qr', 'esquina', 'x', 'y'

def sort_position(coordenate_list):     #Corregir posiciones de los poligonos
    sorted_list_x = sorted(coordenate_list, key=lambda x: x[0], reverse=False)
    sorted_list_left = sorted(sorted_list_x[0:2], key=lambda x: x[1], reverse=True)
    sorted_list_right = sorted(sorted_list_x[2:4], key=lambda x: x[1], reverse=True)
    sorted_list = sorted_list_left + sorted_list_right

    return sorted_list

def generate_heatmap(data, data_qr, data_x, data_y, strategy):     #data_qr es la cantidad de qr reconocidos por iteracion (con un cropped distinto)
    if(strategy == 0):
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
    if(strategy == 1):
        # Guardar valores de coorednadas y cantidad de QR en arreglos independientes
        y_coords = [d[0] for d in data]
        x_coords = [d[1] for d in data]
        values = [d[2] for d in data]

        heatmap_size = (max(y_coords) + 1, max(x_coords) + 1)   # Calcular el tamaño del heatmap
        heatmap = np.zeros(heatmap_size)    # Crear una matriz para almacenar los valores del heatmap

        # Reemplazar los valores de 0 por Cantidad de QR
        for y, x, value in data:
            heatmap[y, x] = value

        # Crear el heatmap
        plt.figure(figsize=(8, 6))
        plt.imshow(heatmap,cmap = "Blues")

        # Añadir las etiquetas de los ejes
        plt.xticks(np.arange(heatmap_size[1]), np.arange(heatmap_size[1]))
        plt.yticks(np.arange(heatmap_size[0]), np.arange(heatmap_size[0]))

        # Añadir los valores dentro de los recuadros del heatmap
        for y in range(heatmap_size[0]):
            for x in range(heatmap_size[1]):
                if heatmap[y, x] != 0:
                    plt.text(x, y, int(heatmap[y, x]), ha='center', va='center', color='white')

        # Mostrar el heatmap
        plt.title('Heatmap')
        plt.xlabel('Divisor de desplazamiento en X')
        plt.ylabel('Divisor de desplazamiento en Y')
        plt.savefig('divisores_heatmap.png')
        plt.show()

def cropp_frame(imagen, div_h, div_w, h, w, desp_x, desp_y):
    x = 0
    y = 0

    qr_frame = []

    global n_qrtotal
    for i in range(0,div_w*div_desp_x):                            #Se itera tantas veces se dividio el ancho  
        for j in range(0,div_h*div_desp_y):                        #Se itera tantas veces se dividio el largo
            crop_img = imagen[y:y+h, x:x+w]          #crop image es la imagen recortada (en forma de arreglo de numpy)

            barcodes = pyzbar.decode(crop_img)      #Reconoce todos los QRs de una imagen. Devuelve una lista
            
            for k, barcode in enumerate(barcodes, start=1):
                
                # Decodificamos el tipo del código, así como la información que contiene.
                data = barcode.data.decode('utf-8')
                coordenate_polygon = barcode.polygon 
                
                if not data in qr_frame: 
                    qr_frame.append(data)
                    #Logica para pasar los puntos devueltos por el poligono a una lista comun de python
                    arr_np, arr = convert_lists(coordenate_polygon)     #Ver funcion

                    corrected_arr = sort_position(arr)

                    n_qrtotal = n_qrtotal + 1
                    #draw_polygons(crop_img, arr_np, corrected_arr)                #Ver funcion
                            
                    #cv2.imshow("cropped", crop_img)
                    csv_write(n_frame, data, positions, corrected_arr, x, y)            #Ver funcion
                    cv2.waitKey(1)
        
            y = y + desp_y  #Se incrementa la posicion base del cropped en altura
        y = 0        #HIJO DE PUTA - Se tiene que resetear a cero la posicion en altura
        x = x + desp_x   #Se incrementa la posicion base del cropped en ancho

# ------------------------

#CUIDADO CON ESTO !!!!!!!
desp_list = []

all_qrs = []
for i in range(2,8):
        
        
        st = time.time()  #tiempo de inicio de ejecución

        n_frame = 0 #numero de frame
        captura = cv2.VideoCapture("VID_20230322_173621.mp4")

        # Seteamos la resolucion casteando de float a int. 
        frame_width = int(captura.get(3)) 
        frame_height = int(captura.get(4)) 
        size = (frame_width, frame_height)

        # Define the codec and create VideoWriter object.The output is stored in 'outpy.avi' file.
        out = cv2.VideoWriter('outpy.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 29.458, size)
        
        n_qrtotal = 0

        div_h = 5          # divisor de altura
        div_w = 3          # divisor de ancho

        div_desp_y = i
        div_desp_x = i+1

        h = int(frame_height/div_h)   #divide en altura y ancho segun la resolucion del video
        w = int(frame_width/div_w)  

        desp_y = int(h/div_desp_y) 
        desp_x = int(w/div_desp_x) 

        #Datos divisores
        dt_x.append(str(div_w))     #Se agregan como string para usarlos como labels en el heatmap
        dt_y.append(str(div_h))

        print("---------------------Iniciando proceso con: ", div_desp_x, ' y ', div_desp_y)
        while (captura.isOpened()):
            ret, image = captura.read() #image es un frame del video
            if ret == True:
                
                cropp_frame(image, div_h, div_w, h , w, desp_x, desp_y)
                n_frame += 1    #se incrementa el numero de frame
                
                #if(n_frame % 10 == 0):
                #    print('frame ',n_frame)
                

                cv2.waitKey(1)
            else:
                break

        desp_list.append([div_desp_y,div_desp_x,n_qrtotal]) 
        print(desp_list)
        et = time.time()  #tiempo de finalizado de ejecución

        elapsed_time = et - st      #tiempo total que tarda el programa
        
        print('Tiempo ejecutado para divisor en x ', div_desp_x, ' divisor en y ',div_desp_y,': ', elapsed_time, 'second, qr totales: ', n_qrtotal)

generate_heatmap(desp_list,[],[],[],1)
captura.release()
cv2.destroyAllWindows()