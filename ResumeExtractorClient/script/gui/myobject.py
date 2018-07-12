# #!/usr/bin/python
# # -*- coding: utf-8 -*-
#

import config
import json
import socket
import time
import os
from PyQt5.QtCore import QObject,pyqtSignal

class ClientObject(QObject):
    single_extract_finished = pyqtSignal(str)
    batch_extract_finished=pyqtSignal()

    text_socket: socket.socket = None
    file_socket:socket.socket=None
    #server_ip = '127.0.0.1'
    server_ip='119.23.44.138'
    text_port = 10001
    file_port=10002

    def __init__(self,srcresume:str=None,resume_filepath_list:list=None,save_dic:str=None):
        super().__init__()
        self.srcresume=srcresume
        self.resume_filepath_list=resume_filepath_list
        self.save_dic=save_dic

    def single_extract(self):
        self.text_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.text_socket.connect((self.server_ip,self.text_port))
        print('连接处理单条简历服务器成功')
        self.send_resume_text(self.srcresume)
        resume=self.recv_resume_text()

        self.text_socket.close()

        self.single_extract_finished.emit(resume)

    def batch_extract(self):
        self.file_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.file_socket.connect((self.server_ip, self.file_port))
        print('连接处理批量简历服务器成功')
        self.send_resume_file(self.resume_filepath_list)
        self.recv_resume_file(self.save_dic)

        self.file_socket.close()

        self.batch_extract_finished.emit()

    #发送单条简历给服务器
    def send_resume_text(self,srcresume:str):
        if self.text_socket.sendall(bytes(srcresume+'$',encoding='utf-8'))==None:
            print('发送成功')
        else:
            print('send resume text error')

    #接收单条简历
    def recv_resume_text(self):
        temp_resume_list=[]
        while True:
            data=self.text_socket.recv(1024)
            if data:
                msg=data.decode('utf-8')
                temp_resume_list.append(msg)
                if msg[-1]=='$':#'$'作为结尾符号
                    break
            else:
                # print('recv resume text error')
                break
        return ''.join(temp_resume_list)[:-1]

    #发送批量简历文件给服务器
    def send_resume_file(self,resume_filepath_list:list):

        # 等待服务器端准备好
        msg = self.file_socket.recv(1024)
        if msg.decode('utf-8') == 'you can send file':
            file_num=len(resume_filepath_list)
            # 发送要发送的文件个数
            self.file_socket.send(bytes(str(file_num), encoding='utf-8'))
            # 等待服务器接收'文件个数'
            msg = self.file_socket.recv(1024)
            if msg.decode('utf-8') == 'recv file num %s' % str(file_num):

                # filename_list = os.listdir(config.PROJECT_ROOT + '/file/filetranslation/client/')

                for filename in resume_filepath_list:#绝对路径
                    file_header = {}
                    file_header['file_name'] = filename.split('/')[-1]
                    file_header['file_size'] = os.path.getsize(filename)

                    file_head_json = json.dumps(file_header).encode('utf-8')
                    # 发送单个文件头
                    self.file_socket.send(file_head_json)
                    # 等待服务器接收'文件头'
                    msg = self.file_socket.recv(1024)
                    if msg.decode('utf-8') == 'recv file header %s %s' % (
                    file_header['file_name'], str(file_header['file_size'])):

                        read_file = open(filename, 'rb')
                        content = read_file.read()
                        read_file.close()
                        # 发送文件
                        self.file_socket.sendall(content)
                        # 等待服务器接收完文件
                        msg = self.file_socket.recv(1024)
                        if msg.decode('utf-8') == 'recv file %s %s' % (
                        file_header['file_name'], str(file_header['file_size'])):
                            print(file_header['file_name'], '发送成功')


    #接收批量简历文件并保存
    def recv_resume_file(self,save_dic:str):
        # self.file_socket.send('you can send file'.encode('utf-8'))  # 发送 you can send file

        file_num = self.file_socket.recv(1024)  # 接收文件个数
        if file_num:
            print('要接收文件个数', file_num.decode('utf-8'))
            file_num = file_num.decode('utf-8')

            self.file_socket.send(bytes('recv file num %s' % file_num, encoding='utf-8'))

            file_num = int(file_num)

            while file_num > 0:
                file_head = self.file_socket.recv(1024)  # 接收文件头
                if file_head:

                    file_header = json.loads(file_head.decode('utf-8'))
                    file_name = file_header['file_name']
                    file_size = file_header['file_size']

                    self.file_socket.send(bytes('recv file header %s %s' % (file_name, str(file_size)), encoding='utf-8'))

                    full_data = []
                    recved_size = 0
                    while file_size - recved_size > 0:
                        if file_size - recved_size > 1024:
                            data = self.file_socket.recv(1024)
                            full_data.append(data)
                        else:
                            data = self.file_socket.recv(file_size - recved_size)
                            full_data.append(data)
                        recved_size += len(data)

                    # 接收完一个文件
                    # 写入文件
                    with open(save_dic +'/'+ file_name, 'wb') as write_file:
                        for data in full_data:
                            write_file.write(data)
                        write_file.close()

                    # 发送接收成功
                    self.file_socket.send(bytes('recv file %s %s' % (file_name, str(file_size)), encoding='utf-8'))
                    print(file_name, '接收成功')

                    file_num -= 1
    pass

