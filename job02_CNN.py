import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from keras.utils import to_categorical
from tensorflow.keras.layers import *
from tensorflow.keras.models import *
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import time
import sys
import warnings

warnings.filterwarnings("ignore")  # 경고문 출력 제거
np.set_printoptions(threshold=sys.maxsize)  # 배열 전체 출력
pd.set_option('display.max_columns', None)

df_training=pd.read_pickle('./datasets/LSWMD_Train.pickle')
df_training.reset_index(inplace=True)
# df_training.info()
df_test=pd.read_pickle('./datasets/LSWMD_Test.pickle')
df_test.reset_index(inplace=True)
# df_test.info()

# print(df_training['fea_cub_mean'], df_training['failureNum'])
print(type(df_training['fea_cub_mean']), type(df_training['failureNum']))     # Series, Series
# print(df_training['fea_cub_mean'].shape, df_training['failureNum'].shape)   # (68692,) (68692,)
X_train = df_training.fea_cub_mean.values#.reshape(-1,20)   # numpy.array(numpy.array)<-변형 필요
print(X_train)
print(type(X_train))
print(X_train.shape)
exit()

X_train, Y_train = np.array(df_training['fea_cub_mean'], df_training.failureNum.values.reshape(-1,1))
print(X_train.shape, Y_train.shape)
X_test, Y_test = df_test['fea_cub_mean'], df_test['failureNum']
print(X_test.shape, Y_test.shape)
print(Y_train, Y_test)

exit()
# one-hot 인코딩 & softmax
# 레이블을 원-핫 인코딩
y_train = to_categorical(Y_train)
y_test = to_categorical(Y_test)
# print(y_train, Y_test)
x_train = X_train
x_test = X_test

model = Sequential()
model.add(Dense(256, input_dim=20, activation='relu'))  # len(X_train[0]) = 20
model.add(Dense(128, activation='relu'))
model.add(Dense(512, activation='relu'))
model.add(Dense(9, activation='softmax'))               # len(y_train) = 9
model.summary()

model.compile(optimizer=Adam(learning_rate=0.01), loss='categorical_crossentropy', metrics=['accuracy'])

fit_hist = model.fit(X_train, Y_train, batch_size=5, epochs=50, verbose=1)
score = model.evaluate(X_test, Y_test, verbose=0)
print('Final test set accuracy :', score[1])
print(score)

plt.plot(fit_hist.history['accuracy'])
plt.show()



# val_acc = round(fit_hist.history['val_accuracy'][-1], 3)
# model.save('./models/CNN_{}.h5'.format(val_acc))
#
# score = model.evaluate(x_test, y_test, verbose=0)
# print('Final test set accuracy', score[1])
#
# plt.plot(fit_hist.history['accuracy'])
# plt.plot(fit_hist.history['val_accuracy'])
# plt.show()
#
# my_sample = np.random.randint(10000)
# plt.imshow(X_test[my_sample], cmap='gray')
# print(labels[Y_test.iloc[my_sample]])
#
# pred = model.predict(x_test[my_sample].reshape(-1, x_dim, y_dim, 1))
#
# labels = ['Normal', 'Center', 'Donut', 'Edge-Loc', 'Edge-Ring', 'Loc', 'Random', 'Scratch', 'Near-full']
# print("pred: ", pred)  # 0~9까지 각 숫자일 확률 출력
# print("argmax: ", labels[np.argmax(pred)])




