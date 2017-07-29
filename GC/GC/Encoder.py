import numpy as np
import math
class Encoder:
    def __init__(self, mlen, numVec):
        self.numBlock, self.blockLength = self.getDem(mlen)
        self.gf=self.nextPrime(2**self.blockLength)
        self.gfinv = self.getgfdict()
        self.numVec=numVec
        #self.enVec=self.oldgetEnVec(self.numBlock,numVec)
        self.enVec=self.getEnVec(numVec)
        self.dvec=np.array(self.enVec[:,:1]).ravel() #only the first columm for fast one deletion decoding
        self.cvec=self.enVec[:,1:] #only the rest of enVec for fast one deletion checking
        
    def getgfdict(self):
        d={}
        for i in range(1, self.gf):
            for j in range(1, self.gf):
                if i*j%self.gf==1:
                    d[i]=j
                    d[j]=i
        d[0]=None
        return d

    def isPrime(self, num):
         if num < 2: return False
         for i in range(2, int(math.sqrt(num)) + 1):
             if num % i == 0:
                 return False
         return True

    def nextPrime(self, num):
        while self.isPrime(num) is False: num+=1
        return num

    def getDem(self, k): #k == original message length
        blockLength=int(math.ceil(math.log(k,2)))#round up
        numBlock=int(math.ceil(k/blockLength))#round up
        return numBlock, blockLength

    def oldgetEnVec(self, numVec):
        '''the last rows are zeros'''
        length=self.numBlock
        vectors=list()
        vectors = np.reshape([i**x for i in range(1,numVec+1) for x in range(length)],(numVec,length))
        return np.transpose(vectors)%self.gf

    def getEnVec(self, numVec):
        def inv(A):
            for x in np.nditer(A, op_flags=['readwrite']):
                x[...] = self.gfinv[int(x)]
        x = np.array(range(self.numBlock),np.int64)
        y = np.array(range(self.numBlock,self.numBlock+numVec),np.int64)
        A=(x.reshape((-1,1)) - y)%self.gf
        inv(A)
        #A[self.numBlock:,:]=[0]
        return A%self.gf

    @staticmethod
    def genMsg(dataInt, mLen):
        '''\return a tuple of original message and deleted message'''
        if dataInt>2**mLen: raise TooShortLength
        orim = bin(dataInt)[2:].zfill(mLen)
        return orim

    def paritize(self, data):

        if type(data) == str:
            data = np.array(self.binString2int(self.breakString(data)))
        p= np.dot(data, self.enVec[:len(data),:])%self.gf
        #print('org', data)
        return p

    def breakString(self, inputString, blockLengths=None):
        if blockLengths==None:
            output=[inputString[i:i+self.blockLength] for i in range(0, len(inputString), self.blockLength)]
            numMissingZeros=self.blockLength-len(output[-1])
            output[-1]=numMissingZeros*'0' + output[-1]
        elif type(blockLengths)==list:
            output=list()
            idx=0
            for blockLength in blockLengths:
                output.append(inputString[idx:idx+blockLength])
                idx+=blockLength
            numMissingZeros=blockLengths[-1]-len(output[-1])
            output[-1]=numMissingZeros*'0' + output[-1]
        return output

    @staticmethod
    def binString2int(b):
        if type(b) == str:
            return int(b,2)
        elif type(b)==list:
            output=[]
            for eachb in b:
                if len(eachb) == 0:
                    output.append(0)
                else:
                    output.append(int(eachb,2))
        return output 

    @staticmethod
    def pop(inputString,idx):
        if type(idx)==int: idx=[idx]
        chars = [c for c in inputString]
        for i in sorted(idx, reverse=True):
            del chars[i]
        return ''.join(chars)

    def __str__(self):
        return ('Decoding matrix: \n'+str(self.enVec)+
                '\nnumBlock: ' + str(self.numBlock) + 
                '\nblockLength: ' + str(self.blockLength) + 
                '\ngf({})'.format(self.gf))