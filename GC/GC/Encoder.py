import numpy as np
import math
class Encoder:
    def __init__(self, mlen, numEn):
        self.numBlock, self.blockLength = self.getDem(mlen)
        self.gf=self.nextPrime(2**self.blockLength)
        self.enVec=self.getEnVec(numEn, self.numBlock)%self.gf
        
      
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
    @staticmethod
    def getEnVec(numVec, length):
        '''the last rows are zeros'''
        vectors=list()
        vectors = np.reshape([i**x for i in range(1,numVec+1) for x in range(length+numVec)],(numVec,length+numVec))
        vectors[:,length:]=0
        return np.transpose(vectors)
    
    def genMsg(self, dataInt, mLen):
        '''\return a tuple of original message and deleted message'''
        if dataInt>2**mLen: raise TooShortLength
        orim = bin(dataInt)[2:].zfill(mLen)
        return orim
    def paritize(self, data):
        return np.dot(data, self.enVec[:len(data),:])%self.gf
    def breakString(self, inputString, blockLengths):
        if type(blockLengths) == int:
            output=[inputString[i:i+blockLengths] for i in range(0, len(inputString), blockLengths)]
            numMissingZeros=blockLengths-len(output[-1])
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
    def binString2int(self, binStrings):
        if type(binStrings) == str:
            return int(binStrings,2)
        elif type(binStrings)==list:
            return [int(binString,2) for binString in binStrings]
    def __str__(self):
        return ('Decoding matrix: \n'+str(self.enVec)+
                '\nnumBlock: ' + str(self.numBlock) + 
                '\nblockLength: ' + str(self.blockLength) + 
                '\ngf({})'.format(self.gf))
    def encode(self,data):
        if type(data)==int: data = genMsg(data, self.numBlock*self.blockLength)
        intLst=self.binString2int(self.breakString(data,self.blockLength))
        parity = self.paritize(intLst)
        return parity