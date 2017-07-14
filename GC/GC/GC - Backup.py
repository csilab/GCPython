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
    #RangeTest(range(1000),16,1)
    #print('result: ', test())
    #mlen = 1024
    #dataInt =  random.randrange(2**mlen)
    #didx = random.randrange(mlen)
    #orgdata= Encoder.genMsg(0,dataInt,mlen)
    #deldata=Simulator.pop(0,orgdata,didx)
    #orgdata='000011110000111'
    #deldata='000111100001111111'
    #UnitTest2(orgdata, deldata)
    #StressTestMulti3New()
    #success=0
    #for i in range(100):
    #    success+=UnitTest3(num=i, mlen=256, dels=[0])
    #print(success)
def bit16test():
    '''Run test on all 16-bit numbers where each number if repeated 16 times for each position
    deletion. Output: total number of fail and success decoding.'''
    results = multiprocessing.Queue()
    pp=[]
    frm=0; to=(2**16); jump=to//8
    count = success = fail = 0
    stime=time.time()
    for i in range(frm, to, jump):
        print('started ',i,'to',i+jump)
        p = Process(target=StressTestMultiNew, args=(i,i+jump,count, results))
        count+=1
        pp.append(p)
        p.start()
    for p in pp:
        p.join()
    ttime=time.time()-stime
    print('Total success:',success,'Total failure:',fail, 'Total time:',ttime)
def editDist(strX, strY):
    '''Check the Lavenshtein distance of the two strings.
    If distance is greater than number of deletions -> False
                                          otherwise -> True'''
    if len(strX) > len(strY):
        strX, strY = strY, strX
    dels=int(math.fabs(len(strX)-len(strY)))
    strX=' '+strX
    strY=' '+strY
    m=len(strX)
    n=len(strY)
    t=[[None for _ in range(m)] for _ in range(n)]
    for j in range(m):
        t[0][j]=j
    for i in range(n):
        t[i][0]=i
    for i in range(1, n):
        donotreturn=False
        for j in range(1, m):
            if strX[j]==strY[i]:
                t[i][j]=t[i-1][j-1]
            else:
                minVal=min(t[i][j-1],t[i-1][j])
                t[i][j]=minVal+1  
            if t[i][j]<=dels: donotreturn=True
        if donotreturn==False and t[i][0]>dels: return False
    return True
def gfCheck(data, blockLength, gf):
    '''Check if each element of data is within the range val < 2^ blockLength'''
    for val in data:
        if val >= 2**blockLength and val < gf:
            print(data)
            return False
    else:
       return True
    ''''''
def UnitTest(orgdata, deldata):
    '''Test on all 16-bit binary number with
    one deletion occuring at any posision.
    This test takes a while'''
    print('Unit test:')
    print('org:', orgdata)
    print('del:', deldata)
    mlen=len(orgdata)
    numDel=mlen-len(deldata)
    success = fail = 0
    en=Encoder(mlen, numDel + 1)
    de=GCdet(mlen, numDel + 1)
    si=Simulator(mlen, numDel+1)
    print(en)
    data=si.breakString(orgdata)
    data=Simulator.binString2int(data)
    print()
    print('data int', data)
    parity=np.matrix(en.paritize(np.matrix([data])))
    print('parity: ', parity)
    dataIntCases, dataBinStringCases, delLocCases=si.getCases(deldata)
    caught=False
    recoveredData=''
    for idx in range(len(dataIntCases)):
        if gfCheck(dataIntCases[idx], si.blockLength, si.gf):
            data=np.matrix(dataIntCases[idx])
            decodedData, valid =de.decode(data, parity)
            print('Case', decodedData, valid)
            if valid:
                temp = si.int2binString(decodedData)
                for i in delLocCases[idx]:
                    delStr=dataBinStringCases[idx][i]
                    frm=i*si.blockLength
                    to=frm+si.blockLength
                    recStr=temp[frm:to].zfill(si.blockLength)
                    editDistCheck = editDist(delStr,recStr)
                    if not editDistCheck:
                        print(orgdata)
                        print(temp)
                        print('Lav Del', delStr)
                        print('Lav Rec', recStr)
                if editDistCheck:
                    if len(recoveredData)==0:
                        recoveredData = temp
                    elif temp!=recoveredData:
                        caught=True
                        break #fail
                    elif temp==recoveredData: pass
                    else: print('what?')
                else:
                    print('Failed distance check')
        else:
            print('failed gf check')
    if recoveredData == orgdata:
        success+=1
    else:
        fail+=1
        if caught==False:
            print()
            print('org',orgdata)
            print('rec',recoveredData)
            print('del',deldata)
        caught=False
    print('Success:',success,'fail:',fail)
