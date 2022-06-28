# MIT License

# Copyright (c) 2022 Filip Kofron

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import argparse
from functools import partial
from logging import DEBUG
from typing import List, NamedTuple, Tuple
from artifactory import ArtifactoryPath
import asynctaskgraph as atg
import httpio
import logging
import os
import pickle
import requests
import symboldb
import symbolhash
from urllib.parse import urlparse
import xml.etree.ElementTree as et
import zipfile

class Params(NamedTuple):
    excludes: List[str]
    skip_last_errors: bool # Not implemented
    threads: int
    link_mode: bool # Stored symbol will be a link to the source location
    artifactory: bool
    overwrite: bool

def is_excluded(path, excludes: List[str]):
    path_forward_slashes = str(path).replace("\\", "/")
    for exclude in excludes:
        if len(exclude) > 0 and path_forward_slashes.find(exclude) >= 0:
            return True
    return False

def is_supported_archive(path):
    """ Checks whether the given path (str or convertible to it) is a supported archive (e.g. zip, nupkg, etc.) """

    supported_archives = [".zip", ".nupkg"]
    for ext in supported_archives:
        if str(path).lower().endswith(ext):
            return True
    return False

def is_symbol_dll_exe(path):
    """ Checks whether the given path (str or convertible to it) is a publishable file to the symbol store (.exe, .dll, .pdb) """

    symbol_dll_exe = [".dll", ".exe", ".pdb"]
    for ext in symbol_dll_exe:
        if str(path).lower().endswith(ext):
            return True
    return False

def copy_buffered_io_to_file(io, file):
    """ Copy the given BufferedIOBase to the given opened file """

    bufsize: int = 256 * 1024
    while True:
        buf = io.read(bufsize)
        if not buf:
            break
        file.write(buf) 

def deploy_zip_contents(opened_file, params: Params):
    with zipfile.ZipFile(opened_file) as zip_contents:
        for zip_info in zip_contents.infolist():
            if not zip_info.is_dir():
                if is_symbol_dll_exe(zip_info.filename) and not is_excluded(zip_info.filename, params.excludes):
                    logging.debug(f"Deploying {zip_info.filename} from zip to DB")
                    raise "Not implemented"
                    #zip_contents.extract(zip_info, dest_path)

