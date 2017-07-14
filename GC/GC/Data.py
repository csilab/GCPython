import numpy as np
import math
class Data:
    def __init__(self, s, p, mlen):
        self.s = s
        self.p = p
        self.mlen = mlen
        self.numBlock, self.blockLength = self.getDem(mlen)

    def decode(self, dels, de):
        b = self.breakString(self.s, dels)
        i = self.bin2int(b)
        self.zero(i, dels)
        pi= np.concatenate((i,self.p))
        r, valid =de.decode(pi, dels)
        if not valid: return None
        r = self.int2bin(r)
        if not self.levCheck(r, b, dels): return None
        lastLen=self.mlen%self.blockLength
        b[-1]=b[-1][-lastLen:]
        return ''.join(b)

    @staticmethod
    def levCheck(r, b, dels):
        def lev(strX, strY):
                '''Check the Lavenshtein distance of the two strings.
                If distance is greater than number of deletions -> False otherwise -> True'''
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
        for i in range(len(r)):
            if lev(b[dels[i]],r[i]):
                b[dels[i]]=r[i]
            else:
                return False
        return True
    
    def int2bin(self, num):
        if type(num) == int:
            return bin(int(num))[2:].zfill(self.blockLength)
        else:#list
            output=[]
            for n in num:
                output.append(bin(int(n))[2:].zfill(self.blockLength))
            return output

    @staticmethod
    def zero(i, dels):
        for d in dels:
            i[d]=0
            
    @staticmethod
    def bin2int(b):
        if type(b) == str:
            return int(b,2)
        else:
            output=[]
            for _b in b:
                try:
                    output.append(int(_b,2))
                except:
                    output.append(None)
        return output  
    
    @staticmethod
    def getDem(k): #k == original message length
        blockLength=int(math.ceil(math.log(k,2)))#round up
        numBlock=int(math.ceil(k/blockLength))#round up
        return numBlock, blockLength   

    def breakString(self, s, dels):
        lens=[self.blockLength]*self.numBlock #fill the array with blockLengths
        for d in dels: #decrement length for each corresponding deletion, deletion is the block idx of a deletion
            lens[d]-=1
        output=[]
        idx=0
        for l in lens:
            output.append(s[idx:idx+l])
            idx+=l
        #add zeros to the end
        numZeros=lens[-1]-len(output[-1])
        output[-1]=output[-1].zfill(numZeros)
        return output
    @staticmethod
    def gfCheck(data, blockLength, gf):
        '''Check if each element of data is within the range val < 2^ blockLength'''
        for val in data:
            if val >= 2**blockLength and val < gf:
                print(data)
                return False
        else:
           return True
