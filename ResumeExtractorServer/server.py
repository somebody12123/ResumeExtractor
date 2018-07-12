#!/usr/bin/python 
# -*- coding: utf-8 -*-

#智能简历信息元抽取服务器

import config
import keras
import gc
import json
import jieba
import socket
import struct
import time
import threading
import os
from script.core.extract import Extractor
from script.model.wordvec_model import WordVecModel
from script.model.sentencerec_model import SentenceRecModel
from script.model.wordrec_model import WordRecModel
from script.object.resume import ResumeTool

class Server(object):
    #属性
    wordvec_model=None#词向量模型
    sentencerec_model=None#句子识别模型
    wordrec_model=None#实体词识别模型

    server_socket:socket.socket=None#服务器
    ip='127.0.0.1'#ip地址
    port=10001#端口
    listen_num=1#同时监听数

    quit=False#用来标示退出程序

    #方法
    #构造方法
    def __init__(self):
        super().__init__()
        print('开始加载模型数据')
        print('开始加载第一层神经网络模型')
        self.sentencerec_model=SentenceRecModel().load_trained_model()
        print('加载第一层神经网络模型结束')
        print('开始加载第二层神经网络模型')
        self.wordrec_model=WordRecModel().load_trained_model()
        print('加载第二层神经网络模型结束')
        print('开始加载词向量模型')
        self.wordvec_model=WordVecModel().load_trained_wordvec_model()
        print('加载词向量模型结束')
        print('加载模型数据结束')
        print('开始加载分词词库')
        jieba.load_userdict(config.CORPUS_DIC+'/name.txt')
        print('加载分词词库结束')

        self.init_server_socket()
        print('开始监听客户端发起聊天')
        # threading.Thread(target=self.accept_client).start()

        self.accept_client()
        # while self.quit==False:
        #     content=input('输入quit退出：')
        #     if content=='quit':
        #         self.quit=True
        #     else:
        #         time.sleep(0.5)

    def init_server_socket(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen(self.listen_num)

    #接收客户端的连接
    def accept_client(self):
        while True:
            if self.quit:
                break

            if self.server_socket:
                client_socket,addr = self.server_socket.accept()
                print(addr, '连接服务器')
                self.recv(client_socket)
                print(client_socket.getpeername(),'断开连接')
                client_socket.close()
            else:
                print('server_socket没有初始化')

            time.sleep(0.1)

    #接收客户端的数据
    def recv(self,client_socket:socket.socket):
        data=client_socket.recv(1024)
        print(data)
        if data:
            msg=data.decode('utf-8')
            if msg=='1':
                print('处理单条简历')
                srcresume = self.recv_single_resume(client_socket)
                resume = self.deal_single_extract(srcresume)
                self.send_single_resume(client_socket, resume)
            elif msg=='0':
                print('处理批量简历')
                resume_filepath_list=self.recv_batch_resume(client_socket)
                self.deal_batch_extract(resume_filepath_list)
                self.send_batch_resume(client_socket)

    def recv_single_resume(self,client_socket:socket.socket):
        temp_resume_list = []
        while True:
            data = client_socket.recv(1024)
            if data:
                msg = data.decode('utf-8')
                temp_resume_list.append(msg)
                if msg[-1] == '$':  # '$'作为结尾符号
                    break
            else:
                print('与服务器的连接中断了')
                #bug
                break
        return ''.join(temp_resume_list)[:-1]

    def send_single_resume(self,client_socket:socket.socket,resume:str):

        if client_socket.sendall(bytes(resume+'$',encoding='utf-8'))==None:
            print('发送成功')
        else:
            print('发送失败')

    def recv_batch_resume(self,client_socket:socket.socket):
        resume_filepath_list=[]

        data = client_socket.recv(1024)
        if data:
            file_num = int(data.decode('utf-8'))
            while file_num > 0:
                data = client_socket.recv(1024)
                file_header = json.loads(data.decode('utf-8'))
                file_name = file_header['file_name']
                file_size = file_header['file_size']

                full_data = []
                current_size = 0
                while current_size < file_size:
                    data = client_socket.recv(1024)
                    full_data.append(data)
                    current_size += len(data)

                new_filepath=config.TESTDATA_DIC + '/' + file_name
                resume_filepath_list.append(new_filepath)
                with open(new_filepath, 'wb') as write_file:
                    for data in full_data:
                        write_file.write(data)
                    write_file.close()

                file_num -= 1

        return resume_filepath_list

    def send_batch_resume(self,client_socket:socket.socket):

        filename_list=os.listdir(config.RESULTDATA_DIC)
        resume_filepath_list=[config.RESULTDATA_DIC+'/'+filename for filename in filename_list]
        file_num = str(len(resume_filepath_list))
        client_socket.send(bytes(file_num, 'utf-8'))
        for resume_filepath in resume_filepath_list:
            with open(resume_filepath, 'rb') as read_file:
                content = read_file.read()
                read_file.close()

                file_header = {}
                file_header['file_name'] = str(resume_filepath).split('/')[-1]
                file_header['file_size'] = len(content)

                client_socket.send(json.dumps(file_header).encode('utf-8'))
                time.sleep(0.1)
                client_socket.sendall(content)

        filename_list = os.listdir(config.TESTDATA_DIC)
        filepath_list = [config.TESTDATA_DIC + '/' + filename for filename in filename_list]
        for filepath in filepath_list:
            os.remove(filepath)

        filename_list = os.listdir(config.RESULTDATA_DIC)
        filepath_list = [config.RESULTDATA_DIC + '/' + filename for filename in filename_list]
        for filepath in filepath_list:
            os.remove(filepath)

    #处理单条简历
    def deal_single_extract(self,resume:str):
        res=Extractor(self.wordvec_model,self.sentencerec_model,self.wordrec_model).single_extract(resume)
        return ResumeTool.resume_to_str(res)

    #处理多条简历
    def deal_batch_extract(self,resume_filepath_list:list,save_dic=config.RESULTDATA_DIC):
        return Extractor(self.wordvec_model,self.sentencerec_model,self.wordrec_model).batch_extract(resume_filepath_list,save_dic)

    #析构函数
    def __del__(self):
        del self.wordvec_model
        del self.sentencerec_model
        del self.wordrec_model
        gc.collect()


class MyServer(object):
    # 属性
    # wordvec_model = None  # 词向量模型
    # sentencerec_model = None  # 句子识别模型
    # wordrec_model = None  # 实体词识别模型
    extractor=None

    text_socket: socket.socket = None  # 服务器
    file_socket:socket.socket=None
    ip = '127.0.0.1'  # ip地址
    text_port = 10001  # 端口
    file_port=10002
    listen_num = 1  # 同时监听数

    # 方法
    # 构造方法
    def __init__(self):

        super().__init__()

        self.extractor=Extractor()

        self.init_server_socket()
        print('开始监听客户端发起聊天')
        text_thread=threading.Thread(target=self.accept_text_socket,daemon=True)
        text_thread.start()

        file_thread=threading.Thread(target=self.accept_file_socket,daemon=True)
        file_thread.start()

        while True:
            content=input('输入quit退出')
            if content=='quit':
                break
            time.sleep(0.1)

    #初始化socket
    def init_server_socket(self):
        self.text_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.text_socket.bind((self.ip, self.text_port))
        self.text_socket.listen(self.listen_num)

        self.file_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.file_socket.bind((self.ip, self.file_port))
        self.file_socket.listen(self.listen_num)

    #接受文本客户端socket的连接
    def accept_text_socket(self):
        while True:
            c_socket,addr= self.text_socket.accept()
            print(addr,'连接到处理单条简历服务器')
            self.handle_resume_text(c_socket)
            c_socket.close()
            time.sleep(0.1)

    #接收简历文本
    def recv_resume_text(self,c_socket:socket.socket):
        temp_resume_list = []
        while True:
            data = c_socket.recv(1024)
            if data:
                msg = data.decode('utf-8')
                temp_resume_list.append(msg)
                if msg[-1] == '$':  # '$'作为结尾符号
                    break
            else:
                print('accept text socket error')
                raise socket.error
        print(''.join(temp_resume_list)[:-1])
        return ''.join(temp_resume_list)[:-1]

    def send_resume_text(self,c_socket:socket.socket,text:str):
        if c_socket.sendall(bytes(text,encoding='utf-8'))==None:
            print('发送单条简历成功')
        else:
            print('发送单条简历失败')

    #处理简历文本
    def handle_resume_text(self,c_socket:socket.socket):
        srcresume=self.recv_resume_text(c_socket)
        # res = Extractor(self.wordvec_model, self.sentencerec_model, self.wordrec_model).single_extract(srcresume)
        res=self.extractor.single_extract(srcresume)
        text= ResumeTool.resume_to_str(res)
        self.send_resume_text(c_socket,text)

    #接收文件socket的连接
    def accept_file_socket(self):
        while True:
            c_socket,addr= self.file_socket.accept()
            print(addr,'连接到处理批量简历服务器')
            self.handle_resume_file(c_socket)
            c_socket.close()
            time.sleep(0.1)

    #处理简历文件
    def handle_resume_file(self,c_socket:socket.socket):
        self.recv_resume_file(c_socket)

        filename_list=os.listdir(config.TESTDATA_DIC)
        filepath_list=[config.TESTDATA_DIC+'/'+filename for filename in filename_list]
        # Extractor(self.wordvec_model, self.sentencerec_model, self.wordrec_model).batch_extract(filepath_list,config.RESULTDATA_DIC)
        self.extractor.batch_extract(filepath_list,config.RESULTDATA_DIC)
        self.send_resume_file(c_socket)

        filename_list = os.listdir(config.TESTDATA_DIC)
        filepath_list = [config.TESTDATA_DIC + '/' + filename for filename in filename_list]
        for filepath in filepath_list:
            os.remove(filepath)

        filename_list = os.listdir(config.RESULTDATA_DIC)
        filepath_list = [config.RESULTDATA_DIC + '/' + filename for filename in filename_list]
        for filepath in filepath_list:
            os.remove(filepath)

    #接收简历文件
    def recv_resume_file(self,c_socket:socket.socket):
        c_socket.send('you can send file'.encode('utf-8'))  # 发送 you can send file

        file_num = c_socket.recv(1024)  # 接收文件个数
        if file_num:
            print('要接收文件个数', file_num.decode('utf-8'))
            file_num = file_num.decode('utf-8')

            c_socket.send(bytes('recv file num %s' % file_num, encoding='utf-8'))

            file_num = int(file_num)

            while file_num > 0:
                file_head = c_socket.recv(1024)  # 接收文件头
                if file_head:
                    print('file_head',file_head)

                    file_header = json.loads(file_head.decode('utf-8'))
                    file_name = file_header['file_name']
                    file_size = file_header['file_size']

                    c_socket.send(
                        bytes('recv file header %s %s' % (file_name, str(file_size)), encoding='utf-8'))

                    full_data = []
                    recved_size = 0
                    while file_size - recved_size > 0:
                        if file_size - recved_size > 1024:
                            data = c_socket.recv(1024)
                            full_data.append(data)
                        else:
                            data = c_socket.recv(file_size - recved_size)
                            full_data.append(data)
                        recved_size += len(data)

                    # 接收完一个文件
                    # 写入文件
                    with open(config.TESTDATA_DIC + '/' + file_name, 'wb') as write_file:
                        for data in full_data:
                            write_file.write(data)
                        write_file.close()

                    # 发送接收成功
                    c_socket.send(bytes('recv file %s %s' % (file_name, str(file_size)), encoding='utf-8'))
                    print(file_name, '接收成功')

                    file_num -= 1

    #发送简历文件
    def send_resume_file(self,c_socket:socket.socket):
        filename_list=os.listdir(config.RESULTDATA_DIC)
        file_num = len(filename_list)
        # 发送要发送的文件个数
        c_socket.send(bytes(str(file_num), encoding='utf-8'))
        # 等待服务器接收'文件个数'
        msg = c_socket.recv(1024)
        if msg.decode('utf-8') == 'recv file num %s' % str(file_num):

            filename_list= [config.RESULTDATA_DIC+'/'+filename for filename in filename_list]

            for filename in filename_list:  # 绝对路径
                file_header = {}
                file_header['file_name'] = filename.split('/')[-1]
                file_header['file_size'] = os.path.getsize(filename)

                file_head_json = json.dumps(file_header).encode('utf-8')
                # 发送单个文件头
                c_socket.send(file_head_json)
                # 等待服务器接收'文件头'
                msg = c_socket.recv(1024)
                if msg.decode('utf-8') == 'recv file header %s %s' % (
                        file_header['file_name'], str(file_header['file_size'])):

                    read_file = open(filename, 'rb')
                    content = read_file.read()
                    read_file.close()
                    # 发送文件
                    c_socket.sendall(content)
                    # 等待服务器接收完文件
                    msg = c_socket.recv(1024)
                    if msg.decode('utf-8') == 'recv file %s %s' % (
                            file_header['file_name'], str(file_header['file_size'])):
                        print(file_header['file_name'], '发送成功')

    # 析构函数
    def __del__(self):

        gc.collect()

if __name__ == '__main__':
    keras.backend.clear_session()
    MyServer()
    # print('开始加载模型数据')
    # print('开始加载第一层神经网络模型')
    # sentencerec_model = SentenceRecModel().load_trained_model()
    # print('加载第一层神经网络模型结束')
    # print('开始加载第二层神经网络模型')
    # wordrec_model = WordRecModel().load_trained_model()
    # print('加载第二层神经网络模型结束')
    # print('开始加载词向量模型')
    # wordvec_model = WordVecModel().load_trained_wordvec_model()
    # print('加载词向量模型结束')
    # print('加载模型数据结束')
    # print('开始加载分词词库')
    # jieba.load_userdict(config.CORPUS_DIC + '/name.txt')
    # print('加载分词词库结束')

    # srcresume='﻿王泉庚,男,汉族,1972年10月出生,中国籍,无境外永久居留权,毕业于中欧国际工商学院工商管理硕士,巴黎国际时装艺术学院艺术管理专业,硕士学位。1995年11月至2013年11月,就职于上海美特斯邦威服饰股份有限公司,历任副总经理、董事兼副总裁;2013年12月至2014年2月,离职调整;2014年3月至今,就职于时朗企业发展(上海)有限公司,任执行董事兼总经理;2014年8月至2015年5月,就职于好孩子(中国)商贸有限公司,任执行董事兼总经理;2015年4月至今,任南京我乐家居股份有限公司独立董事;2016年4月至今,任迅驰时尚(上海)科技股份有限公司董事。'
    # res = Extractor(wordvec_model, sentencerec_model, wordrec_model).single_extract(srcresume)
    # ResumeTool.print_resume(res)