def UnitTest2(orgdata, deldata):
    '''Test on all 16-bit binary number with
    one deletion occuring at any posision.
    This test takes a while'''
    mlen=len(orgdata)
    numDel=mlen-len(deldata)
    success = fail = 0
    en=Encoder(mlen, numDel, 1)
    de=GCdet(mlen, numDel, 1)
    si=Simulator(mlen, numDel)
    print(en)
    data=si.breakString(orgdata)
    data=Simulator.binString2int(data)
    parity=(en.paritize(np.array(data)))
    dataIntCases, dataBinStringCases, delLocCases=si.getCases(deldata)
    caught=False
    recoveredData=''
    for idx in range(len(dataIntCases)):
        pdi=np.concatenate((dataIntCases[idx],parity))
        candidate = decode(pdi, dataBinStringCases[idx], list(set(delLocCases[idx])),de, si)
        if candidate != None:
            if len(recoveredData)==0:
                recoveredData = candidate
            elif candidate!=recoveredData:
                caught=True
                break #fail
            elif candidate==recoveredData: pass
            else: print('what?')
    if recoveredData == orgdata:
        return True
    else:
        if caught==False: raise UnhandleedCase
        return False 
def UnitTest3(num, mlen, dels):
    '''Test on all 16-bit binary number with
    one deletion occuring at any posision.
    This test takes a while'''
    numDel=len(dels)
    en=Encoder(mlen, numDel + 1)
    de=GCdet(mlen, numDel +1)
    orgdata=Encoder.genMsg(num, mlen)
    deldata=Encoder.pop(orgdata,dels)
    
    parity=en.paritize(orgdata)
    return recover(orgdata, deldata, parity, mlen, de)

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

def StressTestMulti(frm, to, name, results):
    '''Test on all 16-bit binary number with
    one deletion occuring at any posision.
    This test takes a while'''
    numDel=1; mlen=16; success=0; fail=0
    miscaught=0
    en=Encoder(mlen, numDel + 1)
    de=GCdet(mlen, numDel + 1)
    si=Simulator(mlen, numDel+1)
    for dataInt in range(frm,to,1):
        for didx in range(mlen):
            orgdata= en.genMsg(dataInt,mlen)
            deldata=si.pop(orgdata,didx)
            data=si.breakString(orgdata)
            data=Simulator.binString2int(data)
            parity=np.matrix(en.paritize(np.matrix([data])))
            dataIntCases, dataBinStringCases, delLocCases = si.getCases(deldata)
            recoveredData=''
            isFailed=False
            for idx in range(len(dataIntCases)):
                if gfCheck(dataIntCases[idx], si.blockLength, si.gf):
                    data=np.matrix(dataIntCases[idx])
                    decodedData, valid =de.decode(data, parity)
                    if valid:
                        temp = si.int2binString(decodedData)
                        editDistCheck=True
                        for i in delLocCases[idx]:
                            delStr=dataBinStringCases[idx][i]
                            frm=i*si.blockLength
                            to=frm+si.blockLength
                            recStr=temp[frm:to].zfill(si.blockLength)
                            editDistCheck = editDist(delStr,recStr)
                        if editDistCheck:
                            if len(recoveredData)==0:
                                recoveredData = temp
                            elif temp!=recoveredData:
                                isFailed=True
                                break #fail
                            elif temp==recoveredData: pass
                            else: print('what?')
                        else:
                            pass
                else:
                    print('failed gf check')
            if isFailed:
                fail+=1
            elif recoveredData == orgdata:
                success+=1
            else:
                print('Something happened!')
                print('orgdata',orgdata)
                print('deldata',deldata)
                print('recoveredData',recoveredData)
                
    results.put((success, fail))
def RangeTest(_range, mlen, numDel):
    '''Test on all 16-bit binary number with
    one deletion occuring at any posision.
    This test takes a while'''
    success=0; fail = 0; unknown=0
    en=Encoder(mlen, numDel + 1)
    de=GCdet(mlen, numDel + 1)
    for dataInt in _range:
        for didx in range(mlen):
            orgdata= Encoder.genMsg(dataInt,mlen)
            deldata=Encoder.pop(orgdata,didx)
            parity=en.paritize(orgdata)
            result = recover(orgdata, deldata, parity, mlen, de)
            if result == 1:
                success+= 1
            elif result==0:
                fail+=1
            else:
                unknown+=1
    print(_range, 'numDel:',numDel,'Fail:',fail, 'Sucess:',success, 'unknown:',unknown)
    
