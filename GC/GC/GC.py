from multiprocessing import Process, queues
import multiprocessing
from Encoder import *
from Decoder import *
from Simulator import *
from GCdet import *
import timeit
import time
from Data import *
from Consumer import *
import random

def test():
    # Establish communication queues
    tasks = multiprocessing.JoinableQueue()
    poison = multiprocessing.JoinableQueue()
    results = multiprocessing.Queue()

    # Start consumers
    #num_consumers = multiprocessing.cpu_count() * 2
    num_consumers =8
    print ('Creating {} consumers'.format(num_consumers))
    consumers = [ Consumer(tasks, results, poison)
                  for i in range(num_consumers) ]

    print('has consumers')
    for w in consumers:
        w.start()
    print('started consumers')    #bit16test()
    
    numDel=1
    data=Data(s='000010011010011', p=[3,16], mlen=16)
    de=GCdet(16, numDel + 1)
    dels=caseGen(4, 1)
    count=0
    for d in dels:
        tasks.put(Task(data,list(d),de))
        count+=1

    # Add a poison pill for each consumer
    rdata=''
    while True:
        if not results.empty():
            candidate=results.get()
            if candidate != None:
                if len(rdata)==0:
                    rdata = candidate
                elif candidate!=rdata:
                    rdata = None
                    break
                elif candidate==rdata: pass
                else: print('what?')
            else: pass #candidate is not None -> next case
        elif tasks.empty():
            break
    poison.put(None)

    # Wait for all of the tasks to finish
    tasks.join()

    return rdata

def main():
    Test(n=10000, mlen=128, numDel=1, numPro=8, f=1)
    #StressTestMulti3New()

def recover(orgdata, deldata, parity, mlen, de, tasks=None, results=None, poison=None, numPro=None):
    def _recover(deldata, parity, mlen, de):
        data=Data(deldata, parity, mlen)
        rdata=''
        dels=caseGen(de.numBlock, mlen-len(deldata))
        for d in dels:
            candidate = data.decode(d,de)
            if candidate != None:
                if len(rdata)==0:
                    rdata = candidate
                elif candidate!=rdata:
                    return None
                elif candidate==rdata: pass
                else: print('what?')
            else: pass#candidate is not None -> next case
        return rdata
    def _recover_mul(deldata, parity, mlen, de, numPro):
        # Establish communication queues
        tasks = multiprocessing.JoinableQueue()
        poison = multiprocessing.JoinableQueue()
        results = multiprocessing.Queue()

        # Start consumers
        #num_consumers = multiprocessing.cpu_count() * 2
        #num_consumers = multiprocessing.cpu_count() * 2
        num_consumers=numPro
        consumers = [ Consumer(tasks, results, poison)
                      for i in range(num_consumers) ]
        for w in consumers:
            w.start()

        data=Data(deldata, parity, mlen)
        dels=caseGen(de.numBlock, mlen-len(deldata))
        numTask=0
        for d in dels:
            tasks.put(Task(data,list(d),de))
            numTask+=1

        rdata=''
        while numTask:
            if not results.empty():
                candidate=results.get()
                if candidate != None:
                    if len(rdata)==0:
                        rdata = candidate
                    elif candidate!=rdata:
                        print('Declare failure')
                        rdata = None
                        break
                    elif candidate==rdata: pass
                    else: print('what?')
                else: pass #candidate is not None -> next case
                numTask-=1
        poison.put(None)
        tasks.join() # Wait for all of the tasks to finish
        return rdata
    def _recover_mul_rec(deldata, parity, mlen, de, tasks, results, poison):
        poison.get() #play
        data=Data(deldata, parity, mlen)
        dels=caseGen(de.numBlock, mlen-len(deldata))
        numTask=0
        for d in dels:
            tasks.put(Task(data,list(d),de))
            numTask+=1
        rdata=''
        while numTask:
            if not results.empty():
                candidate=results.get()
                if candidate != None:
                    if len(rdata)==0:
                        rdata = candidate
                    elif candidate!=rdata:
                        #print('Declare failure')
                        rdata = None
                        break
                    elif candidate==rdata: pass
                    else: print('what?')
                else: pass #candidate is not None -> next case
                numTask-=1
            else:pass
                #print('result is empty')
        #pause processes and clean up Q's
        poison.put('Pause')
        #print('paused')
        tasks.join() # Wait for all of the tasks to finish
        while not results.empty():
            results.get()
        #print('clear results')

        return rdata    
    if tasks==None:
        if numPro==None:
            rdata = _recover(deldata, parity, mlen, de)
        else:
            rdata = _recover_mul(deldata, parity, mlen, de, numPro)
    else:
        rdata = _recover_mul_rec(deldata, parity, mlen, de, tasks, results, poison)
    #final verification.
    if rdata == None:
        return 'f' #Fail sequence, successful simulation
    elif rdata == orgdata:
        return 's' #success
    else:
        return 'u' #Unknown result, need debugging

