from multiprocessing import Process, queues
import multiprocessing
from Encoder import *
from Decoder import *
from Simulator import *
from GCdet import *
import timeit
import time
from Data import *


def test():
    orgdata='0110000000000000'
    deldata='110000000000000'
    UnitTest(orgdata, deldata)
def main():
    #bit16test()
    #mlen = 1024
    #dataInt =  random.randrange(2**mlen)
    #didx = random.randrange(mlen)
    #orgdata= Encoder.genMsg(0,dataInt,mlen)
    #deldata=Simulator.pop(0,orgdata,didx)
    #orgdata='0000111100001111111'
    #deldata='000111100001111111'
    #UnitTest2(orgdata, deldata)
    #StressTestMulti3New()
    print(UnitTest3(num=1010, mlen=16, dels=[1]))
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
    dels=mlen-len(deldata)
    success = fail = 0
    en=Encoder(mlen, dels+1)
    de=Decoder(mlen, dels+1)
    si=Simulator(mlen, dels)
    print(en)
    data=si.breakString(orgdata)
    data=si.binString2int(data)
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
    dels=mlen-len(deldata)
    success = fail = 0
    en=Encoder(mlen, dels+1)
    de=GCdet(mlen, dels+1)
    si=Simulator(mlen, dels)
    print(en)
    data=si.breakString(orgdata)
    data=si.binString2int(data)
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
    ndels=len(dels)
    en=Encoder(mlen, ndels+2)
    de=GCdet(mlen, ndels+2)
    si=Simulator(mlen, ndels+2)

    orgdata= genMsg(num, mlen)
    deldata=si.pop(orgdata,dels)
    
    data = si.breakString(orgdata)
    data = si.binString2int(data)
    parity=en.paritize(np.array(data))
    #return orgdata, deldata, parity, mlen, de
    return recover(orgdata, deldata, parity, mlen, de)

def recover(orgdata, deldata, parity, mlen, de):
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
    rdata = _recover(deldata, parity, mlen, de)
    #final verification.
    if rdata == None:
        return 0 #Simulation is still successful
    elif rdata == orgdata:
        return 1
    else:
        raise UnhandledCase #Something is wrong in the simulation

def StressTestMulti(frm, to, name, results):
    '''Test on all 16-bit binary number with
    one deletion occuring at any posision.
    This test takes a while'''
    dels=1; mlen=16; success=0; fail=0
    miscaught=0
    en=Encoder(mlen, dels+1)
    de=Decoder(mlen, dels+1)
    si=Simulator(mlen, dels)
    for dataInt in range(frm,to,1):
        for didx in range(mlen):
            orgdata= en.genMsg(dataInt,mlen)
            deldata=si.pop(orgdata,didx)
            data=si.breakString(orgdata)
            data=si.binString2int(data)
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
def StressTestMultiNew(frm, to, name, results):
    '''Test on all 16-bit binary number with
    one deletion occuring at any posision.
    This test takes a while'''
    dels=1; mlen=16; success=0
    miscaught=0
    en=Encoder(mlen, dels+1)
    de=GCdet(mlen, dels+1)
    si=Simulator(mlen, dels+1)
    for dataInt in range(frm,to,1):
        for didx in range(mlen):
            orgdata= en.genMsg(dataInt,mlen)
            deldata=si.pop(orgdata,didx)
            data=si.breakString(orgdata)
            data=si.binString2int(data)
            parity=(en.paritize(np.array(data)))
            success+= recover(orgdata, deldata, parity, mlen, de)
    print('Sucess',name,':',success)
import random

def StressTestMulti2(mlen=16):
    '''Test on all 16-bit binary number with
    one deletion occuring at any posision.
    This test takes a while'''
    def setup():
        return '''
import time
mlen={}
dels=1; success=0; fail=0
en=Encoder(mlen, dels+1)
de=Decoder(mlen, dels+1)
si=Simulator(mlen, dels)
t1=time.time()'''                     
    def run():
        return '''
dataInt =  random.randrange(2**mlen)
didx = random.randrange(mlen)
orgdata= en.genMsg(dataInt,mlen)
deldata=si.pop(orgdata,didx)
data=si.breakString(orgdata)
data=si.binString2int(data)
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
dels=1; success=0; fail=0
en=Encoder(mlen, dels+1)
de=GCdet(mlen, dels+1)
si=Simulator(mlen, dels+1)
t1=time.time()'''                     
    def run():
        return '''
dataInt =  random.randrange(2**mlen)
didx = random.randrange(mlen)
orgdata= en.genMsg(dataInt,mlen)
deldata=si.pop(orgdata,didx)
data=si.breakString(orgdata)
data=si.binString2int(data)
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
import time
mlen={}
dels=1; success=0; fail=0
en=Encoder(mlen, dels+3)
de=GCdet(mlen, dels+3)
si=Simulator(mlen, dels+3)
t1=time.time()'''                     
    def run():
        return '''
dataInt =  random.randrange(2**mlen)
didx = random.randrange(mlen)
orgdata= en.genMsg(dataInt,mlen)
deldata=si.pop(orgdata,didx)

data=si.breakString(orgdata)
data=si.binString2int(data)
parity=en.paritize(np.array(data))

if recover(orgdata, deldata, parity, mlen, de):
    success+=1
else:
    fail+=1

if (success+fail)%10000 == 0:
    print('Success: ', success, 'fai: ', fail)'''
    times=[]
    #bits=[768,1024,1536,2048]
    bits=[128,192,256,384,512,768,1024,1536,2048]
    #bits=[1536,2048]
    for i in range(len(bits)):
        print('Start',bits[i])
        times.append((timeit.timeit(stmt=run(),
                                   setup=setup().format(bits[i]),
                                   globals=globals(),
                                   number=100)))
        print('End',bits[i])
    print(bits)
    print(times)
    import matplotlib.pyplot as plt
    plt.plot(bits,times, 'ro')
    plt.show()

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
if __name__ == '__main__':
    main()
