# -*- coding: utf-8 -*-
""""Томск_1new.ipynb"

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Dx9Nk-UieVpapP4NQ0gw-_b5T0SwoiXN
"""

# Commented out IPython magic to ensure Python compatibility.
# Работа с массивами данных
import numpy as np 

# Работа с таблицами
import pandas as pd

# Отрисовка графиков
import matplotlib.pyplot as plt

# Функции-утилиты для работы с категориальными данными
from tensorflow.keras import utils

# Класс для конструирования последовательной модели нейронной сети
from tensorflow.keras.models import Sequential

# Основные слои
from tensorflow.keras.layers import Dense, Dropout, Conv1D, SpatialDropout1D, BatchNormalization, Embedding, Flatten, Activation,MaxPooling1D

# Токенизатор для преобразование текстов в последовательности
from tensorflow.keras.preprocessing.text import Tokenizer

# Заполнение последовательностей до определенной длины
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Матрица ошибок классификатора
from sklearn.metrics import classification_report, confusion_matrix

from sklearn.preprocessing import OneHotEncoder

# Кодирование тестовых меток
from sklearn.preprocessing import LabelEncoder

# Разбиение на тренировочную и тестовую выборки
from sklearn.model_selection import train_test_split

from tensorflow.keras.optimizers import Adam

# Загрузка датасетов из облака google
import gdown

# Отрисовка графиков
import matplotlib.pyplot as plt

# %matplotlib inline

# Для отрисовки графиков
import seaborn as sns
import warnings

from google.colab import drive

drive.mount('/content/drive')

xl = pd.ExcelFile('/content/drive/MyDrive/мой_психолог_ИИ/dataset_train.xlsx')

print(xl.sheet_names)

df1 = xl.parse('Sheet1')

df1.head()

df1.shape

df1.describe(include='all')

# Сводка по распределению данных
warnings.simplefilter('ignore')
sns.countplot(x = "Class_label" , data  = df1)

datas = df1.Data.tolist()
datas2 = df1.Data_2.tolist()

for i in range(43):
# Создание модельного временного ряда
    series1 = datas[i]
    series1 = series1[1:-1]      
    series1= [int(item) for item in series1.split(', ')]
    datas[i]=series1
    series2 = datas2[i]
    #if series2!=0:
    series2 = series2[1:-1]      
    series2= [int(item) for item in series2.split(', ')]
    datas2[i]=series2
    #else: datas2[i]=series1

df1['Data_3']=datas
df1['Data_4']=datas2

figsize=(20, 10)
for i in range(30):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    fig.suptitle('График показаний датчиков')
    ax1.plot(df1.Data_3[i], marker='.')
    ax1.set_xlabel('Время')
    ax1.set_ylabel('Данные')
    ax2.plot(df1.Data_4[i], marker='.')
    ax2.set_xlabel('Время')
    ax2.set_ylabel('Данные')
    plt.show()
    print('Уровень стресса',df1.Class_label[i])

df1 = df1.loc[df1['Data_2']!= '[]']

df1.shape

df1.describe(include='all')

x_data=[]
for i in range(29852):
  num =df1.iloc[i]['Data'].replace('[','').replace(']','')
  num = list(num.split(', '))
  res = [float(item) for item in num]
  x_data.append(res)

x_data_2=[]
for i in range(29852):
  num =df1.iloc[i]['Data_2'].replace('[','').replace(']','')
  num = list(num.split(', '))
  res = [float(item) for item in num]
  x_data_2.append(res)

print(x_data[:10])
print(x_data_2[:10])

print(type(x_data))

dframe = pd.DataFrame(x_data) 
dframe

dframe_2 = pd.DataFrame(x_data_2) 
dframe_2

df_concat = pd.concat([dframe, dframe_2], axis=1)   
df_concat

from sklearn.preprocessing import StandardScaler, MinMaxScaler 
scaler = MinMaxScaler ()
d = scaler.fit_transform(df_concat)
scaled_df = pd.DataFrame(d)
scaled_df

X = scaled_df.values[:, :-1]
Y = np.array(df1.Class_label)

X = X.reshape(X.shape[0], X.shape[1], 1)
Y = Y.reshape(-1, 1)

ohe = OneHotEncoder(sparse=False)
Y = ohe.fit_transform(Y)

print(X.shape)
print(Y.shape)

