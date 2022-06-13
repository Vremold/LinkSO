
from __future__ import print_function
import numpy as np
import csv
np.random.seed(1337)
from keras.preprocessing import sequence
from keras.models import Sequential
from keras.layers import Dense,Embedding
from keras.layers import LSTM
from keras.datasets import imdb
from keras.callbacks import Callback
from tensorflow.keras.optimizers import Adam
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score,accuracy_score

from nltk import word_tokenize
from nltk.corpus import stopwords

# stop_words = stopwords.words('english') + ['!', ',' ,'.' ,'?' ,'-s' ,'-ly' ,'</s> ', 's']
stop_words = []

vocab = dict()
vocab["<PAD>"] = 0
vocab["<UNK>"] = 1

def load_data(src_file):
    global vocab
    Xs = []
    ys = []
    with open(src_file, "r", encoding="utf-8") as inf:
        next(inf)
        csv_reader = csv.reader(inf, delimiter=",")
        for line in csv_reader:
            label = int(line[2])
            words = word_tokenize(line[0].lower()) + word_tokenize(line[1].lower())
            words = [word for word in words if word not in stop_words]
            # words = words[:120]
            for word in words:
                if word not in vocab:
                    vocab[word] = len(vocab)
            Xs.append([vocab[word] for word in words])
            ys.append([label])
    
    return np.array(Xs), np.array(ys)

# 写一个LossHistory类，保存loss和acc
class LossHistory(Callback):
    def on_train_begin(self, logs={}):
        self.losses = {'batch':[], 'epoch':[]}
        self.accuracy = {'batch':[], 'epoch':[]}
        self.val_loss = {'batch':[], 'epoch':[]}
        self.val_acc = {'batch':[], 'epoch':[]}
 
    def on_batch_end(self, batch, logs={}):
        self.losses['batch'].append(logs.get('loss'))
        self.accuracy['batch'].append(logs.get('acc'))
        self.val_loss['batch'].append(logs.get('val_loss'))
        self.val_acc['batch'].append(logs.get('val_acc'))
 
    def on_epoch_end(self, batch, logs={}):
        self.losses['epoch'].append(logs.get('loss'))
        self.accuracy['epoch'].append(logs.get('acc'))
        self.val_loss['epoch'].append(logs.get('val_loss'))
        self.val_acc['epoch'].append(logs.get('val_acc'))
 
    def loss_plot(self, loss_type):
        iters = range(len(self.losses[loss_type]))
        plt.figure()
        # acc
        plt.plot(iters, self.accuracy[loss_type], 'r', label='train acc')
        # loss
        plt.plot(iters, self.losses[loss_type], 'g', label='train loss')
        if loss_type == 'epoch':
            # val_acc
            plt.plot(iters, self.val_acc[loss_type], 'b', label='val acc')
            # val_loss
            plt.plot(iters, self.val_loss[loss_type], 'k', label='val loss')
        plt.grid(True)
        plt.xlabel(loss_type)
        plt.ylabel('acc-loss')
        plt.legend(loc="upper right")
        plt.savefig("imdb_keras.png")
        plt.show()
 
# 训练参数
learning_rate = 0.001
epochs = 3
batch_size = 128
 
x_train, y_train = load_data("./data/train")
x_test, y_test = load_data("./data/validate")
# (x_train,y_train),(x_test,y_test) = imdb.load_data(num_words= 5000)
print(len(x_train),'train sequences')
print(len(x_test),'test sequences')
print(x_train[0])
# sys.exit(0)
x_train = sequence .pad_sequences(x_train ,maxlen= 120 )
x_test = sequence .pad_sequences(x_test ,maxlen= 120 )
print('x_train shape:',x_train .shape )
print('x_test shape:',x_test .shape )
 
print('Build model...')
model = Sequential()
model.add(Embedding(len(vocab) ,64))#嵌入层将正整数下标转换为固定大小的向量。只能作为模型的第一层
# model.add(LSTM(units=16,return_sequences=True))
model.add(LSTM(units=16))
model.add(Dense(1,activation= 'sigmoid'))
 
model.summary()
model.compile(loss= 'binary_crossentropy',optimizer=Adam(lr=learning_rate),metrics= ['accuracy'])
history = LossHistory()
model.fit(x_train ,y_train ,batch_size= batch_size ,epochs= epochs,validation_data= (x_test ,y_test ),callbacks=[history])
 
 
y_predict = model.predict(x_test, batch_size=512, verbose=1)
y_predict = (y_predict >= 0.5).astype(int)
y_true = np.reshape(y_test, [-1])
y_pred = np.reshape(y_predict, [-1])
 
# 评价指标
accuracy = accuracy_score(y_true, y_pred)
precision = precision_score(y_true, y_pred)
recall = recall_score(y_true, y_pred, average='binary')
f1score = f1_score(y_true, y_pred, average='binary')
 
print('accuracy:',accuracy)
print('precision:',precision)
print('recall:',recall)
print('f1score:',f1score)
 