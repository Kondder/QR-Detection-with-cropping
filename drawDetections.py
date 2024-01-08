import cv2 
import json
import math
import os 
import errno 
import time
import argparse 
import sys 

def drawCircle(args): #Esta deberia llamarse main
    """
    Devuelve fotos de cada frame de los videos con circunferencias dibujadas alrededor de las bayas
    y las guarda en la carpeta 'output' dentro del directorio especificado mediante el parámetro --o pasado por consola.
    """

    #Diccionario de colores
    color = {
        "red": (0,0,255),
        "green": (0,255,0),
        "blue": (255,0,0)
    }

    #Se obtiene los nombres de los videos y json y se crea una lista con ellos.
    archivos_v = contenido = os.listdir(args.v)
    archivos_j = os.listdir(args.j)
    process = 0

    #Crea directorio output donde se guardaran las imagenes modificadas
    os.mkdir(args.o + "output")

    while process < len(archivos_j):

        #Obteniendo informacion JSON. Pasaje de cadena literal a diccionario Python
        archivo = open(args.j + archivos_j[process], "r")
        contenido = json.loads(archivo.read())
        archivo.close()

        cap = cv2.VideoCapture(args.v + archivos_v[process])

        output_directory_videos = args.o + "output/" + archivos_v[process].replace(".mp4", "")

        try:
            os.mkdir(output_directory_videos)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise    
        img_index = 0

        print("Ingreso a creacion de imagenes " + archivos_v[process])
        while(cap.isOpened()):
            ret, frame = cap.read()
            if ret == False:
                break 
            
            cv2.imwrite(output_directory_videos + "/" + str(img_index)+ ".jpg", frame)
            img_index +=1
        cap.release()
        cv2.destroyAllWindows()

        img= 0
        print("Ingreso a dibujar circulos " +  archivos_v[process])
        while(img < len(contenido)):
                i = 0
                im = cv2.imread(output_directory_videos + "/" + str(img) + ".jpg")

                for i in contenido[str(img)]:
                    x = math.trunc(contenido[str(img)][i][0])
                    y = math.trunc(contenido[str(img)][i][1])
                    r = math.trunc(contenido[str(img)][i][2])

                    cv2.circle(im, (x,y), r, color[args.c], 1)
                    cv2.imwrite(output_directory_videos + "/" + str(img) + ".jpg", im)
                    
                img = img + 1
        process = process + 1

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--v", type=str, help="Directorio de los videos")
    parser.add_argument("--j", type=str, help="Directorio de los JSON")
    parser.add_argument("--c", type=str, default="green" ,help="Color de circunferencia (red, green, blue)")
    parser.add_argument("--o", type=str, help="Directorio donde se almacenara el resultado del script")

    args = parser.parse_args()
    drawCircle(args)

#La carpeta creada no tiene que decir .mp4, solo el nombre del video replace