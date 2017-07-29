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
    def onedel(self,data, parity, dels):
        '''cX + sumknown = p0
            X = (p0-sumknown)*cInverse
        Where:
            X = deletion integer
            sumknown = np.inner(data,dvec)
            p0 = parity[0]
            cInverse = self.gfinv(dvec[dels[0]])
        '''
        #print(data)
        def isvalid(i):
            return ((self.enVec[dels[0]][i] * X) - pprime[i])%self.gf == 0
        pprime = parity - np.dot(data,self.enVec)
        #print(pprime, dels)
        X = (self.gfinv[self.enVec[dels[0]][0]] * (pprime[0])) % self.gf
        #print(dels, X)
        for i in range(1, len(pprime)):
            valid = isvalid(i)
            if not valid: break
        #X = (self.gfinv[self.dvec[dels[0]]]*(parity[0]-np.inner(data,self.dvec)))%self.gf
        #data[dels[0]]=X
        #valid = self.isValid(data, self.cvec, parity[1:])
        return [X], valid
    def _onedel(self,pprime, dels):
        def isvalid(i):
            return ((self.enVec[dels][i] * X) - pprime[i])%self.gf == 0
        X = (self.gfinv[self.enVec[dels][0]] * (pprime[0])) % self.gf
        valid = True
        for i in range(1, len(pprime)):
            valid = isvalid(i)
            if not valid: break
        return X, valid

    def _twodels(self, pprime, dels):
        def isvalid(i):
            return ((self.enVec[dels[0]][i] * X1 + self.enVec[dels[1]][i]*X2) - pprime[i])%self.gf == 0
        # detA = ad - bc
        detA = ((self.enVec[dels[0]][0]*self.enVec[dels[1]][1])-(self.enVec[dels[1]][0]*self.enVec[dels[0]][1]))
        idetA = self.gfinv[detA%self.gf]
        detX1 = (pprime[0]*self.enVec[dels[1]][1])-(pprime[1]*self.enVec[dels[1]][0])
        detX2 = (pprime[1]*self.enVec[dels[0]][0])-(pprime[0]*self.enVec[dels[0]][1])
        X1 = detX1*idetA%self.gf
        X2 = detX2*idetA%self.gf
        for i in range(2, len(pprime)):
            valid = isvalid(i)
            if not valid: break
        return [X1, X2], valid

    def decode(self, data, parity, dels):
        print(sum(data),',',data,',' ,',',dels)
        dels=list(sorted(set(dels)))
        numDel=len(dels)
        #print(sum(data), data, dels)
        if numDel==1: return self.onedel(data, parity, dels)
        if numDel==2: return self.twodels(data, parity,dels)
        if numDel==3: return self.twodels(data, parity,dels)
        checkerVec=self.enVec[:,numDel:] #use the rest of decoding vectors as the checker
        checkerP=pdata[self.numBlock+numDel:] #corresponding parity bits
        B = self.hieu(dels)%self.gf
        X=np.dot(pdata,B)*self.gfinv[self.det(dels)%self.gf]%self.gf
        for i in range(len(X)):
            pdata[dels[i]]=X[i]
        valid = self.isValid(pdata, checkerVec, checkerP)
        #print('case',temppdata,valid)
        return X, valid
    def twodels(self, data, parity, dels):
        def isvalid(i):
            return ((self.enVec[dels[0]][i] * X1 + self.enVec[dels[1]][i]*X2) - pprime[i])%self.gf == 0
        pprime = parity - np.dot(data,self.enVec)
        #print(pprime, dels)
        # detA = ad - bc
        detA = ((self.enVec[dels[0]][0]*self.enVec[dels[1]][1])-(self.enVec[dels[1]][0]*self.enVec[dels[0]][1]))
        idetA = self.gfinv[detA%self.gf]
        detX1 = (pprime[0]*self.enVec[dels[1]][1])-(pprime[1]*self.enVec[dels[1]][0])
        detX2 = (pprime[1]*self.enVec[dels[0]][0])-(pprime[0]*self.enVec[dels[0]][1])
        X1 = detX1*idetA%self.gf
        X2 = detX2*idetA%self.gf
        for i in range(2, len(pprime)):
            valid = isvalid(i)
            if not valid: break
        return [X1, X2], valid
    def threedels(self, data, parity, dels):
        return 2, True
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