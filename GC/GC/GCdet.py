from Decoder import *
import numpy
class GCdet(Decoder):
    def __init__(self, mlen, numVec):
        super().__init__(mlen, numVec)
    @staticmethod
    def _det(dels, numBlock, subMat):
        if subMat.size == 0:
            return 1
        else:
            #print(subMat,dels)
            return GCdet.sign(dels, numBlock) * np.linalg.det(subMat.astype(np.int64))
    def det(self, dels):
        return GCdet._det(dels, self.numBlock, self.enVec[dels,:len(dels)])
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
    def hieu(self, dels):
        output=[]
        numDel=len(dels)
        for i in range(numDel):
            rowPicks = list(dels)
            curRow = rowPicks.pop(i)
            if curRow%2==0: #even rows, zero indexing
                sign=1
            else: #odd rows, zero indexing
                sign=-1
            #calculate regular item
            lst=[0]*(self.numBlock+self.numVec)
            for j in range(self.numBlock+numDel): # all envecs coloumn
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
                            subMat = self.enVec[sorted(rowPicks),:len(rowPicks)]
                            del rowPicks[-1]
                        else:
                            #colPicks takes numDel columns of enVec but the current column
                            colPicks=[x for x in range(numDel) if x!=(j%self.numBlock)]
                            subMat = self.enVec[sorted(rowPicks),:][:,colPicks]
                        #calculate item at curRow then append to a list
                        c = sign*GCdet._det(sorted(subDels), self.numBlock-1, subMat)
                        sign*=-1
                        lst[j]=c
            output.append(np.around(lst).astype(int))
        return np.transpose(output)
    def onedel(self,pdata,dels):
        numDels=len(dels)
        deVec=np.array(self.enVec[:,:numDels]).ravel() #same as number of dels
        checkerVec=self.enVec[:,numDels:] #use the rest of decoding vectors as the checker
        checkerP=pdata[self.numBlock+numDels:] #corresponding parity bits
        if (dels[0]+self.numBlock)%2 == 1:
            aSign=-1
        else:
            aSign=1
        #one deletion
        deVec[self.numBlock]=-1
        idet = self.gfinv(GCdet.sign(dels,self.numBlock)*deVec[dels[0]])
        product = np.inner(pdata,deVec)
        X = (aSign*idet*product)%self.gf
        pdata[dels[0]]=X
        valid = self.isValid(pdata, checkerVec, checkerP)

        return [X], valid
    def onedel2(self,pdata,dels):
        '''Use '111' encoding vector, do only additions and subtractions'''
        numDels=1
        checkerVec=self.enVec[:,numDels:] #use the rest of decoding vectors as the checker
        checkerP=pdata[self.numBlock+numDels:] #corresponding parity bits
        pdata[dels[0]]=0
        X = (pdata[self.numBlock]+pdata[self.numBlock]+sum(checkerP)-sum(pdata))%self.gf
        pdata[dels[0]]=X
        valid = self.isValid(pdata, checkerVec, checkerP)
        return [X], valid
    def decode(self, pdata, dels):
        #temppdata=np.array(pdata)
        dels=list(sorted(set(dels)))
        numDel=len(dels)
        if numDel==1: return self.onedel(pdata,dels)
        checkerVec=self.enVec[:,numDel:] #use the rest of decoding vectors as the checker
        checkerP=pdata[self.numBlock+numDel:] #corresponding parity bits
        B = self.hieu(dels)%self.gf
        X=np.dot(pdata,B)*self.gfinv(self.det(dels))%self.gf
        for i in range(len(X)):
            pdata[dels[i]]=X[i]
        valid = self.isValid(pdata, checkerVec, checkerP)
        #print('case',temppdata,valid)
        return X, valid
    @staticmethod
    def show(dels,numBlock):
        iden = np.identity(numBlock)
        diden= np.delete(iden,dels,1)
        enVecs=GCdet.getEnVec(len(dels)+1, numBlock, len(dels))
        return np.concatenate((diden,enVecs),1)
    
    def gfinv(self, x):
        x=int(round(x))%self.gf
        if x==0: return 0
        for i in range(self.gf):
            if (i*x)%self.gf==1:
                return i
        else:
            raise CantFindGFinv
    def __repr__(self):
        return 'Dels: {} '.format(self.dels) + 'numBlock: {} '.format(self.numBlock) + 'enVecs: {}'.format(self.constrainDecVec)