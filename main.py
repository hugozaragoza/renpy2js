import json
import getpass
import io
import logging
import pathlib
import shutil
import argparse
import os
import re
import sys
from ftplib import FTP

from os import listdir
from os.path import isfile, join

from renpy_parser.parser import parse_renpy


def myassert(test, msg):
    if not test:
        print("\nFAILURE! : " + msg + "\n")
        sys.exit(1)


def str2file(str, file):
    with open(file, 'w') as fh:
        print(str, file=fh)
    print(f"WROTE {file}")


def dir_path(path):
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")


def copy_all_files(pathsource, pathtarget):
    assert os.path.isdir(pathsource), "CANNOT FIND source directory: " + pathsource
    assert os.path.isdir(pathtarget), "CANNOT FIND target directory: " + pathtarget
    files = [f for f in listdir(pathsource) if isfile(join(pathsource, f))]
    for f in files:
        shutil.copy2(os.path.join(pathsource, f), pathtarget)
    print(f"WROTE {len(files)} files from {pathsource} to {pathtarget}")


# Check if directory exists (in current location)
def ftp_directory_exists(ftp, dir, mk_if_missing=False):
    assert dir, "ftp_directory_exists: no dir indicated?"    

    filelist = []
    ftp.retrlines('LIST', filelist.append)
    for f in filelist:
        if f.split()[-1] == dir and f.upper().startswith('D'):
            return True
    if mk_if_missing:
        ftp.mkd(dir)
        return ftp_directory_exists(ftp, dir, False)        
    return False


def ftp_all_files(ftp_session, pathsource, pathtarget):
    assert os.path.isdir(pathsource)
    ftp_session.cwd('/')
    dirsofar=""
    for dir in pathtarget.split("/"):
        assert dir
        assert ftp_directory_exists(ftp_session, dir, True), "COULD NOT CREATE DIRECTORY in FTP: " + pathtarget
        ftp_session.cwd(dir)
        dirsofar += "/"+dir
        files = [f for f in listdir(pathsource) if isfile(join(pathsource, f)) and f[0] != '.']
        for f in files:
            file = open(os.path.join(pathsource, f), 'rb')
            ftp_session.storbinary('STOR ' + f, file)
        print(f"FTP: copied {len(files)} files from {pathsource} to {pathtarget}")


if __name__ == "__main__":

    def parse_ftp(arg_value):
        pat=re.compile(r"^(.+):(.+):(.+)$")
        m = pat.match(arg_value)
        if not m:
            print("\nERROR: FTP argument should be ip:user:passwd\n")
            raise argparse.ArgumentTypeError
        return m.groups()

    parser = argparse.ArgumentParser(description='Renpy2JS Engine')
    parser.add_argument(dest="indir", type=dir_path)
    parser.add_argument(dest="storyname", type=str)
    parser.add_argument(dest="outdir", type=str)
    parser.add_argument("--ftp", dest='ftp', type=parse_ftp, required=False)
    #parser.add_argument("--ftp", dest='ftp', action='store_const', const=True, default=False)
    args = parser.parse_args()

    storyname = args.storyname
    indir = args.indir

    outdir = os.path.join(args.outdir,storyname)

    ftp_outdir = os.path.join("public_html",storyname)

    codedir = os.path.dirname(os.path.realpath(__file__))
    html_resourcedir = os.path.join(codedir, "html")

    myassert(os.path.isdir(indir), "INPUT DIRECTORY NOT FOUND: " + indir)
    pathlib.Path(outdir).mkdir(parents=True, exist_ok=True)

    script_file = os.path.join(indir, "script.rpy")
    myassert(os.path.exists(script_file), "SCRIPT FILE NOT FOUND: " + script_file)

    outdir_data = os.path.join(outdir, "data")
    pathlib.Path(outdir_data).mkdir(parents=True, exist_ok=True)

    print("-----------------")
    print("CODE DIRECTORY  : " + codedir)
    print("INPUT DIRECTORY : " + indir)
    print("  SCRIPT: " + script_file)
    print("OUTPUT DIRECTORY: " + outdir)
    if args.ftp:
        print(f"FTP DIRECTORY: {args.ftp[1]}@{args.ftp[0]}:{ftp_outdir}")

    print("-----------------")

    logging.basicConfig(filename=os.path.join(outdir, 'renpy2js.log'), level=logging.DEBUG, filemode="w")

    with io.open(script_file, mode="r", encoding="utf-8-sig") as fh:  # renpy script.rpy is utf8
        renpy_str = fh.read()

    diclabels, debug = parse_renpy(renpy_str)


    json_str1 = json.dumps(diclabels, indent=4).replace("'", "\\'")
    js_json = "var data=JSON.parse( `\n" + json_str1 + "\n`)"

    str2file(js_json, os.path.join(outdir, "script.js"))

    copy_all_files(html_resourcedir, outdir)
    shutil.copytree(os.path.join(html_resourcedir, "serverapp"),outdir)

    for dir in ["img"]:
        pin = os.path.join(indir, dir)
        pout = os.path.join(outdir, dir)
        pathlib.Path(pout).mkdir(parents=True, exist_ok=True)
        copy_all_files(pin, pout)

    if (args.ftp):
        print(f"FTPing to {args.ftp[0]} with user {args.ftp[1]}")
        session = FTP(args.ftp[0],args.ftp[1],args.ftp[2])
        ftp_all_files(session, outdir, ftp_outdir)
        ftp_all_files(session, outdir_img, ftp_outdir + "/img")
        session.quit()
