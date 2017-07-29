from multiprocessing import Process, Queue, Pool, Pipe
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
from ctypes import c_int, c_char_p

def test():
    sPermission = LockedInt(8)
    sAvai = LockedInt(0)
    sDelData = LockedString('hieu')
    sParity = LockedList([1,2])
    sResult = LockedString('')
    numPro = 2
    consumers = [ Consumer2(sDelData, sParity, sResult, sPermission, sAvai, data)
                    for i in range(numPro) ]
    for w in consumers:
        w.start()
    sDelData.set('1111000011110000')
    sParity.set([5,6,7])

def test2():
    numBlock = 8 ; numDel=4
    t = getTable(numBlock, numDel)
    dels = caseGen1(numBlock, numDel, frm = [200],to = 80, table = t)
    c=0
    for d in dels:
        print(c,d)
        c+=1

def main():
    
    #bits=[128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 131072]
    #bits=[128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 131072]
    bits=[128]
    for mlen in bits:
        Simulation(n=1000, mlen=mlen, numDel=1, numPro=None, f=1000)
        print('Ended', mlen)
        print()

def Simulation(n=1000, mlen=16, numDel=1, numPro=None, f=10):
    """
     Decodes a large amount of sequences using GC algorithms.

    Args:
        n: Number of sequence to run GC on. If n is None, run on all possible one deletion cases of all numbers of mlen length.
        mlen: The length of each sequence.
        numDel: Number of deletions obviously.
        numPro: Number of decoding processes assisting the simulation.
        f: The frequency of priting out the result to the command line.

    Returns:
        The total elapsed time of the simulation.

    Raises:
        None
    """
    def _recover_early(data):
        dels=data.caseGenDistinct()
        for d in dels:
            #print('dels case', d)
            candidate = data.decode(d)
            if candidate != None:
                #print(d, candidate)
                return candidate
        raise NoResultFound
    def _recover(data):
        rdata=''
        #dels=caseGen(data.numBlock, data.numDel)
        dels=data.caseGenFast(reverse=False)
        for d in dels:
            candidate = data.decode(d)
            if candidate != None:
                #return candidate
                if len(rdata)==0:
                    rdata = candidate
                elif candidate!=rdata:pass
                    #return None
                elif candidate==rdata: pass
                else: print('what?')
            else: pass#candidate is not None -> next case
        return rdata
    def _recover_cached(data):
        return data.onedecode()
    def _recover_cachedAll(data):
        return data.twodecode()

    def getRanges():
        """
        Generates sequences and deletions to run the simulation on.

        Args:
            n: Number of sequence to run GC on. If n is None, run on all possible one deletion cases of all numbers of mlen length.
            mlen: The length of each sequence.
            numDel: Number of deletions obviously.
            numPro: Number of decoding processes assisting the simulation.
            f: The frequency of priting out the result to the command line.

        Returns:
            Return 2 ranges/generators:
            orange: a collection of integers representing original sequences to decode.
            irange: the indeces of the deletions on the original sequences.

        Raises:
            None
        """
        if n != None:#random
            def genO():
                for _ in range(n):
                    yield random.randrange(2**mlen)
            def genI():
                for _ in range(n):
                    yield random.sample(range(mlen), numDel)
            orange=genO()
            irange = genI()
        else:
            orange=range(2**mlen)
            irange=range(mlen)
        return orange, irange
    def initConsumer(numPro):
        """
         Initialize decoding processes.

        Args:
            numPro: Number of decoding processes assisting the simulation (received from the outer method - Test).

        Returns:
            None, None, None, None if numPro is None
            consumers, tasks, results, poison: References to queue and processes

        Raises:
            None
        """
        if numPro==None: return None, None ,None, None, None, None
        # Establish communication queues
        sPermission = LockedInt(0)
        sAvai = LockedInt(numPro)
        sDelData = LockedString('hieu')
        sParity = LockedList([1,2])
        sResult = LockedString(None)
        de=GCdet(mlen, numDel + numChecker)
        print(de)
        data=Data(mlen, de, numDel)
        consumers = [ Consumer2(sDelData, sParity, sResult, sPermission, sAvai, data, i, numPro)
                        for i in range(numPro) ]
        for w in consumers:
            w.start()
        return consumers, sDelData, sParity, sResult, sPermission, sAvai, data
    def initPool():
        """
         Initialize decoding processes.

        Args:
            numPro: Number of decoding processes assisting the simulation (received from the outer method - Test).

        Returns:
            None, None, None, None if numPro is None
            consumers, tasks, results, poison: References to queue and processes

        Raises:
            None
        """
        if numPro==None: return None
        # Establish communication queues
        p = Pool(numPro)
        return p
    def useConsummer2():
        #start timer here
        sDelData.set(deldata)
        sParity.set(parity)
        sPermission.set(numPro)
        while sPermission == numPro:pass
            #print('wating 1')
        while sAvai != numPro:pass
            #print('waiting 2')
        print('main', sResult)
    def endConsummer2():
        #time.sleep(2)
        sPermission.set(-numPro)
    def initConsumer3(numPro):
        """
         Initialize decoding processes.

        Args:
            numPro: Number of decoding processes assisting the simulation (received from the outer method - Test).

        Returns:
            None, None, None, None if numPro is None
            consumers, tasks, results, poison: References to queue and processes

        Raises:
            None
        """
        if numPro==None: return None, None
        # Establish communication queues
        de=GCdet(mlen, numDel + numChecker)
        #print(de)
        data=Data(mlen, de, numDel)
        fq=[Queue() for _ in range(numPro)] #Feeder Queue
        mq=[Queue() for _ in range(numPro)] #Merger Queue
        rq=Queue() #Result Queue
        decoders = [ Consumer3(id, fq[id], mq[id], data, numPro) for id in range(numPro) ]        
        merger=Merger(mq, rq)
        
        for w in decoders:
            w.start()
        merger.start()
        return fq, rq
    def useConsummer3():
        fq, rq = initConsumer3(numPro) #init multiprocessing if numPro is not None.
        count=0
        o=[]
        for num in orange:
            for dels in irange:
                orgdata= Encoder.genMsg(num,mlen) # converts the integer num to its binary string representation.
                deldata=Encoder.pop(orgdata,dels) # pop one or more bits out to create a deleted sequence.
                parity=en.paritize(orgdata) # Compute the parity integers in based on the original sequence (encoder's end).
                for i in range(numPro):
                    fq[i].put(Job(count, deldata, parity))
                o.append(orgdata)
                count+=1
        #add poison
        for i in range(numPro):
            fq[i].put(None)
        while count:
            if not rq.empty():
                #print('getting result')
                result = rq.get()
                record(o[result.id], result.s, result.valid)
                count-=1
    def sequential():
        de=GCdet(mlen, numDel + numChecker)
        print(de)
        t1=time.time()
        count=0
        #irange = [[x] for x in range(128)]
        for num in orange:
            for dels in irange:
                #num = 54245426
                #print(dels)
                #dels[0]=1
                #dels[1]=7
                #dels[2]=18
                orgdata= Encoder.genMsg(num,mlen) # converts the integer num to its binary string representation.
                #orgdata='1011000011101101001011111001110010001001111111100111001001100001'
                #print(orgdata)
                deldata=Encoder.pop(orgdata,dels) # pop one or more bits out to create a deleted sequence.
                #print(deldata)
                parity=en.paritize(orgdata) # Compute the parity integers in based on the original sequence (encoder's end).
                data=Data(mlen, de, numDel, deldata, parity)
                #t1=time.time()
                #for i in range(1000):
                #    hieu=data.caseGenFast()
                #    for i in hieu:
                #        pass
                #        #print(i)
                #print(time.time()-t1)
                #r = data.twodecode()
                #r = data.decode()
                #print(len(r))
                r = _recover_cached(data)
                record(orgdata, r, True)
                count+=1
        print('Average time: ',(time.time()-t1)/count*1000,'ms')
        print('Failure rate:',(stat['f']+stat['u'])/count*100,'%')
    def record(org, rec, valid):
        if valid:
            if rec==None:
                r='f'
            elif org==rec:
                r='s'
            else:
                r='u'
                #print('org',org)
                #print('rec',rec)
            stat[r]+=1
        else:
            r='f'
        if (sum(stat.values()))%f == 0: #display the results every f sequences.
            print(stat)
    print('Testing with', 'n=', n, ' mlen=', mlen, ' numDel=', numDel, ' numPro=', numPro,' f=', f)
    stat = {'s':0, 'f':0, 'u':0} #number of success, failure and unknown decoding.
    numChecker=2 # the number of excess parities to further confirm the decoded sequence.
    en=Encoder(mlen, numDel + numChecker)
    orange, irange = getRanges() # get sequences and indices of deletions to run the simulation on.
    if numPro == None:
        sequential()
    else:
        useConsummer3()

