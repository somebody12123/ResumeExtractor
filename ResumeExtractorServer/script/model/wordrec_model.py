# -*- coding: utf-8 -*-
"""
Created on Tue Mar 27 13:02:26 2018

@author: aaaaa123ad
"""
import os
import numpy as np
import keras
from keras.layers import Bidirectional,LSTM
from keras.models import Sequential
from keras.preprocessing import sequence
from keras.optimizers import Adam
from keras.utils import np_utils
from keras_contrib.layers.crf import CRF
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder
import random
import config
from script.tool import bigfile
from script.model.wordvec_model import WordVecModel

#实体词识别模型工具类
class WordRecModelTool:
    #构造方法
    def __init__(self):
        self.labels = ['B-company', 'I-company', 'E-company',
                  'B-time', 'I-time', 'E-time',
                  'B-edu', 'I-edu', 'E-edu',
                  'B-name', 'I-name', 'E-name',
                  'B-job', 'I-job', 'E-job',
                  'B-nationality', 'I-nationality', 'E-nationality',
                  'B-sex', 'I-sex', 'E-sex',
                  'B-school', 'I-school', 'E-school',
                  'B-pborn', 'I-pborn', 'E-pborn', 'O']

    #获取标签总数
    def get_labels_size(self):
        return len(self.labels)

    def get_one_hot_vec(self, label: str):
        vector = []

        if label in self.labels:
            for l in self.labels:
                if l == label:
                    vector.append(1.0)
                else:
                    vector.append(0.0)

            return vector
        else:
            print('没有该标签：', label)

    # 将标签向量转成标签字符串
    def labelvecs2strs(self, labelvec_list:list)->list:#[[1,0],[1,0],[1,0]]
        label_list=[]
        for labelvec in labelvec_list:
            maxindex = np.argmax(labelvec)  # 获取向量最大值的第一个索引值
            if int(maxindex)<self.get_labels_size():
                label_list.append(self.labels[int(maxindex)])
        return label_list


    #class end

