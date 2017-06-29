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
    def _getDelLocCases(self, numBlock, numDel, start=0, lst=list(), root=list()):
        '''Recursion'''
        if numDel==1:
            for loc in range(start, numBlock,1):
                lst.extend(root)
                lst.append(loc)
        else:
            for loc in range(start, numBlock,1):
                root.append(loc)
                self._getDelLocCases(numBlock, numDel-1, loc, lst, root)
                del root[-1]
        return lst

    def getDelLocCases(self):
        lst=self._getDelLocCases(self.numBlock, self.numDel, lst=list())
        return np.reshape(lst,(int(len(lst)/self.numDel),self.numDel))

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
        return bloLenCases

    def getCases(self, delMessage):
        #numBlock, blockLength = self.getDem(mLen)
        casesInt=list()
        casesBinString=list()
        bloLenCases = self.getBloLenCases()
        for bloLenCase in bloLenCases:
            caseBinString=self.breakString(delMessage, bloLenCase)
            caseInt=self.del2gf(caseBinString)
            casesInt.append(caseInt)
            casesBinString.append(caseBinString)
        return casesInt, casesBinString

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

    def binString2int(self, binStrings):
        if type(binStrings) == str:
            return int(binStrings,2)
        elif type(binStrings)==list:
            return [int(binString,2) for binString in binStrings]
    def int2binString(self, npbinString):
        lastLen=self.mlen%self.blockLength
        binString=''
        for item in np.nditer(npbinString[0]):
            binString+=bin(int(item))[2:].zfill(self.blockLength)
        if lastLen != 0: binString=binString[:-self.blockLength]+binString[-lastLen:]
        return binString
    def pop(self, inputString,idx):
        if type(idx)==int: idx=[idx]
        chars = [c for c in inputString]
        for i in sorted(idx, reverse=True):
            del chars[i]
        return ''.join(chars)
    def NotAllBitEqual(ori,rec):
        print('ori: ',ori)
        print('rec: ',rec)