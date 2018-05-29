#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
from random import random
from math import ceil
from datetime import datetime, timedelta
import operator
import time
from operator import itemgetter, attrgetter
class  KLL:
    def __init__(self, k, Window, c = 2.0/3.0):
        if k<=0: raise ValueError("k must be a positive integer.")
        if c <= 0.5 or c > 1.0: raise ValueError("c must larger than 0.5 and at most 1.0.")
        self.k = k
        self.c = c
        self.compactors = []
        self.stack = []
        self.H = 0
        self.size = 0
        self.maxSize = 0
        self.grow()

        self.Window = Window
        self.count = 0

    def grow(self):
        self.compactors.append(compactor())
        # 更新新的变量 stack

        self.stack.append(0)
        self.H = len(self.compactors)
        assert(self.H == len(self.stack))
        self.maxSize = sum(self.capacity(height) for height in range(self.H))

    def printCompactors(self):
        print('-----------------print start ------------------------')
        length = self.H
        for i in range(0, length):
            print('---------------value----------------------')
            print([item.value for item in self.compactors[i]])

            print('---------------- id ----------------------')
            print([item.id for item in self.compactors[i]])

    def capacity(self, hight):
        depth = self.H - hight - 1
        return int(ceil(self.c**depth*self.k)) + 1

    '''
    normal update
    '''
    def update(self, element):
        item = element
        self.compactors[0].append(item)
        self.size += 1
        if self.size >= self.maxSize:
            self.compress()
            assert(self.size < self.maxSize)

    '''
    in the time based Window
    '''
    def time_base_update(self, element):
        item = element
        # add operation
        self.compactors[0].append(item)
        self.size += 1
        if self.size >= self.maxSize or len(self.compactors[0]) > self.capacity(0):
            self.compress()
            assert(self.size < self.maxSize)

        newest_time_mark = datetime.fromtimestamp( float(item.timestamp) )
        # delete the element beyond the 0.1 second window
        time_based_window = timedelta(seconds = 0.1)
        oldest_window_threshold = newest_time_mark - time_based_window
        all_weights = 0
        all_delete_numbers = 0
        length = self.H
        for i in range(0, length):
            for item in self.compactors[i]:
                if datetime.fromtimestamp( float(item.timestamp) ) < oldest_window_threshold:
                    self.compactors[i].remove(item)
                    all_weights += 2**i
                    all_delete_numbers += 1

        self.size -= all_delete_numbers
    '''
    N fixed size window
    '''

    def add(self, element):
        item = element
        self.count += 1
        if self.count <= self.Window:
            self.compactors[0].append(item)
            self.size += 1
            if self.size >= self.maxSize:
                self.compress()
                assert(self.size < self.maxSize)
            # self.printCompactors()
        else:
            self.compactors[0].append(item)

            self.size += 1
            self.stack[0] += 1

            for h in range(0, self.H):
                # self.printCompactors()
                if(h == self.H-1):
                    # 最上面一层需要进行判断
                    self.compactors[h].sort(key=lambda x: x.id)
                    if self.stack[h] == 2 :
                        self.delete(h)
                        self.delete(h)
                        self.stack[h] = 0
                else:
                    if self.stack[h] == 2 :
                        # 先排序，再讲列表的前 2 个元素，单独进行压缩操作
                        # 进一步解释一下， 这里的排序只是为了压缩两个元素的时候，能够压缩到相邻的两个，这样不会影响 Rank 的结果

                        self.compactors[h].sort(key=lambda x: x.value)
                        # print('-------value sort-------')
                        # self.printCompactors()
                        #self.compactors[h](key=operator.attrgetter('value'))
                        # 目标还是选择老的元素去丢
                        chooseOne, index = self.findOld(h)
                        # print('old element 1 ------', chooseOne.value, 'index number----',index)
                        chooseIndex1 = index
                        # 边界判断，如果后面还有数，则选后面的，没有选前面的，如果前面也没有，那就自己
                        if index + 1 < len(self.compactors[h]):
                                chooseTwo = self.compactors[h][index+1]
                                chooseIndex2 = index + 1
                        elif  index - 1 >= 0:
                                chooseTwo = self.compactors[h][index-1]
                                chooseIndex2 = index - 1
                        else:
                                chooseTwo = self.compactors[h][index]
                                chooseIndex2 = index
                        # print('old element ------', chooseTwo.value, 'index number 2----',chooseIndex2)
                        # 50% 的概率 将其中一个数压入下一层
                        if random() < 0.5:
                            choose = chooseOne
                        else:
                            choose = chooseTwo

                        # 添加到下一个压缩器当中
                        self.compactors[h+1].append(choose)
                        # 也要更新 下一个的栈
                        self.stack[h+1] += 1
                        # 不知道当时为什么加的这个
                        #self.stack[0] += 1
                        # 删除操作
                        indices = chooseIndex1,chooseIndex2
                        self.compactors[h] = [i for j, i in enumerate(self.compactors[h]) if j not in indices]
                        # self.compactors[h].remove(self.compactors[h][0])
                        # self.compactors[h].remove(self.compactors[h][0])
                        self.size -= 2
                        # 归零
                        self.stack[h] = 0
                        # print('-------after delete-------')
                        # self.printCompactors()


    def compress(self):
        for h in range(len(self.compactors)):
            if len(self.compactors[h]) >= self.capacity(h):
                if h+1 >= self.H: self.grow()
                self.compactors[h+1].extend(self.compactors[h].compact())
                # print('I want to know the order ******')
                # self.printCompactors()
                self.size = sum(len(c) for c in self.compactors)
                # Here we break because we reduced the size by at least 1
                # break
                # Removing this "break" will result in more eager
                # compression which has the same theoretical guarantees
                # but performs worse in practice

    def merge(self, other):
        # Grow until self has at least as many compactors as other
        while self.H < other.H: self.grow()
        # Append the items in same height compa  kctors
        for h in range(other.H): self.compactors[h].extend(other.compactors[h])
        self.size = sum(len(c) for c in self.compactors)
        # Keep compressing until the size constraint is met
        while self.size >= self.maxSize:
            self.compress()
        assert(self.size < self.maxSize)

    def rank(self, value):
        r = 0
        for (h, c) in enumerate(self.compactors):
             for item in c:
                 if int(item.value) <= value:
                     r += 2**h
        #print('nei bu de r ', r)
        return r
    def cdf(self):
        itemsAndWeights = []
        for (h, items) in enumerate(self.compactors):
            itemsAndWeights.extend( (item, 2**h) for item in items )
        totWeight = sum( weight for (item, weight) in itemsAndWeights)
        itemsAndWeights.sort(key=lambda x: int(x[0].value))

        '''
        print('*********************debug cdf********************')
        print([x[0].value for x in itemsAndWeights])
        print([x[1] for x in itemsAndWeights])
        print('totWeight',totWeight)
        '''
        #itemsAndWeights.sort()
        # sorted(student_tuples, key=itemgetter(2))
        # data.sort(key=lambda tup: tup[1])
        itemsAndWeights.sort(key=lambda x: int(x[0].value))
        '''
        print('----------------------after sort----------------------')
        print([x[0].value for x in itemsAndWeights])
        '''
        # sorted(itemsAndWeights, key = lambda x: x[0].value)
        cumWeight = 0
        cdf = []
        for (item, weight) in itemsAndWeights:
            cumWeight += weight
            cdf.append( (item.timestamp, item.value, float(cumWeight)/float(totWeight) ) )
        '''
        print([y[1] for y in cdf])
        print([y[2] for y in cdf])
        '''
        return cdf

    def ranks(self):
        ranksList = []
        itemsAndWeights = []
        for (h, items) in enumerate(self.compactors):
             itemsAndWeights.extend( (item, 2**h) for item in items )
        itemsAndWeights.sort()
        cumWeight = 0
        for (item, weight) in itemsAndWeights:
            cumWeight += weight
            ranksList.append( (item, cumWeight) )
        return ranksList

    def add(self, element):
        item = element
        self.count += 1
        #self.printCompactors()
        self.compactors[0].append(item)
        self.size += 1
        if self.size >= self.maxSize:
            self.compress()
            assert(self.size < self.maxSize)




    def findOld(self, h):
        oldElement = self.compactors[h][0]
        oldElementindex = 0
        for i in range(0, len(self.compactors[h])):
            if oldElement.id > self.compactors[h][i].id:
                oldElement = self.compactors[h][i]
                oldElementindex = i
                # print(oldElementindex)
        # for item in self.compactors[h]:
        #     if oldElement.id > item.id:
        #         oldElement = item
        #         oldElementindex =

        return oldElement, oldElementindex
    '''
    删除 h 层中最老的元素
    '''
    def delete(self, h):
        oldElement, index = self.findOld(h)
        #if oldElement.id == self.count - self.Window:
            #print('mininm index is {i} and element value is {v} the element id is {id}'.format(i = index, v = oldElement.value, id = oldElement.id))
        self.compactors[h].remove(oldElement)
            # last_list = self.compactors[self.H-1]
            # print(" delete ",last_list.pop().value)
            # print(" now the compactor {i} is ".format(i = self.H-1))
            # print([item.value for item in self.compactors[self.H-1]])
        self.size -= 1

