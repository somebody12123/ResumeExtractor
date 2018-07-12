#!/usr/bin/python 
# -*- coding: utf-8 -*-

#简历信息类
class Resume:
    def __init__(self):
        self._name=''#名字
        self._sex=''#性别
        self._born=''#出生
        self._nationality=''#国籍
        self._edu=''#教育
        self._pexps=[]#过去经验 过去时间 过去地点 过去职位
        self._cexps=[]#现在经验 现在时间 现在地点 现在职位
        self._uexps=[]

    def set_name(self,name:str):
        self._name=name
    def get_name(self):
        return self._name

    def set_sex(self,sex:str):
        self._sex=sex
    def get_sex(self):
        return self._sex

    def set_born(self,born:str):
        self._born=born
    def get_born(self):
        return self._born

    def set_nationality(self,nationality:str):
        self._nationality=nationality

    def get_nationality(self):
        return self._nationality

    def set_edu(self,edu:str):
        self._edu=edu

    def get_edu(self):
        return self._edu

    def add_pexp(self,pexp:dict):
        self._pexps.append(pexp)

    def get_pexps(self):
        return self._pexps

    def add_cexp(self,cexp:dict):
        self._cexps.append(cexp)

    def get_cexps(self):
        return self._cexps

    def get_uexps(self):
        return self._uexps

    def add_uexp(self,uexp:dict):
        self._uexps.append(uexp)
    pass #Resume class end

class ResumeTool():
    @staticmethod
    def print_resume(resume:Resume):
        print('--------------start---------------')
        print('姓名：', resume.get_name())
        print('性别：', resume.get_sex())
        print('出生时间：', resume.get_born())
        print('国籍：', resume.get_nationality())
        print('学历：', resume.get_edu())
        print('过去经验：')
        for pexp in resume.get_pexps():
            print('      时间：', pexp['time'])
            print('      地点：', pexp['place'])
            print('      职位：', '、'.join(pexp['job']))
            print()
        print('现在经验：')
        for cexp in resume.get_cexps():
            print('      时间：', cexp['time'])
            print('      地点：', cexp['place'])
            print('      职位：', '、'.join(cexp['job']))
            print()
        # print('不确定时间经验：')
        # for uexp in resume.get_uexps():
        #     print('      地点：', uexp['place'])
        #     print('      职位：', '、'.join(uexp['job']))
        #     print()
        print('---------------end----------------')

    @staticmethod
    def save_reusme(resume: Resume, path: str):
        with open(path,'a',encoding='utf-8') as write_file:
            write_file.write('--------------------start-----------------------')
            write_file.write('\n')
            write_file.write('姓名：'+resume.get_name())
            write_file.write('\n')
            write_file.write('性别：'+resume.get_sex())
            write_file.write('\n')
            write_file.write('出生时间：'+resume.get_born())
            write_file.write('\n')
            write_file.write('国籍：'+resume.get_nationality())
            write_file.write('\n')
            write_file.write('学历：'+resume.get_edu())
            write_file.write('\n')
            write_file.write('过去经验：')
            write_file.write('\n')
            for pexp in resume.get_pexps():
                write_file.write('      时间：'+pexp['time'])
                write_file.write('\n')
                write_file.write('      地点：'+pexp['place'])
                write_file.write('\n')
                write_file.write('      职位：'+'、'.join(pexp['job']))
                write_file.write('\n')
                write_file.write('\n')
            write_file.write('现在经验：')
            write_file.write('\n')
            for cexp in resume.get_cexps():
                write_file.write('      时间：'+cexp['time'])
                write_file.write('\n')
                write_file.write('      地点：'+cexp['place'])
                write_file.write('\n')
                write_file.write('      职位：'+'、'.join(cexp['job']))
                write_file.write('\n')
                write_file.write('\n')
            # write_file.write('不确定时间经验：')
            # write_file.write('\n')
            # for uexp in resume.get_uexps():
            #     write_file.write('      地点：' + uexp['place'])
            #     write_file.write('\n')
            #     write_file.write('      职位：' + '、'.join(uexp['job']))
            #     write_file.write('\n')
            #     write_file.write('\n')
            write_file.write('----------------------end------------------------')
            write_file.write('\n')
            write_file.write('\n')
            write_file.write('\n')
            write_file.close()

    @staticmethod
    def resume_to_str(resume:Resume):
        resume_msg_list=[]
        resume_msg_list.append('姓名：'+resume.get_name())
        resume_msg_list.append('性别：'+ resume.get_sex())
        resume_msg_list.append('出生时间：'+ resume.get_born())
        resume_msg_list.append('国籍：'+ resume.get_nationality())
        resume_msg_list.append('学历：'+ resume.get_edu())
        resume_msg_list.append('过去经验：')
        for pexp in resume.get_pexps():
            resume_msg_list.append('      时间：'+ pexp['time'])
            resume_msg_list.append('      地点：'+ pexp['place'])
            resume_msg_list.append('      职位：'+ '、'.join(pexp['job']))
            resume_msg_list.append('\n')
        resume_msg_list.append('现在经验：')
        for cexp in resume.get_cexps():
            resume_msg_list.append('      时间：' + cexp['time'])
            resume_msg_list.append('      地点：' + cexp['place'])
            resume_msg_list.append('      职位：' + '、'.join(cexp['job']))
            resume_msg_list.append('\n')

        return '\n'.join(resume_msg_list)

    @staticmethod
    def resume_to_dict(resume:Resume):
        resume_dic={}
        basic_info=resume_dic['person_basic_info']={}
        basic_info['name']=resume.get_name()
        basic_info['birth']=resume.get_born()
        basic_info['sex']=resume.get_sex()
        basic_info['nationality']=resume.get_nationality()
        basic_info['edu']=resume.get_edu()

        resume_dic['﻿person_curwork_info'] = resume.get_cexps()
        resume_dic['﻿person_prework_info'] = resume.get_pexps ()

        return resume_dic


    pass #ResumeTool class end


