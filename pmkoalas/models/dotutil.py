
import os.path
import shutil
import subprocess
import tempfile
from logging import info

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


