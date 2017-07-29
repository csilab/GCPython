import numpy as np
import math
class Data:
    def __init__(self, mlen, de, numDel, s=None, p=None):
        """
         Initialization of each deleted sequence.

        Args:
            s: The binary string of the deleted sequence.
            p: A list of parity integers.
            mlen: The bit length of the original sequences.
        """
        if s != None: self.s = s
        if p != None: self.p = p
        self.mlen = mlen
        self.de = de
        self.numBlock, self.blockLength = self.getDem(mlen)
        self.numDel = numDel
        self.table = self.getTable()
        
    def case(self):
        """
         Return a LIST of all possible indices where deletions might occur. Example, [[0], [1], [2], [3]] is the result of calling case(numBlock=4, numDel=1).
         Notice this call is not memory efficient because it actaully creates a list in memory. Use caseGen for a more memory friendly method.

        Args:
            numBlock: Number of blocks where deletions might occur.
            numDel: Number of deletions.

        Returns:
            A list of all possible indices where deletions might occur. 

        Raises:
            None
        """
        numBlock, numDel = self.numBlock, self.mlen-len(self.s)
        def case_rec(numDel, start=0, lst=list(), root=list()):
            """
             A recursive method assiting the generation of deletion cases. This is not memory and time efficient.

            Args:
                numDel: Number of deletions.
                start: The first deletion index of the remaining deletion.
                lst: 1-D array of guesses for deletion indices. To be broken down into a x by numDel 2-D array.
                root: The base indices for each each guess.

            Returns:
                A list of all possible indices where deletions might occur. 

            Raises:
                None
            """
            if numDel==1:
                for loc in range(start, numBlock,1):
                    lst.extend(root)
                    lst.append(loc)
            else:
                for d in range(start, numBlock,1):
                    root.append(d)
                    case_rec(numDel-1, d, lst, root)
                    del root[-1]
            return lst
        cases=case_rec(numDel, lst=list())
        return np.reshape(cases,(int(len(cases)/numDel),numDel))
    
    def caseGen(self, reverse = False):
        """
         Return a GENERATOR of all possible indices where deletions might occur. Example, [[0], [1], [2], [3]] is the result of calling case(numBlock=4, numDel=1).
         Notice this call does not use too much memory because it return a generator instead of a actual list. It is also less time consumming.

        Args:
            numBlock: Number of blocks where deletions might occur.
            numDel: Number of deletions.

        Returns:
            A generator of all possible indices where deletions might occur. 

        Raises:
            None
        """
        numBlock, numDel = self.numBlock, self.mlen-len(self.s)
        def case_rec(numDel, first, last, root=list()):
            """
             A recursive method assiting the generation of deletion cases.

            Args:
                numDel: Number of deletions.
                start: The first deletion index of the remaining deletion.
                root: The base indices for each each guess.

            Returns:
                A generator of all possible indices where deletions might occur. 

            Raises:
                None
            """
            if numDel==1:
                for current in range(first, last, change):
                    root.append(current)
                    yield root
                    del root[-1]
            else:
                for current in range(first, last, change):
                    root.append(current)
                    yield from case_rec(numDel-1, current , last, root)
                    del root[-1]
        if reverse == False:
            change=1
            return case_rec(numDel, 0, numBlock) 
        else:
            change=-1
            return case_rec(numDel, numBlock-1, 0-1)
    def caseGenFast(self, reverse = False):
        """
         Return a GENERATOR of all possible indices where deletions might occur. Example, [[0], [1], [2], [3]] is the result of calling case(numBlock=4, numDel=1).
         Notice this call does not use too much memory because it return a generator instead of a actual list. It is also less time consumming.

        Args:
            numBlock: Number of blocks where deletions might occur.
            numDel: Number of deletions.

        Returns:
            A generator of all possible indices where deletions might occur. 

        Raises:
            None
        """
        numBlock, numDel = self.numBlock, self.mlen-len(self.s)
        def case_rec(first, last, idx=0, pprime=0):
            """
             A recursive method assiting the generation of deletion cases.

            Args:
                numDel: Number of deletions.
                start: The first deletion index of the remaining deletion.
                root: The base indices for each each guess.

            Returns:
                A generator of all possible indices where deletions might occur. 

            Raises:
                None
            """
            if idx != numDel-1:
                for current in range(first, last, change):
                    if current != first:
                        pprime-=d[-1][current]
                    root[idx] = current
                    yield from case_rec(current, last, idx + 1, pprime)
                    if idx==0 or current != first:
                        pprime+=d[idx][current]
            else:
                for current in range(first, last, change):
                    root[idx] = current
                    if current != first:
                        pprime-=d[-1][current]
                    print(pprime)
                    yield root
                    if idx==0 or current != first:
                        pprime+=d[idx][current]

        d= self.baseCase2(numDel)
        root=[0]*numDel
        pprime=sum(d[-1])
        if reverse == False:
            change=1
            return case_rec(0, numBlock, pprime=pprime) 
        else:
            change=-1
            return case_rec(numBlock-1, -1, pprime=pprime)
    def rcaseGen(self, sidx, number=None):
        """
         Return a GENERATOR of all possible indices where deletions might occur. Example, [[0], [1], [2], [3]] is the result of calling case(numBlock=4, numDel=1).
         Notice this call does not use too much memory because it return a generator instead of a actual list. It is also less time consumming.

        Args:
            numBlock: Number of blocks where deletions might occur.
            numDel: Number of deletions.

        Returns:
            A generator of all possible indices where deletions might occur. 

        Raises:
            None
        """
        numBlock, numDel = self.numBlock, self.mlen-len(self.s)
        sidx=[sidx+1]
        def case_rec(numDel, last=0, root=list()):
            """
             A recursive method assiting the generation of deletion cases.

            Args:
                numDel: Number of deletions.
                last: The last deletion index of the remaining deletion.
                root: The base indices for each each guess.

            Returns:
                A generator of all possible indices where deletions might occur. 

            Raises:
                None
            """
            if numDel==1:
                for loc in range(numBlock - sidx[0], last -1 , -1):
                    if count[0] >= number: break
                    else:
                        root.append(loc)
                        yield root
                        del root[-1]
                    count[0]+=1
            else:
                idx = 0
                for i in range(len(self.table[numDel])):
                    if self.table[numDel][i]>=sidx[0]:
                        idx = i
                        break
                sidx[0] = sidx[0] - self.table[numDel][idx - 1]
                for d in range(numBlock - idx, last -1 , -1):
                    if count[0] >= number: break
                    root.append(d)
                    yield from case_rec(numDel-1, d, root)
                    del root[-1]
        if number == None: number = self.numCase()
        count=[0]
        return case_rec(numDel)

    def caseGenDistinctFast(self):
        """
         Return a GENERATOR of all possible indices where deletions might occur. Example, [[0], [1], [2], [3]] is the result of calling case(numBlock=4, numDel=1).
         Notice this call does not use too much memory because it return a generator instead of a actual list. It is also less time consumming.

        Args:
            numBlock: Number of blocks where deletions might occur.
            numDel: Number of deletions.

        Returns:
            A generator of all possible indices where deletions might occur. 

        Raises:
            None
        """
        numBlock, numDel = self.numBlock, self.mlen-len(self.s)
        def case_rec(tempNumDel, pprime, start=-1, root=list()):
            """
             A recursive method assiting the generation of distinct deletion cases.

            Args:
                numDel: Number of deletions.
                start: The first deletion index of the remaining deletion.
                root: The base indices for each each guess.

            Returns:
                A generator of all possible indices where deletions might occur. 

            Raises:
                None
            """
            if tempNumDel < numDel:# and loc < numBlock-1:
                for loc in range(numBlock-1, start, -1):
                    root.append(loc)
                    pprime+=d[tempNumDel-1][loc]*self.de.enVec[loc,:]
                    #pprime-=d[tempNumDel-1][loc]
                    #yield root, pprime
                    yield from case_rec(tempNumDel+1, np.array(pprime), loc - 1, root)
                    del root[-1]
                    pprime-=d[tempNumDel][loc]*self.de.enVec[loc,:]
                    #pprime+=d[tempNumDel][loc]
            else:
                for loc in range(numBlock-1, start, -1):
                    root.append(loc)
                    pprime+=d[tempNumDel-1][loc]*self.de.enVec[loc,:]
                    #pprime-=d[tempNumDel-1][loc]
                    yield root, pprime
                    del root[-1]
                    pprime-=d[tempNumDel][loc]*self.de.enVec[loc,:]
                    #pprime+=d[tempNumDel][loc]
        d= self.baseCase(numDel)
        return case_rec(1, self.p - np.dot(d[0],self.de.enVec))
        #return case_rec(1, sum(d[0]))

    def numCase(self):
        return self.table[self.numDel][self.numBlock]
    
    def getTable(self):
        l=self.numBlock+1
        t = []
        d1 = [1]*l
        d1[0]=0
        t.append(d1)
        for n in range(self.numDel):
            t.append([sum(t[-1][:i+1]) for i in range(l)])
        return t
    
    def decode(self, dels):
        """
         A recursive method assiting the generation of deletion cases. This is not memory and time efficient.

        Args:
            dels: A list of deltion indices.
            de: A decoder that has a decode method.

        Returns:
            A binary string of the recovered sequence.
        """
        b = self.breakString(self.s, dels) # Bring the deleted sequence in to blocks of smaller binary strings with the deleted bits removed.
        i = self.bin2int(b) # convert each block in b into an equivalent integer.
        for d in dels: i[d]=0 # set the blocks that contain the deletion to zeros.
        #print(i, dels)
        r, valid =self.de.decode(i, self.p, dels) # decode using a decoder, r is a list of candidates for the deleted value.
        if not valid: return None# valid means it has passed the parity check.
        #print('Valid')
        r = self.int2bin(r) # converts the recovered deleted values to binary strings.
        for i in range(len(r)):
            b[dels[i]]=r[i]
        #if not self.levCheck(r, b, dels):
        #    print('failed Lev')
        #    return None #Do the Levanshtein Distance check of the recovered deleted binary strings.
        lastLen=self.mlen%self.blockLength
        b[-1]=b[-1][-lastLen:] # re-adjust the length of the last block in case of awkward mlen (not 2^x).
        #print('returned something')
        return ''.join(b) # return the sequence if all tests are passed.

    def onedecode(self):

        """
            A recursive method assiting the generation of deletion cases. This is not memory and time efficient.

        Args:
            dels: A list of deltion indices.
            de: A decoder that has a decode method.

        Returns:
            A binary string of the recovered sequence.
        """
        data = self.baseCase(1)
        pprime = self.p - np.dot(data[0],self.de.enVec)
        delBlock = self.numBlock - 1
        for i in range(self.numBlock):
            pprime+=data[0][delBlock]*self.de.enVec[delBlock,:]
            #print(pprime,delBlock)
            X, valid = self.de._onedel(pprime,delBlock)
            if valid: break
            pprime-=data[1][delBlock]*self.de.enVec[delBlock,:]
            delBlock-=1
        X = self.int2bin(X) # converts the recovered deleted values to binary strings.
        left = delBlock*self.blockLength
        right = (delBlock+1)*self.blockLength-1
        if delBlock == self.numBlock-1:
            lastLen=self.mlen%self.blockLength
            X =  X[-lastLen:]
        return self.s[:left] + X + self.s[right:] # return the sequence if all tests are passed.
    def twodecode(self):

        """
            A recursive method assiting the generation of deletion cases. This is not memory and time efficient.

        Args:
            dels: A list of deltion indices.
            de: A decoder that has a decode method.

        Returns:
            A binary string of the recovered     sequence.
        """
        cases = self.caseGenDistinctFast()
        for case in cases:
            d = case[0]
            pprime = case[1]
            if len(d) ==1: X, valid = self.de._onedel(pprime,d[0])
            else: X, valid = self.de._twodels(pprime,d)
            #print(pprime, d)
            if valid:
                #print("valid")
                X = self.int2bin(X) # converts the recovered deleted values to binary strings. 
                for i in range(len(d)):
                    left = d[i]*self.blockLength
                    right = (d[i]+1)*self.blockLength-(3-len(d))
                    if d[i] == self.numBlock-1:
                        lastLen=self.mlen%self.blockLength
                        X[i] =  X[i][-lastLen:]
                    self.s = self.s[:left] + X[i] + self.s[right:] # return the sequence if all tests are passed.
                    #print(self.s)
                return self.s
        raise DecodingError
    def int2bin(self, num):
        """
         Converts an integer or a list of integers to binary strings with zeros left filled to make them blockLength size.

        Args:
            num: an integer or a list of integers.

        Returns:
            A binary string or a list of binary strings with zeros left filled to make them blockLength size
        """
        if type(num) != list:
            return bin(int(num))[2:].zfill(self.blockLength)
        else:#list
            output=[]
            for n in num:
                output.append(bin(int(n))[2:].zfill(self.blockLength))
            return output
    def baseCase(self, numDel=1):
        lst = []
        lst.append(self.bin2int(self.breakString(self.s, [self.numBlock-1]))) # convert each block in b into an equivalent integer.
        for i in range(1, numDel+1):
            lst.append(self.bin2int(self.breakString(self.s, list(range(i)))))
            for j in range(i):
                lst[-1][j]=0
        return lst
    def baseCase2(self, numDel=1):
        dels=[self.numBlock-1]*self.numDel
        lst = []
        lst.append(self.bin2int(self.breakString(self.s, dels))) # convert each block in b into an equivalent integer.
        lst[-1][self.numBlock-1]=0
        for i in range(self.numDel):
            dels[i]=0
            lst.append(self.bin2int(self.breakString(self.s, dels)))
            for j in set(dels):
                lst[-1][j]=0
        return lst
    @staticmethod
    def bin2int(b):
        """
         Converts a binary string or a list of binary strings to integers.

        Args:
            b: a binary string or a list of binary strings.

        Returns:
            A integer or a list of integers.
        """
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
        """
         Return the number of blocks and the bit length of each block for a given total bit length k.

        Args:
            k: the total bit length of a sequence.

        Returns:
            blockLength: the ceiling of log k based 2.
            numBlock: the ceiling of k devided by blockLength.
        """
        blockLength=int(math.ceil(math.log(k,2)))#round up
        numBlock=int(math.ceil(k/blockLength))#round up
        return numBlock, blockLength   

    @staticmethod
    def levCheck(r, b, dels):
        """
         Check the posibility of each recovered deleted binary string using Lavenshtein distance algorithms.

        Args:
            r: a list of recovered deleted binary string.
            dels: indices of the deletions.

        Returns:
            True if all recovery pass the Lev test.
            False if any one them fails.
        """
        def lev(strX, strY):
                '''Check the Lavenshtein distance of the two strings strX and strY.

                Args:
                    strX: the first string.
                    strY: the second string.

                Returns:
                    True if distance is greater than number of deletions.
                    False otherwise.
                '''
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

    def breakString(self, s, dels):
        """
         Break a long binary string into blocks of smaller binary strings
         with each block has the length of self.blocklength - number of deletion in that block.

        Args:
            s: the binary string to break down.
            dels: indices of the deletion in the string s.
        Returns:
            A list of smaller binary strings.
        """
        lens=[self.blockLength]*self.numBlock #create an array and fill it with blockLengths integers.
        for d in dels: #decrement the length of each block that has one or more deletions
            lens[d]-=1
        output=[]
        idx=0
        for l in lens: #build a binary string list with each block's length specified by the lens list.
            output.append(s[idx:idx+l])
            idx+=l
        numZeros=lens[-1]-len(output[-1])
        output[-1]=output[-1].zfill(numZeros) #left fill zeros to the last block in case of awkward mlen.
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

