#!/usr/bin/python 
# -*- coding: utf-8 -*-

if __name__ == '__main__':

    import sys
    from PyQt5.QtWidgets import QApplication
    from script.gui.mywindow import MyWindow

    app = QApplication(sys.argv)

    mw = MyWindow()

    sys.exit(app.exec_())