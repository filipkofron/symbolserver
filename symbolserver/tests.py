from time import sleep
from zipfile import ZipFile
from testserver import start_server
import fileio
import httpio
import os
import shutil
import symboldb
import symbolhash
import symbolpublisher
import tempfile


def prepare_and_get_test_data_dir() -> str:
    test_data_dir = tempfile.mkdtemp()
    try:
        zip_file_path = "../testdata.zip"

        # Copy the zip itself
        shutil.copyfile(zip_file_path, os.path.join(test_data_dir, "testdata.zip"))

        # Unpack the zip contents as well
        with ZipFile(zip_file_path, "r") as test_data_zip:
            test_data_zip.extractall(test_data_dir)

    except Exception as e:
        # Delete temporary files
        shutil.rmtree(test_data_dir)
        raise e

    return test_data_dir


def fill_test_data():
    symboldb.store_symbol(
        symboldb.Symbol("DEADBEEF", "poo.exe", "http://example.com/poo.exe", None)
    )
    symboldb.store_symbol(
        symboldb.Symbol(
            "FEEDBABE",
            "foo.pd_",
            "http://example.com/foo.exe",
            "stored/FEEDBABE/foo.pd_",
        )
    )
    symboldb.store_symbol(
        symboldb.Symbol(
            "FEEDBABE",
            "foo.pd_",
            "http://example.com/foo.pdb",
            "stored/FEEDBABE/foo.pd_",
        )
    )
    symboldb.store_symbol(
        symboldb.Symbol("FEEDBABE", "boo.dll", None, "stored/FEEDBABE/boo.dll")
    )
    symboldb.store_source(symboldb.Source("C:\\foo.exe", False, 1))
    symboldb.store_source(symboldb.Source("C:\\foo.pdb", False, 2))
    symboldb.store_source(symboldb.Source("C:\\foo.pdb", True, 2))
    symboldb.store_source(symboldb.Source("C:\\moo.exe", True, 0))


def hash_test(server_addr: str, path_fs: str):
    files_to_test = [
        ('HelloWorld.exe',  '62A0EB958000'),
        ('HelloWorld.pdb',  '59442B4112F54557AE800C736F2B5DAD1'),
        ('HelloDll.dll',    '62A0EC129000'),
        ('HelloDll.pdb',    '7BE215C28E704CFC85F579A7025B1C131')
    ]

    for file, hash in files_to_test:
        http_path = server_addr + f'/testdata/{file}'
        with httpio.open(http_path, 1024 * 1024 * 4) as f:
            current_hash = symbolhash.hash(f)
            assert(hash == current_hash)
            print(f'{http_path}: {current_hash}')

        disk_path = os.path.join(path_fs, 'testdata', file)
        with fileio.open_rb(disk_path) as f:
            current_hash = symbolhash.hash(f)
            assert(hash == current_hash)
            print(f'{disk_path}: {current_hash}')


def test():
    symboldb.init_db(":memory:")
    fill_test_data()
    print(symboldb.find_symbol("FEEdBABE", "foo.pd_"))
    print(symboldb.dump())
    pass


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as symstore_dir:
        test_data_dir = prepare_and_get_test_data_dir()

        try:
            server_addr = start_server(test_data_dir)
            test()
            hash_test(server_addr, test_data_dir)

            link_mode = False
            params = symbolpublisher.Params([], symstore_dir, False, 1, link_mode, False, False)
            symbolpublisher.publish_path(
                os.path.join(test_data_dir, "testdata", "HelloWorld.exe"), params
            )
            link_mode = True
            params = symbolpublisher.Params([], symstore_dir, False, 1, link_mode, False, False)
            symbolpublisher.publish_path(
                os.path.join(test_data_dir, "testdata", "HelloDll.dll"), params
            )
            print(symboldb.dump())

        except Exception as e:
            raise e
        finally:
            # Delete temporary files
            shutil.rmtree(test_data_dir)

        exit(0)
