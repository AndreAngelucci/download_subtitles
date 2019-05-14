#!python3

import os
import hashlib
import sys
import http.client
import re
import glob

USAGE = "Sintaxe -> download_subtitle arquivo_1.mkv ./arquivos/*.mkv etc.*"

def calc_file_hash(file):
    if not(os.path.isfile(file)):
        raise Exception("Arquivo %s nao existe." % file)
    readsize = 64 * 1024
    with open(file, 'rb') as f:
        size = os.path.getsize(file)
        data = f.read(readsize)
        f.seek(-readsize, os.SEEK_END)
        data += f.read(readsize)
    return hashlib.md5(data).hexdigest()

def download(hash_str, file_name):    
    conn = http.client.HTTPConnection("api.thesubdb.com")
    headers = {"User-Agent":"SubDB/1.0 (andre/0.1; https://github.com/AndreAngelucci/download_subtitles)"}
    conn.request(
        "GET",
        "/?action=download&hash=%s&language=pt" % hash_str,
        headers = headers
    )
    res = conn.getresponse()
    if (res.status == 200):      
        subtitle = res.read().decode('latin-1')        
        file_subtitle = re.sub("\.\w+$", ".srt", file_name)        
        with open(file_subtitle, "w") as f:            
            f.writelines(subtitle)
            f.close()
    else:
        raise Exception("Legenda nao encontrada.")

try:
    print("Procurando legendas...")
    #encontra os arquivos nos parametros
    files = []
    for p in sys.argv[1:]:
        for f in glob.glob(p):
            files.append(f)
    assert(len(files) > 0), USAGE 
    #dict arquivo:hash
    hashs = dict()
    for f in files:
        try:
            hashs[f] = calc_file_hash(f)
            if (hashs[f] == None):
                raise Exception("Arquivo invalido")
        except Exception as error:
            print("Falha ao calcular o hash do arquivo %s: %s" % (f, error))
    #faz os downloads
    c = 0
    for a, h in hashs.items():
        try:
            download(h, a)
            c += 1
        except Exception as error:
            print("Falha ao baixar lengenda do arquivo %s: %s" % (a, error))
    print(
        "Download finalizado. %d legenda(s) encontrada(s)" % c if (c > 0) else "Nenhum legenda baixada."
    )
except Exception as error:
    print("Erro:", error)