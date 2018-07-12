#!/usr/bin/python 
# -*- coding : utf-8 -*-

# 该文件一定要放在项目的根目录下

import os

# 目录路径
PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))  # 获取项目根目录

SRCDATA_DIC=PROJECT_ROOT+'/file/01_srcdata' #简历源数据目录

PREDATA_DIC=PROJECT_ROOT+'/file/02_predata' #中间文件目录

TESTDATA_DIC=PROJECT_ROOT+'/file/03_testdata' #测试文件目录

RESULTDATA_DIC=PROJECT_ROOT+'/file/04_resultdata' #结果文件目录

CORPUS_DIC=PROJECT_ROOT+'/file/corpus_file' #文集文件目录

MODEL_DIC=PROJECT_ROOT+'/file/model_file' #模型文件目录

TAG_DIC=PROJECT_ROOT+'/file/tag_file' #标注数据文件目录

DATABASE_DIC=PROJECT_ROOT+'/file/database_file' #数据库文件目录

SRCRESUME_DIC=PROJECT_ROOT+'/file/srcresume_file' #源简历数据目录


# 其他配置
SENTENCE_LEN = 22  # 句子长度为22

WORDVEC_SIZE = 120  # 词向量维度 100
