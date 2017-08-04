from multiprocessing import Process, Queue, Pool, Pipe
import multiprocessing
from Encoder import *
from Decoder import *
from Consumer import *
import timeit
import time
import random
from ctypes import c_int, c_char_p

def test():
    de=Decoder(mlen=16, numDel=1, numChecker=1, lengthExtension=1)
    en=Encoder(mlen=16, numVec=2, lengthExtension=1)
    print(de)
    orgdata='1111000011110000'
    deldata='111100001110000'
    parity=en.paritize(orgdata)
    print(deldata, parity)
    cases = de.caseGen()
    for dels in cases:
        b = de.breakString(deldata, dels)
        i = de.bin2int(b)
        for d in dels:
            i[d] = 'X'
        print(dels, b, i)
    
    r = de.decode(deldata, parity)
    print(r)

def main():
    #test()
    #bits=[128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 131072]
    bits=[1024]
    for mlen in bits:
        for lengthExtension in range(1,2):
            #try:
                Simulation(n=1000, mlen=mlen, numDel=2, numPro=None, f=1000, lengthExtension=lengthExtension)
                print('Ended', mlen)
                print()
            #except:
                print("failed", mlen, lengthExtension)

def Simulation(n=1, mlen=16, numDel=1, numPro=None, f=10, lengthExtension=0):
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
        dels=data.caseGen(reverse=False)
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
    def sequential():
        de=Decoder(mlen, numDel, numChecker, lengthExtension)
        print(de)
        print(de.gf)
        ttime = 0
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

                #t1=time.time()
                #for i in range(1000):
                #hieu=data.caseGenFast()
                #for i in hieu:
                #    print(i)
                #print(time.time()-t1)
                t1=time.time()
                r = de.decode(deldata, parity)
                ttime+=(time.time()-t1)
                #r = _recover(data)
                #print(len(r))
                record(orgdata, r, True)
                count+=1
        print('Average time: ',ttime/count*1000,'ms')
        print('Failure rate:',(stat['f']+stat['u'])/count*100,'%')
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
    print('Testing with', 'n=', n, ' mlen=', mlen, ' numDel=', numDel, ' numPro=', numPro,' f=', f, ' lengthExtension=', lengthExtension)
    stat = {'s':0, 'f':0, 'u':0} #number of success, failure and unknown decoding.
    numChecker=2 # the number of excess parities to further confirm the decoded sequence.
    en=Encoder(mlen, numDel + numChecker, lengthExtension)
    orange, irange = getRanges() # get sequences and indices of deletions to run the simulation on.
    if numPro == None:
        sequential()
    else:
        useConsummer3()

if __name__ == '__main__':
    main()
