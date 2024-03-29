# -*- coding: utf-8 -*-
#---------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------x-----
"""

Autor: Anderson Amaya Pulido

Libreria personal para el manejo del serson lector qr por serial.




# ideas a implementar





"""
#---------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------

#-------------------------------------------------------
#----      importar complementos                    ----
#-------------------------------------------------------

#---------------------------------
#           Librerias personales
#---------------------------------
from lib.Fun_Serial_S1 import *  # importar con los mismos nombres

#-----------------------------------------------------------
#                       CONSTANTES
#-----------------------------------------------------------
SQ_Mensajes  = 1                 # 0: NO print  1: Print
#Puerto_Serial   = '/dev/ttyUSB2'  # '/dev/ttyS0'

print Puerto_Serial

Activo = Iniciar_Serial()

if Activo == 1  :
    if SQ_Mensajes: print 'Serial Activo'
    Datos_Serial()
else            :
    if SQ_Mensajes: print 'Serrando el proceso por fallo grave en el Puerto'



#if SQ_Mensajes: print 'Puerto:'+ str(port)
#if SQ_Mensajes: print 'tipo:'+ str(type(port))
#if SQ_Mensajes: print 'tipo:'+ str(type(port) is serial.serialposix.Serial)





"""








TAG_NFC =''              # guardado de qr valido
TAG_NFC_antes =''        # QR anterior
T_Nuev_TAG = 0
T_Repe_TAG = 0
T_Maximo_TAG = 7

QR =''              # guardado de qr valido
QR_antes =''        # QR anterior
Init_QR = ''        # parte inicial de un qr
Fin_QR = ''         # parte Final de un qr

T_Maximo = 7        # timepo maximo para verificar un repetido para tipo  3 o tiket
T_Nuev_QR = 0       # timepo de inicioa de un nuevo qr
T_Repe_QR = 0       # timepo de inicioa de un nuevo qr

Memoria_RX =""


def Tx_datos():
    global SQ_Mensajes
    #-------------------------------
    #Para dispotitos CCCB
    #-------------------------------

    rele = Get_File(COM_TX_RELE)
    #port.write('DDDDD')
    #print 'TX:DDD'
    if len(rele)>= 1:
        #if SQ_Mensajes: print 'TX:' + rele
        rele=rele.rstrip('\n')            # eliminar caracteres extras
        rele=rele.rstrip('\r')

        if rele == 'Access granted-E': rele = 'EEEEE'
        elif rele == 'Access granted-S': rele = 'SSSSS'
        else: rele = 'DDDDD'
        #rele = 'SSSSS'


        if SQ_Mensajes: print 'TX:' + rele

        port.write(rele)
        Clear_File(COM_TX_RELE)

#---------------------------------------------------------------------------------------
#                                   Funciones para la lectura de QR
#---------------------------------------------------------------------------------------
def No_Valido_QR(x):
    global SQ_Mensajes, QR, QR_antes, T_Nuev_QR, T_Repe_QR, T_Maximo
    QR = x
    if 'Igual' in QR :
        if SQ_Mensajes: print 'Repetido'
        Set_File(STATUS_REPEAT_QR, '2')    # Estado QR repetido
    elif QR != QR_antes:
        QR_antes = QR
        #T_Nuev_QR = time.time()
        if SQ_Mensajes: print 'NO QR: ' + QR
        Guardar_QR()
        Activar_QR()
    else:
        if SQ_Mensajes: print 'Repetido'
        Set_File(STATUS_REPEAT_QR, '2')    # Estado QR repetido


#---------------------------------------------------------------------------------------

def Nueva_Avilitacion_portiempo_y_Tipo():
    global SQ_Mensajes, QR
    #print 'Repe_Nueva habilitacion'
    puntos = QR.count(".")
    #print puntos
    if puntos == 1:
        if SQ_Mensajes: print 'R_Avi Tiket: '+QR
        Set_File(STATUS_QR, '1')
    elif puntos == 3:
        if SQ_Mensajes: print 'R_Avi Tiket: '+QR
        Set_File(STATUS_QR, '1')
    elif puntos == 4:               #para tipo 3
        if SQ_Mensajes: print 'R_Avi Tipo 3: '+QR
        Set_File(STATUS_QR, '1')
    else:
        if SQ_Mensajes: print 'Repetido'
        Set_File(STATUS_REPEAT_QR, '2')

#---------------------------------------------------------------------------------------

def Decision_Qr(x):
    global SQ_Mensajes, QR, QR_antes, T_Nuev_QR, T_Repe_QR, T_Maximo
    #--------- QR repetido
    QR = x
    if QR != QR_antes:
        QR_antes = QR
        T_Nuev_QR = time.time()
        if SQ_Mensajes: print 'Nuevo: ' + QR
        Guardar_QR()
        Activar_QR()
    else:
        #print 'Repetido:' + x + ' , Estado Valido: ' + str(Valido)
        T_Repe_QR = time.time()
        T_transcurido = int(T_Repe_QR-T_Nuev_QR)
        #print 'T_Diferencia: ' + str(T_transcurido)
        if T_transcurido >= T_Maximo :
            T_Nuev_QR = T_Repe_QR = time.time()
            Nueva_Avilitacion_portiempo_y_Tipo()
        else:
            if SQ_Mensajes: print 'Repetido'
            Set_File(STATUS_REPEAT_QR, '2')    # Estado QR repetido

        #print 'T_Nuevo:' + str(T_Nuev_QR) + ' , T_Repetido:' + str(T_Repe_QR) + ', T_Diferencia: ' + str(int(T_Repe_QR-T_Nuev_QR))

#---------------------------------------------------------------------------------------

def Activar_QR():
    Set_File(STATUS_QR, '1')    #Escrivir_Estados('1',8) # Cambiar estado del QR

#---------------------------------------------------------------------------------------

def Guardar_QR():
    global QR
    #QRG = QR.replace ("<","")
    #QRG = QRG.replace (">","")
    Clear_File(COM_QR)          # Borrar QR
    Set_File(COM_QR, QR)       # Guardar QR

#---------------------------------------------------------------------------------------

def Parte_Inicial_QR(x):
    global Init_QR, Fin_QR
    Init_QR = x
    Fin_QR  = ''

#---------------------------------------------------------------------------------------

def Parte_Fin_QR(x):
    global Init_QR, Fin_QR
    Fin_QR  = x
    Total = Init_QR + Fin_QR

    if Validar_QR(Total) == 1:
        Almacenar_Trama(Total)
        #Decision_Qr(Total)          #QR valido
        Init_QR = Fin_QR = ''





#---------------------------------------------------------------------------------------

def Decision_Telado(Teclado):
    if SQ_Mensajes: print 'TC:'+ Teclado
    Guardar_Telado(Teclado)
    Activar_Telado()

#---------------------------------------------------------------------------------------

def Guardar_Telado(Teclado):
    TecladoG = Teclado.replace ("<","")
    TecladoG = TecladoG.replace (">","")
    TecladoG = TecladoG.replace ("TC:","")
    Clear_File(COM_TECLADO)          # Borrar QR
    Set_File(COM_TECLADO, TecladoG)       # Guardar QR

#---------------------------------------------------------------------------------------

def Activar_Telado():
    Set_File(STATUS_TECLADO, '1')    #Escrivir_Estados('1',8) # Cambiar estado del QR






#---------------------------------------------------------------------------------------

def Decision_Tag(Tag):

    global TAG_NFC
    global TAG_NFC_antes
    global T_Nuev_TAG, T_Repe_TAG, T_Maximo_TAG

    TAG_NFC = Tag
    if TAG_NFC != TAG_NFC_antes:
        TAG_NFC_antes = TAG_NFC
        if 'TN:' in TAG_NFC:
            if SQ_Mensajes: print 'TN:'+ TAG_NFC
            Guardar_Tag(TAG_NFC)
            Activar_Tag()
        elif 'TR:' in TAG_NFC:
            if SQ_Mensajes: print 'TR:'+ TAG_NFC
            #Set_File(STATUS_REPEAT_NFC, '2')    # Estado QR repetido
            Guardar_Tag(TAG_NFC)
            Activar_Tag()
    else:
        #T_Nuev_TAG, T_Repe_TAG, T_Maximo_TAG
        T_Repe_TAG = time.time()
        T_transcurido = int(T_Repe_TAG-T_Nuev_TAG)
        #print 'T_Diferencia: ' + str(T_transcurido)
        if T_transcurido >= T_Maximo_TAG :
            T_Nuev_TAG = T_Repe_TAG = time.time()
            if 'TN:' in TAG_NFC:
                if SQ_Mensajes: print 'TN:'+ TAG_NFC
                Guardar_Tag(TAG_NFC)
                Activar_Tag()

            elif 'TR:' in TAG_NFC:
                if SQ_Mensajes: print 'TR:'+ TAG_NFC
                #Set_File(STATUS_REPEAT_NFC, '2')    # Estado QR repetido
                Guardar_Tag(TAG_NFC)
                Activar_Tag()

        else:
            #Set_File(COM_BUZZER,'1')       #sonido eliminar si no es necesario
            if SQ_Mensajes: print 'Repetido'
            Set_File(STATUS_REPEAT_QR, '2')    # Estado QR repetido








#---------------------------------------------------------------------------------------

def Activar_Tag():
    Set_File(STATUS_NFC, '1')    #Escrivir_Estados('1',8) # Cambiar estado del QR
    #Set_File(STATUS_TECLADO, '1')    #Escrivir_Estados('1',8) # Cambiar estado del QR


#---------------------------------------------------------------------------------------

def Guardar_Tag(Tag):
    #global QR
    TagG = Tag.replace ("<","")
    TagG = TagG.replace (">","")
    TagG = TagG.replace ("TN:","")
    TagG = TagG.replace ("TR:","")

    #Set_File(COM_RELE,'Access granted-E')

    Clear_File(COM_NFC)          # Borrar QR
    Set_File(COM_NFC, TagG)       # Guardar QR


    #Clear_File(COM_TECLADO)          # Borrar QR
    #Set_File(COM_TECLADO, '6.' + TagG)       # Guardar QR










#---------------------------------------------------------------------------------------
def Validar_QR(x):
    TaCadena = len (x)
    Inicio = x[0:1]
    Fin = x[TaCadena-1:TaCadena]
    #print TaCadena
    if TaCadena >= 1:
        if (Inicio == '<' ) and (Fin == '>'):       return 1    #print 'OK' valido y completo
        else:
            if (Inicio == '<' ):                    return 2    #print 'Inicio: ' + Inicio parte inicial de un qr valido
            elif (Fin == '>'):                      return 3    #print 'Fin' + Fin parte final de un qr valido
            else:                                   return -1   #print 'NO' no tine ninguna parte valida
    else:                                           return -2   #print 'NO' no hay cadena

#---------------------------------------------------------------------------------------
def Validar_Trama(x):
    TaCadena = len (x)
    Inicio = x[0:1]
    Fin = x[TaCadena-1:TaCadena]
    #print TaCadena



    if TaCadena >= 1:
        if (Inicio == '<' ) and (Fin == '>'):       return 1    #print 'OK' valido y completo
        else:
            if (Inicio == '<' ):                    return 2    #print 'Inicio: ' + Inicio parte inicial de un qr valido
            elif (Fin == '>'):                      return 3    #print 'Fin' + Fin parte final de un qr valido
            else:                                   return -1   #print 'NO' no tine ninguna parte valida
    else:                                           return -2   #print 'NO' no hay cadena

#---------------------------------------------------------------------------------------
def Almacenar_Trama(x):
    #print 'Dato en almacenar _Trama:' + x



    if 'TN:' in x:      Decision_Tag(x)#print 'tag'
    elif 'TR:' in x:    Decision_Tag(x)#print 'tag'
    elif 'TC:' in x:    Decision_Telado(x)#print 'tag'
    else:               Decision_Qr(x)#print 'QR'




#---------------------------------------------------------------------------------------
def Procesar_Datos(rcv):
    global SQ_Mensajes
    rcv = rcv.replace ('\r',"")
    if SQ_Mensajes: print 'Datos RX:' + rcv

    #Memoria_RX = rcv.split('?', maxsplit=1)



    Lineas = rcv.split('\r')
    for x in Lineas:
        if(len(x)>0):

            if SQ_Mensajes: print 'RX_1:' + x +'Tama:'+ str(len(x))
            if x.count('>') >= 2:
                x1=x.split('>')
                #print x1[0]+'>'
                #print x1[1]+'>'
                x=x1[0]+'>'


            Valido = Validar_Trama(x)
            if SQ_Mensajes: print 'Valido:' + str(Valido)

            if Valido == -1:
                T_rcv = len(x)
                #if SQ_Mensajes: print 'Cuantos:' + str(T_rcv)
                #print 'RX:' + x
                #print " ".join(hex(ord(n)) for n in rcv)

                if  (T_rcv>=16) & (hex(ord(x[0]))== '0x2') & (hex(ord(x[1]))== '0xff') & (hex(ord(x[2]))== '0x1') & (hex(ord(x[3]))== '0x9'):# & (hex(ord(rcv[T_rcv-4]))== '0xd9') & (hex(ord(rcv[T_rcv-3]))== '0x5') & (hex(ord(rcv[T_rcv-2]))== '0xb0') & (hex(ord(rcv[T_rcv-1]))== '0x29') :
                    Tag_data = ""
                    for i in range(5, T_rcv-7):
                        datohex=hex(ord(x[i]))
                        #s = datohex.replace('0x',"")
                        #print hex(ord(rcv[i]))
                        Tag_data += datohex.replace('0x',"")
                        #Tag_data.join(datohex.replace('0x',""))
                    #print Tag_data
                    x='TN:'+Tag_data
                    Valido =1



            #if      Valido == 1:    print 'Valido:' + x

            if      Valido == 1:    Almacenar_Trama(x)#print 'Valido:' + x #print 'QR valido' #Decision_Qr(x)          #QR valido
            elif    Valido == 2:    Parte_Inicial_QR(x) #print 'Inicio QR' #Parte_Inicial_QR(x)     #Inicio QR
            elif    Valido == 3:    Parte_Fin_QR(x) #print 'Fin QR'    #Parte_Fin_QR(x)         #Fin QR
            #elif    Valido == -1:   print 'No valido:' + x +'Tama:'+ str(len(x)) #print 'No valido' #No_Valido_QR(x)         #No valido









#---------------------------------------------------------------------------------------
def Procesar_Datos_Hex(rcv):
    global SQ_Mensajes
    #rcv = rcv.replace ('\r',"")
    #if SQ_Mensajes: print 'Datos RX:' + rcv

    #Memoria_RX = rcv.split('?', maxsplit=1)




    Lineas = rcv.split('\r')
    #print len(Lineas)
    for x in Lineas:
        if(len(x)>0):
            Tag_data =""
            for letra in x:
                datohex = hex(ord(letra))
                Tag_data += datohex.replace('0x'," ")

            #print Tag_data
            Analisis_Trama(Tag_data)







#---------------------------------------------------------------------------------------
def Analisis_Trama(Tag_data):
    if len(Tag_data) > 0:
        # print 'Cuantos:'+ str(len(Tag_data)) +'Tama:'+ Tag_data

        if ' aa 1' in Tag_data:
            if ' aa 1 97 1 0 7 1 b6'        in Tag_data: print 'Peticion      : ' + Tag_data
            elif ' aa 1 c9 1 0 0 53 9c 55'  in Tag_data: print 'Rx sin Nada   : ' + Tag_data
            elif ' aa 1 c8 '                in Tag_data:
                #print 'Datos         : ' + Tag_data
                Datos = Tag_data.split(" ")
                Tipo = int(Datos[7])
                print 'Tipo          : ' + str(Tipo)
                if Tipo == 2:
                    #covercion de formato de hex a decimal
                    Numero =""
                    for i in range(9 + int(Datos[8]), 9, -1):  Numero += Datos[i]
                    print 'Tag o Targeta :'+ str(int(Numero,base=16))
                    TX_datos_hex('Verde')
                elif Tipo == 3:
                    #covercion de formato de desima a anssi numerico
                    Numero =""
                    for i in range(10, 10 + int(Datos[8])):  Numero += str(int(Datos[i])-30)
                    print 'Teclado   : ' + Numero
                    TX_datos_hex('Verde')
                else:
                    print 'No definido  : ' + Tag_data
                    TX_datos_hex('Rojo')

            else:
                print 'Otras      : ' + Tag_data





def TX_datos_hex(Tipo):
    data = Trama_TX_ProID30(Tipo)
    port.write(data)


#---------------------------------------------------------------------------------------


#---------------------------------------------------------------------------------------





















#-------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------

if SQ_Mensajes: print 'Activo mensajes: ' + str(SQ_Mensajes)
if SQ_Mensajes: print Puerto_Serial
print 'Listo'
#-------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------

while 1:
    #---------------------------------------------------------
    #  Lectura de serial
    #---------------------------------------------------------
    Datos_Serial()

"""
