#!/usr/bin/python 
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QWidget,QLabel,QApplication,QVBoxLayout,QTextEdit,QPushButton,
                             QHBoxLayout,QLineEdit,QCheckBox,QMainWindow,QFileDialog,QRadioButton,QMessageBox,QProgressDialog)
from PyQt5.QtCore import QThread
import config
from script.gui.myobject import ClientObject

#单条简历信息元抽取组件
class SingleExtractQWidget(QWidget):

    def __init__(self,mainwindow:QMainWindow):
        super().__init__()

        self.mainwindow=mainwindow
        self.thread=None
        self.init_ui()

    def init_ui(self):
        '''
        添加简历标签 输入框

        添加按钮

        添加格式化简历信息标签 输入框

        '''

        #添加组件并绑定事件
        srcresume_label=QLabel('原始简历')

        self.srcresume_edit=QTextEdit()
        self.srcresume_edit.textChanged.connect(self._revise_textedit)

        extract_button=QPushButton('处理简历')
        extract_button.clicked.connect(self._single_extract)

        formatresume_label=QLabel('格式化简历信息')

        self.formatresume_edit=QTextEdit()
        self.formatresume_edit.setReadOnly(True)#只读，不能输入

        #设置布局
        vbox1=QVBoxLayout()
        vbox1.addWidget(srcresume_label)
        vbox1.addWidget(self.srcresume_edit)

        vbox2=QVBoxLayout()
        vbox2.addWidget(formatresume_label)
        vbox2.addWidget(self.formatresume_edit)

        hbox=QHBoxLayout()
        hbox.addLayout(vbox1)
        hbox.addWidget(extract_button)
        hbox.addLayout(vbox2)

        self.setLayout(hbox)

        #设置主窗体属性
        self.mainwindow.setMinimumSize(700,700)
        self.mainwindow.resize(700, 700)
        self.mainwindow.setWindowTitle('处理单条简历界面')
        self.mainwindow.center()

        #设置组件显示
        self.show()

    def _revise_textedit(self):
        text=self.srcresume_edit.toPlainText()
        # text=text.strip().replace('\n','')
        # line_length=24
        # lines=[]
        #
        # start = 0
        # end = start + line_length
        # while True:
        #     if len(text)>line_length:
        #         lines.append(text[start:end])
        #         text = text[end:]
        #     else:
        #         lines.append(text[start:])
        #         break
        #
        # print('\n'.join(lines))
        # text='\n'.join(lines)
        self.srcresume_edit.textChanged.disconnect(self._revise_textedit)
        self.srcresume_edit.setText(text)
        self.srcresume_edit.textChanged.connect(self._revise_textedit)

    #单条简历信息抽取
    def _single_extract(self):

        text=self.srcresume_edit.toPlainText()
        if self.thread!=None and self.thread.isRunning():
            QMessageBox.about(self, 'message', '正在处理简历中，请稍等！')
            return
        if text!='':
            #发送给服务器端处理数据
            self.thread=QThread()
            self.object_client=ClientObject(srcresume=text)

            self.object_client.single_extract_finished.connect(self._show_resume_result)
            self.object_client.moveToThread(self.thread)

            self.thread.started.connect(self.object_client.single_extract)
            self.thread.start()

            print('发送给服务器端处理数据')
            pass

        else:
            QMessageBox.about(self,'message','请输入一条简历！')

    #显示简历结果
    def _show_resume_result(self,resume:str):
        self.formatresume_edit.setText(resume)
        self.thread.quit()
    pass #SingleExtractQWidget class end


