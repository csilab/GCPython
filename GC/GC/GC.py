import multiprocessing
from Encoder import *
from Decoder import *
from Simulator import *
import timeit
import time
def editDist(strX='101', strY='101'):
    #x must be the shorter one
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
        if donotreturn==False: return False
    return True
def gfCheck(data, blockLength, gf):
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
    mlen=len(orgdata)
    dels=mlen-len(deldata)
    success=0
    fail=0
    dup=0
    conflix=0
    en=Encoder(mlen, dels+1)
    de=Decoder(mlen, dels+1)
    si=Simulator(mlen, dels)
    print(en)
    data=si.breakString(orgdata)
    data=si.binString2int(data)
    print('data int', data)
    parity=np.matrix(en.paritize(np.matrix([data])))
    print('parity: ', parity)
    dataIntCases, dataBinStringCases=si.getCases(deldata)
    recoveredData=''
    for idx in range(len(dataIntCases)):
        print('case: ',dataIntCases[idx])
        data=np.matrix(dataIntCases[idx])
        decodedData, valid =de.decode(data, parity)
        print('decode: ', decodedData, valid)
        if valid:
            temp = si.int2binString(decodedData)
            if temp==recoveredData:
                dup+=1
            elif len(recoveredData)==0:
                recoveredData = temp
                print('new rec:, ', decodedData)
            else:
                conflix+=1
                if editDist(deldata,temp):
                    recoveredData = temp
                    print('new rec:, ', decodedData)
    if recoveredData == orgdata:
        success+=1
    else: 
        fail+=1
        print()
        print('org',orgdata)
        print('rec',recoveredData)
        print('del',deldata)
    print('Success:',success,'fail:',fail,'dup:',dup,'conflict:',conflix,)

orgdata='0010000100001000111'
deldata='0010001000000111'
#UnitTest(orgdata, deldata)

def StressTestOne():
    '''Test on all 16-bit binary number with
    one deletion occuring at any posision.
    This test takes a while'''
    dels=1
    mlen=16
    success=0
    fail=0
    dup=0
    conflix=0
    en=Encoder(mlen, dels+1)
    de=Decoder(mlen, dels+1)
    si=Simulator(mlen, dels)
    for dataInt in range(2**mlen):
        for didx in range(mlen):
            orgdata= en.genMsg(dataInt,mlen)
            deldata=si.pop(orgdata,didx)
            data=si.breakString(orgdata)
            data=si.binString2int(data)
            parity=np.matrix(en.paritize(np.matrix([data])))
            dataIntCases, dataBinStringCases=si.getCases(deldata)
            recoveredData=''
            isFail=False
            for idx in range(len(dataIntCases)):
                if gfCheck(dataIntCases[idx], si.blockLength, si.gf):
                    data=np.matrix(dataIntCases[idx])
                    decodedData, valid =de.decode(data, parity)
                    if valid:
                        temp = si.int2binString(decodedData)
                        if len(recoveredData)==0 and editDist(deldata,temp) == True:
                            recoveredData = temp
                        else:
                            if temp==recoveredData:
                                dup+=1
                            else:
                                print('Success:',success,'fail:',fail,'dup:',dup)
                                isFail=True
                                break
            if isFail:
                fail+=1
            else:
                if recoveredData == orgdata:
                    success+=1
                else: 
                    print()
                    print('org',orgdata)
                    print('rec',recoveredData)
                    print('del',deldata)
def StressTestMulti(frm, to):
    '''Test on all 16-bit binary number with
    one deletion occuring at any posision.
    This test takes a while'''
    dels=1
    mlen=16
    success=0
    fail=0
    dup=0
    conflix=0
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
            dataIntCases, dataBinStringCases=si.getCases(deldata)
            recoveredData=''
            isFail=False
            for idx in range(len(dataIntCases)):
                if gfCheck(dataIntCases[idx], si.blockLength, si.gf):
                    data=np.matrix(dataIntCases[idx])
                    decodedData, valid =de.decode(data, parity)
                    if valid:
                        temp = si.int2binString(decodedData)
                        if len(recoveredData)==0 and editDist(deldata,temp) == True:
                            recoveredData = temp
                        else:
                            if temp==recoveredData:
                                dup+=1
                            else:
                                print('Success:',success,'fail:',fail,'dup:',dup)
                                isFail=True
                                break
            if isFail:
                fail+=1
            else:
                if recoveredData == orgdata:
                    success+=1
                else: 
                    print()
                    print('org',orgdata)
                    print('rec',recoveredData)
                    print('del',deldata)
#StressTestOne()
#print(timeit.timeit(editDist,number=100000))
from multiprocessing import Process
import os

def f(name):
    while True:
        print('hello', name)

if __name__ == '__main__':
    pp=[]
    frm=0
    to=(2**16)
    jump=to//8
    for i in range(frm,to,jump):
        print('started ',i,'to',i+jump)
        p = Process(target=StressTestMulti, args=(i,i+jump))
        pp.append(p)
        p.start()
    for p in pp:
        p.joint()
