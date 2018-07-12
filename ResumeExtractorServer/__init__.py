#!/usr/bin/python 
# -*- coding: utf-8 -*-

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import config
from script.core.extract import Extractor
from script.database import mongotool as mtool

if __name__ == '__main__':
    filenames = os.listdir (config.SRCDATA_DIC)
    filepaths = [config.SRCDATA_DIC + '/' + filename for filename in filenames]

    e = Extractor ()

    resume_jsons = []
    count = 0

    for filepath in filepaths:
        print(filepath)
        with open (filepath, 'r') as read_file:
            for line in read_file:
                resume = e.single_extract (line)
                if resume:
                    print(resume)
                    resume_jsons.append (resume.copy ())
                    count += 1

                    if count > 10:
                        mtool.insert_many ('extractor', 'network', resume_jsons)
                        resume_jsons.clear ()
                        count = 0

            read_file.close ()

    if len (resume_jsons) > 0:
        mtool.insert_many ('extractor', 'network', resume_jsons)
