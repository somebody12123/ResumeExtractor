# -*- coding: utf-8 -*-
"""
Created on Wed Mar 14 17:43:43 2018

@author: aaaaa123ad
"""

import numpy as np
import jieba
import re
import config
import os
from script.model.sentencerec_model import SentenceRecModelTool
from script.model.wordrec_model import WordRecModelTool
from script.tool import bigfile
from script.object.resume import Resume,ResumeTool
from script.database.name_database import NameDatabase
from script.database import mongotool as mtool

from script.model.wordvec_model import WordVecModel
from script.model.sentencerec_model import SentenceRecModel
from script.model.wordrec_model import WordRecModel
import tensorflow as tf
class Extractor:
    def __init__(self):

        print('开始加载模型数据')
        print('开始加载第一层神经网络模型')
        self.sentencerec_model = SentenceRecModel().load_trained_model()

        print('加载第一层神经网络模型结束')
        print('开始加载第二层神经网络模型')
        self.wordrec_model = WordRecModel().load_trained_model()
        print('加载第二层神经网络模型结束')
        print('开始加载词向量模型')
        self.wordvec_model = WordVecModel().load_trained_wordvec_model()
        print('加载词向量模型结束')
        print('加载模型数据结束')
        print('开始加载分词词库')
        jieba.load_userdict(config.CORPUS_DIC + '/name.txt')
        print('加载分词词库结束')
        self.graph = tf.get_default_graph()

    # 处理源简历 返回句子列表
    def _deal_data(self, srcresume: str):
        # 停用掉某些符号 《》<>（）()「」{}|
        pattern = r'[|]+'
        pat = re.compile (pattern)
        srcresume = re.sub (pat, '，', srcresume)  # 将'|'转成'，'

        pattern1 = r'[《》<>（）()「」{}]'
        pat1 = re.compile (pattern1)
        srcresume = re.sub (pat1, '', srcresume)  # 将'《》<>（）()「」{}'去掉

        # 分句 ，。？！；
        pattern2 = r'[,，。?？！;；\\n\\t\\r]'
        pat2 = re.compile (pattern2)
        sentences = re.split (pat2, srcresume.strip ())  # 以'，。？！；'为句子分隔符分割句子

        return sentences

    def _sentence2array(self,sentence:str):
        words = jieba.lcut (sentence)  # 分词

        sentencevec = []  # 句子向量
        sent_len = 0
        for word in words:  # 将词转成词向量
            if sent_len < config.SENTENCE_LEN:
                try:
                    sentencevec.append (self.wordvec_model[word])
                except:
                    sentencevec.append (self.wordvec_model['。'])
                sent_len += 1
            else:
                break

        while sent_len < config.SENTENCE_LEN:
            sentencevec.append (self.wordvec_model['。'])
            words.append ('。')
            sent_len += 1

        # 输入数据最后处理
        test_x = np.array (sentencevec).reshape (1, config.SENTENCE_LEN, config.WORDVEC_SIZE)
        return words,test_x

    # 句子识别模型预测
    def _sentence_predict(self, test_x):
        # 第一层神经网络模型预测
        global first_forecast
        with self.graph.as_default ():
            first_forecast = self.sentencerec_model.predict (test_x)
        sentence_label = SentenceRecModelTool ().labelvec2str (first_forecast)
        return sentence_label

    # 实体词识别模型预测
    def _word_predict(self, test_x):
        global second_forecast
        with self.graph.as_default ():
            second_forecast = self.wordrec_model.predict (test_x)
        word_labels = WordRecModelTool ().labelvecs2strs (second_forecast[0])
        return word_labels

    #从一条原始简历抽取信息元 返回一个简历类对象
    def _extract(self,srcresume:str):
        person_data = {
            'person_basic_info':
                {
                    'name': '',
                    'birth': '',
                    'sex': '',
                    'nationality': '',
                    'degree': '',
                    'school': ''  # str: time,schoolname,major
                },
            'person_curwork_info':
            #  str: time_str, str: org list:job
                [],
            'person_prework_info':
            #  str: time_str, str: org + list:job
                []
        }

        current_exp_label = ''  # 经验标签
        current_exp_time = ''  # 经验时间

        sentences = self._deal_data (srcresume)

        for sentence in sentences:

            words, test_x = self._sentence2array (sentence)
            # 第一层神经网络模型预测
            sentence_label = self._sentence_predict (test_x)

            # 第一层神经网络模型识别出来的标签 根据标签识别第二层
            if sentence_label == 'noinfo':
                current_exp_label = ''
                current_exp_time = ''
            else:
                word_labels = self._word_predict (test_x)
                if sentence_label == 'ctime':
                    current_exp_label = 'ctime'

                    cexp = {
                        'time': '',
                        'place': '',
                        'job': []
                    }

                    time_words = []  # 组合时间词
                    company_words = []  # 组合地点词
                    job_words = []  # 组合工作词

                    for word, label in zip (words, word_labels):  # 遍历
                        if label == 'B-time':
                            if len (time_words) > 0:
                                time_words.clear ()
                            time_words.append (word)
                        elif label == 'I-time':
                            time_words.append (word)
                        elif label == 'E-time':
                            if len (time_words) > 0:
                                time_words.append (word)
                                if cexp['time'] == '':
                                    cexp['time'] = ''.join (time_words)
                                    current_exp_time = cexp['time']
                                time_words.clear ()
                            else:
                                if cexp['time'] == '':
                                    cexp['time'] = word
                                    current_exp_time = cexp['time']
                        # ---------------------------
                        elif label == 'B-company':
                            if len (company_words) > 0:
                                company_words.clear ()
                            company_words.append (word)
                        elif label == 'I-company':
                            company_words.append (word)
                        elif label == 'E-company':
                            if len (company_words) > 0:
                                company_words.append (word)
                                if cexp['place'] == '':
                                    cexp['place'] = ''.join (company_words)
                                    company_words.clear ()
                            else:
                                if cexp['place'] == '':
                                    cexp['place'] = word
                        # ---------------------------
                        elif label == 'B-job':
                            if len (job_words) > 0:
                                job_words.clear ()
                            job_words.append (word)
                        elif label == 'I-job':
                            job_words.append (word)
                        elif label == 'E-job':
                            if len (job_words) > 0:
                                job_words.append (word)
                                cexp['job'].append (''.join (job_words))
                                job_words.clear ()
                            else:
                                cexp['job'].append (''.join (word))

                    ###################################################
                    if cexp['place'] != '' or len (cexp['job']) > 0:
                        person_data['person_curwork_info'].append (cexp)

                elif sentence_label == 'ptime':
                    current_exp_label = 'ptime'

                    pexp = {
                        'time': '',
                        'place': '',
                        'job': []
                    }

                    time_words = []  # 组合时间词
                    company_words = []  # 组合地点词
                    job_words = []  # 组合工作词

                    for word, label in zip (words, word_labels):  # 遍历
                        if label == 'B-time':
                            if len (time_words) > 0:
                                time_words.clear ()
                            time_words.append (word)
                        elif label == 'I-time':
                            time_words.append (word)
                        elif label == 'E-time':
                            if len (time_words) > 0:
                                time_words.append (word)
                                if pexp['time'] == '':
                                    pexp['time'] = ''.join (time_words)
                                    current_exp_time = pexp['time']
                                time_words.clear ()
                            else:
                                if pexp['time'] == '':
                                    pexp['time'] = word
                                    current_exp_time = pexp['time']
                        # ---------------------------
                        elif label == 'B-company':
                            if len (company_words) > 0:
                                company_words.clear ()
                            company_words.append (word)
                        elif label == 'I-company':
                            company_words.append (word)
                        elif label == 'E-company':
                            if len (company_words) > 0:
                                company_words.append (word)
                                if pexp['place'] == '':
                                    pexp['place'] = ''.join (company_words)
                                    company_words.clear ()
                            else:
                                if pexp['place'] == '':
                                    pexp['place'] = word
                        # ---------------------------
                        elif label == 'B-job':
                            if len (job_words) > 0:
                                job_words.clear ()
                            job_words.append (word)
                        elif label == 'I-job':
                            job_words.append (word)
                        elif label == 'E-job':
                            if len (job_words) > 0:
                                job_words.append (word)
                                pexp['job'].append (''.join (job_words))
                                job_words.clear ()
                            else:
                                pexp['job'].append (''.join (word))

                    ####################################################
                    if pexp['place'] != '' or len (pexp['job']) > 0:
                        person_data['person_prework_info'].append (pexp)

                elif sentence_label == 'unc':
                    # dic place job
                    exp = {
                        'time': '',
                        'place': '',
                        'job': []
                    }

                    company_words = []  # 组合地点词
                    job_words = []  # 组合工作词

                    for word, label in zip (words, word_labels):  # 遍历
                        if label == 'B-company':
                            if len (company_words) > 0:
                                company_words.clear ()
                            company_words.append (word)
                        elif label == 'I-company':
                            company_words.append (word)
                        elif label == 'E-company':
                            if len (company_words) > 0:
                                company_words.append (word)
                                if exp['place'] == '':
                                    exp['place'] = ''.join (company_words)
                                    company_words.clear ()
                            else:
                                if exp['place'] == '':
                                    exp['place'] = word
                        # ---------------------------
                        elif label == 'B-job':
                            if len (job_words) > 0:
                                job_words.clear ()
                            job_words.append (word)
                        elif label == 'I-job':
                            job_words.append (word)
                        elif label == 'E-job':
                            if len (job_words) > 0:
                                job_words.append (word)
                                exp['job'].append (''.join (job_words))
                                job_words.clear ()
                            else:
                                exp['job'].append (''.join (word))
                    ############################################################################
                    # if exp['place'] == '' or len (exp['job']) > 0:
                    #     if current_exp_label == 'ctime':
                    #         if len (person_data['person_curwork_info']) > 0:
                    #             cexp = person_data['person_curwork_info'][-1]
                    #             if cexp['place'] != '' and len (cexp['job']) == 0:
                    #                 for job in exp['job']:
                    #                     person_data['person_curwork_info'][-1]['job'].append (job)
                    #     elif current_exp_label == 'ptime':
                    #         if len (person_data['person_prework_info']) > 0:
                    #             pexp = person_data['person_prework_info'][-1]
                    #             if pexp['place'] != '' and len (pexp['job']) == 0:
                    #                 for job in exp['job']:
                    #                     person_data['person_prework_info'][-1]['job'].append (job)
                    # else:
                    #     exp['time'] = current_exp_time
                    #     if current_exp_label == 'ctime':
                    #         person_data['person_curwork_info'].append (exp)
                    #     elif current_exp_label == 'ptime':
                    #         person_data['person_prework_info'].append (exp)
                    #     elif current_exp_label == '':
                    #         person_data['person_prework_info'].append (exp)
                    exp['time']=current_exp_time

                    if exp['place'] != '' or len (exp['job']) > 0:
                        if exp['place'] != '' and len (exp['job']) == 0:#有 地方 值
                            if current_exp_label == 'ctime':
                                if len (person_data['person_curwork_info']) > 0:
                                    cexp = person_data['person_curwork_info'][-1]
                                    if cexp['place'] == '' :#前一个字典中的place的值为''，插到原来的字典中
                                        person_data['person_curwork_info'][-1]['place']=exp['place']
                                    else:#前一个字典中的place的值不为''，将新的字典插入
                                        person_data['person_curwork_info'].append(exp)
                            elif current_exp_label == 'ptime':
                                if len (person_data['person_prework_info']) > 0:
                                    pexp = person_data['person_prework_info'][-1]
                                    if pexp['place'] == '':
                                        person_data['person_prework_info'][-1]['place']=exp['place']
                                    else:
                                        person_data['person_prework_info'].append(exp)
                            else:#如果current_exp_label == ''，插入到过去经历列表中
                                person_data['person_prework_info'].append(exp)
                        elif exp['place'] == '' and len (exp['job']) > 0:#有 职位 值
                            if current_exp_label == 'ctime':
                                if len (person_data['person_curwork_info']) > 0:
                                    cexp = person_data['person_curwork_info'][-1]
                                    if len(cexp['job']) ==0 :
                                        for job in exp['job']:
                                            person_data['person_curwork_info'][-1]['job'].append (job)
                                    else:
                                        person_data['person_curwork_info'].append(exp)
                            elif current_exp_label == 'ptime':
                                if len (person_data['person_prework_info']) > 0:
                                    pexp = person_data['person_prework_info'][-1]
                                    if len (pexp['job']) == 0:
                                        for job in exp['job']:
                                            person_data['person_prework_info'][-1]['job'].append (job)
                                    else:
                                        person_data['person_prework_info'].append(exp)
                            else:
                                person_data['person_prework_info'].append(exp)
                        elif exp['place'] != '' and len (exp['job']) > 0:#都有
                            if current_exp_label == 'ctime':
                                person_data['person_curwork_info'].append(exp)
                            elif current_exp_label == 'ptime':
                                person_data['person_prework_info'].append(exp)


                elif sentence_label == 'peri':
                    current_exp_label = ''
                    current_exp_time = ''

                    name_words = []  # 组合姓名词
                    sex_words = []  # 组合性别词
                    edu_words = []  # 组合教育词
                    school_words = []  # 组合学校词
                    nationality_words = []  # 组合国籍词
                    time_words = []  # 组合时间词

                    for word, label in zip (words, word_labels):  # 遍历
                        if label == 'B-time':
                            if len (time_words) > 0:
                                time_words.clear ()
                            time_words.append (word)
                        elif label == 'I-time':
                            time_words.append (word)
                        elif label == 'E-time':
                            if len (time_words) > 0:
                                time_words.append (word)
                                if person_data['person_basic_info']['birth'] == '':
                                    person_data['person_basic_info']['birth'] = ''.join (time_words)
                                time_words.clear ()
                            else:
                                if person_data['person_basic_info']['birth'] == '':
                                    person_data['person_basic_info']['birth'] = word
                        # ---------------------------
                        elif label == 'B-edu':
                            if len (edu_words) > 0:
                                edu_words.clear ()
                            edu_words.append (word)
                        elif label == 'I-edu':
                            edu_words.append (word)
                        elif label == 'E-edu':
                            if len (time_words) > 0:
                                edu_words.append (word)
                                if person_data['person_basic_info']['degree'] == '':
                                    person_data['person_basic_info']['degree'] = ''.join (edu_words)
                                    edu_words.clear ()
                            else:
                                if person_data['person_basic_info']['degree'] == '':
                                    person_data['person_basic_info']['degree'] = word
                        # ---------------------------
                        elif label == 'B-name':
                            if len (name_words) > 0:
                                name_words.clear ()
                            name_words.append (word)
                        elif label == 'I-name':
                            name_words.append (word)
                        elif label == 'E-name':
                            if len (name_words) > 0:
                                name_words.append (word)
                                if person_data['person_basic_info']['name'] == '':
                                    person_data['person_basic_info']['name'] = ''.join (name_words)
                                    name_words.clear ()
                            else:
                                if person_data['person_basic_info']['name'] == '':
                                    person_data['person_basic_info']['name'] = word
                        # ---------------------------
                        elif label == 'B-nationality':
                            if len (nationality_words) > 0:
                                nationality_words.clear ()
                            nationality_words.append (word)
                        elif label == 'I-nationality':
                            nationality_words.append (word)
                        elif label == 'E-nationality':
                            if len (nationality_words) > 0:
                                nationality_words.append (word)
                                if person_data['person_basic_info']['nationality'] == '':
                                    person_data['person_basic_info']['nationality'] = ''.join (nationality_words)
                                    nationality_words.clear ()
                            else:
                                if person_data['person_basic_info']['nationality'] == '':
                                    person_data['person_basic_info']['nationality'] = word
                        # ---------------------------
                        elif label == 'B-school':
                            if len (school_words) > 0:
                                school_words.clear ()
                            school_words.append (word)
                        elif label == 'I-school':
                            school_words.append (word)
                        elif label == 'E-school':
                            if len (school_words) > 0:
                                school_words.append (word)
                                if person_data['person_basic_info']['school'] == '':
                                    person_data['person_basic_info']['school'] = ''.join (school_words)
                                    school_words.clear ()
                            else:
                                if person_data['person_basic_info']['school'] == '':
                                    person_data['person_basic_info']['school'] = word
                        # ---------------------------
                        elif label == 'B-sex':
                            if len (sex_words) > 0:
                                sex_words.clear ()
                            sex_words.append (word)
                        elif label == 'I-sex':
                            sex_words.append (word)
                        elif label == 'E-sex':
                            if len (school_words) > 0:
                                school_words.append (word)
                                if person_data['person_basic_info']['sex'] == '':
                                    sex_word = ''.join (school_words)
                                    if sex_word == '男' or sex_word == '先生':
                                        person_data['person_basic_info']['sex'] = '男'
                                    elif word == '女' or word == '女士':
                                        person_data['person_basic_info']['sex'] = '女'
                                    school_words.clear ()
                            else:
                                if person_data['person_basic_info']['sex'] == '':
                                    if word == '男' or word == '先生':
                                        person_data['person_basic_info']['sex'] = '男'
                                    elif word == '女' or word == '女士':
                                        person_data['person_basic_info']['sex'] = '女'

        return person_data

    #抽取简历信息
    # def batch_extract(self,resume_filepath_list:list,save_dic:str) :
    #     if len(resume_filepath_list)>0 and save_dic!='':
    #         #遍历所有文件
    #         for filepath in resume_filepath_list:
    #             #获取当前文件名
    #             current_filename=str(filepath).split('/')[-1]
    #             #处理成保存文件路径
    #             savefile_path = save_dic + '/' + current_filename
    #             #先创建新文件
    #             with open(savefile_path, 'w') as write_file:
    #                 write_file.close()
    #
    #             #遍历所有行
    #             reader=bigfile.get_file_content(filepath)
    #             line=reader.__next__()
    #             while line:
    #                 res=self._extract(line)#抽取简历信息元 返回一个简历类对象
    #                 if res!=None:
    #                     ResumeTool.save_reusme(res,savefile_path)#保存到文件中
    #
    #                 line = reader.__next__()
    #         return True
    #     else:
    #         print('简历文件或保存目录出错！')
    #         return False

    #单条简历抽取
    def single_extract(self,srcresume:str):
        return self._extract(srcresume)