def StressTestMulti2(mlen=16):
    '''Test on all 16-bit binary number with
    one deletion occuring at any posision.
    This test takes a while'''
    def setup():
        return '''
import time
mlen={}
numDel=1; success=0; fail=0
en=Encoder(mlen, numDel + 1)
de=GCdet(mlen, numDel + 1)
t1=time.time()'''                     
    def run():
        return '''
dataInt =  random.randrange(2**mlen)
didx = random.randrange(mlen)
orgdata= Encoder.genMsg(dataInt,mlen)
deldata=Encoder.pop(orgdata,didx)
data=si.breakString(orgdata)
data=Encoder.binString2int(data)
parity=np.matrix(en.paritize(np.matrix([data])))
#1.3161867
dataIntCases, dataBinStringCases, delLocCases = si.getCases(deldata)
#56.8222068
recoveredData=''
isFailed=False
for idx in range(len(dataIntCases)):
    if gfCheck(dataIntCases[idx], si.blockLength, si.gf):
        data=np.matrix(dataIntCases[idx])
        #84.8819049
        #0.96
        decodedData, valid =de.decode(data, parity)
        #5.4289
        #532.5281518
        if valid:
            temp = si.int2binString(decodedData)
            #480.3780228
            editDistCheck=True
            for i in delLocCases[idx]:
                delStr=dataBinStringCases[idx][i]
                frm=i*si.blockLength
                to=frm+si.blockLength
                recStr=temp[frm:to].zfill(si.blockLength)
                editDistCheck = editDist(delStr,recStr)
            #659.3036765
            if editDistCheck:
                if len(recoveredData)==0:
                    recoveredData = temp
                elif temp!=recoveredData:
                    isFailed=True
                    break #fail
                elif temp==recoveredData: pass
                else: print('what?')
            else:
                pass
            #517.352637
    else:
        print('failed gf check')
if isFailed:
    fail+=1
elif recoveredData == orgdata:
    success+=1
else:
    print('Something happened!')
    #UnitTest(orgdata, deldata)
if (success+fail)%10000 == 0:
    print('Success: ', success, 'fai: ', fail)'''
    print(timeit.timeit(stmt=run(),
                               setup=setup().format(10000),
                               globals=globals(),
                               number=3))
def StressTestMulti2New(mlen=16):
    '''Test on all 16-bit binary number with
    one deletion occuring at any posision.
    This test takes a while'''
    def setup():
        return '''
import time
mlen={}
numDel=1; success=0; fail=0
en=Encoder(mlen, numDel + 1)
de=GCdet(mlen, numDel + 1)
si=Simulator(mlen, numDel+1)
t1=time.time()'''                     
    def run():
        return '''
dataInt =  random.randrange(2**mlen)
didx = random.randrange(mlen)
orgdata= Encoder.genMsg(dataInt,mlen)
deldata=Encoder.pop(orgdata,didx)
data=en.breakString(orgdata)
data=Encoder.binString2int(data)
parity=en.paritize(np.array(data))
#1.3161867
dataIntCases, dataBinStringCases, delLocCases = si.getCases(deldata)
#56.8222068
recoveredData=''
isFailed=False
for idx in range(len(dataIntCases)):
    if gfCheck(dataIntCases[idx], si.blockLength, si.gf):
        data=np.array(dataIntCases[idx])
        dels=list(set(delLocCases[idx])) #distinct
        bsdata = dataBinStringCases[idx]
        pdata=np.concatenate((data,parity))
        #1.04
        rdels, valid =de.decode(pdata, dels)
        #11.9408
        if valid:
            bsrdels = [si.int2binString(rdels)]
            #480.3780228
            editDistCheck=True
            for i in range(len(bsrdels)):
                editDistCheck = editDist(bsdata[dels[i]],bsrdels[i])
                if editDistCheck:
                    bsdata[dels[i]]=bsrdels[i]
                else:
                    break
            #659.3036765
            if editDistCheck:
                #change length of the last one
                lastLen=si.mlen%si.blockLength
                bsdata[-1]=bsdata[-1][-lastLen:]
                temp=''.join(bsdata)
                if len(recoveredData)==0:
                    recoveredData = temp
                elif temp!=recoveredData:
                    isFailed=True
                    break #fail
                elif temp==recoveredData: pass
                else: print('what?')
            else:
                pass
            #517.352637
    else:
        print('failed gf check')
if isFailed:
    fail+=1
elif recoveredData == orgdata:
    success+=1
else:
    print('Something happened!')
    UnitTest2(orgdata, deldata)
if (success+fail)%10000 == 0:
    print('Success: ', success, 'fai: ', fail)'''
    times=[]
    #bits=[768,1024,1536,2048]
    #bits=[128,192,256,384,512,768,1024,1536,2048]
    bits=[128]
    for i in range(len(bits)):
        print('Start',bits[i])
        times.append((timeit.timeit(stmt=run(),
                                   setup=setup().format(bits[i]),
                                   globals=globals(),
                                   number=100000)))
        print('End',bits[i])
    print(bits)
    print(times)
    import matplotlib.pyplot as plt
    plt.plot(bits,times, 'ro')
    plt.show()
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
        #import matplotlib.pyplot as plt
        #plt.plot(bits,times, 'ro')
        #plt.show()
def decode(pdi, dbs, dels, de, si):
    rdels, valid =de.decode(pdi, dels)
    if not valid: return ''
    else:
        rdelsbs = [si.int2binString(rdels)]
        editDistCheck=True
        for i in range(len(rdelsbs)):
            editDistCheck = editDist(dbs[dels[i]],rdelsbs[i])
            if editDistCheck:
                dbs[dels[i]]=rdelsbs[i]
            else:
                break
        if editDistCheck:
            #change length of the last one
            lastLen=si.mlen%si.blockLength
            dbs[-1]=dbs[-1][-lastLen:]
            return ''.join(dbs)
        else: return ''
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
def genMsg(num, mLen):
    '''\return a tuple of original message and deleted message'''
    if num>2**mLen: raise TooShortLength
    b = bin(num)[2:].zfill(mLen)
    return b

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
