
import math
from pmkoalas.models.petrinet import PetriNetDOTFormatter
from pmkoalas.models.dotutil import exportDOTToImage


class ScaledFormatter(PetriNetDOTFormatter):
    # These sizes should probably be relative instead of absolute

    def __init__(self,pn,sslog:dict,font='SimSun'):
        rfont = 'SimSun' if (font is None) else font
        super().__init__(pn,rfont)
        self._nodemap = {}
        self._defaultFontSize=12
        actfreq = {}
        actsum = 0
        for caseId in sslog:
            for ss in sslog[caseId]:
                for act in ss.activities:
                    if act in actfreq:
                        actfreq[act] += 1
                    else:
                        actfreq[act] = 1
                    actsum += 1
        self._actfreq = actfreq
        self._actsum = actsum
        self._sf = 40
        self._arcscale = 10
        self._plscale = 2


    def tranDOT(self,tran,ti):
        tl = '' # tran.name if tran.name and tran.name != 'tau' else '&tau;'
        SPACE = ' '
        if SPACE in tl:
            tl = tl.replace(SPACE,"\n")
        fstr = f'n{str(ti)} [shape="box",margin="0, 0.1",'
        fstr += f'label="{tl} {tran.weight}", style="filled",'
        fstr += '];\n'
        return fstr

    def placeDOT(self,place,pi):
        height = self._defaultHeight
        fs = self._defaultFontSize
        SPACE = ' '
        placeName = place.name
        if SPACE in place.name:
            placeName = place.name.replace(SPACE,"\n")
        if place.name in self._actfreq:
            sf = self._plscale * \
                   math.sqrt(self._sf * self._actfreq[place.name] /self._actsum)
            height = self._defaultHeight + sf
            fs = round(self._defaultFontSize + 8*sf)
        fstr = f'n{str(pi)} [shape="circle",label="{placeName}",'
        fstr += f'height="{height}", fontsize="{fs}"];\n'
        return fstr

    def arcDOT(self,arc):
        fromNode = self._nodemap[arc.fromNode]
        toNode = self._nodemap[arc.toNode]
        weight = 1
        if arc.fromNode in self._pn.transitions:
            weight = arc.fromNode.weight
        elif arc.toNode in self._pn.transitions:
            weight = arc.toNode.weight
        asize = self._arcscale * math.sqrt(self._sf * weight / self._actsum )
        return f'n{fromNode}->n{toNode}[penwidth="{asize}"]\n'


def exportToScaledDOT(net,sslog: set,font) -> str:
    return ScaledFormatter(net,sslog,font).netToDOT()


def exportNetToScaledImage(vard,oname,pn,sslog,font):
    dotStr = exportToScaledDOT(pn,sslog,font)
    exportDOTToImage(vard,oname,dotStr) 



