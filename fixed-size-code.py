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
