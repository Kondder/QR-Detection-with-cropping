import csv
import math

infoqr = []
dictqr = {}
keys = []
count = 0

def mostWatched(name): #Retorna un diccionario: key -> id_qr; value -> int: apariciones
    i = 1
    with open(name) as file_obj:  
        reader_obj = csv.reader(file_obj)
        #Lee lineas donde hay qr_id diferentes.
        for row in reader_obj:
            if(i % 4 == 0):
                infoqr.append(row) #Se añade informacion qr a un arreglo. [[ ]]
            i = i + 1 
        #Obtiene qrid de infoqr y guarda en listqr
        for qrid in infoqr:
            #Ordenar listqr
            id = qrid[1]
            if id not in dictqr.keys():
                dictqr[id] = 0
            else:
                dictqr[id] = dictqr[id] + 1
    return dict(sorted(dictqr.items(), key=lambda x:x[1], reverse=True))    #Entender como ordena

def mostWatchedbyColumn(dictQR):        
    columnDict = createColumnDict(dictQR)
    columnDict = {}
    for id in dictQR:
        columnNumber = clm(id)
        if columnNumber in columnDict:
            if dictQR[columnDict[columnNumber]] < dictQR[id]:
                columnDict[columnNumber] = id
            #print("el id "+id +" tiene menos visiones que "+columnDict[columnNumber])
        else:
            columnDict[columnNumber] = id

    sorted_col = dict(sorted(columnDict.items()))
    print(sorted_col)
    #print(sorted_col)
    #sorted_dictQR = {k: dictQR[k] for k in sorted(dictQR, key=lambda x: int(x))} #Entender como ordena
    #print(sorted_dictQR)
    return sorted_col

def clm(qrId):
    return math.trunc((int(qrId) - 71)/7)

def createColumnDict(DictQr):
    keysId = list(DictQr.keys())
    columnDict = {}
    for qrId in keysId:
        columnNumber = clm(qrId)
        if columnNumber in columnDict:
            columnDict[columnNumber] = columnDict[columnNumber] + 1
        else:
            columnDict[columnNumber] = 0
    return dict(sorted(columnDict.items()))

def createCSVFile(rank, dictQR, strategy): #Crea archivo CSV dependiendo de la estrategia seleccionada
    for i in range(0,rank):
        keys.append(list(dictQR.keys())[i])
    if (strategy == 0):
        for id in keys: # '80'
            fileName = 'qr_'+ id +'.csv'
            with open(fileName, 'w', newline='') as file: # qr_80.csv
                writer = csv.writer(file) 
                writer.writerow(['frame', 'qr','esquina','x','y']) # escribe header

                with open('qr_csv.csv') as file_obj: #Abre archivo
                    reader_obj = csv.reader(file_obj) 
                    for row in reader_obj:
                        if(row[1] == id):
                            writer.writerow(row)
            print("Se creo archivo " + fileName)

    if (strategy == 1):
        fileName = 'ranking_top_'+ str(rank) +'_qr_.csv'
        infoqr = []
        #Obtener y guardar informacion de qr con mas apariciones 
        for id in keys:
            print("Iniciando proceso qr_id: " + id)
            with open('qr_csv.csv') as file_obj: #Abre archivo
                reader_obj = csv.reader(file_obj) 
                for row in reader_obj:
                    if(row[1] == id):
                        infoqr.append(row)
        #Ordenar lista
        listSorted = sorted(infoqr, key=lambda x: int(x[0])) #la lista de listas se ordenará según el primer elemento numérico de cada sublista.
        #Escribir lista ordenada en archivo .csv
        with open(fileName, 'w', newline='') as file: # qr_80.csv
            writer = csv.writer(file) 
            writer.writerow(['frame', 'qr','esquina','x','y']) # escribe header
            for row in listSorted:
                writer.writerow(row)
        print("Se creo archivo " + fileName)
        
    if (strategy == 2):
        idColumn = list(mostWatchedbyColumn(dictQR).values())
        fileName = 'ranking_by_col.csv'
        infoqr = []

        print(idColumn)
        for id in idColumn:
            print("Iniciando proceso qr_id: " + id)
            with open('qr_csv.csv') as file_obj: #Abre archivo
                reader_obj = csv.reader(file_obj) 
                for row in reader_obj:
                    if(row[1] == id):
                        infoqr.append(row)
        listSorted = sorted(infoqr, key=lambda x: int(x[0]))
        with open(fileName, 'w', newline='') as file:
            writer = csv.writer(file) 
            writer.writerow(['frame', 'qr','esquina','x','y']) # escribe header
            for row in listSorted:
                writer.writerow(row)
        print("Se creo archivo " + fileName)

def main():
    dictqr = mostWatched('qr_csv.csv')
    print(dictqr)
    # primer parametro(rank):       cantidad de qr mas vistos a guardar en CSV
    # tercer parametro(strategy):   0 -> multi archivos , 1 -> unico archivo
    #createCSVFile(3,dictqr,0)
    #createCSVFile(3,dictqr,1)
    #createCSVFile(3,dictqr,2)
main()