x_train, x_test, y_train, y_test = train_test_split(X, # набор параметров
                                                    Y, # набор меток классов
                                                    test_size=0.2, # процент в тестовую
                                                    shuffle=True, #  перемешивание
                                                    random_state=3) # воспроизводимость

# Выведем размерность полученных выборок

print('Обучающая выборка параметров', x_train.shape)
print('Обучающая выборка меток классов', y_train.shape)
print()
print('Тестовая выборка параметров', x_test.shape)
print('Тестовая выборка меток классов', y_test.shape)

from tensorflow.keras.layers import LSTM, Bidirectional

def LSTMModel(seq_length=479, depth=1, n_class=3):
    
    model = tf.keras.Sequential()
    model.add(Bidirectional(LSTM(256, input_shape=(seq_length, depth))))
    model.add(BatchNormalization())
    model.add(Dropout(rate=0.2))
    model.add(Dense(200, activation='relu'))
    model.add(Dense(100, activation='relu'))
    model.add(Dense(n_class, activation="softmax"))
    
    return model

import logging
from typing import Tuple
import tensorflow as tf
import matplotlib.pyplot as plt
from IPython.display import clear_output

# tf warning suppression
tf.autograph.set_verbosity(0)
logging.getLogger("tensorflow").setLevel(logging.ERROR)

class TrackMetrics(tf.keras.callbacks.Callback):
    """
      Callback to plot the learning curves of model during the training.
    """
    def on_train_begin(self, logs={}):
        self.metrics = {}
        for metric in logs:
            self.metrics[metric] = []
            

    def on_epoch_end(self, epoch, logs={}):
        # Storing metrics
        for metric in logs:
            if metric in self.metrics:
                self.metrics[metric].append(logs.get(metric))
            else:
                self.metrics[metric] = [logs.get(metric)]
        
        # Plotting
        metrics = [x for x in logs if 'val' not in x]
   
        f, axs = plt.subplots(1, len(metrics), figsize=(12,4))
        clear_output(wait=True)
        
        for i, metric in enumerate(metrics):
            axs[i].plot(range(1, epoch + 2), 
                        self.metrics[metric], 
                        label=metric)
            if metric != "lr":       
                if logs['val_' + metric]:
                    axs[i].plot(range(1, epoch + 2), 
                                self.metrics['val_' + metric], 
                                label='val_' + metric)
            
            axs[i].set_xlabel("Epoch")
            axs[i].legend()
            axs[i].grid()

        plt.tight_layout()
        plt.show()
        
        
        
class Trainer:
    '''Custom Trainer class'''
    
    def __init__(self, model, optimizer="adam", learning_rate=0.001, callbacks=None):
        self.model = model
        if optimizer == "adam":
            self.optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate, beta_1=0.9, beta_2=0.999, epsilon=1e-7)
        self.model.compile(optimizer=self.optimizer, loss="categorical_crossentropy", metrics=["accuracy"])
        
        if not callbacks:
            self.callbacks = [tf.keras.callbacks.ModelCheckpoint("best_model.h5", save_best_only=True, monitor="val_loss"),
                              tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.25, patience=5, min_lr=0.0001),
                              tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=10, verbose=1),
                              TrackMetrics()]
        else:
            self.callbacks = callbacks
            
    def run(self, X, y, epochs=5, batch_size=256, validation_data: Tuple=None):
        
        if not validation_data:  
            split_ratio = 0.2     
        else:
            split_ratio = 0.0
        
        self.model.fit(X, y, 
                       epochs=epochs,
                       batch_size=batch_size,
                       verbose=1,
                       validation_split=split_ratio, 
                       validation_data=validation_data,
                       callbacks=self.callbacks
                      )
        return self.model

X_tr, X_val, y_tr, y_val = train_test_split(x_train, y_train, test_size=0.05, random_state=22, shuffle=True)

model = LSTMModel(seq_length=479, depth=1, n_class=3)

trainer = Trainer(model)

model = trainer.run(X_tr, y_tr, epochs=35, validation_data=(X_val, y_val))

y_pred = model.predict(x_test, batch_size=512)

print(classification_report(y_test.argmax(axis=1), y_pred.argmax(axis=1)))

model = trainer.run(X_tr, y_tr, epochs=35, validation_data=(X_val, y_val))