if __name__ == '__main__':

    # srcresume='电光防爆科技股份有限公司|||施胜济|||施胜济先生，中国国籍，无永久境外居留权，1957年出生，身份证号码：33030219*******418，住所：浙江省温州市鹿城区水心街道水心桂组段将军桥路68号乳品厂。1976年-2003年就职于温州乳品罐厂，2004年-2006年在上海建桥国际贸易有限公司任总经理，2006年-2007年任朗诗德公司副总经理，2008年2月至今任公司物控部副总经理。资金主要来源于个人薪资收入、家庭多年积累及房产转让所得的收入。施胜济先生自1976年起至今工作三十余年，且曾有创办合伙企业乐清市三胜胶木塑料制品厂等其他收入来源，另外出售转让了上海、温州等地多处市值数百万房产，本人及家庭经过多年积累形成了一定积蓄。'
    # resume=Extractor().single_extract(srcresume)
    # resume.print_resume()
    # filename_list=os.listdir(config.TESTDATA_DIC)
    # filepath_list=[config.TESTDATA_DIC+'/'+filename for filename in filename_list]
    # Extractor().batch_extract(filepath_list,config.RESULTDATA_DIC)


    filenames = os.listdir (config.SRCDATA_DIC)
    filepaths = [config.SRCDATA_DIC + '/' + filename for filename in filenames]

    e = Extractor()

    resume_jsons = []
    count = 0

    for filepath in filepaths:
        with open(filepath,'r') as read_file:
            for line in read_file:
                resume=e.single_extract(line)
                if resume:

                    resume_dict=ResumeTool.resume_to_dict(resume)
                    resume_jsons.append (resume_dict.copy())
                    count+=1

                    if count>100:
                        mtool.insert_many('extractor','networks',resume_jsons)
                        resume_jsons.clear()
                        count=0

            read_file.close()

    if len(resume_jsons)>0:
        mtool.insert_many ('extractor', 'networks', resume_jsons)