class Element(object):
    def __init__(self, idd, value, timestamp):

        self.id = idd
        self.value = value
        self.timestamp = timestamp

class compactor(list):
    def compact(self):
        '''
        student_tuples = [
...     ('john', 'A', 15),
...     ('jane', 'B', 12),
...     ('dave', 'B', 10),
... ]
        '''
        # sorted(student_tuples, key=lambda student: student[2])   # sort by age
        #self.sort()
        #print('************')
        # student_objects.sort(key=operator.attrgetter('age'))
        #print([item.value for item in self])
        self.sort(key=lambda x: x.value)
        # list.sort(key=operator.attrgetter('value'))
        #sorted(self, key=attrgetter('value'))
        # print('查看排序结果 -》》》：')
        # print([item.value for item in self])
        #print('************')
        if random() < 0.5:
            while len(self) >= 2:
                _ = self.pop()
                yield self.pop()
        else:
            while len(self) >= 2:
                yield self.pop()
                _ = self.pop()

        # print('showing the compact result：')
        # print([item.value for item in self])
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', type=int, default=128,
                        help='''controls the number of elements in the sketch which is
                        at most 3k+log2(n). n is the length of the stream.''')
    parser.add_argument('-t', type=str, choices=["string","int","float"], default='string',
                        help='defines the type of stream items, default="string".')
    args = parser.parse_args()

    k = args.k if args.k > 0 else 128
    conversions = {'int':int,'string':str,'float':float}
    # 初始化
    Window = 10000
    kll1 = KLL(k, Window)
    kll2 = KLL(k, Window)
    # 定义数据的先后顺序
    countID = 0
    time1 = time.time()
    print(time1)
    # 读取数据
    file_object1 = open('part1.txt','rU')
    try:
        for line in file_object1:
            countID += 1
            words = line.split(',')
            idd = countID
            value = conversions[args.t](words[0])
            timestamp = conversions['float'](words[1])
            element = Element(idd, value, timestamp)
            #print('insert ', element.id, element.value, element.timestamp)
            kll1.update(element)
    finally:
        file_object1.close()
    kll1.printCompactors()
    file_object2 = open('part2.txt','rU')
    countID = 0
    try:
        for line in file_object2:
            countID += 1
            words = line.split(',')
            idd = countID
            value = conversions[args.t](words[0])
            timestamp = conversions['float'](words[1])
            element = Element(idd, value, timestamp)
            #print('insert ', element.id, element.value, element.timestamp)
            kll2.update(element)
    finally:
        file_object2.close()
    kll2.printCompactors()
    kll1.merge(kll2)
    fo = open("log.txt", "w+")
    length = len(kll1.compactors)
    for (tiemstamp, item, quantile) in kll1.cdf():
        fo.write('%s, %s,%s\n'%(tiemstamp, item, quantile))
    fo.close()
    kll1.printCompactors()
    '''
    for line in sys.stdin:
        countID += 1
        words = line.split(',')
        idd = countID
        value = conversions[args.t](words[0])
        timestamp = conversions['float'](words[1])
        element = Element(idd, value, timestamp)
        #print('insert ', element.id, element.value, element.timestamp)
        ## 普通添加
        # kll.update(element)
        ## window 添加
        kll.add(element)

        # kll time based window
        # kll.time_base_update(element)
    time2 = time.time()
    print(time2)

    print('add time which includes the transform time', time2 - time1)
    print("the rank of 8326742:->>>>", kll.rank(88))
    print(kll.rank(88))
    time3 = time.time()
    print(time3 - time2)
    #kll.printCompactors()

    fo = open("log.txt", "w+")

    length = len(kll.compactors)



    for (tiemstamp, item, quantile) in kll.cdf():
        fo.write('%s, %f,%s\n'%(tiemstamp, quantile,str(item)))
    time4 = time.time()
    print('query time :', time4 - time3)
    fo.close()
    '''
