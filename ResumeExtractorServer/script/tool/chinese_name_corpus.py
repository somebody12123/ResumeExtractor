#!/usr/bin/python 
# -*- coding: utf-8 -*-

import config
import os
from script.tool import bigfile

#该模块是用于处理中文人名集

def deal_chinesename_corpus(corpus_dic:str=config.CORPUS_DIC,srcdata_dic:str=config.SRCDATA_DIC):
    name_list=[]
    if os.path.exists(corpus_dic+'/中文人名集.txt') and len(os.listdir(srcdata_dic))>0:
            reader=bigfile.get_file_content(corpus_dic+'/中文人名集.txt')
            line=reader.__next__()
            while line:
                name=line.strip().strip('\n')
                if name != '':
                    print(name)
                    name_list.append(name)
                line=reader.__next__()

            filepath_list=[srcdata_dic+'/'+filename for filename in os.listdir(srcdata_dic)]
            for filepath in filepath_list:
                reader= bigfile.get_file_content(filepath)
                line=reader.__next__()
                while line:
                    data=line.strip().strip('\n').split('|')
                    if len(data)>4:
                        if data[1]!='':
                            if data[1] not in name_list:
                                print(data[1])
                                name_list.append(data[1])
                        elif data[3]!='':
                            if data[3] not in name_list:
                                print(data[3])
                                name_list.append(data[3])
                    line=reader.__next__()

            with open(corpus_dic+'Chinese_Names_Corpus.txt','w',encoding='utf-8') as write_file:
                for name in name_list:
                    write_file.write(name)
                    write_file.write('\n')

                write_file.close()

    else:
        print('没有中文人名源材料！')



#test
# deal_chinesename_corpus()
