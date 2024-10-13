
import os.path
import shutil
import subprocess
import tempfile
from logging import info
from typing import Dict
from warnings import warn

from pmkoalas.models.petrinet import LabelledPetriNet,Place

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


# colour scheme for lpns
START_PLACE_COLOUR = "#c5e1a5"
FINAL_PLACE_COLOUR = "#ef9a9a"
PLACE_COLOUR = "#ffe0b2"
TRANSITION_COLOUR = "#81c784"
ARC_COLOUR = "#263238"
BACKWARDS_COLOUR = "gray"
FONT_COLOUR = "black"

def prettier_handler_place(p:Place, lpn:LabelledPetriNet, nodeId) -> str:
    ret = ""
    label = '<'+'<BR/>'.join([p.name[i:i+16] for i in range(0, len(p.name), 16)])+">"
    if lpn.initial_marking is not None and lpn.initial_marking.contains(p):
        ret += f"\t\t{nodeId}[label={label},fillcolor=\"{START_PLACE_COLOUR}\"];"
    elif lpn.final_marking is not None and lpn.final_marking.contains(p):
        ret += f"\t\t{nodeId}[label={label},fillcolor=\"{FINAL_PLACE_COLOUR}\"];"
    else:
        ret += f"\t\t{nodeId}[label={label}];"
    ret += "\n"
    return ret

def lpn_prettier_dot(lpn:LabelledPetriNet):
    ret = "digraph{\n"
    ret += "\tdpi=150;rankdir=LR;nodesep=0.6;ranksep=0.3;\n"
    ret += "\tedge[penwidth=4,fontsize=16,minlen=2,fontname=\"roboto\"];\n"
    nodeIds = dict()
    nid = 0
    # here is where I would write a walking algorithm
    # but I am not ready to do that...
    if (False):
        # walks places (if marking is set)
        walked_places = []
        walked_transitions = []
        seen = set()
        ret += "\t{\n"
        ret += f"\t\tnode[shape=circle,margin=\"0.05, 0.05\",fillcolor=\"{PLACE_COLOUR}\",style=filled,width=1,penwidth=2,fontsize=9,fontname=\"roboto\"];\n" 
        # handle places
    else:
        ret += "\t{\n"
        ret += f"\t\tnode[shape=circle,margin=\"0.05, 0.05\",fillcolor=\"{PLACE_COLOUR}\",style=filled,width=1,penwidth=2,fontsize=9,fontname=\"roboto\"];\n"
        for v in lpn.places:
            nodeIds[v.nodeId] = f"n{nid}"
            ret += prettier_handler_place(v, lpn, nodeIds[v.nodeId])
            nid += 1
        assert nid == len(lpn.places)
        ret += "\t}\n"
        ret += "\t{\n"
        ret += f"\t\tnode[shape=box,style=\"rounded,filled\",fillcolor=\"{TRANSITION_COLOUR}\",width=2,penwidth=3,fontsize=18,fontname=\"roboto\",margin=\"0, 0.2\"];\n"
        for t in lpn.transitions:
            nodeIds[t.nodeId] = f"n{nid}"
            label = '<'+'<BR/>'.join([t.name[i:i+16] for i in range(0, len(t.name), 16)])+">"
            ret += f"\t\t{nodeIds[t.nodeId]}[label={label}];\n"
            nid += 1
        assert nid == len(lpn.places) + len(lpn.transitions)
        ret += "\t}\n"
        elabel = 0
        for a in lpn.arcs:
            if a.from_node.nodeId in nodeIds:
                dotNode_from = nodeIds[a.from_node.nodeId]
            else:
                warn(f"Node {a.from_node} not found in nodeIds, likely something is wrong with the given LPN")
                dotNode_from = f"n{nid}"
                nid += 1
            if a.to_node.nodeId in nodeIds:
                dotNode_to = nodeIds[a.to_node.nodeId]
            else:
                warn(f"Node {a.to_node} not found in nodeIds, likely something is wrong with the given LPN")
                dotNode_to = f"n{nid}"
                nid += 1
            ret += f"\t{dotNode_from} -> {dotNode_to}[arrowhead=normal,color=\"{ARC_COLOUR}\"];\n"
            elabel += 1
        ret += "}"
    # assert elabel == len(lpn.arcs)
    return ret