def caseGen1(numBlock, numDel, frm, to=None, table = None):
        """
         Return a GENERATOR of all possible indices where deletions might occur. Example, [[0], [1], [2], [3]] is the result of calling case(numBlock=4, numDel=1).
         Notice this call does not use too much memory because it return a generator instead of a actual list. It is also less time consumming.

        Args:
            numBlock: Number of blocks where deletions might occur.
            numDel: Number of deletions.

        Returns:
            A generator of all possible indices where deletions might occur. 

        Raises:
            None
        """
        #numBlock, numDel = self.numBlock, self.mlen-len(self.s)
        frm[0]+=1
        def case_rec(numDel, start=0, root=list()):
            """
             A recursive method assiting the generation of deletion cases.

            Args:
                numDel: Number of deletions.
                start: The first deletion index of the remaining deletion.
                root: The base indices for each each guess.

            Returns:
                A generator of all possible indices where deletions might occur. 

            Raises:
                None
            """
            if numDel==1:
                for loc in range(numBlock - frm[0], start -1 , -1):
                    if count[0] >= to: break
                    else:
                        root.append(loc)
                        yield root
                        del root[-1]
                    count[0]+=1
            else:
                idx = 0
                for i in range(len(table[numDel])):
                    if table[numDel][i]>=frm[0]:
                        idx = i
                        break
                frm[0] = frm[0] - table[numDel][idx - 1]
                for d in range(numBlock - idx, start -1 , -1):
                    if count[0] >= to: break
                    root.append(d)
                    yield from case_rec(numDel-1, d, root)
                    del root[-1]
        if to == None: to = table[numDel][numBlock]
        count=[0]
        return case_rec(numDel)

