import math
import numpy as np
class Simulator:
    def __init__(self, mlen, numDel):
        self.mlen=mlen
        self.numBlock, self.blockLength = self.getDem(mlen)
        self.gf=self.nextPrime(2**self.blockLength)
        self.numDel=numDel
    def isPrime(self, num):
         if num < 2: return False
         for i in range(2, int(math.sqrt(num)) + 1):
             if num % i == 0:
                 return False
         return True
    def nextPrime(self, num):
        while self.isPrime(num) is False: num+=1
        return num

    def getBloLenCases(self):
        '''
        /param numBlock number of message blocks
        /param blockLength length of each block
        /param numDel number of deletions
        /return an array (cases) of array of block lengths after deletions
        '''
        bloLenCases=list()
        delLocCases=self.getDelLocCases()
        for delIdxs in delLocCases:
            bloLenCase=[self.blockLength]*self.numBlock #fill the array with blockLengths
            for delIdx in delIdxs: #decrement length for each corresponding deletion, deletion is the block idx of a deletion
                bloLenCase[delIdx]-=1
            bloLenCases.append(bloLenCase)
        return bloLenCases, delLocCases

    def getCases(self, delMessage):
        casesInt=list()
        casesBinString=list()
        bloLenCases, delLocCases = self.getBloLenCases()
        for i in range(len(bloLenCases)):
            caseBinString=self.breakString(delMessage, bloLenCases[i])
            caseInt = self.binString2int(caseBinString)
            for loc in delLocCases[i]:
                caseInt[loc] = 0
            casesInt.append(caseInt)
            casesBinString.append(caseBinString)
        return casesInt, casesBinString, delLocCases

    def del2gf(self, caseBinStr):
        caseInt=list()
        for i in range(len(caseBinStr)):
            if len(caseBinStr[i]) == self.blockLength: val=self.binString2int(caseBinStr[i])
            else:val=self.gf
            caseInt.append(val)
        return caseInt

    def getDem(self, k): #k == original message length
        blockLength=int(math.ceil(math.log(k,2)))#round up
        numBlock=int(math.ceil(k/blockLength))#round up
        return numBlock, blockLength

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
    def binString2int(binStrings):
        if type(binStrings) == str:
            return int(binStrings,2)
        elif type(binStrings)==list:
            output=[]
            for binString in binStrings:
                if len(binString) == 0:
                    output.append(self.gf)
                else:
                    output.append(int(binString,2))
        return output    

    def int2binString(self, num):
        if type(num) == int:
            return bin(int(num))[2:].zfill(self.blockLength)
        else:
            lastLen=self.mlen%self.blockLength
            binString=''
            for item in num:
                binString+=bin(int(item))[2:].zfill(self.blockLength)
            return binString

    @staticmethod
    def pop(inputString,idx):
        if type(idx)==int: idx=[idx]
        chars = [c for c in inputString]
        for i in sorted(idx, reverse=True):
            del chars[i]
        return ''.join(chars)
    
    def NotAllBitEqual(ori,rec):
        print('ori: ',ori)
        print('rec: ',rec)