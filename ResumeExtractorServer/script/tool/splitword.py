#!/usr/bin/python 
# -*- coding: <encoding name> -*-

from config import *
import jieba
import os
from script.tool import bigfile
import config

# 将中文wiki预料库和简历源材料分词，保存到predata目录下
def split2word():
    print('开始分词')
    filenames=os.listdir(config.SRCDATA_DIC)#获取源数据目录下的源数据文件名
    filepaths=[config.SRCDATA_DIC+'/'+file_name for file_name in filenames]

    jieba.load_userdict(config.CORPUS_DIC+'/chinese_name.txt')  # 载入中文人名词到jieba词典中

    with open(config.PREDATA_DIC+'/totalpart.txt','w')as totalpart_file:# 以读方式打开totalpart.txt文件
        for filepath in filepaths:# 将所有源文件分词并写入totalpart.txt文件
            reader= bigfile.get_file_content(filepath)# yield 方式读取每行内容，防止过于耗内存
            line=reader.__next__()
            while line:
                result=jieba.lcut(line)
                for word in result:
                    totalpart_file.write(word+' ')
                totalpart_file.write('\n')
                totalpart_file.flush()  # 刷新缓冲区，防止过于耗内存
                line=reader.__next__()

        reader= bigfile.get_file_content(config.CORPUS_DIC+'/wiki_chs')#yield 方式读取每行内容，防止过于耗内存
        line=reader.__next__()
        while line:
            result=jieba.lcut(line.strip())
            for word in result:
                totalpart_file.write(word+' ')
            totalpart_file.write('\n')
            line=reader.__next__()
        totalpart_file.close()

    print('分词结束')


#代码测试
if __name__ == '__main__':
    split2word()