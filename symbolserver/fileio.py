#from symstore

from __future__ import absolute_import

import errno
import errs
import os


def read_all(fname, mode=None):
    """
    read all contents of a file
    """
    args = [fname]
    if mode is not None:
        args.append(mode)

    with open(*args) as f:
        return f.read()


def open_rb(filepath):
    """
    open file for reading, in binary mode

    :raises symstore.FileNotFound: if specified file does not exist
    """
    try:
        return open(filepath, "rb")
    except IOError as e:
        # to be backward compatible with python 2,
        # catch IOError exception and check the errnor,
        # to detect when specified file does not exits
        if e.errno == errno.ENOENT:
            raise errs.FileNotFound(e.filename)
        # unexpected error
        raise e

def copy_buffered_io_to_file(io, file):
    """ Copy the given BufferedIOBase to the given opened file """

    

def write_opened_file(file, path: str):
    #file.seek(0, os.SEEK_END)
    #fsize = file.tell()
    file.seek(0, os.SEEK_SET)

    try:
        with open(path, "wb") as f_new:
            f_new.seek(0, os.SEEK_SET)
            bufsize: int = 256 * 1024
            while True:
                buf = file.read(bufsize)
                if not buf:
                    break
                f_new.write(buf)
            f_new.truncate
    except IOError as e:
        # to be backward compatible with python 2,
        # catch IOError exception and check the errnor,
        # to detect when specified file does not exits
        if e.errno == errno.ENOENT:
            raise errs.FileNotFound(e.filename)
        # unexpected error
        raise e
