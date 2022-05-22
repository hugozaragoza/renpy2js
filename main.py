import argparse
import io
import json
import logging
import os
import pathlib
import shutil
import sys
from os import listdir
from os.path import isfile, join

import pygraphviz as pgv

from renpy_parser import utils
from renpy_parser.parser import parse_renpy


def myassert(test, msg):
    if not test:
        print("\nFAILURE! : " + msg + "\n")
        sys.exit(1)


def str2file(str, file):
    with open(file, 'w') as fh:
        print(str, file=fh)
    # print(f"WROTE {file}")


def dir_path(path):
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")


def copy_all_files_in_dir(pathsource, pathtarget):
    assert os.path.isdir(pathsource), "CANNOT FIND source directory: " + pathsource
    assert os.path.isdir(pathtarget), "CANNOT FIND target directory: " + pathtarget
    files = [f for f in listdir(pathsource) if isfile(join(pathsource, f))]
    for f in files:
        shutil.copy2(os.path.join(pathsource, f), pathtarget)
    # print(f"WROTE {len(files)} files from {pathsource} to {pathtarget}")


## Check if directory exists (in current location)
# def ftp_directory_exists(ftp, dir, mk_if_missing=False):
#    assert dir, "ftp_directory_exists: no dir indicated?"    
#
#    filelist = []
#    ftp.retrlines('LIST', filelist.append)
#    for f in filelist:
#        if f.split()[-1] == dir and f.upper().startswith('D'):
#            return True
#    if mk_if_missing:
#        ftp.mkd(dir)
#        return ftp_directory_exists(ftp, dir, False)        
#    return False
#
#
# def ftp_all_files(ftp_session, pathsource, pathtarget):
#    assert os.path.isdir(pathsource)
#    ftp_session.cwd('/')
#    dirsofar=""
#    for dir in pathtarget.split("/"):
#        assert dir
#        assert ftp_directory_exists(ftp_session, dir, True), "COULD NOT CREATE DIRECTORY in FTP: " + pathtarget
#        ftp_session.cwd(dir)
#        dirsofar += "/"+dir
#        files = [f for f in listdir(pathsource) if isfile(join(pathsource, f)) and f[0] != '.']
#        for f in files:
#            file = open(os.path.join(pathsource, f), 'rb')
#            ftp_session.storbinary('STOR ' + f, file)
#        print(f"FTP: copied {len(files)} files from {pathsource} to {pathtarget}")


if __name__ == "__main__":

    #    def parse_ftp(arg_value):
    #        pat=re.compile(r"^(.+):(.+):(.+)$")
    #        m = pat.match(arg_value)
    #        if not m:
    #            print("\nERROR: FTP argument should be ip:user:passwd\n")
    #            raise argparse.ArgumentTypeError
    #        return m.groups()

    parser = argparse.ArgumentParser(description='Renpy2JS Engine')
    parser.add_argument(dest="indir", type=dir_path)
    parser.add_argument(dest="storyname", type=str)
    parser.add_argument(dest="outdir", type=str)
    #    parser.add_argument(dest='ftp', nargs='?', default=None, type=parse_ftp)
    args = parser.parse_args()

    # 0. BASIC CHECKS AND DIR SETUP:
    myassert(args.storyname == args.storyname.lower(), f"STORY NAME MUST BE ALL lowercase: [{args.storyname}]")

    indir = args.indir
    script_file = os.path.join(indir, "script.rpy")
    out_dir = args.outdir

    myassert(os.path.isdir(indir), "INPUT DIRECTORY NOT FOUND: " + indir)
    myassert(os.path.isdir(out_dir), "OUTPUT DIRECTORY NOT FOUND: " + out_dir)
    myassert(os.path.exists(script_file), "SCRIPT FILE NOT FOUND: " + script_file)

    logging.basicConfig(filename=os.path.join(out_dir, 'renpy2js.log'), level=logging.DEBUG, filemode="a")

    # 1. PARSE STORY
    with io.open(script_file, mode="r", encoding="utf-8-sig") as fh:  # renpy script.rpy is utf8
        renpy_str = fh.read()
        if renpy_str[-1] != "\n":  # add last \n if missing
            renpy_str += "\n"
    diclabels, debug = parse_renpy(renpy_str)

    # 1b. SETUP output dir
    storyname = args.storyname
    out_story_dir = os.path.join(out_dir, storyname)
    pathlib.Path(out_story_dir).mkdir(parents=True, exist_ok=False)

    # 1c. debug story
    G = pgv.AGraph(directed=True)
    nodes = set()
    for k, v in diclabels.items():
        if k.startswith("choice_label"):
            continue
        utils.debug(v, k + "  v")
        fv = utils.flatten(v)
        utils.debug(fv, k + "  fv")
        for count, value in enumerate(fv):
            if value == "jump_line":
                goto = fv[count + 1]
                if goto == "TODO":  # RMEOVE TODO (they cluster)
                    continue
                if goto == "END":  # RMEOVE TODO (they cluster)
                    goto = "END__" + k
                for n in [k, goto]:
                    if n not in nodes:
                        nodes.add(n)
                        color = "grey"
                        if n == "start":
                            color = "green"
                        elif n.startswith("END__"):
                            color = "red"
                        G.add_node(n, color=color)
                G.add_edge(k, goto)

    G.layout(prog="dot", args="-Gscale=2")
    fout = os.path.join(out_story_dir, "storygraph.png")
    G.draw(fout)

    # 2. WRITE WEB STORY
    codedir = os.path.dirname(os.path.realpath(__file__))
    resource_dir = os.path.join(codedir, "resources")
    html_resourcedir = os.path.join(resource_dir, "html")

    json_str1 = json.dumps(diclabels, indent=4).replace("'", "\\'")
    js_json = "var data=JSON.parse( `\n" + json_str1 + "\n`)"
    str2file(js_json, os.path.join(out_story_dir, "script.js"))

    # 3 ADD HTML RESOURCES
    copy_all_files_in_dir(html_resourcedir, out_story_dir)
    for dir in ["img"]:
        pin = os.path.join(indir, dir)
    pout = os.path.join(out_story_dir, dir)
    pathlib.Path(pout).mkdir(parents=True)
    copy_all_files_in_dir(pin, pout)

    # 4 ADD logger service
    out_logger_dir = os.path.join(out_dir, "logger")
    shutil.copytree(os.path.join(resource_dir, "logger"), out_logger_dir, dirs_exist_ok=True)

    # 5 INFO
    print(f"Wrote site to  : {out_story_dir}")
    print(f"Wrote logger to: {out_logger_dir}")

    #    if (args.ftp):
    #        print(f"FTPing to {args.ftp[0]} with user {args.ftp[1]}")
    #        session = FTP(args.ftp[0],args.ftp[1],args.ftp[2])
    #        ftp_all_files(session, outdir, ftp_outdir)
    #        session.quit()