#批量抽取简历信息元组件
class BatchExtractQWidget(QWidget):
    def __init__(self,mainwindow:QMainWindow):
        super().__init__()

        self.mainwindow=mainwindow
        self.thread=None
        self.init_ui()

    def init_ui(self):
        '''
        添加简历文件标签

        添加简历文件展示框

        添加选择文件按钮

        添加保存路径标签
        添加保存路径展示框
        添加修改保存路径窗口
        '''
        #添加组件并绑定事件
        srcresume_label=QLabel('简历文件')

        self.srcresume_edit = QTextEdit()
        self.srcresume_edit.setReadOnly(True)

        resume_choose_button=QPushButton('选择简历文件')
        resume_choose_button.clicked.connect(self._choose_extract_file)

        save_label=QLabel('处理好的简历文件保存路径：')
        self.save_edit=QLineEdit()
        self.save_edit.setReadOnly(True)

        change_save_button=QPushButton('选择保存路径')
        change_save_button.clicked.connect(self._choose_save_dic)

        batch_extract_button=QPushButton('   批量抽取    ')
        batch_extract_button.clicked.connect(self._batch_extract)

        #设置布局
        hbox=QHBoxLayout()
        hbox.addStretch(10)
        hbox.addWidget(resume_choose_button)

        hbox1=QHBoxLayout()
        hbox1.addWidget(save_label)
        hbox1.addWidget(self.save_edit)
        hbox1.addWidget(change_save_button)

        hbox2=QHBoxLayout()
        hbox2.addStretch(10)
        hbox2.addWidget(batch_extract_button)

        vbox=QVBoxLayout()
        vbox.addWidget(srcresume_label)
        vbox.addWidget(self.srcresume_edit)
        vbox.addLayout(hbox)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)

        self.setLayout(vbox)

        #设置主窗体属性
        self.mainwindow.setMinimumSize(700, 700)
        self.mainwindow.resize(700, 700)
        self.mainwindow.setWindowTitle('处理批量简历界面')
        self.mainwindow.center()
        #显示组件
        self.show()

    #选择要抽取的文件
    def _choose_extract_file(self):
        #选择文件
        file_names=QFileDialog.getOpenFileNames(self,'Open Files',config.TESTDATA_DIC)
        #处理文件名
        file_name_list=[file_name for file_name in file_names[0]]
        text='\n'.join(file_name_list)
        #显示到srcresume_edit上面
        self.srcresume_edit.setText(text)

    #选择要保存的文件路径
    def _choose_save_dic(self):
        #选择文件夹
        dic_name=QFileDialog.getExistingDirectory(self,'Change Save Dic',config.RESULTDATA_DIC)
        #显示到save_edit上面
        self.save_edit.setText(str(dic_name))

    #批量抽取简历信息
    def _batch_extract(self):
        if self.thread!=None and self.thread.isRunning():
            QMessageBox.about(self, 'message', '正在处理简历中，请稍等！')
            return

        file_names=str(self.srcresume_edit.toPlainText())
        save_dic=str(self.save_edit.text())

        if file_names=='' and save_dic=='':#都没有内容
            QMessageBox.about(self, 'message', '请选择要处理的简历文件和保存路径！')

        elif file_names=='':
            QMessageBox.about(self,'message','请选择处理的简历文件！')

        elif save_dic=='':
            QMessageBox.about(self, 'message', '请选择保存路径！')

        elif file_names!='' and save_dic!='':
            #将所有文件发送给服务器端
            self.thread = QThread()
            self.object_client = ClientObject(resume_filepath_list=file_names.split('\n'),save_dic=save_dic)

            self.object_client.batch_extract_finished.connect(self._batch_extract_finish)
            self.object_client.moveToThread(self.thread)

            self.thread.started.connect(self.object_client.batch_extract)
            self.thread.start()
            QMessageBox.about(self, 'message', '正在处理简历中，请稍等！')
            pass

    #显示弹出框信息
    def _batch_extract_finish(self):
        QMessageBox.about(self, 'message', '处理批量简历完成！')
        self.thread.quit()

    pass #BatchExtractQWidget class end

