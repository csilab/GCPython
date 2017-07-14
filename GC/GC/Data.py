import numpy as np
import math
class Data:
    def __init__(self, s, p, mlen):
        """
         Initialization of each deleted sequence.

        Args:
            s: The binary string of the deleted sequence.
            p: A list of parity integers.
            mlen: The bit length of the original sequences.
        """
        self.s = s
        self.p = p
        self.mlen = mlen
        self.numBlock, self.blockLength = self.getDem(mlen)

    def decode(self, dels, de):
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
        pi= np.concatenate((i,self.p)) # combine the list i with the list of parity.
        r, valid =de.decode(pi, dels) # decode using a decoder, r is a list of candidates for the deleted value.
        if not valid: return None # valid means it has passed the parity check.
        r = self.int2bin(r) # converts the recovered deleted values to binary strings.
        if not self.levCheck(r, b, dels): return None #Do the Levanshtein Distance check of the recovered deleted binary strings.
        lastLen=self.mlen%self.blockLength
        b[-1]=b[-1][-lastLen:] # re-adjust the length of the last block in case of awkward mlen (not 2^x).
        return ''.join(b) # return the sequence if all tests are passed.

    def int2bin(self, num):
        """
         Converts an integer or a list of integers to binary strings with zeros left filled to make them blockLength size.

        Args:
            num: an integer or a list of integers.

        Returns:
            A binary string or a list of binary strings with zeros left filled to make them blockLength size
        """
        if type(num) == int:
            return bin(int(num))[2:].zfill(self.blockLength)
        else:#list
            output=[]
            for n in num:
                output.append(bin(int(n))[2:].zfill(self.blockLength))
            return output
            
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
