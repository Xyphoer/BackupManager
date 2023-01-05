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
parser.add_argument("-cb", "--check-backup", action="store_true",
                    help="Checks the backup directory for any files not present in the original directory.")

args = parser.parse_args()

original_path = pathlib.Path(args.input)
duplicate_path = pathlib.Path(args.output)

# check if provided path's exist
original_exists = original_path.exists()
duplicate_exists = duplicate_path.exists()

# keep track of how many files are going to be copied
copied_amount = 0

#####
# Name: ignore
# Inputs: visiting (string) [current directory], contents (list) [contained directories & files]
# Output: exclude (list) [files to ignore]
# Description: ignore function for shutil.copytree - determines whether files in a directory need to be backed up.
#              Called for the original directory and all subdirectories in original_path when used in shutil.copytree.
#####
def ignore(visiting, contents):
    global copied_amount

    exclude = []    # to contain unchanged previously backed up files
    files = 0   # to contain how many files have been backed up

    extension = visiting.replace(original_path.as_posix(), "") # get the extra dirs walked from original_path

    for item in contents:
        file = pathlib.Path(visiting+'/'+item)  # use current folder's path and current item in folder to get desired file's path
        if file.is_file():
            files += 1
            dupe_file = pathlib.Path(duplicate_path.as_posix() + extension + "\\" + item)  # find location to check/copy duplicate file
            if dupe_file.exists() and dupe_file.stat().st_mtime == file.stat().st_mtime:
                exclude.append(item)    # add file to be ignored if it already exists in backup and modified time of orig = dupe
                files -= 1  # decriment files if not copying
    print("Visiting: " + visiting)
    print("Number of files already backed up: " + str(len(exclude)))
    copied_amount += files
    print(f"Copying: {files} Total: {copied_amount}")
    return exclude

#####
# Name: check_backup
# Inputs: tree (string) [directory in backup directory]
# Output: None
# Description: Check the backup directory and all contained directories for files not present in the original directory.
#####
def check_backup(tree = duplicate_path.as_posix()):
    dupe_dir = pathlib.Path(tree)
    extension = tree.replace(duplicate_path.as_posix(), "") # get the extra dirs walked from duplicate_path
    for child in dupe_dir.iterdir():    # iterate over all contents of the directory
        # if the child is a file check for it's existince in the original directory
        if child.is_file():
            original_file = pathlib.Path(original_path.as_posix() + extension + "\\" + child.name)
            if not original_file.exists():
                print(f"{child} in backup has no corresponding file at {original_file.as_posix()}")
        # if the child is a directory, recursively call self function with that directory as the working tree
        elif child.is_dir():
            check_backup(tree = child.as_posix())
    return

# perform backup or output error messages depending on whether provided path's exist
if original_exists and duplicate_exists:
    start = perf_counter()

    shutil.copytree(original_path, duplicate_path, ignore=ignore, dirs_exist_ok=True)

    end = perf_counter()

    print(f"Backup finished in {round(end-start, ndigits=2)} seconds")    # output time taken for backup

    if args.check_backup:
        check_backup()
elif not original_exists and duplicate_exists:
    print(f"Input path {original_path.as_posix()} doesn't exist.")
elif not duplicate_exists and original_exists:
    print(f"Output path {duplicate_path.as_posix()} doesn't exist.")
else:
    print(f"Input path {original_path.as_posix()} and output path {duplicate_path.as_posix()} don't exist.")