#训练模型组件
# class TrainModelQWidget(QWidget):
#     def __init__(self,mainwindow:QMainWindow):
#         super().__init__()
#
#         self.mainwindow=mainwindow
#         self.init_ui()
#
#     def init_ui(self):
#         '''
#         添加分词词库标签 勾选
#         添加词向量模型标签 勾选
#         添加第一层神经网络模型标签 勾选
#         添加第二层神经网络模型标签 勾选
#
#         添加获取分词词库按钮
#         添加训练词向量模型按钮
#         添加训练第一层神经网络模型按钮
#         添加训练第二层神经网络模型按钮
#
#         '''
#         #添加组件并绑定事件
#
#         self.split_check=QCheckBox('分词词库')
#         self.split_check.setEnabled(False)
#         if 'totalpart.txt' in os.listdir(config.PREDATA_DIC):
#             self.split_check.toggle()
#
#         split_button=QPushButton('获取分词词库')
#         split_button.clicked.connect(self._splitword)
#
#         self.wordvec_check=QCheckBox('词向量模型')
#         self.wordvec_check.setEnabled(False)
#         filename_list=os.listdir(config.MODEL_DIC)
#         if 'word_vector.model' in filename_list and 'word_vector.model.trainables.syn1neg.npy' in filename_list \
#             and 'word_vector.model.wv.vectors.npy' in filename_list:
#             self.wordvec_check.toggle()
#
#         wordvec_button= QPushButton('训练词向量模型')
#         wordvec_button.clicked.connect(self._train_wordvec_model)
#
#         self.sentencerec_check=QCheckBox('第一层神经网络模型')
#         self.sentencerec_check.setEnabled(False)
#         if 'sentence_model' in os.listdir(config.MODEL_DIC):
#             self.sentencerec_check.toggle()
#
#         sentencerec_button=QPushButton('训练第一层神经网络模型')
#         sentencerec_button.clicked.connect(self._train_sentencerec_model)
#
#         self.wordrec_check=QCheckBox('第二层神经网络模型')
#         self.wordrec_check.setEnabled(False)
#         if 'ner_model' in os.listdir(config.MODEL_DIC):
#             self.wordrec_check.toggle()
#
#         wordrec_button = QPushButton('训练第二层神经网络模型')
#         wordrec_button.clicked.connect(self._train_wordrec_model)
#
#
#         #设置布局
#         vbox1=QVBoxLayout()
#         vbox1.addWidget(self.split_check)
#         vbox1.addWidget(self.wordvec_check)
#         vbox1.addWidget(self.sentencerec_check)
#         vbox1.addWidget(self.wordrec_check)
#
#         vbox2=QVBoxLayout()
#         vbox2.addWidget(split_button)
#         vbox2.addWidget(wordvec_button)
#         vbox2.addWidget(sentencerec_button)
#         vbox2.addWidget(wordrec_button)
#
#         hbox=QHBoxLayout()
#         hbox.addLayout(vbox1)
#         hbox.addStretch(10)
#         hbox.addLayout(vbox2)
#
#         self.setLayout(hbox)
#
#         #设置主窗体属性
#         self.mainwindow.setMinimumSize(400, 400)
#         self.mainwindow.resize(400, 400)
#         self.mainwindow.setWindowTitle('训练模型界面')
#         self.mainwindow.center()
#
#         #显示组件
#         self.show()
#
#     #action function
#
#     #分词
#     def _splitword(self):
#         print('开始分词')
#         if self.split_check.isChecked()==False:
#             self.thread=QThread()
#             self.object_splitword=SplitWordObject()
#
#             self.object_splitword.finished.connect(self._toggle_split_check)
#             self.object_splitword.moveToThread(self.thread)
#
#             self.thread.started.connect(self.object_splitword.splitword)
#             self.thread.start()
#
#             pass
#         else:
#             reply=QMessageBox().question(self,'message','确定重新分词?',QMessageBox.Yes|QMessageBox.No,
#                                          QMessageBox.No)
#             if reply==QMessageBox.Yes:
#                 self.split_check.hide()
#                 self.split_check.toggle()
#                 self.split_check.show()
#                 #分词
#                 #test
#                 self.thread = QThread()
#                 self.object_splitword = SplitWordObject()
#
#                 self.object_splitword.finished.connect(self._toggle_split_check)
#                 self.object_splitword.moveToThread(self.thread)
#
#                 self.thread.started.connect(self.object_splitword.splitword)
#                 self.thread.start()
#                 pass
#             pass
#         print('分词结束')
#
#     #训练词向量模型
#     def _train_wordvec_model(self):
#         print('开始训练词向量模型')
#         if self.wordvec_check.isChecked()==False:
#             self.thread = QThread()
#             self.object_train_wordvec_model = TrainWordVecModelObject()
#
#             self.object_train_wordvec_model.finished.connect(self._toggle_wordvec_check)
#             self.object_train_wordvec_model.moveToThread(self.thread)
#
#             self.thread.started.connect(self.object_train_wordvec_model.train_wordvec_model)
#             self.thread.start()
#
#             pass
#         else:
#             reply = QMessageBox().question(self, 'message', '确定重新训练词向量模型?', QMessageBox.Yes | QMessageBox.No,
#                                            QMessageBox.No)
#             if reply==QMessageBox.Yes:
#                 #判断是否分词了
#                 if self.split_check.isChecked()==False:
#                     QMessageBox().about(self,'message','训练词向量模型要先分词！')
#                     pass
#                 else:
#                     self.wordvec_check.hide()
#                     self.wordvec_check.toggle()
#                     self.wordvec_check.show()
#                     # 训练词向量模型
#                     # test
#                     self.thread = QThread()
#                     self.object_train_wordvec_model = TrainWordVecModelObject()
#
#                     self.object_train_wordvec_model.finished.connect(self._toggle_wordvec_check)
#                     self.object_train_wordvec_model.moveToThread(self.thread)
#
#                     self.thread.started.connect(self.object_train_wordvec_model.train_wordvec_model)
#                     self.thread.start()
#                     pass
#             pass
#
#
#     #训练句子识别模型
#     def _train_sentencerec_model(self):
#         print('开始训练第一层神经网络模型')
#         if self.sentencerec_check.isChecked()==False:
#             self.thread = QThread()
#             self.object_train_sentencerec_model = TrainSentenceRecModelObject()
#
#             self.object_train_sentencerec_model.finished.connect(self._toggle_sentencerec_check)
#             self.object_train_sentencerec_model.moveToThread(self.thread)
#
#             self.thread.started.connect(self.object_train_sentencerec_model.train_sentencerec_model)
#             self.thread.start()
#             pass
#         else:
#             reply = QMessageBox().question(self, 'message', '确定重新训练第一层神经网络模型?', QMessageBox.Yes | QMessageBox.No,
#                                            QMessageBox.No)
#             if reply == QMessageBox.Yes:
#                 if self.wordvec_check.isChecked()==False:
#                     QMessageBox().about(self, 'message', '训练第一层神经网络模型要先训练词向量模型！')
#                     pass
#                 else:
#                     self.sentencerec_check.hide()
#                     self.sentencerec_check.toggle()
#                     self.sentencerec_check.show()
#                     # 训练第一层神经网络模型
#                     # test
#                     self.thread = QThread()
#                     self.object_train_sentencerec_model = TrainSentenceRecModelObject()
#
#                     self.object_train_sentencerec_model.finished.connect(self._toggle_sentencerec_check)
#                     self.object_train_sentencerec_model.moveToThread(self.thread)
#
#                     self.thread.started.connect(self.object_train_sentencerec_model.train_sentencerec_model)
#                     self.thread.start()
#                     pass
#             pass
#
#     #训练实体词识别模型
#     def _train_wordrec_model(self):
#         print('开始训练第二层神经网络模型')
#         if self.wordrec_check.isChecked()==False:
#             self.thread = QThread()
#             self.object_train_wordrec_model = TrainWordRecModelObject()
#
#             self.object_train_wordrec_model.finished.connect(self._toggle_wordrec_check)
#             self.object_train_wordrec_model.moveToThread(self.thread)
#
#             self.thread.started.connect(self.object_train_wordrec_model.train_wordrec_model)
#             self.thread.start()
#             pass
#         else:
#             reply = QMessageBox().question(self, 'message', '确定重新训练第二层神经网络模型?', QMessageBox.Yes | QMessageBox.No,
#                                            QMessageBox.No)
#             if reply == QMessageBox.Yes:
#                 if self.wordvec_check.isChecked()==False:
#                     QMessageBox().about(self, 'message', '训练第二层神经网络模型要先训练词向量模型！')
#                     pass
#                 else:
#                     self.wordrec_check.hide()
#                     self.wordrec_check.toggle()
#                     self.wordrec_check.show()
#                     #训练第二层神经网络模型
#                     # test
#                     self.thread = QThread()
#                     self.object_train_wordrec_model = TrainWordRecModelObject()
#
#                     self.object_train_wordrec_model.finished.connect(self._toggle_wordrec_check)
#                     self.object_train_wordrec_model.moveToThread(self.thread)
#
#                     self.thread.started.connect(self.object_train_wordrec_model.train_wordrec_model)
#                     self.thread.start()
#                     pass
#             pass
#
#     #让用户等待 分词结束
#     def _toggle_split_check(self):
#         self.split_check.hide()
#         self.split_check.toggle()
#         self.split_check.show()
#
#         self.thread.quit()
#         pass
#
#     #让用户等待 训练词向量模型结束
#     def _toggle_wordvec_check(self):
#         self.wordvec_check.hide()
#         self.wordvec_check.toggle()
#         self.wordvec_check.show()
#
#         self.thread.quit()
#         pass
#
#     #让用户等待 训练第一层神经网络模型结束
#     def _toggle_sentencerec_check(self):
#         self.sentencerec_check.hide()
#         self.sentencerec_check.toggle()
#         self.sentencerec_check.show()
#
#         self.thread.quit()
#         pass
#
#     #让用户等待 训练第二层神经网络模型结束
#     def _toggle_wordrec_check(self):
#         self.wordrec_check.hide()
#         self.wordrec_check.toggle()
#         self.wordrec_check.show()
#
#         self.thread.quit()
#         pass
# #TrainModelQWidget class end

