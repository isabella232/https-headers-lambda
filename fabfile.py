#!/usr/bin/env python
# _*_ coding:utf-8 _*_
from fabric.api import local, task, execute
import os
import logging
import zipfile

"""
Logging
"""
LOG_FORMAT = '%(levelname)s:%(name)s:%(asctime)s: %(message)s'
LOG_LEVEL = logging.INFO

# GLOBAL SETTINGS
cwd = os.path.dirname(__file__)
logging.basicConfig(format=LOG_FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)


def zip_file(zipname, path, arcname=None, mode='w'):
    """
    Zip or append files
    - path: relative to fabfile.py
    - arcname: if different from path
    """
    OUTPUT_PATH = os.path.join(cwd, 'zip')
    INPUT_PATH = os.path.join(cwd, path)
    if not arcname:
        arcname = os.path.basename(INPUT_PATH)

    with zipfile.ZipFile('%s/%s.zip' % (OUTPUT_PATH, zipname), mode) as z:
        z.write(INPUT_PATH, arcname, zipfile.ZIP_DEFLATED)


def zip_contents(zipname, folder, excl_dirs, excl_ext, mode='w'):
    """
    Zip contents of folders recursively
    - folder: relative to fabfile.py
    - Ignoring folders names in excl_dirs
    - Ignoring file extensions in excl_ext
    """

    INPUT_PATH = os.path.join(cwd, folder)
    OUTPUT_PATH = os.path.join(cwd, 'zip')

    if not excl_ext:
        excl_ext = []
    if not excl_dirs:
        excl_dirs = []

    with zipfile.ZipFile('%s/%s.zip' % (OUTPUT_PATH, zipname), mode) as z:
        rootlen = len(INPUT_PATH) + 1
        for base, dirs, files in os.walk(INPUT_PATH):
            # Exclude folders in-place
            dirs[:] = [d for d in dirs if d not in excl_dirs]
            for file in files:
                if os.path.splitext(file)[1].lower() in excl_ext:
                    continue
                fn = os.path.join(base, file)
                logger.debug("arcname: %s" % fn[rootlen:])
                z.write(fn, fn[rootlen:], zipfile.ZIP_DEFLATED)


@task
def render(name='code'):
    """
    Create lambda code deployment package
    - Add code files
    - compress into zipfile
    """
    BASE_PATH = os.path.join(cwd, name)
    OUTPUT_PATH = os.path.join(cwd, 'zip')
    # Create output files folder if needed
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)
    # Add source files
    zip_contents('code', 'code', None, None, 'w')


@task
def deploy(name='code', function='https-headers-lambda'):
    execute('render', name)
    command = 'aws lambda update-function-code'
    command += ' --zip-file=fileb://zip/%s.zip' % (name)
    command += ' --function-name %s' % (function)
    logger.info('command: %s' % command)
    local(command)
