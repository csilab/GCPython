import numpy as np
from Encoder import *
class Decoder(Encoder):
    def __init__(self, mlen, numEn):
        super().__init__(mlen, numEn)
        self.constrainDecVec= self.enVec[:,:-1]
        self.checkerDecVec = self.enVec[:,-1:]
    def decode(self, data, parity):
        #last parity -> checkerParity, the rest is constrainParity
        constrainParity, checkerParity = parity[:,:-1], parity[:,-1:]
        
        #create constrain vectors and result vectors
        numColumm=data.shape[1]
        constrains=np.identity(numColumm)
        data, constrains = self.delColGF(data, constrains, self.gf)
        
        #concatenate result vector with parities
        paritizedData=np.concatenate((data,constrainParity),1)
        paritizedData=self.trimCol(paritizedData,paritizedData.shape[1]-constrains.shape[0])       
        
        #concatenate constrains vectors with parity vector
        paritizedConstrains=np.concatenate((constrains,self.constrainDecVec),1)
        paritizedConstrains=self.trim2Square(paritizedConstrains)
        #solve matrix and validate the result with the checker parity
        X=self.solve(paritizedConstrains,paritizedData)  
        valid=np.array_equal(np.dot(X, self.checkerDecVec)%self.gf,checkerParity)
        
        return X, valid
    
    def solve(self, A, B):
        '''Find X in GF field where AX=B'''
        detA=int(np.linalg.det(A))
        invA=np.linalg.inv(A)
        #adjust the invA into an equi. GF field
        invDetAinGF=self.invgf(int(np.round(detA%self.gf)))
        adjInvA=invA*detA*invDetAinGF #adjusted inverse of matrix A
        #Calculate result matrix
        X=np.dot(B,adjInvA)
        return X%self.gf
        
    def delColGF(self, data, constrains, indicator):
        '''Delete columms whose value is equal to self.gf'''
        numColumm=data.shape[1]
        cidxs=list()
        for cidx in range(numColumm):
            if data.item(0,cidx) == indicator:
                cidxs.append(cidx)
        data=np.delete(data,cidxs,1) #delete columm
        constrains=np.delete(constrains,cidxs,1) #delete columm
        return data,constrains
    
    def trim2Square(self, A):
        numRow=A.shape[0]
        numColumm=A.shape[1]
        rowMore=numRow-numColumm
        if rowMore==0: pass
        elif rowMore>0:
            A=np.delete(A, range(numColumm,numRow,1), 0)
        else: #trim columms
            A=np.delete(A, range(numRow,numColumm,1), 1)
        return A
    def trimCol(self, A, count):
        numColumm=A.shape[1]
        A=np.delete(A, range(numColumm-count,numColumm,1), 1)
        return A

    def invgf(self, x):
        return x**(self.gf-2)%self.gf