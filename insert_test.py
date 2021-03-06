#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
from random import random
from math import ceil
from datetime import datetime, timedelta
import operator
import time
from operator import itemgetter, attrgetter
from kll import KLL
from kll import Element

if __name__ == '__main__':
    # '''
    # import argparse
    # parser = argparse.ArgumentParser()
    # parser.add_argument('-k', type=int, default=128,
    #                     help='''controls the number of elements in the sketch which is
    #                     at most 3k+log2(n). n is the length of the stream.''')
    # parser.add_argument('-t', type=str, choices=["string","int","float"], default='string',
    #                     help='defines the type of stream items, default="string".')
    # args = parser.parse_args()
    #
    # k = args.k if args.k > 0 else 128
    # '''
    # 初始化 k 值
    # 32 64 128 256
    k = 32
    conversions = {'int':int,'string':str,'float':float}
    # 初始化 window size
    Window = 100000
    kll1 = KLL(k, Window)
    print('k is ', kll1.k)
    print('window size', kll1.Window)
    # 计数
    countID = 0
    # 开始时间
    time1 = time.time()
    print('start time:',time1)
    # 读取数据
    file_object1 = open('numbers_10000000.csv','rU')
    try:
        for line in file_object1:
            countID += 1
            words = line.split(',')
            idd = countID
            # value 默认值为 int
            value = conversions['int'](words[0])
            # 时间戳默认 为 float
            timestamp = conversions['float'](words[1])
            element = Element(idd, value, timestamp)
            #print('insert ', element.id, element.value, element.timestamp)
            # window size fixed add
            kll1.add(element)
    finally:
        file_object1.close()
    time2 = time.time()
    print(time2)
    print('update data time', time2-time1)

    fo = open("log.txt", "w+")
    length = len(kll1.compactors)
    for (tiemstamp, item, quantile) in kll1.cdf():
        fo.write('%s, %s,%s\n'%(tiemstamp, item, quantile))
    fo.close()