def deploy_file(name, opened_file, params: Params):
    logging.debug(f"Deploying {name} to DB")

    hash = symbolhash.hash(opened_file)

    existing_symbol = symboldb.find_symbol(hash, name)
    if existing_symbol and not params.overwrite
        logging.info(f"{name}:{hash} already exists, skipping")
        return

    if existing_symbol and params.overwrite:
        logging.info(f"{name}:{hash} already exists, overwriting")

    logging.info(f"{name}:{hash} deploying..")

    symbol = symboldb.Symbol(hash, filename, opened_file.name if params.link_mode else None, 

    symboldb.store_symbol
    
    raise("Not implemented")

    #with open(dest_path + os.path.sep + name, 'wb') as output_file:
    #    copy_buffered_io_to_file(opened_file, output_file)

def deploy_file_or_archive(path, params: Params):
    """ Fetches the given symbol file path (str or convertible to it) to destination folder path, extracts files if it is a known archive. """

    if is_excluded(path, params.excludes):
        return

    # Try http or fallback to os filesystem path
    if str(path).lower().startswith("http"):
        # Check if archive and extract all files
        if is_supported_archive(path):
            with httpio.open(path, 1024 * 1024 * 4) as remote_file:
                deploy_zip_contents(remote_file, params)
        # Check if a supported file
        elif is_symbol_dll_exe(path):
            with httpio.open(path, 1024 * 1024 * 4) as remote_file:
                deploy_file(os.path.basename(urlparse(str(path)).path), remote_file, params)
        else:
            raise Exception(f"Unsupported symbol file or archive of symbol files: {str(path)}")
    else:
        # Check if archive and extract all files
        if is_supported_archive(path):
            with open(path, "rb") as file:
                deploy_zip_contents(file, params)
        # Check if a supported file
        elif is_symbol_dll_exe(path):
            with open(path, "rb") as file:
                deploy_file(os.path.basename(urlparse(str(path)).path), file, params)
        else:
            raise Exception(f"Unsupported symbol file or archive of symbol files: {str(path)}")

def find_latest_artifact_in_maven_metadata_xml(maven_path_xml):
    # JsonFile.xml :)
    json = requests.get(maven_path_xml).json()
    xml = requests.get(json["downloadUri"]).text
    version = et.fromstring(xml).find("version").text
    path = maven_path_xml.split("maven-metadata.xml")[0].replace("api/storage/", "") + "/" + version
    arti = ArtifactoryPath(path)
    last_zip = None
    for p in arti.glob("**/*.zip"):
        last_zip = p

    if last_zip:
        return str(last_zip)

    raise Exception("No artifact found")

def publish_path_or_maven_metadata(path, params: Params):

    actual_file_or_archive = find_latest_artifact_in_maven_metadata_xml(path) if str(path).lower().endswith(".xml") else path
    deploy_file_or_archive(actual_file_or_archive, params)

def publish_path(url, params: Params) -> None:
    """ Publishes a given symbol or archive of symbols and publishes it to the given symbol store path. """

    if is_excluded(url, params.excludes):
        return

    try:
        publish_path_or_maven_metadata(url, params)    
    except Exception as e:
        raise e

# TODO: Replace with source
class ArtifactorySet:
    def __init__(self):
        self.version = 0
        self.string_set = set()

    def __id_from_parts(self, parts: List[str]) -> str:
        return "".join(parts)

    def contains(self, parts: List[str]) -> bool:
        return self.__id_from_parts(parts) in self.string_set

    def set(self, parts: List[str]):
        self.string_set.add(self.__id_from_parts(parts))

class ArtifactoryDatabase:
    def __init__(self, path: str):
        self.path = path
        self.deploy_counter_buffer = 16
        self.deploy_counter = 1
        try:
            with open(self.path, "rb") as f:
                self.__set = pickle.load(f)
                if self.__set.version != ArtifactorySet().version:
                    msg = f"Incompatible database version in {self.path}"
                    logging.warning(msg)
                    raise Exception(msg)
            logging.info(f"Artifactory DB loaded from {str(self.path)}")
        except:
            logging.warning(f"Artifactory DB failed to load from {str(self.path)}, creating new one.")
            self.__set = ArtifactorySet()

    def buffered_commit(self):
        self.deploy_counter -= 1
        if self.deploy_counter <= 0:
            logging.info(f"DB reached {self.deploy_counter_buffer} buffered commits.")
            self.commit()

    def commit(self):
        self.deploy_counter = self.deploy_counter_buffer
        logging.info(f"Commiting DB of {len(self.__set.string_set)} items to {self.path}")
        with open(self.path, "wb") as f:
            pickle.dump(self.__set, f, pickle.HIGHEST_PROTOCOL)

    def get_set(self):
        return self.__set

def artifactory_deploy_task(db: ArtifactoryDatabase, path: ArtifactoryPath, params: Params, executor: atg.Executor) -> List[atg.Task]:
    present = db.get_set().contains(path.parts)
    logging.debug(f"{path.parts} present: {present}")
    if not present:
        logging.info(f"Trying to publish {str(path)}")
        try:
            publish_path(path, params) # move params
            db.get_set().set(path.parts)
            logging.info(f"Success {str(path)}")
            db.buffered_commit()
        except Exception as e:
            logging.exception(e)
            logging.info(f"Fail {str(path)}")

    return []

def artifactory_traverse_step(path: ArtifactoryPath, params: Params) -> Tuple[List[ArtifactoryPath], List[ArtifactoryPath]]:
    files = []
    dirs = []
    try:
        for p in path:
            try:
                if not is_excluded(p, params.excludes):
                    # TODO: is_dir sometimes throws 401
                    if p.is_dir():
                        dirs.append(p)
                    else:
                        if is_supported_archive(p) or is_symbol_dll_exe(p):
                            files.append(p)
            except:
                logging.warning(f"Error accessing: {p}")
    except:
        logging.warning(f"Error accessing: {path}")
    return files, dirs

def artifactory_traverse_task(db: ArtifactoryDatabase, artifactory_path: ArtifactoryPath, params: Params, deploy_executor: atg.Executor, parallel_executor: atg.Executor) -> List[atg.Task]:
    logging.debug(f"artifactory_traverse_task: {artifactory_path}")

    files, dirs = artifactory_traverse_step(artifactory_path, params)

    for dir in dirs:
        parallel_executor.schedule_func(artifactory_traverse_task, db, dir, params, deploy_executor)

    for file in files:
        deploy_executor.schedule_func(artifactory_deploy_task, db, file, params)
    return []

def publish_artifactory(artifactory_path, params: Params):
    artifactory_root = ArtifactoryPath(artifactory_path)

    paths = []

    if len(artifactory_root.repo) > 0:
        paths.append(artifactory_root)
    else:
        # Find all repositories, but ignore virtual ones as they are duplicates
        logging.debug("Looking up existing repositories")
        repositories = filter(lambda repo : str(repo).lower().find("virtual") == -1, artifactory_root.get_repositories())
        for repo in repositories:
            paths.append(ArtifactoryPath(str(artifactory_root / repo.name)))

    db_store = params.store_path + os.path.sep +  "data.pickle"

    db = ArtifactoryDatabase(db_store)

    with atg.Executor(1) as deploy_executor:
        with atg.Executor(params.threads) as parallel_executor:
            for path in paths:
                parallel_executor.schedule_func(artifactory_traverse_task, db, path, params, deploy_executor)

    db.commit()
    logging.info("All done")

if __name__ == "__main__":
    logging.basicConfig(format="%(threadName)s:%(message)s")
    # logging.basicConfig(format="%(threadName)s:%(message)s")
    logging.root.setLevel(logging.INFO)

    parser = argparse.ArgumentParser(description="""
        Symbol publisher for individual symbol files (exe, dll, pdb), archives containing them (zip, nuget) or Artifactory.
    """)

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--arti", type=str, help="URL of Artifactory server, will upload everything in all subdirectories (virtual repositories are skipped if they are not part of the given URL).")
    group.add_argument("--file", type=str, help="URL or file system path of symbol files (exe, dll, pdb) or archive (zip, nuget)")

    parser.add_argument("--threads", type=int, default=8, help="Number of threads for parallel traversal.")
    parser.add_argument("--exclude", type=str, default="", help="Exclude files by comma separated keywords. If a keyword is found in a path, it is completely skipped. Only forward slashes are supported.")
    parser.add_argument("--store", type=str, required=True, help="Path to a symbole store. Committing to a non-existing symbol store will creata a new one.")
    parser.add_argument("--verbose", dest="verbose", action="store_true", help="Verbose mode, all messages will be printed.")
    parser.add_argument("--quiet", dest="quiet", action="store_true", help="Nothing will be printed")
    parser.add_argument("--skipLastErrors", dest="skipLastErrors", action="store_true", help="Last errored out items will be skipped.")
    parser.add_argument("--linkMode", dest="linkMode", action="store_true", help="Instead of actual file deploys only a text file with path to the actual file. Supported for artifactory or http paths only.")
    parser.set_defaults(verbose=False)
    parser.set_defaults(quiet=False)
    parser.set_defaults(skipLastErrors=False)
    parser.set_defaults(linkMode=False)

    args = parser.parse_args()

    excludes = [item.strip() for item in args.exclude.split(",")]

    params = Params(args.store, excludes, args.skipLastErrors, args.threads, args.linkMode, True if args.arti else False)

    if args.verbose:
        logging.root.setLevel(logging.DEBUG)

    if args.quiet:
        logging.root.setLevel(logging.CRITICAL)

    if args.arti:
        publish_artifactory(args.arti, params)

    if args.file:
        publish_path(args.file, params)