#实体词识别模型预处理类
class WordRecModelPreprocessor:
    # 构造方法
    def __init__(self,
                 train_rate: float = 0.8,# 80%数据用来训练
                 sentence_len:int=config.SENTENCE_LEN,
                 wordvec_size=config.WORDVEC_SIZE
                 ):
        self.train_rate=train_rate
        self.sentence_len=sentence_len
        self.wordvec_size=wordvec_size

    #获取训练数据
    def get_train_data(self):

        sentences=[]
        labels=[]

        if os.path.exists(config.PREDATA_DIC+'/second_model_train_sentences.txt') and os.path.exists(config.PREDATA_DIC+'/second_model_train_labels.txt'):#如果存在该训练文件)

            reader=bigfile.get_file_content(config.PREDATA_DIC+'/second_model_train_sentences.txt')
            line=reader.__next__()
            while line:
                sentences.append(line.strip('\n'))
                line=reader.__next__()

            reader=bigfile.get_file_content(config.PREDATA_DIC+'/second_model_train_labels.txt')
            line = reader.__next__()
            while line:
                labels.append(line.strip('\n'))
                line = reader.__next__()

            s_l=[pair for pair in zip(sentences,labels)]

            sentences.clear()
            labels.clear()

            random.shuffle(s_l)#打乱数据

            for sentence,label in s_l:
                print(sentence,label)
                sentences.append(sentence)
                labels.append(label)

            sentencevec_list,labelvec_list= self._data2vec(sentences, labels)
            return np.array(sentencevec_list),np.array(labelvec_list)

        else:

            reader=bigfile.get_file_content(config.TAG_DIC+'/rnndata.txt')
            line=reader.__next__()
            while line:
                sentences.append(line.strip('\n'))
                line=reader.__next__()

            reader=bigfile.get_file_content(config.TAG_DIC+'/rnndatalabel.txt')
            line=reader.__next__()
            while line:
                labels.append(line.strip('\n'))
                line=reader.__next__()

            traindata_size = int(len(sentences) * self.train_rate)

            with open(config.PREDATA_DIC + '/second_model_train_sentences.txt', 'w') as write_file:  # 将测试数据写入文件
                for line in sentences[:traindata_size]:
                    write_file.write(line.strip() + '\n')
                write_file.close()

            with open(config.PREDATA_DIC + '/second_model_train_labels.txt', 'w') as write_file:  # 将测试数据写入文件
                for line in labels[:traindata_size]:
                    write_file.write(line.strip() + '\n')
                write_file.close()

            s_l = [pair for pair in zip(sentences[:traindata_size], labels[:traindata_size])]

            sentences.clear()
            labels.clear()

            random.shuffle(s_l)

            for sentence, label in s_l:
                print(sentence, label)
                sentences.append(sentence)
                labels.append(label)

            sentencevec_list, labelvec_list = self._data2vec(sentences, labels)
            return np.array(sentencevec_list), np.array(labelvec_list)


    # 获取测试数据
    def get_test_data(self):

        sentences=[]
        labels=[]

        if os.path.exists(config.PREDATA_DIC+'/second_model_test_sentences.txt') and os.path.exists(config.PREDATA_DIC+'/second_model_test_labels.txt'):#如果存在该训练文件)

            reader=bigfile.get_file_content(config.PREDATA_DIC+'/second_model_test_sentences.txt')
            line=reader.__next__()
            while line:
                sentences.append(line.strip('\n'))
                line=reader.__next__()

            reader=bigfile.get_file_content(config.PREDATA_DIC+'/second_model_test_labels.txt')
            line = reader.__next__()
            while line:
                labels.append(line.strip('\n'))
                line = reader.__next__()

            s_l=[pair for pair in zip(sentences,labels)]

            sentences.clear()
            labels.clear()

            random.shuffle(s_l)

            for sentence,label in s_l:
                print(sentence, label)
                sentences.append(sentence)
                labels.append(label)

            sentencevec_list,labelvec_list= self._data2vec(sentences, labels)
            return np.array(sentencevec_list),np.array(labelvec_list)

        else:

            reader=bigfile.get_file_content(config.TAG_DIC+'/rnndata.txt')
            line=reader.__next__()
            while line:
                sentences.append(line.strip('\n'))
                line=reader.__next__()

            reader=bigfile.get_file_content(config.TAG_DIC+'/rnndatalabel.txt')
            line=reader.__next__()
            while line:
                labels.append(line.strip('\n'))
                line=reader.__next__()

            traindata_size = int(len(sentences) * self.train_rate)

            with open(config.PREDATA_DIC + '/second_model_test_sentences.txt', 'w') as write_file:  # 将测试数据写入文件
                for line in sentences[traindata_size:]:
                    write_file.write(line.strip() + '\n')
                write_file.close()

            with open(config.PREDATA_DIC + '/second_model_test_labels.txt', 'w') as write_file:  # 将测试数据写入文件
                for line in labels[traindata_size:]:
                    write_file.write(line.strip() + '\n')
                write_file.close()

            s_l = [pair for pair in zip(sentences[traindata_size:], labels[traindata_size:])]

            sentences.clear()
            labels.clear()

            random.shuffle(s_l)

            for sentence, label in s_l:
                print(sentence, label)
                sentences.append(sentence)
                labels.append(label)

            sentencevec_list, labelvec_list = self._data2vec(sentences, labels)
            return np.array(sentencevec_list), np.array(labelvec_list)

    # 处理数据
    def _deal_data(self):
        pass

    # 数据转成向量
    def _data2vec(self,rnndata_list:list,rnnlabel_list:list):

        print('开始将数据转成向量！')

        wordvec_model=WordVecModel().load_trained_wordvec_model()# 加载词向量模型

        sentencevec_list=[]
        labelvec_list=[]


        for sentence in rnndata_list:
            sentencevec=[]

            sent_len=0
            for word in sentence.split():# 一行词
                #测试----------------
                print(sentence)

                if sent_len<self.sentence_len:# 如果词数量小于句子长度
                    # 把词向量加进入
                    try:
                        sentencevec.append(wordvec_model[word])
                    except:
                        sentencevec.append(wordvec_model['。'])
                else:# 如果词数量大于句子长度
                    break #截断
                sent_len+=1

            while sent_len<self.sentence_len:# 防止在词数量过短时补'。'的词向量
                sentencevec.append(wordvec_model['。'])
                sent_len+=1

            sentencevec_list.append(sentencevec)

        wrmt= WordRecModelTool()
        for labels in rnnlabel_list:
            labelvec=[]
            #测试-----------------
            print('标签开始')
            sent_len = 0
            for label in labels.split():

                if sent_len < self.sentence_len:  # 如果词数量小于句子长度

                    try:
                        # 标签成标准化编码 one-hot
                        print(label,wrmt.get_one_hot_vec(str(label)))
                        labelvec.append(wrmt.get_one_hot_vec(str(label)))
                    except:
                        print('O', wrmt.get_one_hot_vec('O'))
                        labelvec.append(wrmt.get_one_hot_vec('O'))
                else:
                    break
                sent_len += 1

            while sent_len < self.sentence_len:  # 如果词数量小于句子长度
                print('O',wrmt.get_one_hot_vec('O'))
                # 标签成标准化编码 one-hot
                labelvec.append(wrmt.get_one_hot_vec('O'))
                sent_len+=1

            # 测试-----------------
            print('标签结束')

            labelvec_list.append(labelvec)

        print('数据转成向量结束！')

        return sentencevec_list,labelvec_list

    #class end

