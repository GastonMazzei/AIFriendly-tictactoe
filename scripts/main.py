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

def generator(ngames: list, grid: tuple, verbose: bool=False):
    try:
        L, pL = grid
        core(ngames,L,pL,verbose)
    except Exception as ins:
        mssg = f'\n STATUS: an error ocurred'
        print(mssg, ins.args)
    return 


if __name__=='__main__':
  
    try:
        played=False
        if sys.argv[1]=='play': 
            try:
                play(*[int(j_) for j_ in sys.argv[2:]])
            except IndexError:
                play(3,3)
            played=True
    except: 
        pass 

    if played:
        sys.exit(0)
    else:
        # Generate games!
        grid = (3,3)
        verbose = False
        N = 20000
        generator(N , grid, verbose)

        # Process game-results!
        for _ in ['o']:#,'x']:
            df = processer(init(), _)
            df.to_csv(f'./../data/processed-{_}.csv',index=False)
 
        # Fit a network!
        #
        # EXTRA: do we want to see each training-result?
        plot = True #<-- True or False 
        for _ in ['o']:#,'x']:    
            create_and_predict(preprocess(load(f'./../data/processed-{_}.csv'),),
                neurons=16, epochs=120, plot=plot, model=_)

        # Play!
        play(*grid)
