#!/usr/bin/python 
# -*- coding: utf-8 -*-

from script.tool import splitword
from script.model.wordvec_model import WordVecModel
from script.model.sentencerec_model import SentenceRecModel
from script.model.wordrec_model import WordRecModel

#训练所有模型的总流程
if __name__ == '__main__':

    #分词
    splitword.split2word()

    #训练词向量模型
    WordVecModel().train_and_save_wordvec_model()

    #训练句子识别模型
    srm= SentenceRecModel()
    srm.train()
    srm.test()

    #训练实体词识别模型
    wrm=WordRecModel()
    wrm.train()
    wrm.test()

#--------------------



