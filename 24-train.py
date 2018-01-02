import pickle
import gzip
import numpy as np
import random
import os
import sys
import statistics
import glob
import re
import json
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential, Model, load_model
from keras.layers import Lambda, Input, Activation, Dropout, Flatten, Dense, Reshape, merge
from keras.layers import Concatenate, Multiply, Conv1D, MaxPool1D, BatchNormalization, RepeatVector, GRU
from keras import optimizers
from keras.preprocessing.image import ImageDataGenerator
from keras.layers.normalization import BatchNormalization as BN
from keras.layers.core import Dropout
from keras.optimizers import SGD, Adam
from keras import backend as K
from keras.layers.wrappers import Bidirectional as Bi
from keras.layers.wrappers import TimeDistributed as TD

def CBRD(inputs, filters=64, kernel_size=3, droprate=0.5):
  x = Conv1D(filters, kernel_size, padding='same',
            kernel_initializer='random_normal')(inputs)
  x = BatchNormalization()(x)
  x = Activation('relu')(x)
  return x

input_tensor = Input( shape=(10, 2000) )

enc = input_tensor
enc = CBRD(enc, 2)
enc = CBRD(enc, 2)
x = MaxPool1D()(enc)

enc = CBRD(enc, 8)
enc = CBRD(enc, 8)
enc = MaxPool1D()(enc)

encode = Flatten()(enc)

dec = RepeatVector(30)(encode)
dec = Bi(GRU(2647, return_sequences=True))(dec)
decode  = TD(Dense(2647, activation='softmax'))(dec)


model = Model(inputs=input_tensor, outputs=decode)
model.compile(loss='categorical_crossentropy', optimizer='adam')

import pickle
import gzip
import numpy as np
import glob

for i in range(500):
  for name in glob.glob("dataset/*"):
    chunk = pickle.loads(gzip.decompress(open("dataset/000000000.pkl.gz", "rb").read()))

    X, y = [], []
    for outputs, inputs in chunk:
      inputs =  np.array(inputs)
      inputs = inputs.reshape( (10, 2000) )
      #print( inputs.shape )
      X.append(inputs)
      outputs = np.array(outputs) 
      #print(outputs.shape)
      y.append(outputs)

    X, y = np.array(X), np.array(y)

    model.fit(X, y, epochs=1)
    #break
  model.save_weights("models/{:09d}.h5".format(i))
