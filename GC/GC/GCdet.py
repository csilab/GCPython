
from Decoder import *
import numpy
class GCdet(Decoder):
    def __init__(self, mlen, numEn):
        super().__init__(mlen, numEn)
    @staticmethod
    def _det(dels, numBlock, subMat):
        if subMat.size == 0:
            return 1
        else:
            #print(subMat,dels)
            return GCdet.sign(dels, numBlock) * np.linalg.det(subMat.astype(np.int64))
    def det(self):
        return GCdet._det(self.dels, self.numBlock, self.constrainDecVec[self.dels,:len(self.dels)])
    @staticmethod
    def sign(dels,numBlock):
        numMi = 0
        if len(dels)%2 == 0: #even
            for i in range(len(dels)-1, 0, -1):
                numMi += dels[i] - dels[i-1] - 1
        else:#odd
            numMi += numBlock - dels[-1] - 1
            if len(dels)>1:
                for i in range(len(dels)-2, 0, -1):
                    numMi += dels[i] - dels[i-1] - 1
        if numMi%2==0:
            return 1
        else:
            return -1
    def hieu(self):
        output=[]
        for i in range(len(self.dels)):
            rowPicks = list(self.dels)
            curRow = rowPicks.pop(i)
            if curRow%2==0: #even rows, zero indexing
                sign=1
            else: #odd rows, zero indexing
                sign=-1
            #calculate regular item
            lst=[]
            for j in range(self.numBlock+len(self.dels)): # all envecs coloumn
                if j not in rowPicks:
                    if j == curRow: pass
                    else:
                        subDels=[]                            
                        for row in rowPicks:
                            if row > curRow: #Horizontal slice, below
                                subDels.append(row-1)
                            else:#Horizontal slice, above
                                subDels.append(row)
                        if j < self.numBlock:
                            if j > curRow:#Verital slice, below
                                subDels.append(j-1)
                            else: #Verital slice, above
                                subDels.append(j)
                            rowPicks.append(j)
                            subMat = self.constrainDecVec[sorted(rowPicks),:len(rowPicks)]
                            del rowPicks[-1]
                        else:
                            #colPicks takes all columns of enVecs but the current column
                            colPicks=[x for x in range(len(self.dels)) if x!=(j%self.numBlock)]
                            subMat = self.constrainDecVec[sorted(rowPicks),:][:,colPicks]
                        #calculate item at curRow then append to a list
                        #print(sorted(subDels), self.numBlock-1, subMat)
                        c = sign*GCdet._det(sorted(subDels), self.numBlock-1, subMat)
                        sign*=-1
                        lst.append(c)
                else:pass
            output.append(np.around(lst).astype(int))
        return np.transpose(output)
    def onedel(self,pdata,dels):
        deVec=np.array(self.constrainDecVec[:,:1]).ravel()
        if (dels[0]+self.numBlock)%2 == 1:
            aSign=-1
        else:
            aSign=1
        checkerP=pdata[self.numBlock+1:]
        checkerVec=self.enVec[:,1:]
        deVec[self.numBlock]=-1
        det = GCdet.sign(dels,self.numBlock)*deVec[dels[0]]
        deletion = (aSign*self.invgf(det)*np.inner(pdata,deVec))%self.gf
        #deletion = (aSign*self.invgf(det)*np.inner(pdata,np.array(self.constrainDecVec).ravel()))%self.gf
        pdata[dels[0]]=deletion
        valid = self.isValid(pdata, checkerVec, checkerP)
        return [deletion], valid
    def decode(self, pdata, dels):
        if len(dels)==1: return self.onedel(pdata,dels)
        self.dels=dels
        det = self.det()
        B = self.hieu()
        X=np.dot(pdata[:self.numBlock],B)
        for i in range(len(X)):
            pdata=np.insert(pdata, [self.dels[i]], (X[i]*self.invgf(det))%self.gf)
        ddata = pdata[:self.numBlock]
        return ddata, self.isValid(ddata, pdata[-1])
    @staticmethod
    def show(dels,numBlock):
        iden = np.identity(numBlock)
        diden= np.delete(iden,dels,1)
        enVecs=GCdet.getEnVec(len(dels), numBlock)
        return np.concatenate((diden,enVecs),1)
    def __repr__(self):
        return 'Dels: {} '.format(self.dels) + 'numBlock: {} '.format(self.numBlock) + 'enVecs: {}'.format(self.constrainDecVec)