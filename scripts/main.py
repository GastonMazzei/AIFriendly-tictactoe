#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""main:
   run once and it
   (1) generates games (default: random vs random, 10k)
   (2) process them into ".csv" files 
   (3) train a neural network with it and generate "model" files
"""

import os
import pickle
import random
import re
import sys
import time
import uuid

import pandas as pd
import numpy as np

from SmartGame.generating.classdef import TickTackToe
from SmartGame.generating.core import core
from SmartGame.processing.process import init, processer
from SmartGame.processing.network import load, preprocess, create_and_predict
from SmartGame.interactive.play import play
from SmartGame.interactive.play_x import play_x

def generator(ngames: list, grid: tuple, verbose: bool=False, enhace=False, perspective=''):
    try:
        L, pL = grid
        if perspective:
          core(ngames,L,pL,verbose, enhace, perspective)
        else:
          core(ngames,L,pL,verbose, enhace)
    except Exception as ins:
        mssg = f'\n STATUS: an error ocurred'
        print(mssg, ins.args)
    return 


if __name__=='__main__':
  
    try:
        played=False
        if sys.argv[1]=='play': 
            played=True
            version = sys.argv[2]
            try:
                raise Exception('not built yet')
                play(*[int(j_) for j_ in sys.argv[3:]])
            except:
                if version=='first':
                  play(3,3)
                else: 
                  play_x(3,3) 
                  print('problem')           
    except: 
        pass 

    if played:
        sys.exit(0)
    else:
        try:
          if sys.argv[1]=='enhace': enhace=True
        except: enhace=False

        # Generate games!
        grid = (3,3)
        verbose = False
        N = 5
        perspective = ['o','x']

        # Process game-results!
        if enhace:
          for _ in perspective:
            generator(N , grid, verbose, enhace, _)
            df = processer(init(True), _)
            df.to_csv(f'./../data/processed-{_}_enhace.csv',index=False)
 
          # Fit a network!
          #
          # EXTRA: do we want to see each training-result?
          plot = True #<-- True or False 
          for _ in perspective:    
            create_and_predict(preprocess(load(f'./../data/processed-{_}_enhace.csv'),),
                                          neurons=16, epochs=120, plot=plot,
                                          model=_, saving_name='_enhace')
          # Play!
          AGAINST = 'O'
          if AGAINST=='O':
            play(*grid, True)
          else:
            play_x(*grid, True)
        else:
          generator(N , grid, verbose, enhace)
          for _ in perspective:
              df = processer(init(), _)
              df.to_csv(f'./../data/processed-{_}.csv',index=False)
 
          # Fit a network!
          #
          # EXTRA: do we want to see each training-result?
          plot = True #<-- True or False 
          for _ in perspective:    
              create_and_predict(preprocess(load(f'./../data/processed-{_}.csv'),),
                  neurons=16, epochs=120, plot=plot, model=_)
          # Play!
          AGAINST = 'O'
          if AGAINST=='O':
            play(*grid)
          else:
            play_x(*grid)