class MainQWidget(QWidget):
    def __init__(self,mainwindow:QMainWindow):
        super().__init__()

        self.mainwindow=mainwindow#赋值主窗口

        self.init_ui()

    def init_ui(self):
        #创建按键并绑定事件

        batch_extract_button=QPushButton('进入处理批量简历界面')
        batch_extract_button.clicked.connect(self._to_batch_extract)

        single_extract_button=QPushButton('进入处理单条简历界面')
        single_extract_button.clicked.connect(self._to_single_extact)

        #设置布局
        vbox=QVBoxLayout()
        vbox.addWidget(batch_extract_button)
        vbox.addWidget(single_extract_button)

        hbox=QHBoxLayout()
        hbox.addStretch(10)
        hbox.addLayout(vbox)
        hbox.addStretch(10)

        self.setLayout(hbox)

        #设置主窗体的属性
        self.mainwindow.setMinimumSize(300, 300)
        self.mainwindow.resize(300, 300)
        self.mainwindow.setWindowTitle('智能简历信息元抽取主界面')
        self.mainwindow.center()
        #显示组件
        self.show()

    # action function

    def _to_batch_extract(self):
        self.mainwindow.setCentralWidget(BatchExtractQWidget(self.mainwindow))

    def _to_single_extact(self):
        self.mainwindow.setCentralWidget(SingleExtractQWidget(self.mainwindow))


