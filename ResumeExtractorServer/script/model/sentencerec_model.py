# -*- coding: utf-8 -*-
"""
Created on Mon Apr  2 00:34:41 2018

@author: aaaaa123ad
"""

import os
from keras.layers import Bidirectional, Dense, GRU
from keras.models import Sequential
from keras.preprocessing import sequence
from keras.optimizers import Adam
from sklearn.metrics import classification_report
import numpy as np
import random
import jieba
from script.tool import bigfile
from script.model.wordvec_model import WordVecModel
import config

#句子识别模型工具类
class SentenceRecModelTool:

    def __init__(self):
        self.labels=['ctime', 'ptime', 'peri', 'unc', 'noinfo'] #标签列表

    #获取标签总数
    def get_labels_count(self):
        return len(self.labels)

    def get_one_hot_vec(self,label:str):
        vector=[]

        if label in self.labels:
            for l in self.labels:
                if l==label:
                    vector.append(1.0)
                else:
                    vector.append(0.0)

            return vector
        else:
            print('没有该标签：',label)

    #将标签向量转成标签字符串
    def labelvec2str(self, labelvec):
        maxindex = np.argmax(labelvec)  # 获取向量最大值的第一个索引值
        if int(maxindex)<self.get_labels_count():
            return self.labels[int(maxindex)]
        else:
            print('索引值超出范围')

    def get_index(self,label):
        if label in self.labels:
            for index in range(len(self.labels)):
                if label==self.labels[index]:
                    return index
        else:
            print(label,'不在标签列表内')
    #class end


