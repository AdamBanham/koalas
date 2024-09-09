
import os.path
import shutil
import subprocess
import tempfile
from logging import info

from pmkoalas.models.petrinet import LabelledPetriNet

DFENC='utf-8'

def dot_to_img(dot:str,dotf:str,imgf:str,outformat:str,dfenc:str=DFENC):
    with open(dotf,'w',encoding=dfenc) as outf:
        outf.write(dot)
        outf.write('\n')
    tfd, tfnamed = tempfile.mkstemp()
    tfi, tfnamei = tempfile.mkstemp()
    shutil.copy(dotf,tfnamed)
    cmdout = subprocess.run(['dot','-T' + outformat,'-o' + tfnamei, tfnamed])
    shutil.copy(tfnamei,imgf)

def export_DOT_to_image(vard:str,oname:str,dotStr:str,outformat:str='png'):
    dotf = os.path.join(vard,oname+'.dot')
    imgpnf = os.path.join(vard,oname+'_pn.' + outformat)
    info(f"Generating diagram {oname} ... ")
    dot_to_img(dotStr,dotf,imgpnf,outformat)

def lpn_prettier_dot(lpn:LabelledPetriNet):
    ret = "digraph{"
    ret += "dpi=150;rankdir=LR;nodesep=0.6;ranksep=0.3;"
    ret += "edge[penwidth=4,fontsize=16,minlen=2,fontname=\"roboto\"];"
    nodeIds = dict()
    nid = 0
    ret += "{"
    ret += "node[shape=circle,margin=\"0.05, 0.05\",fillcolor=lightgray,style=filled,width=1,penwidth=2,fontsize=9,fontname=\"roboto\"];"
    for v in lpn.places:
        nodeIds[v.nodeId] = f"n{nid}"
        label = '<'+'<BR/>'.join([v.name[i:i+16] for i in range(0, len(v.name), 16)])+">"
        ret += f"{nodeIds[v.nodeId]}[label={label}];"
        nid += 1
    assert nid == len(lpn.places)
    ret += "}"
    ret += "{"
    ret += "node[shape=box,style=\"rounded\",width=2,penwidth=3,fontsize=18,fontname=\"roboto\",margin=\"0, 0.2\"];"
    for t in lpn.transitions:
        nodeIds[t.nodeId] = f"n{nid}"
        label = '<'+'<BR/>'.join([t.name[i:i+16] for i in range(0, len(t.name), 16)])+">"
        ret += f"{nodeIds[t.nodeId]}[label={label}];"
        nid += 1
    assert nid == len(lpn.places) + len(lpn.transitions)
    ret += "}"
    elabel = 0
    seen = set()
    for a in lpn.arcs:
        ret += f"{nodeIds[a.from_node.nodeId]} -> {nodeIds[a.to_node.nodeId]}[arrowhead=normal,color=gray];"
        elabel += 1
    ret += "}"
    # assert elabel == len(lpn.arcs)
    return ret


