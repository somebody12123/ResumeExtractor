# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 16:40:06 2018

@author: aaaaa123ad
"""

from gensim.models import Word2Vec  
import gensim
import config

#词向量模型
class WordVecModel:
    # 构造方法
    def __init__(self,
                 corpus_path:str=config.PREDATA_DIC+'/totalpart.txt',# 分词后的语料库路径
                 model_path:str=config.MODEL_DIC+'/word_vector.model',# 词向量模型保存路径
                 wordvec_size:int=config.WORDVEC_SIZE# 词向量维度
                 ):
        self.corpus_path=corpus_path
        self.model_path=model_path
        self.wordvec_size=wordvec_size

    # 训练并保存词向量模型
    def train_and_save_wordvec_model(self):
        print('开始训练词向量模型!')
        sentences = gensim.models.word2vec.Text8Corpus(self.corpus_path)  # 加载分词后的文件
        model = Word2Vec(sentences, size=self.wordvec_size, window=5, min_count=1, workers=4)  # 训练词向量模型

        print('词向量模型训练结束!')
        print('开始保存词向量模型！')
        model.save(self.model_path)  # 保存词向量模型
        print('保存词向量模型结束！')

    # 加载训练好的词向量模型
    def load_trained_wordvec_model(self):
        try:
            model = Word2Vec.load(self.model_path)
            return model
        except:
            print('该路径下没有词向量模型：%s',self.model_path)
            return None

if __name__ == '__main__':
    WordVecModel().train_and_save_wordvec_model()