def getTable(numDel, numBlock):
    t = []
    d1 = [1]*numBlock
    d1[0]=0
    t.append(d1)
    for n in range(numDel+1):
        t.append([sum(t[-1][:i]) for i in range(1, numBlock +1)])
    return t

def recover(data, deldata):
    """
    Recover the original sequence from the deleted sequence and its parity using GC algorithms.

    Args:
        orgdata: A binary string of the original sequence, this is just to verify the simulation result.
        deldata: A binary string of the deleted sequence.
        parity: A list/numpy array of partity intergers.
        mlen: The bit length of the original sequence.
        de: A decoder.
        tasks: A multiprocessing Queue that contains decoding tasks.
        results: A multiprocessing Queue that contains the decoded sequences which are candidates of the original sequence.
        poison: A multiprocessing Queue that signals stop/play the processes.
        numPro: Number of decoding processes assisting the simulation.

    Returns:
        None if there are two distinct, valid sequences recovered -> simulation succeed.
        An empty string if all predictions are invalid -> simulation fails.
        A binary string of the recovered sequence if -> simultation succeeds.

    Raises:
        None
    """
    def _recover():
        rdata=''
        dels=caseGen(data.numBlock, data.numDel)
        for d in dels:
            candidate = data.decode(d)
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
    def _recover_mul_rec(deldata, parity, mlen, de, tasks, results, poison, control, result):
        with control.lock:
            control.val.value=1
        with result.lock:
            result.val.value=''
        data=Data(deldata, parity, mlen)
        dels=caseGen(de.numBlock, mlen-len(deldata))
        rdata=''
        numTask=0
        got=0
        for d in dels:
            print(d)
            if len(d)==0: raise F
            tasks.put(Task(data,list(d),de))
            numTask+=1
        
        while not tasks.empty(): pass
        #results.join()
        #tasks.join() # Wait for all of the tasks to finish
        with control.lock:
            control.val.value=0
    return _recover()

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
    """
     Return a LIST of all possible indices where deletions might occur. Example, [[0], [1], [2], [3]] is the result of calling case(numBlock=4, numDel=1).
     Notice this call is not memory efficient because it actaully creates a list in memory. Use caseGen for a more memory friendly method.

    Args:
        numBlock: Number of blocks where deletions might occur.
        numDel: Number of deletions.

    Returns:
        A list of all possible indices where deletions might occur. 

    Raises:
        None
    """
    def case_rec(numDel, start=0, lst=list(), root=list()):
        """
         A recursive method assiting the generation of deletion cases. This is not memory and time efficient.

        Args:
            numDel: Number of deletions.
            start: The first deletion index of the remaining deletion.
            lst: 1-D array of guesses for deletion indices. To be broken down into a x by numDel 2-D array.
            root: The base indices for each each guess.

        Returns:
            A list of all possible indices where deletions might occur. 

        Raises:
            None
        """
        if numDel==1:
            for loc in range(start, numBlock,1):
                lst.extend(root)
                lst.append(loc)
        else:
            for d in range(start, numBlock,1):
                root.append(d)
                case_rec(numDel-1, d, lst, root)
                del root[-1]
        return lst
    cases=case_rec(numDel, lst=list())
    return np.reshape(cases,(int(len(cases)/numDel),numDel))
#remove this
def caseGen(numBlock, numDel):
    """
     Return a GENERATOR of all possible indices where deletions might occur. Example, [[0], [1], [2], [3]] is the result of calling case(numBlock=4, numDel=1).
     Notice this call does not use too much memory because it return a generator instead of a actual list. It is also less time consumming.

    Args:
        numBlock: Number of blocks where deletions might occur.
        numDel: Number of deletions.

    Returns:
        A generator of all possible indices where deletions might occur. 

    Raises:
        None
    """
    def case_rec(numDel, start=0, root=list()):
        """
         A recursive method assiting the generation of deletion cases.

        Args:
            numDel: Number of deletions.
            start: The first deletion index of the remaining deletion.
            root: The base indices for each each guess.

        Returns:
            A generator of all possible indices where deletions might occur. 

        Raises:
            None
        """
        if numDel==1:
            for loc in range(start, numBlock,1):
                root.append(loc)
                yield root
                del root[-1]
        else:
            for loc in range(start, numBlock,1):
                root.append(loc)
                yield from case_rec(numDel-1, loc, root)
                del root[-1]
    return case_rec(numDel)


if __name__ == '__main__':
    main()
