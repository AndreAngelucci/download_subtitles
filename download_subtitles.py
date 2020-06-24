#!python

import os
import hashlib
import sys
import requests
import re
import glob

USAGE = "Sintaxe -> download_subtitle arquivo_1.mkv ./arquivos/*.mkv etc.*"

def calc_file_hash(file):
    if not(os.path.isfile(file)):
        raise Exception("Arquivo %s nao existe." % file)
    readsize = 64 * 1024
    with open(file, 'rb') as f:
        data = f.read(readsize)
        f.seek(-readsize, os.SEEK_END)
        data += f.read(readsize)
    return hashlib.md5(data).hexdigest()

def download(hash_str, file_name):
    r = requests.get(
        f'http://api.thesubdb.com/?action=download&hash={hash_str}&language=pt',
        headers={'User-Agent':'SubDB/1.0 (andre/0.1; https://github.com/AndreAngelucci/download_subtitles)'})
    r.raise_for_status()
    file_subtitle = os.path.splitext(file_name)[0] + '.srt'
    with open(file_subtitle, 'w', encoding=r.encoding) as f:
        f.write(r.text)

try:
    print("Procurando legendas...")
    #encontra os arquivos nos parametros
    files = []
    files = sys.argv[1:]
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