# 句子识别模型预处理器类
# 将标注好的第一层框架的训练数据处理成句子向量和one-hot向量
class SentenceRecModelPreprocessor:
    # 构造函数
    def __init__(self,
                 train_rate: float = 0.85,  # 用作训练的数据比值
                 sentence_len=config.SENTENCE_LEN,
                 wordvec_size=config.WORDVEC_SIZE
                 ):
        self.train_rate = train_rate
        self.sentence_len=sentence_len
        self.wordvec_size=wordvec_size

    # 获取训练数据
    def get_train_data(self):
        print('开始获取第一层训练数据！')

        datas=[]
        # sentences=[]
        # labels=[]
        if os.path.exists(config.PREDATA_DIC+'/first_model_train_sentences.txt'):#如果存在该训练文件
            reader=bigfile.get_file_content(config.PREDATA_DIC+'/first_model_train_sentences.txt')#直接读取该文件的数据
            line=reader.__next__()
            while line:
                datas.append(line.strip('\n'))
                line=reader.__next__()

            sentences, labels = self._deal_data(datas)  # 将数据拆分成句子和标签

            print('句子数量：',len(sentences),'标签数量：',len(labels))

        else:
            reader = bigfile.get_file_content(config.TAG_DIC + '/sdata.txt')#读取所有训练数据文件
            line = reader.__next__()
            while line:
                datas.append(line.strip('\n'))
                line = reader.__next__()

            traindata_size = int(len(datas) * self.train_rate)

            with open(config.PREDATA_DIC + '/first_model_train_sentences.txt', 'w') as write_file:#将训练数据写入文件
                for line in datas[:traindata_size]:
                    write_file.write(line.strip()+'\n')
                write_file.close()

            if os.path.exists(config.PREDATA_DIC + '/first_model_test_sentences.txt')==False:#如果测试数据文件不存在
                with open(config.PREDATA_DIC + '/first_model_test_sentences.txt', 'w') as write_file:  # 将训练数据写入文件
                    for line in datas[traindata_size:]:
                        write_file.write(line.strip()+'\n')
                    write_file.close()

            sentences, labels = self._deal_data(datas[:traindata_size])  # 将数据拆分成句子和标签

            print('句子数量：', len(sentences), '标签数量：', len(labels))

        train_pair_list = [pair for pair in zip(sentences, labels)]  # 组合成训练集

        sentences.clear()
        labels.clear()

        random.shuffle(train_pair_list)  # 打乱数据顺序

        for sentence, label in train_pair_list:
            print(sentence, label)
            sentences.append(sentence.strip())
            labels.append(str(label).strip())

        sentencevec_list, labelvec_list = self._data2vec(sentences, labels)  # 将句子转成句子向量，将标签转成标签向量

        print('获取第一层训练数据结束！')
        return np.array(sentencevec_list),np.array(labelvec_list)

    # 获取测试数据
    def get_test_data(self):
        #1判断测试数据文件是否存在
        #2存在；直接读取测试数据文件，将数据拆分成句子和标签；将句子用词向量表示，标签用one-hot向量表示
        #3不存在；读取所有训练数据文件，按比例将数据分成训练集和测试集，再进行第二步
        print('开始获取第一层测试数据！')

        data_list = []
        sentences = []
        labels = []
        if os.path.exists(config.PREDATA_DIC + '/first_model_test_sentences.txt'):  # 如果存在该测试文件
            reader = bigfile.get_file_content(config.PREDATA_DIC + '/first_model_test_sentences.txt')  # 直接读取该文件的数据
            line = reader.__next__()
            while line:
                data_list.append(line.strip('\n'))
                line = reader.__next__()

            sentences, labels = self._deal_data(data_list)  # 将数据拆分成句子和标签

            print('句子数量：', len(sentences), '标签数量：', len(labels))

        else:
            reader = bigfile.get_file_content(config.TAG_DIC + '/sdata.txt')  # 读取所有训练数据文件
            line = reader.__next__()
            while line:
                data_list.append(line.strip('\n'))
                line = reader.__next__()

            traindata_size = int(len(data_list) * self.train_rate)

            with open(config.PREDATA_DIC + '/first_model_test_sentences.txt', 'w') as write_file:  # 将测试数据写入文件
                for line in data_list[traindata_size:]:
                    write_file.write(line.strip() + '\n')
                write_file.close()

            if os.path.exists(config.PREDATA_DIC + '/first_model_train_sentences.txt') == False:  # 如果训练数据文件不存在
                with open(config.PREDATA_DIC + '/first_model_train_sentences.txt', 'w') as write_file:  # 将训练数据写入文件
                    for line in data_list[:traindata_size]:
                        write_file.write(line.strip() + '\n')
                    write_file.close()

            sentences, labels = self._deal_data(data_list[traindata_size:])  # 将数据拆分成句子和标签

            print('句子数量：', len(sentences), '标签数量：', len(labels))

        train_pair_list = [pair for pair in zip(sentences, labels)]  # 组合成训练集

        sentences.clear()
        labels.clear()

        random.shuffle(train_pair_list)  # 打乱数据顺序

        for sentence, label in train_pair_list:
            print(sentence, label)
            sentences.append(sentence.strip())
            labels.append(str(label).strip())

        sentencevec_list, labelvec_list = self._data2vec(sentences, labels)  # 将句子转成句子向量，将标签转成标签向量

        print('获取第一层测试数据结束！')
        return np.array(sentencevec_list), np.array(labelvec_list)


    # 处理数据 将句子和标签分开 并把句子分词
    def _deal_data(self,data_list:list):
        print('开始处理数据！')

        jieba.load_userdict(config.CORPUS_DIC+'/Chinese_Names_Corpus.txt')  # 将中文人名添加到分词词典

        sentences = []  # 保存分词后的句子
        labels = []  # 保存标签

        # temp_sentence_words_list=[]#用来判断是否有重复的句子

        for line in data_list:
            try:
                if len(line.strip()) > 0:
                    pair = line.split(';;;')  # 将句子和标签分开
                    if len(pair) > 1 and pair[0] != '':
                        sentence_words = ' '.join(jieba.cut(pair[0]))  # 将句子分词
                        # if sentence_words not in temp_sentence_words_list:
                        sentences.append(sentence_words)
                        label = pair[1].strip()
                        labels.append(label)
                            # temp_sentence_words_list.append(sentence_words)
            except:
                print('error', line)

        print('处理数据结束！')

        return sentences, labels  # 返回 分词后的句子列表，表示该句句子的标签列表

    # 数据转成向量
    def _data2vec(self, sentences: list, labels: list):

        print('开始将数据转成向量！')
        wordvec_model = WordVecModel().load_trained_wordvec_model()  # 加载训练好的词向量模型

        sentencevec_list = []  # 句子向量列表
        labelvec_list = []  # 标签向量列表

        for sentence in sentences:
            sentencevec = []

            sent_len = 0
            for word in sentence.split():
                if sent_len < self.sentence_len:
                    try:
                        sentencevec.append(wordvec_model[word])
                    except:
                        sentencevec.append(wordvec_model['。'])
                else:
                    break
                sent_len += 1

            while sent_len < self.sentence_len:
                sentencevec.append(wordvec_model['。'])
                sent_len += 1

            sentencevec_list.append(sentencevec)

        srmt=SentenceRecModelTool()
        for label in labels:
            labelvec=srmt.get_one_hot_vec(label)
            print(label,labelvec)
            labelvec_list.append(labelvec)

        print('数据转成向量结束！')

        return sentencevec_list, labelvec_list

    # class end


