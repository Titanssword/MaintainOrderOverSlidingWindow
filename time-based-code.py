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
