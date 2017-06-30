from multiprocessing import Process, queues
import multiprocessing
from Encoder import *
from Decoder import *
from Simulator import *
import timeit
import time

def test():
    orgdata='0110000000000000'
    deldata='110000000000000'
    UnitTest(orgdata, deldata)
def main():
    bit16test()
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
        p = Process(target=StressTestMulti, args=(i,i+jump,count, results))
        count+=1
        pp.append(p)
        p.start()
    for p in pp:
        p.join()
    while count>0:
        result= results.get()
        success+=result[0]
        fail+=result[1]
        count-=1       
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
    mlen=len(orgdata)
    dels=mlen-len(deldata)
    success = fail = 0
    en=Encoder(mlen, dels+1)
    de=Decoder(mlen, dels+1)
    si=Simulator(mlen, dels)
    #print(en)
    data=si.breakString(orgdata)
    data=si.binString2int(data)
    print()
    print('data int', data)
    parity=np.matrix(en.paritize(np.matrix([data])))
    #print('parity: ', parity)
    dataIntCases, dataBinStringCases=si.getCases(deldata)
    caught=False
    recoveredData=''
    for idx in range(len(dataIntCases)):
        if gfCheck(dataIntCases[idx], si.blockLength, si.gf):
            data=np.matrix(dataIntCases[idx])
            decodedData, valid =de.decode(data, parity)
            print('Case', decodedData, valid)
            if valid:
                temp = si.int2binString(decodedData)
                if editDist(deldata,temp) == True:
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
            dataIntCases, dataBinStringCases=si.getCases(deldata)
            recoveredData=''
            isFailed=False
            for idx in range(len(dataIntCases)):
                if gfCheck(dataIntCases[idx], si.blockLength, si.gf):
                    data=np.matrix(dataIntCases[idx])
                    decodedData, valid =de.decode(data, parity)
                    if valid:
                        temp = si.int2binString(decodedData)
                        if editDist(deldata,temp) == True:
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
    results.put((success, fail))
if __name__ == '__main__':
    main()
