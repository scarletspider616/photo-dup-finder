import send2trash

def delete_duplicates(dups, delete_duplicate_update=None):
    total = len(dups)
    count = 0
    for hash, files in dups.items():
        if delete_duplicate_update:
            count += 1
            delete_duplicate_update(count / total)
        delete_duplicate(hash, files)

def delete_file(file):
    send2trash.send2trash(file)

def delete_duplicate(hash, files):
    print(f'Identified files for {hash}:')
    print(f'{files}')
    for file in files[1:]:
        # delete everything except the first one
        print(f'Sending {file} to trash....')
        delete_file(file)