def StressTestMulti3New(mlen=16):
    '''Test on all 16-bit binary number with
    one deletion occuring at any posision.
    This test takes a while'''
    def setup():
        return '''
random.seed(9)
import time
mlen={}
numPro={}
numDel=1; success=0; fail=0; unknown=0
numChecker=1
en=Encoder(mlen, numDel + numChecker)
de=GCdet(mlen, numDel + numChecker)
print(en)
t1=time.time()

## Establish communication queues
#tasks = multiprocessing.JoinableQueue()
#poison = multiprocessing.JoinableQueue()
#results = multiprocessing.Queue()
#poison.put('Pause')
## Start consumers
##num_consumers = multiprocessing.cpu_count() * 2
##num_consumers = multiprocessing.cpu_count() * 2
#num_consumers=numPro
#consumers = [ Consumer(tasks, results, poison)
#                for i in range(num_consumers) ]
#for w in consumers:
#    w.start()'''                     
    def run():
        return '''

dataInt =  random.randrange(2**mlen)
didx = random.randrange(mlen)

orgdata= Encoder.genMsg(dataInt,mlen)
deldata=Encoder.pop(orgdata,didx)
parity=en.paritize(orgdata)
#if recover(orgdata, deldata, parity, mlen, de, tasks, results, poison):

result = recover(orgdata, deldata, parity, mlen, de)

if result==1:
    success+=1
elif result==0:
    fail+=1
else:
    unknown+=1

if (success+fail)%10 == 0:
    print('Success: ', success, 'fail: ', fail, 'unknown: ', unknown)'''
    
    #bits=[768,1024,15326,2048]
    #bits=[128,192,256,384,512,768,1024,1536,2048, 4096, 8192, 16384]
    bits=[128]#,192,256,384,512,768,1024]
    numPros=[8]
    #bits=[32768,65536,131072]
    #bits=[10000]

    #bits=[1536,2048]
    for numPro in numPros:
        times=[]
        print('Started with {} processes'.format(numPro))
        for numBit in bits:
            print('Start',numBit)
            times.append((timeit.timeit(stmt=run(),
                                       setup=setup().format(numBit,numPro),
                                       globals=globals(),
                                       number=10000)))
            print('End',numBit)
        print(bits)
        print(times)
        print('Ended with {} processes'.format(numPro))
        import matplotlib.pyplot as plt
        plt.plot(bits,times, 'ro')
        plt.show()

def case(numBlock, numDel):
    def case_rec(numBlock, numDel, start=0, lst=list(), root=list()):
        '''Recursion'''
        if numDel==1:
            for loc in range(start, numBlock,1):
                lst.extend(root)
                lst.append(loc)
        else:
            for loc in range(start, numBlock,1):
                root.append(loc)
                case_rec(numBlock, numDel-1, loc, lst, root)
                del root[-1]
        return lst
    cases=case_rec(numBlock, numDel, lst=list())
    return np.reshape(cases,(int(len(cases)/numDel),numDel))

def caseGen(numBlock, numDel):
    def case_rec(numBlock, numDel, start=0, root=list()):
        '''Recursion'''
        if numDel==1:
            for loc in range(start, numBlock,1):
                root.append(loc)
                yield root
                del root[-1]
        else:
            for loc in range(start, numBlock,1):
                root.append(loc)
                yield from case_rec(numBlock, numDel-1, loc, root)
                del root[-1]
    return case_rec(numBlock, numDel)

def Test(n=None, mlen=16, numDel=1, numPro=None, f=1000):
    def initConsumer():
        if numPro==None: return None, None ,None, None
        # Establish communication queues
        tasks = multiprocessing.JoinableQueue()
        poison = multiprocessing.JoinableQueue()
        results = multiprocessing.Queue()
        poison.put('Pause')
        # Start consumers
        #numPro = multiprocessing.cpu_count() * 2
        consumers = [ Consumer(tasks, results, poison)
                        for i in range(numPro) ]
        for w in consumers:
            w.start()
        return consumers, tasks, results, poison
    def getRanges():
        if n != None:#random
            def genO():
                for _ in range(n):
                    yield random.randrange(2**mlen)
            orange=genO()
            irange = [random.sample(range(mlen), numDel)]
        else:
            orange=range(2**mlen)
            irange=range(mlen)
        return orange, irange
    print('Testing with', 'n=', n, ' mlen=', mlen, ' numDel=', numDel, ' numPro=', numPro,' f=', f)
    stat = {'s':0, 'f':0, 'u':0} #success, failure, unknown
    numChecker=1
    en=Encoder(mlen, numDel + numChecker)
    de=GCdet(mlen, numDel + numChecker)
    consumers, tasks, results, poison = initConsumer()#init multiprocessing if numPro is not None
    orange, irange = getRanges()
    for num in orange:
        for dels in irange:
            orgdata= Encoder.genMsg(num,mlen)
            deldata=Encoder.pop(orgdata,dels)
            parity=en.paritize(orgdata)
        
            result = recover(orgdata, deldata, parity, mlen, de, tasks, results, poison)
            stat[result]+=1

            if (sum(stat.values()))%f == 0:
                print(stat)

if __name__ == '__main__':
    main()
