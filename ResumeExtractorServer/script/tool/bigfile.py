#_*_coding:utf-8_*_

#读取所有文件内容 通过yield每次返回一行内容
def get_file_content(file_path:str) :
    with open(file_path,'r') as read_file:#以读的方式打开文件
        for line in read_file:
            yield line#返回每行内容

        read_file.close()
        yield None