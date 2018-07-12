#!/usr/bin/python 
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import QMainWindow,QMenuBar,QApplication ,QDesktopWidget
from script.gui.mywidget import MainQWidget,SingleExtractQWidget,BatchExtractQWidget

class MyWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        #创建action

        #设置菜单栏
        menubar=QMenuBar()

        menu=menubar.addMenu('菜单')

        batch_extract_action=menu.addAction('处理批量简历界面')
        batch_extract_action.triggered.connect(self._to_batch_extract)#绑定跳转事件

        single_extract_action=menu.addAction('处理单条简历界面')
        single_extract_action.triggered.connect(self._to_single_extact)#绑定跳转事件

        self.setMenuBar(menubar)

        self.setCentralWidget(MainQWidget(self))#设置主要组件为MainQWidget
        self.show()

    #事件函数
    #跳转到批量
    def _to_batch_extract(self):
        self.setCentralWidget(BatchExtractQWidget(self))

    def _to_single_extact(self):
        self.setCentralWidget(SingleExtractQWidget(self))

    # 窗口居中
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


if __name__ == '__main__':
    app=QApplication(sys.argv)

    mw=MyWindow()

    sys.exit(app.exec_())