import os
import shutil
import tempfile
from time import sleep
from symboldb import test as symboldb_test
from symbolhash import test as symbolhash_test
from symbolpublisher import publish_file
from symbolpublisher import Params
from zipfile import ZipFile
from testserver import start_server

def prepare_and_get_test_data_dir() -> str:
    test_data_dir = tempfile.mkdtemp()
    try:
        zip_file_path = '../testdata.zip'

        # Copy the zip itself
        shutil.copyfile(zip_file_path, os.path.join(test_data_dir, 'testdata.zip'))

        # Unpack the zip contents as well
        with ZipFile(zip_file_path, 'r') as test_data_zip:
            test_data_zip.extractall(test_data_dir)

    except Exception as e:
        # Delete temporary files
        shutil.rmtree(test_data_dir)
        raise e

    return test_data_dir

if __name__ == '__main__':
    symstore_dir = tempfile.mkdtemp()
    test_data_dir = prepare_and_get_test_data_dir()

    try:
        symboldb_test()
        symbolhash_test()

        start_server(test_data_dir)

        params = Params(symstore_dir, [], False, 1, True, False)
        publish_file(os.path.join(test_data_dir, 'testdata', "HelloWorld.exe"), params)

    except Exception as e:
        raise e
    finally:
        # Delete temporary files
        shutil.rmtree(test_data_dir)

    exit(0)
