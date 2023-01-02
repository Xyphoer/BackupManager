from time import perf_counter

import shutil
import pathlib
import argparse

# set up parser
parser = argparse.ArgumentParser(prog="Backup Manager",
                                 description="Manages backup of everything contained in a specified directory")
parser.add_argument("-i", "--input", required=True,
                    help="The original directory path.")
parser.add_argument("-o", "--output", required=True,
                    help="The backup directory path.")

args = parser.parse_args()

original_tree = args.input
duplicate_tree = args.output

original_path = pathlib.Path(original_tree)
duplicate_path = pathlib.Path(duplicate_tree)

# check if provided path's exist
original_exists = original_path.exists()
duplicate_exists = duplicate_path.exists()

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

# perform backup or output error messages depending on whether provided path's exist
if original_exists and duplicate_exists:
    start = perf_counter()

    shutil.copytree(original_path, duplicate_path, ignore=ignore, dirs_exist_ok=True)
    # make feeback for if something exists in backup but not in original. Implement verbosity levels.
    # test with over 260 character paths copying to external drive (maybe create a thing to detect if it's necissary for those ones and notify to transfer by self)

    end = perf_counter()

    print(end-start)    # output time taken for backup
elif not original_exists and duplicate_exists:
    print(f"Input path {original_tree} doesn't exist.")
elif not duplicate_exists and original_exists:
    print(f"Output path {duplicate_path} doesn't exist.")
else:
    print(f"Input path {original_tree} and output path {duplicate_path} don't exist.")