#实体词识别模型类
class WordRecModel:
    # 构造方法
    def __init__(self,
                 model_path: str = config.MODEL_DIC + '/ner_model' , # 模型保存路径
                 train_rate:float=0.8,
                 wordvec_size: int = config.WORDVEC_SIZE,  # 词向量维度
                 sentence_len: int = config.SENTENCE_LEN,  # 句子长度
                 ):
        self.wordvec_size=wordvec_size
        self.sentence_len=sentence_len
        self.model_path=model_path
        self.train_rate=train_rate

    # 训练模型
    def train(self):

        print('开始训练模型！')

        wrmp=WordRecModelPreprocessor(train_rate=self.train_rate,sentence_len=self.sentence_len,wordvec_size=self.wordvec_size)
        train_x,train_y= wrmp.get_train_data()
        test_x,test_y=wrmp.get_test_data()

        traindata_size=len(train_x)
        testdata_size=len(test_x)

        wrmt=WordRecModelTool()

        train_x = sequence.pad_sequences(train_x,
                                            maxlen=self.sentence_len, padding='post', truncating='post')
        train_y = sequence.pad_sequences(train_y,
                                             maxlen=self.sentence_len, padding='post', truncating='post',
                                             value=wrmt.get_one_hot_vec('O'))

        test_x = sequence.pad_sequences(test_x,
                                           maxlen=self.sentence_len, padding='post', truncating='post')
        test_y = sequence.pad_sequences(test_y,
                                            maxlen=self.sentence_len, padding='post', truncating='post',
                                            value=wrmt.get_one_hot_vec('O'))

        train_x = np.reshape(train_x,
                                (traindata_size, self.sentence_len, self.wordvec_size))
        train_y = np.reshape(train_y,
                                 (traindata_size, self.sentence_len, wrmt.get_labels_size()))
        test_x = np.reshape(test_x,
                               (testdata_size, self.sentence_len, self.wordvec_size))
        test_y = np.reshape(test_y,
                                (testdata_size, self.sentence_len, wrmt.get_labels_size()))

        model=self._get_model()
        model.fit(train_x, train_y, epochs=15,
                  batch_size=250, validation_data=(test_x, test_y))

        print('训练模型结束！')
        print('开始保存模型！')
        # 保存模型到本地
        model.save(self.model_path)

        print('保存模型结束！')

    # 测试模型
    def test(self):
        print('开始测试模型！')

        wrmp = WordRecModelPreprocessor(train_rate=self.train_rate, sentence_len=self.sentence_len,wordvec_size=self.wordvec_size)
        test_x, test_y = wrmp.get_test_data()

        testdata_size = len(test_x)

        wrmt = WordRecModelTool()

        test_x = sequence.pad_sequences(test_x,
                                           maxlen=self.sentence_len, padding='post', truncating='post')
        test_y = sequence.pad_sequences(test_y,
                                            maxlen=self.sentence_len, padding='post', truncating='post',
                                            value=wrmt.get_one_hot_vec('O'))

        test_x = np.reshape(test_x,
                            (testdata_size, self.sentence_len, self.wordvec_size))
        test_y = np.reshape(test_y,
                            (testdata_size, self.sentence_len, wrmt.get_labels_size()))

        model= self.load_trained_model()

        y_pred = np.argmax(model.predict(test_x), 2)
        y_pred = np.append([], y_pred)

        y_true = np.argmax(test_y, 2)
        y_true = np.append([], y_true)

        # 打印分类报告 精度 召回率
        print(classification_report(y_true, y_pred))

        print('测试模型结束！')

    # 加载训练好的模型
    def load_trained_model(self):
        model= self._get_model()
        # 加载训练好的模型数据
        # keras.backend.clear_session()
        model.load_weights(self.model_path)
        return model

    # 获取模型
    def _get_model(self):
        # 创建模型
        model = Sequential()
        model.add(Bidirectional(
            LSTM(256, return_sequences=True),
            input_shape=(self.sentence_len, self.wordvec_size), name='biLSTM1'))
        model.add(Bidirectional(LSTM(512, return_sequences=True),
                                name='biLSTM2'))
        crf = CRF(WordRecModelTool().get_labels_size(), name='crf')
        model.add(crf)
        model.summary()
        adam = Adam()
        # 编译模型
        model.compile(adam, loss=crf.loss_function, metrics=[crf.accuracy])
        return model

    #class end
if __name__ == '__main__':
    WordRecModel().train()
    WordRecModel().test()
