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
    case
    Simulation(n=10000, mlen=128, numDel=1, numPro=8, f=1)
    #StressTestMulti3New()
def recover(orgdata, deldata, parity, mlen, de, tasks=None, results=None, poison=None, numPro=None):
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
        return 'u' #Unknown results need debugging

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

def Simulation(n=None, mlen=16, numDel=1, numPro=None, f=1000):
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
    def initConsumer():
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
            orange=genO()
            irange = [random.sample(range(mlen), numDel)]
        else:
            orange=range(2**mlen)
            irange=range(mlen)
        return orange, irange
    print('Testing with', 'n=', n, ' mlen=', mlen, ' numDel=', numDel, ' numPro=', numPro,' f=', f)
    stat = {'s':0, 'f':0, 'u':0} #number of success, failure and unknown decoding.
    numChecker=1 # the number of excess parities to further confirm the decoded sequence.
    en=Encoder(mlen, numDel + numChecker)
    de=GCdet(mlen, numDel + numChecker)
    consumers, tasks, results, poison = initConsumer() #init multiprocessing if numPro is not None.
    orange, irange = getRanges() # get sequences and indices of deletions to run the simulation on.
    for num in orange:
        for dels in irange:
            orgdata= Encoder.genMsg(num,mlen) # converts the integer num to its binary string representation.
            deldata=Encoder.pop(orgdata,dels) # pop one or more bits out to create a deleted sequence.
            parity=en.paritize(orgdata) # Compute the parity integers in based on the original sequence (encoder's end).
        
            result = recover(orgdata, deldata, parity, mlen, de, tasks, results, poison) # decode.
            stat[result]+=1 

            if (sum(stat.values()))%f == 0: #display the results every f sequences.
                print(stat)

if __name__ == '__main__':
    main()
