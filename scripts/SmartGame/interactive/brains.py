import numpy as np

import random
import os
import numpy as np
import pandas as pd
import uuid
import time
import pandas as pd
import sys

from sklearn import preprocessing, metrics
from sklearn.externals import joblib
from sklearn.model_selection import train_test_split
from keras.models import Sequential, load_model
from keras.layers import Dense

from keras import backend
import os

from SmartGame.generating.classdef import TickTackToe


           

#-----------------------------------------------------------END OF TickTackToe CLASS DEFINITION-------------------------



#-------------------------------------END OF AI FUNCTIONS-----------------------------------------



def tablero_printer(matrix):
    aux = np.asarray(matrix)
    L = len(aux)
    tabla_visual = [[1 for x in range(L)] for x in range(L)] 
    for x in range(L):
        for y in range(L):
            if aux[x][y]==-1: pass
            elif aux[x][y]==1: tabla_visual[x][y] = 'X'
            elif aux[x][y]==0: tabla_visual[x][y] = 'O'
            else: raise Exception('this was not a valid matrix input!')    
    underline = '_'*5*L + '_.'
    filler = '.'*int(((2+5*L)-len('TABLERO ACTUAL'))/2)
    print(f'{filler}Tablero Actual{filler}')
    print(underline)
    for x in range(L):
        q = '|'
        for y in range(L):
            if tabla_visual[x][y]==1: q += '|___|'
            elif tabla_visual[x][y]=='X': q += '|_X_|'
            elif tabla_visual[x][y]=='O': q += '|_O_|'
            else: q = '|err|'
        q += '|'        
        print(q)
    print('\n\n\n')
    return



def request_and_return(matrix):
    aux = np.asarray(matrix)
    L = len(aux)
    tabla_visual = [[1 for x in range(L)] for x in range(L)] 
    for x in range(L):
        for y in range(L):
            if aux[x][y]==-1: pass
            elif aux[x][y]==0: tabla_visual[x][y] = 'O'
            elif aux[x][y]==1: tabla_visual[x][y] = 'X'
            else: raise Exception('this was not a valid matrix input!')    
    underline = '_'*5*L + '_.'
    filler = '.'*int(((2+5*L)-len('TABLERO ACTUAL'))/2)
    print(f'\n\n\n\n\n\n\n{filler}Tablero Actual	{filler}\n')
    print(underline)
    for x in range(L):
        q = '|'
        for y in range(L):
            if tabla_visual[x][y]==1: q += '|___|'
            elif tabla_visual[x][y]=='X': q += '|_X_|'
            elif tabla_visual[x][y]=='O': q += '|_O_|'
            else: q = '|err|'
        q += '|'        
        print(q)
    control = 0
    while control==0:
        print('\n')
        print(f'Donde quieres poner la X? (indices del 1 al {L})')
        print('\nFila:')
        D1 = input()
        if D1.isdigit():
            while not (int(D1) in list(range(1,L+1)) ):
                print(f'\nEntrada Incorrecta... por favor indique un numero del 1 al {L} para la fila\n')
                D1 = input() 
        else:
            print(f'\nEntrada Incorrecta... por favor indique un numero del 1 al {L} para la fila\n')
            D1 = input()
        print('Columna:')
        D2 = input()
        if D2.isdigit():
            while not (int(D2) in list(range(1,L+1))):
                print(f'\nEntrada Incorrecta... por favor indique un numero del 1 al {L} para la columna\n')
                D2 = input()
        else:
            print(f'\nEntrada Incorrecta... por favor indique un numero del 1 al {L} para la columna\n')
            D2 = input()
        D1 = int(D1)-1
        D2 = int(D2)-1
        if matrix.item(D1,D2)==-1: control += 1
        else:
            print('No puede sobreescribir valores; por favor elija de vuelta') 
            control = 0
    #print('\n\n\n')
    print(f'Su respuesta es: FILA {D1+1} y COLUMNA {D2+1} ! \n')
    # pedirle si quiere cambiar antes de salir... 
    return D1,D2

def hacer_y_copiar_desacoplado(A,L,pL):
    B = TickTackToe(L,pL)
    for x in range(L):
        for y in range(L):
            B.board.itemset((x,y),A.board.item(x,y))
    return B

def respond(TickTackToe,model,scaler,name,allowedMoves,L,pL):
    if TickTackToe.checkO(): return TickTackToe,f"--HAS GANADO!--", False # chequear afuera desp de que mueve...
    #time.sleep(3)
    #print('input tablero is', TickTackToe.board)
    #time.sleep(3)
    a = TickTackToe.board.ravel().tolist()[0]
    j = 0
    for i in range(allowedMoves):
        j = i
        copia = hacer_y_copiar_desacoplado(TickTackToe,L,pL)
        #print('tablero original de esto copiado es', copia.board)
        copia.movesX()
        #print('and then it moves and it is',copia.board)
        #time.sleep(1)
        b = copia.board.ravel().tolist()[0]
        c = a + b
        c = [int(x) for x in c]
        INPUT = np.asarray(c).reshape(1,-1)
        #print('SENDING TO processer input was',INPUT)
        result = processInData(model, scaler, INPUT)
        result = result[0][0]
        if result==1: break
        else: pass
        #else: print('result of input was',INPUT,result)
    if copia.checkX(): return copia,f"------{name} TE HA GANADO!-------", False
#    elif j==allowedMoves-1:
#        raise Exception(f'{name} surrenders... couldnt find a move :(')
    elif j==allowedMoves-1: return copia,f"-------{name} no quiere pensar mas... usando output aleatorio...----",True
    else:
        return copia, f'{name} ha jugado...MIRA:', True
#-----------------new respond

def processInData(model, s, inData):
    inData_scale = s.transform(inData)
    #result = (model.predict(inData_scale) > 0.5).astype("int32") 
    result = model.predict(inData_scale)
    return result

#--------------------------------------------------------------------------
def new_respond(TickTackToe,model,scaler,name):
    a = TickTackToe.board.ravel().tolist()[0]
    L = TickTackToe.length
    pL = TickTackToe.patternLength
    cases = []
    probas = []
    #j = 0
    for K1 in range(L):
        for K2 in range(L):
            if TickTackToe.board.item(K1,K2)==-1:
                copia = hacer_y_copiar_desacoplado(TickTackToe,L,pL)
                copia.board.itemset((K1,K2),0)
                b = copia.board.ravel().tolist()[0]
                c = a + b
                c = [int(x) for x in c]
                INPUT = np.asarray(c).reshape(1,-1)          
                result = processInData(model, scaler, INPUT)
                result = result[0][0]
                print(f'result for {K1} and {K2} is ',result)
                #if result==1: cases.append(b)
                cases.append(b)
                probas.append(result)
            else: pass
    if not cases: #  PLEASE KILL THIS PART!
        copia = hacer_y_copiar_desacoplado(TickTackToe,L,pL)
        copia.movesX()
        if copia.checkX(): return copia,f"------{name} TE HA GANADO!-(anque fue aleatorio esto ultimo)---", False
        else: return copia,f"-------{name} no recomienda nada... usando output aleatorio...----",True
    print(f'probas are {probas}')
    move = cases[np.argmax(probas)]
    copia = hacer_y_copiar_desacoplado(TickTackToe,L,pL)
    copia.board = np.matrix([x for x in np.asarray(move).reshape((L,L)) ])
    if copia.checkO(): return copia,f"------{name} TE HA GANADO!-------", False 
    else: return copia, f'{name} ha elegido...MIRA:', True       

#------------------------------------------------------------------NO MORE TickTackToe FUNCTION


