# Code originally by:
# https://stackoverflow.com/questions/748675/finding-duplicate-files-and-removing-them
# https://gist.github.com/tfeldmann/fc875e6630d11f2256e746f67a09c1ae

# with minor modifications by me

from collections import defaultdict
import hashlib
import os
import sys

import os
import sys
import hashlib
from collections import defaultdict


def chunk_reader(fobj, chunk_size=1024):
    """ Generator that reads a file in chunks of bytes """
    while True:
        chunk = fobj.read(chunk_size)
        if not chunk:
            return
        yield chunk


def get_hash(filename, first_chunk_only=False, hash_algo=hashlib.sha1):
    hashobj = hash_algo()
    with open(filename, "rb") as f:
        if first_chunk_only:
            hashobj.update(f.read(1024))
        else:
            for chunk in chunk_reader(f):
                hashobj.update(chunk)
    return hashobj.digest()


def check_for_duplicates(path, size_hash_update=None, small_hash_update=None, full_hash_update=None):
    files_by_size = defaultdict(list)
    files_by_small_hash = defaultdict(list)
    files_by_full_hash = dict()

    # maybe not worth doing this just for percentages but kind of fun...
    curr_files = 0
    total_files = count_files(path)

    for dirpath, _, filenames in os.walk(path):
        for filename in filenames:
            curr_files += 1
            if size_hash_update:
                size_hash_update(curr_files / total_files)
            full_path = os.path.join(dirpath, filename)
            try:
                # if the target is a symlink (soft one), this will
                # dereference it - change the value to the actual target file
                full_path = os.path.realpath(full_path)
                file_size = os.path.getsize(full_path)
            except OSError:
                # not accessible (permissions, etc) - pass on
                continue
            files_by_size[file_size].append(full_path)

    if size_hash_update:
        size_hash_update(1)

    # For all files with the same file size, get their hash on the first 1024 bytes
    total_files = len(files_by_size.items())
    curr_files = 0
    for file_size, files in files_by_size.items():
        curr_files += 1
        if small_hash_update:
            small_hash_update(curr_files / total_files)

        if len(files) < 2:
            continue  # this file size is unique, no need to spend cpu cycles on it

        for filename in files:
            try:
                small_hash = get_hash(filename, first_chunk_only=True)
            except OSError:
                # the file access might've changed till the exec point got here
                continue
            files_by_small_hash[(file_size, small_hash)].append(filename)

    if small_hash_update:
        small_hash_update(1)

    # For all files with the hash on the first 1024 bytes, get their hash on the full
    # file - collisions will be duplicates
    total_files = len(files_by_small_hash.values())
    curr_files = 0
    for files in files_by_small_hash.values():
        curr_files += 1
        if full_hash_update:
            full_hash_update(curr_files / total_files)
        if len(files) < 2:
            # the hash of the first 1k bytes is unique -> skip this file
            continue

        for filename in files:
            try:
                full_hash = get_hash(filename, first_chunk_only=False)
            except OSError:
                # the file access might've changed till the exec point got here
                continue

            # lets take some inspiration from hash-table collision chaining to return a dictonary
            # with a list of duplicated files :)
            if full_hash in files_by_full_hash:
                files_by_full_hash[full_hash].append(filename)
            else:
                files_by_full_hash[full_hash] = [filename]
    if full_hash_update:
        full_hash_update(1)
    return files_by_full_hash


def count_files(path):
    count = 0
    for root_dir, cur_dir, files in os.walk(path):
        count += len(files)
    return count