# 句子识别模型类
class SentenceRecModel:
    # 构造方法
    def __init__(self,
                 model_path=config.MODEL_DIC+'/sentence_model',  # 第一层神经网络模型路径
                 train_rate:float=0.85,#85%用来训练
                 wordvec_size=config.WORDVEC_SIZE,  # 词向量维度
                 sentence_len=config.SENTENCE_LEN):  # 句子长度 即一句话由多少个词组成
        self.model_path = model_path
        self.train_rate=train_rate
        self.wordvec_size = wordvec_size
        self.sentence_len = sentence_len

    # 训练模型
    def train(self):
        print('开始训练模型！')
        srmp = SentenceRecModelPreprocessor(train_rate=self.train_rate,sentence_len=self.sentence_len,wordvec_size=self.wordvec_size)
        train_x, train_y = srmp.get_train_data()  # 获取训练数据
        test_x, test_y = srmp.get_test_data()  # 获取测试数据

        # 训练数据大小
        traindatas_size = len(train_x)
        # 测试数据大小
        testdatas_size = len(test_x)

        # 填充数据
        train_x = sequence.pad_sequences(train_x,
                                            maxlen=self.sentence_len, padding='post',truncating='post')  # 如果句子长度大于sentence_size，后面的就不要；小于就补9
        test_x = sequence.pad_sequences(test_x,
                                           maxlen=self.sentence_len, padding='post', truncating='post')
        train_x = np.reshape(train_x,
                                (traindatas_size, self.sentence_len, self.wordvec_size))
        test_x = np.reshape(test_x,
                               (testdatas_size, self.sentence_len, self.wordvec_size))

        model = self._get_model()

        # 训练模型
        model.fit(train_x, train_y, epochs=20,
                  batch_size=250, validation_data=(test_x, test_y))
        # 保存模型
        model.save(self.model_path)

        print('训练模型结束！')

    # 测试模型
    def test(self):
        print('开始测试模型！')
        # 获取训练好的模型
        model = self.load_trained_model()
        # 加载数据
        srmp = SentenceRecModelPreprocessor(train_rate=self.train_rate, sentence_len=self.sentence_len,wordvec_size=self.wordvec_size)
        test_x, test_y = srmp.get_test_data()

        testdatas_size = len(test_x)
        # 填充数据
        test_x = sequence.pad_sequences(test_x,
                                           maxlen=self.sentence_len, padding='post', truncating='post')
        test_x = np.reshape(test_x,
                               (testdatas_size, self.sentence_len, self.wordvec_size))

        # 测试模型
        y_pred = np.argmax(model.predict(test_x), 1)  # 行的最大值的索引 推测值
        y_true = np.argmax(test_y, 1)  # 行的最大值的索引 真实值

        t_name = ['ctime', 'ptime', 'peri', 'unc', 'noinfo']

        print(classification_report(y_true, y_pred, target_names=t_name))

        print('测试模型结束！')

    # 加载训练完成的模型
    def load_trained_model(self):
        print('开始加载模型！')
        model = self._get_model()
        try:
            # keras.backend.clear_session()
            model.load_weights(self.model_path)
        except:
            print('该路径下没有句子识别模型：%s'%self.model_path)
        print('加载模型结束！')
        return model

    # 获取模型
    def _get_model(self):
        # 创建模型
        model = Sequential()
        model.add(Bidirectional(GRU(400, return_sequences=False, dropout=0.5),
                                input_shape=(self.sentence_len, self.wordvec_size), name='biGRU'))
        model.add(Dense(5, activation='softmax', name='softmax'))
        model.summary()
        adam = Adam()
        # 编辑模型
        model.compile(adam, loss='binary_crossentropy', metrics=['accuracy', 'mse'])
        return model

    #class end

# test

if __name__ == '__main__':
    srm=SentenceRecModel()
    srm.train()
    srm.test()
