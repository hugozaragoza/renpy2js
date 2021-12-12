import json
import io
import logging
import pathlib
import shutil
import argparse
import os
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
def directory_exists(ftp, dir, mk_if_missing=False):
    filelist = []
    ftp.retrlines('LIST', filelist.append)
    for f in filelist:
        if f.split()[-1] == dir and f.upper().startswith('D'):
            return True
    if mk_if_missing:
        ftp.mkd(dir)
        print(f"FTP: mkdir [{dir}]")
        return directory_exists(ftp, dir, False)
    return False


def ftp_all_files(ftp_session, pathsource, pathtarget):
    assert os.path.isdir(pathsource)
    ftp_session.cwd('/public_html')
    for dir in pathtarget.split("/"):
        assert directory_exists(ftp_session, dir, True), "COULD NOT CREATE DIRECTORY in FTP: " + pathtarget
        ftp_session.cwd(dir)
    files = [f for f in listdir(pathsource) if isfile(join(pathsource, f)) and f[0] != '.']
    for f in files:
        file = open(os.path.join(pathsource, f), 'rb')
        ftp_session.storbinary('STOR ' + f, file)
    print(f"FTP: copied {len(files)} files to " + pathtarget)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Renpy2JS Engine')
    parser.add_argument(dest="indir", type=dir_path)
    parser.add_argument(dest="outdir", type=str)
    parser.add_argument("--ftp", dest='ftp', action='store_const', const=True, default=False)
    args = parser.parse_args()

    indir = args.indir
    outdirname = args.outdir
    outdir = os.path.join("/Users/hugzarag/Sites", outdirname)
    indir_img = os.path.join(indir, "img")
    html_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "html")
    outdir_img = os.path.join(outdir, "img")

    myassert(os.path.isdir(indir), "INPUT DIRECTORY NOT FOUND: " + indir)
    pathlib.Path(outdir).mkdir(parents=True, exist_ok=True)

    script_file = os.path.join(indir, "script.rpy")
    myassert(os.path.exists(script_file), "SCRIPT FILE NOT FOUND: " + script_file)

    print("-----------------")
    print("INPUT DIRECTORY: " + indir)
    print("INPUT SCRIPT: " + script_file)
    print("OUTPUT DIRECTORY: " + outdir)
    print("-----------------")

    logging.basicConfig(filename=os.path.join(outdir, 'renpy2js.log'), level=logging.DEBUG, filemode="w")

    with io.open(script_file, mode="r", encoding="utf-8-sig") as fh:  # renpy script.rpy is utf8
        renpy_str = fh.read()

    diclabels, debug = parse_renpy(renpy_str)

    outdir_data = os.path.join(outdir, "data")
    pathlib.Path(outdir_data).mkdir(parents=True, exist_ok=True)

    json_str1 = json.dumps(diclabels, indent=4).replace("'", "\\'")
    js_json = "var data=JSON.parse( `\n" + json_str1 + "\n`)"

    str2file(js_json, os.path.join(outdir, "script.js"))
    copy_all_files(html_dir, outdir)

    if os.path.exists(indir_img):
        pathlib.Path(outdir_img).mkdir(parents=True, exist_ok=True)
    copy_all_files(indir_img, outdir_img)

    if (args.ftp):
        session = FTP('92.205.2.244', 'export@helpp.net', 'export___')
        ftp_all_files(session, outdir, outdirname)
        ftp_all_files(session, outdir_img, outdirname + "/img")
        session.quit()
