
import os.path
import shutil
import subprocess
import tempfile
from logging import info

DFENC='utf-8'

def dotToImg(dot:str,dotf:str,imgf:str,outformat:str,dfenc:str=DFENC):
    with open(dotf,'w',encoding=dfenc) as outf:
        outf.write(dot)
        outf.write('\n')
    tfd, tfnamed = tempfile.mkstemp()
    tfi, tfnamei = tempfile.mkstemp()
    shutil.copy(dotf,tfnamed)
    cmdout = subprocess.run(['dot','-T' + outformat,'-o' + tfnamei, tfnamed])
    shutil.copy(tfnamei,imgf)

def exportDOTToImage(vard:str,oname:str,dotStr:str,outformat:str='png'):
    dotf = os.path.join(vard,oname+'.dot')
    imgpnf = os.path.join(vard,oname+'_pn.' + outformat)
    info(f"Generating diagram {oname} ... ")
    dotToImg(dotStr,dotf,imgpnf,outformat)


