from binascii import hexlify
import configparser
import json
import os
import shutil
import subprocess
import sys
from uuid import uuid1

from git import Repo

def main():
    config = configparser.ConfigParser()
    config.read('ltm.ini')

    outpath = config['default']['outpath']
    if os.path.exists(outpath):
        i = 0
        while os.path.exists(outpath + '.' + str(i)):
            i += 1
        shutil.move(outpath, outpath + '.' + str(i))


    runinfo_file = os.path.join(outpath, 'runinfo.json')
    repo_path = config['git']['repo_path']

    origin_repo = Repo('.')
    try:
        repo = Repo(repo_path)
    except:
        repo = origin_repo.clone(repo_path)

    repo.remote().fetch()
    repo.head.reset(origin_repo.head.commit, working_tree=True)
    for x in repo.untracked_files:
        name = os.path.join(repo.working_tree_dir, x)
        if os.path.isdir(name):
            shutil.rmtree(name)
        else:
            os.remove(name)

    # TODO handle all change types
    for x in origin_repo.head.commit.diff(None).iter_change_type('M'):
        shutil.copy2(x.b_path, os.path.join(repo_path, x.b_path))

    for name in origin_repo.untracked_files:
        if os.path.isdir(name):
            shutil.copytree(name, os.path.join(repo_path, name), symlinks=True)
        else:
            dst = os.path.join(repo_path, name)
            basedir = os.path.dirname(dst)
            if not os.path.exists(basedir):
                os.makedirs(basedir)
            shutil.copy2(name, dst, follow_symlinks=False)



    repo.index.add(
        [x.b_path for x in repo.head.commit.diff(None).iter_change_type('M')])
    repo.index.add([x for x in repo.untracked_files])
    commit = repo.index.commit('msg')
    tag = uuid1()
    repo.create_tag(tag)


    result = subprocess.call(sys.argv[1:])
    if not os.path.exists(outpath):
        os.makedirs(outpath)
    with open(runinfo_file, 'w') as f:
        json.dump({
            'cmd': {
                'args': sys.argv[1:],
                'returncode': result,
            },
            'git': {
                'path': repo_path,
                'tag': str(tag),
                'sha': hexlify(commit.binsha).decode('utf-8'),
            }
        }, f, indent=4)
    return 0


if __name__ == '__main__':
    sys.exit(main())
