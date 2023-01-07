from time import perf_counter
from pathlib import Path
from shutil import copytree

import argparse

# set up parser
parser = argparse.ArgumentParser(prog="Backup Manager",
                                 description="Manages backup of everything contained in a specified directory")
parser.add_argument("-i", "--input", required=True,
                    help="The original directory path. If ommitted will not backup anything.")
parser.add_argument("-o", "--output", required=True,
                    help="The backup directory path. If ommitted will not backup anything.")
parser.add_argument("-eb", "--exclude-backup", nargs="*",
                    help="Excludes specified directories/files from backup (todo). If used without arguments, doesn't backup any files.")
parser.add_argument("-cb", "--check-backup", action="store_true",
                    help="Checks the backup directory for any files not present in the original directory.")

args = parser.parse_args()

original_path = Path(args.input)
duplicate_path = Path(args.output)

# check if provided path's exist
original_exists = original_path.exists()
duplicate_exists = duplicate_path.exists()

# keep track of how many files are going to be copied
copied_amount = 0

# store files and directories to skip in backup process
skip = args.exclude_backup if args.exclude_backup != None else []

#####
# Name: ignore
# Inputs: visiting (string) [current directory], contents (list) [contained directories & files]
# Output: exclude (list) [files to ignore]
# Description: ignore function for shutil.copytree - determines whether files in a directory need to be backed up.
#              Called for the original directory and all subdirectories in original_path when used in shutil.copytree.
#####
def ignore(visiting, contents):
    global copied_amount
    global skip

    exclude = []    # to contain unchanged previously backed up files
    folder_skip = []    # to contain any files to skip in this folder
    copy = 0   # to contain how many files have been backed up
    files = 0   # to contain how many files are contained

    print("Visiting: " + visiting)

    if visiting in skip:
        print("Skipping folder.") # test is skipping a parent dir skips child dirs
        exclude = contents
    else:
        extension = visiting.replace(str(original_path), "") # get the extra dirs walked from original_path

        for item in contents:
            file = Path(visiting+'/'+item)  # use current folder's path and current item in folder to get desired file's path
            if file.is_file():
                if str(file) in skip:
                    print("Skipping: " + item)
                    folder_skip.append(item)
                else:
                    files += 1
                    copy += 1

                    dupe_file = Path(str(duplicate_path) + extension + "\\" + item)  # find location to check/copy duplicate file
                    if dupe_file.exists() and dupe_file.stat().st_mtime == file.stat().st_mtime:
                        exclude.append(item)    # add file to be ignored if it already exists in backup and modified time of orig = dupe
                        copy -= 1  # decriment copy if not copying
        
        print(f"Number of {'unskipped ' if folder_skip != [] else ''}files already backed up: {str(len(exclude))}/{str(files)}")
        exclude += folder_skip
    
        copied_amount += copy
        print(f"Copying: {copy} Total: {copied_amount}")
    
    return exclude

#####
# Name: check_backup
# Inputs: tree (string) [directory in backup directory]
# Output: None
# Description: Check the backup directory and all contained directories for files not present in the original directory.
#####
def check_backup(tree = str(duplicate_path)):
    dupe_dir = Path(tree)
    extension = tree.replace(str(duplicate_path), "") # get the extra dirs walked from duplicate_path
    for child in dupe_dir.iterdir():    # iterate over all contents of the directory
        # if the child is a file check for it's existince in the original directory
        if child.is_file():
            original_file = Path(str(original_path) + extension + "\\" + child.name)
            if not original_file.exists():
                print(f"{child} in backup has no corresponding file at {str(original_file)}")
        # if the child is a directory, recursively call self function with that directory as the working tree
        elif child.is_dir():
            check_backup(tree = str(child))
    return

# perform backup or output error messages depending on whether provided path's exist
if (original_exists and duplicate_exists):

    # if exclude_backup is specified without arguments, don't perform backup operation
    if args.exclude_backup == []:
        print("Skipping Backup.")
    else:
        start = perf_counter()

        copytree(original_path, duplicate_path, ignore=ignore, dirs_exist_ok=True)

        end = perf_counter()

        print(f"Backup finished in {round(end-start, ndigits=2)} seconds")    # output time taken for backup

    if args.check_backup:
        check_backup()
elif not original_exists and duplicate_exists:
    print(f"Input path {str(original_path)} doesn't exist.")
elif not duplicate_exists and original_exists:
    print(f"Output path {str(duplicate_path)} doesn't exist.")
else:
    print(f"Input path {str(original_path)} and output path {str(duplicate_path)} don't exist.")