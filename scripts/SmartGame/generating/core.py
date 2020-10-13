#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""core-dispatcher:
   recieves the request to generate
   N games under specs, handles it and
   finally calls the results-saver
"""

import os
import pickle
import random
import re
import sys
import time

import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler
from keras.models import load_model

from SmartGame.generating.classdef import TickTackToe
from SmartGame.generating.utils.core_utils import saver
from SmartGame.generating.smart import smart_O, smart_X
from SmartGame.generating.enhaced import AIFriendly_O, AIFriendly_X


def core(Ngames : int, L : int, pL : int, verbose: bool=False, enhace=False, **kwargs): 
    """
    kwargs:

        random_o = 0-1  <-- probability of the "O-move" being random
        random_x = 0-1  <-- probability of the "X-move" being random

        alt_o = 'algo' (OR 'ai') <--             ' ' 
        alt_x = 'algo' (OR 'ai') <-- alternative to random: encoded pattern-seeking
                                                          algorithm or ai-network 
    """

    random_O = kwargs.get('random_o',1)
    random_X = kwargs.get('random_x',1)
    alt_O = kwargs.get('alt_o','algo')
    alt_X = kwargs.get('alt_x','algo')

    results = {}
    
    #**********************************FLAGGED FOR KILL
    # make a dict for each game-stage (step 0,1,2,3,4)
    if False:
      Stage_0 = {}
      Stage_1 = {}
      Stage_2 = {}
      Stage_3 = {}
      Stage_4 = {}
      Stage_full = {}      # currently not splitting by hands before saving..
      #              Cesar Miquel's approach!
      #stages = {0:Stage_0 ,1:Stage_1, 2:Stage_2, 3:Stage_3, 4:Stage_4 , 5:Stage_full}
      stages = {5:Stage_full}
      processing_dispatcher = {3:aux1, 2:aux2, 1:aux2}
    #***************************************************************

    if enhace:
      scaler_X = StandardScaler().fit(pd.read_csv(f'../data/processed-x.csv').to_numpy()[:,:-1])
      scaler_O = StandardScaler().fit(pd.read_csv(f'../data/processed-o.csv').to_numpy()[:,:-1])
      model_O = load_model(f'./../data/models/model-o')
      model_X = load_model(f'./../data/models/model-x')
      X_mover = (lambda x,y: AIFriendly_X(x, model_X, scaler_X,y) )
      O_mover = (lambda x,y: AIFriendly_O(x, model_O, scaler_O,y) )
    else: 
      X_mover = (lambda x,y: smart_X(x, random_X))  
      O_mover = (lambda x,y: smart_O(x, random_O))  

    past = [{}]
    for x in range(Ngames): 
        try:
            # (0) Report
            #
            if x%200==0: 
              print(f'Lap N{x}')
              if enhace: 
                print(f'past dictionary has {len(past[0].keys())} keys')
                threshold = 2
                if len(past[0].keys())<threshold: 
                  #for k,v in past[0].values(): print(k,v,sep=' ',end='\t')
                  print(past)
            #
            # (1) Initialize
            #
            log = []
            t = TickTackToe(L,pL)
            i = 0
            #
            # (2) Play
            #
            while i==0: 
                temp = []
                try:
                    # (2.0)   "X moves"
                    #t = smart_X(t, random_X)
                    t,*past = X_mover(t,past[0])
                    temp.append(tuple(t.board.ravel().tolist()[0])) 

                    # (2.1)   "if X won, break"
                    if t.checkX(): 
                        i = 1
                        log += temp
                        break    

                    # (2.2)   "O moves"
                    #t = smart_O(t, random_O) 
                    t,*past = O_mover(t,past[0])
                    temp.append(tuple(t.board.ravel().tolist()[0]))
                    log += temp

                    # (2.3)   "if O won, break"
                    if t.checkO():
                        i = 3    
                        break

                except:
                    #    "if an exception occurred, it was raised by a tie"
                    log += temp
                    i = 2
                    break

 
            # (3) Convert "list" to "tuple"
            #     -"tuples" are hashable; 
            #            "lists" are not-
            #
            log = tuple(log)

            # (4) Append results
            # INDEX: 
            #       1 - X won
            #       2 - Tie
            #       3 - O won
            #
            if log in results.keys():
              results[log][i-1] += 1
            else:
              results[log] = [0,0,0]
              results[log][i-1] += 1

    #**********************************FLAGGED FOR KILL  
            if False:        
              # Iterate over game-stages
              #             
              for y in stages.keys():
                  temp_pand =  tuple(processing_dispatcher[i](log, y))                       
                  if temp_pand in stages[y].keys(): 
                      stages[y][temp_pand][i-1] += 1
                  else:
                      stages[y][temp_pand] = [0,0,0]
                      stages[y][temp_pand][i-1] += 1
    #**********************************FLAGGED FOR KILL

        except Exception as ins:
            print(f'Game {x}/{Ngames} failed with code: ', ins.args)

    #**********************************FLAGGED FOR KILL   
    if False:
      # (5) Save
      tagger = {0: 'all-but-last', 1:'first-hand',
                2:'second-hand', 3:'third-hand',
                4:'fourth-hand', 5:'full' }
      for x in stages.keys():
          saver(stages[x],tagger[x])
    #**********************************FLAGGED FOR KILL   

    # (5) Save
    if enhace: saver(results,'_enhace')
    else: saver(results,'')    
    return

