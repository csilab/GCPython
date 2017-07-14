import multiprocessing
import time

class Consumer(multiprocessing.Process):
    def __init__(self, task_queue, result_queue, poison_queue):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.poison_queue = poison_queue

    def run(self):
        while True:
             if not self.poison_queue.empty():
                 while not self.task_queue.empty():
                     next_task=self.task_queue.get()
                     #print ('Emptied',self.name, next_task)
                     self.task_queue.task_done()
                 #print ('Exiting'.format(self.name))
                 #self.task_queue.task_done()
             elif not self.task_queue.empty():
                 next_task = self.task_queue.get()
                 #print ('Started',self.name, next_task)
                 answer = next_task()
            
                 self.result_queue.put(answer)
                 self.task_queue.task_done()
                 #print ('Finished',self.name, next_task)
             else:pass
                #print('passed')
class Task(object):
    def __init__(self, data, d, de):
        self.data = data
        self.d = d
        self.de = de
    def __str__(self):
        return 'Doing job ' + str(self.d)
    def __call__(self):
        return self.data.decode(self.d,self.de)