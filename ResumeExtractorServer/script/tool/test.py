#!/usr/bin/python 
# -*- coding: utf-8 -*-

#测试第一层和第二层神经网络模型

import math
import re
import os
import jieba
import config
from script.tool import bigfile
from script.model.wordvec_model import WordVecModel
from script.model.sentencerec_model import *
from script.model.wordrec_model import *

#测试句子识别模型
def test_sentencerec_model():

    labels=['ctime', 'ptime', 'peri', 'unc', 'noinfo']
    counts=[0,0,0,0,0]
    rights=[0,0,0,0,0]
    persents=[]

    wordvec_model=WordVecModel().load_trained_wordvec_model()
    sentencerec_model=SentenceRecModel().load_trained_model()
    srt = SentenceRecModelTool()
    #wordrec_model=WordRecModel().load_trained_model()
    jieba.load_userdict(config.CORPUS_DIC+'/Chinese_Names_Corpus.txt')

    reader=bigfile.get_file_content(config.PREDATA_DIC+'/first_model_train_sentences.txt')
    line=reader.__next__()
    while line:
        sentence_label=line.strip()#一条简历信息
        if sentence_label != None and sentence_label != '':
            #分句
            temp=sentence_label.split(';;;')
            if len(temp)==2:
                sentence=temp[0]
                label=temp[1]

                if sentence.strip() != '':
                    sent_len = 0
                    sentencevec=[]
                    for word in jieba.lcut(sentence):
                        if (word != ' ') and (word != '') and (word != '\n'):
                            if sent_len < config.SENTENCE_LEN:
                                try:
                                    sentencevec.append(wordvec_model[word])
                                except:
                                    sentencevec.append(wordvec_model['。'])
                            else:
                                break
                            sent_len += 1

                    while sent_len < config.SENTENCE_LEN:
                        sentencevec.append(wordvec_model['。'])
                        sent_len+=1

                    test_x=np.array(sentencevec).reshape(1,config.SENTENCE_LEN,config.WORDVEC_SIZE)
                    forecast=sentencerec_model.predict(test_x)

                    forecast_label=srt.labelvec2str(forecast)

                    label_index= srt.get_index(label)
                    print('test',label,label_index)

                    counts[label_index]+=1
                    if label==forecast_label:
                        rights[label_index]+=1

                    print('句子：'+sentence,'真实类别：'+label,'预测类别：'+forecast_label)

        line=reader.__next__()
    for right,count in zip(rights,counts):
        present=float(int(right)*1.0/int(count))
        persents.append(present)
    print('标签',labels)
    print('标签总数',counts)
    print('标签正确数',rights)
    print('标签正确率',persents)

#测试实体词识别模型
def test_wordrec_model():
    labels = ['B-company', 'I-company', 'E-company',
              'B-time', 'I-time', 'E-time',
              'B-edu', 'I-edu', 'E-edu',
              'B-name', 'I-name', 'E-name',
              'B-job', 'I-job', 'E-job',
              'B-nationality', 'I-nationality', 'E-nationality',
              'B-sex', 'I-sex', 'E-sex',
              'B-school', 'I-school', 'E-school',
              'B-pborn', 'I-pborn', 'E-pborn', 'O']
    count=0
    right=0

    wordvec_model = WordVecModel().load_trained_wordvec_model()
    wordrec_model = WordRecModel().load_trained_model()
    jieba.load_userdict(config.CORPUS_DIC + '/Chinese_Names_Corpus.txt')

    wrmt=WordRecModelTool()

    reader1 = bigfile.get_file_content(config.PREDATA_DIC+'/second_model_test_sentences.txt')
    reader2=bigfile.get_file_content(config.PREDATA_DIC+'/second_model_test_labels.txt')
    words = reader1.__next__()
    labels=reader2.__next__()
    while words and labels:
        words=words.split()
        labels=labels.split()

        if len(words)==len(labels):

            sentencevec=[]
            label_list=[]#长度为句子长度的标签列表

            sen_len = 0
            for word in words:
                if sen_len<config.SENTENCE_LEN:
                    try:
                        sentencevec.append(wordvec_model[word])
                    except:
                        sentencevec.append(wordvec_model['。'])
                    sen_len+=1
                else:
                    break

            while sen_len<config.SENTENCE_LEN:
                sentencevec.append(wordvec_model['。'])
                sen_len+=1

            sen_len = 0
            for label in labels:
                if sen_len < config.SENTENCE_LEN:
                    label_list.append(label)
                    sen_len+=1
                else:
                    break

            while sen_len<config.SENTENCE_LEN:
                label_list.append('O')
                sen_len+=1

            #处理数据
            test_x = np.array(sentencevec).reshape(1, config.SENTENCE_LEN, config.WORDVEC_SIZE)
            #预测
            forecast = wordrec_model.predict(test_x)
            #转成标签
            word_label_list = wrmt.labelvecs2strs(forecast[0])

            print('句子：',words)
            print('正确标签:',label_list)
            print('预测标签:',word_label_list)
            count+=1

            index=0
            for label in label_list:
                if word_label_list[index]!=label:
                    break
                index+=1

            if index==len(label_list):
                right+=1
                print('right')
            else:
                print('wrong')

        words=reader1.__next__()
        labels=reader2.__next__()

    print('句子总数：',count)
    print('预测正确数：',right)


if __name__ == '__main__':
    # test_sentencerec_model()
    test_wordrec_model()