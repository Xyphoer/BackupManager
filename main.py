from time import perf_counter

import shutil
import pathlib

original_tree = ""
duplicate_tree = ""

original_path = pathlib.PurePath(original_tree)
duplicate_path = pathlib.PurePath(duplicate_tree)

copied_amount = 0

#####
# Name: ignore
# Inputs: visiting (string) [current directory], contents (list) [contained directories & files]
# Output: exclude (list) [files to ignore]
# Description: ignore function for shutil.copytree - determines whether files in a directory need to be backed up.
#              Called for the original directory and all subdirectories in original_tree when used in shutil.copytree.
#####
def ignore(visiting, contents):
    global copied_amount

    exclude = []    # to contain unchanged previously backed up files
    files = 0   # to contain how many files have been backed up

    for item in contents:
        file = pathlib.Path(visiting+'/'+item)  # use current folder's path and current item in folder to get desired file's path
        if file.is_file():
            files += 1
            extension = visiting.replace(original_tree, "") # get the extra dirs walked from original_tree
            dupe_file = pathlib.Path(duplicate_tree + extension + "\\" + item)  # find location to check/copy duplicate file
            if dupe_file.exists() and dupe_file.stat().st_mtime == file.stat().st_mtime:
                exclude.append(item)    # add file to be ignored if it already exists in backup and modified time of orig = dupe
                files -= 1  # decriment files if not copying
    print("Visiting: " + visiting)
    print("Number of files: " + str(len(exclude)))
    copied_amount += files
    print(f"Copied: {files} Total: {copied_amount}")
    return exclude

start = perf_counter()

shutil.copytree(original_path, duplicate_path, ignore=ignore, dirs_exist_ok=True)
# make feeback for if something exists in backup but not in original. Implement verbosity levels.
# test with over 260 character paths copying to external drive (maybe create a thing to detect if it's necissary for those ones and notify to transfer by self)

end = perf_counter()

print(end-start)    # output time taken for backup