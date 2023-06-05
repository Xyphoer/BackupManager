from time import perf_counter
from pathlib import Path
from shutil import copytree

import argparse
import logging

# set up parser
parser = argparse.ArgumentParser(prog="Backup Manager",
                                 description="Manages backup of everything contained in a specified directory")
parser.add_argument("-i", "--input", required=True,
                    help="The original directory path.")
parser.add_argument("-o", "--output", required=True,
                    help="The backup directory path. If this doesn't exist it will be created.")
parser.add_argument("-eb", "--exclude-backup", nargs="*",
                    help="""Excludes specified directories/files from backup. Accepts folder/file paths or a text file of paths
                    seperated by new lines. Precede text file with '>'.
                    If used without arguments, doesn't backup any files.
                    Takes precedence over --only-backup""")
parser.add_argument("-ob", "--only-backup", nargs="*",
                    help="""Only backup specified directories/files. Accepts folder/file paths or a text file of paths
                    seperated by new lines. Precede text file with '>'.""")
parser.add_argument("-cb", "--check-backup", action="store_true",
                    help="Checks the backup directory for any files not present in the original directory.")
parser.add_argument("-log", "--loglevel", type=int, choices=range(4), default=2,
                    help="""Details how much info should be displayed. The higher, the more info.
                    0: No info  1: Warnings only  2: Basic info & warnings  3: Debug info & previous""")

args = parser.parse_args()

log_dict = {0: logging.NOTSET, 1: logging.WARNING, 2: logging.INFO, 3: logging.DEBUG}

logging.basicConfig(format='%(levelname)s: %(message)s', level=log_dict[args.loglevel])

original_path = Path(args.input)
duplicate_path = Path(args.output)

# check if provided path's exist
original_exists = original_path.exists()
duplicate_exists = duplicate_path.exists()

logging.debug(str(original_path) + " -> " + str(duplicate_path))

# keep track of how many files are going to be copied
copied_amount = 0

#####
# Name: check_file
# Inputs: in_file (Path) [input text file]
# Output: out (list) [files to skip or only include]
# Description: Checks to see if a provided file exists, is a text file, and can be read.
#####
def check_file(in_file):
    out = []
    if not in_file.exists():
            logging.warning(str(in_file) + " doesn't exist.")
    elif in_file.is_dir():
        logging.warning(str(in_file) + " is not a file.")
    elif not in_file.suffix == ".txt":
        logging.warning(str(in_file) + " is not a text (txt) file.")
    else:
        try:
            with open(in_file) as file:
                out = file.read().split("\n")     # if file exists and is a txt file, read it as out ("skip"/"only_backup")
        except PermissionError:
            logging.warning("Permission Denied: Unable to open " + str(in_file))
    return out

# store files and directories to skip in backup process
skip = args.exclude_backup if args.exclude_backup != None else []  # read the command line for files

if len(skip) == 1 and skip[0][0] == ">":  # check if providing a text file
    input_file = Path(skip[0][1:])   # get text file path (exclude ">")
    skip = check_file(input_file)
    

# store files and directories to only backup
only_backup = args.only_backup if args.only_backup != None else []  # read the command line for files

if len(only_backup) == 1 and only_backup[0][0] == ">":  # check if providing a text file
    input_file = Path(args.only_backup[0][1:])   # get text file path (exclude ">")
    only_backup = check_file(input_file)
    

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
    global only_backup

    exclude = []    # to contain unchanged previously backed up files
    folder_skip = []    # to contain any files to skip in this folder
    copy = 0   # to contain how many files have been backed up
    files = 0   # to contain how many files are contained

    logging.info("Visiting: " + visiting)

    if only_backup:     # is only_backup is not empty
        if visiting not in only_backup:     # if visiting is in only_backup move forward as normal
            # if visiting is not in only_backup set folder_skip to initially be everything in visiting that's not in only_backup
            folder_skip = [location for location in contents if visiting+"\\"+location not in only_backup]

    # if visiting is listed to skip or only_backup isn't empty and neither visiting nor anything in contents are in only_backup
    if visiting in skip or len(contents) == len(folder_skip):
        logging.info("Skipping folder.") # test is skipping a parent dir skips child dirs
        exclude = contents
    else:
        extension = visiting.replace(str(original_path), "") # get the extra dirs walked from original_path
        logging.info("Backup location: " + str(duplicate_path) + extension)

        for item in contents:  # contents - [s.split("\\")[-1] for s in skip] - [e.split("\\")[-1] for e in exclude]
            file = Path(visiting+"\\"+item)  # use current folder's path and current item in folder to get desired file's path
            if file.is_file():

                if str(file) in skip:   # skip item because item listed in exclude_backup
                    logging.debug("Skipping (eb): " + item)
                    folder_skip.append(item)
                elif item in folder_skip:   # skip item because item not listed in only_backup
                    logging.debug("Skipping (ob): " + item)

                else:
                    files += 1
                    copy += 1

                    dupe_file = Path(str(duplicate_path) + extension + "\\" + item)  # find location to check/copy duplicate file
                    if dupe_file.exists() and dupe_file.stat().st_mtime == file.stat().st_mtime:
                        logging.debug("Already Backed Up: " + item)
                        exclude.append(item)    # add file to be ignored if it already exists in backup and modified time of orig = dupe
                        copy -= 1  # decriment copy if not copying
        
        if len(folder_skip) != 0:
            logging.info(f"Skipping {len(folder_skip)} files")
        logging.info(f"Number of {'unskipped ' if folder_skip != [] else ''}files already backed up: {str(len(exclude))}/{str(files)}")
        exclude += folder_skip
    
        copied_amount += copy
        logging.info(f"Copying: {copy} Total: {copied_amount}")
    
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
                logging.info(f"{child} in backup has no corresponding file at {str(original_file)}")
        # if the child is a directory, recursively call self function with that directory as the working tree
        elif child.is_dir():
            check_backup(tree = str(child))
    return

# perform backup or output error messages depending on whether provided path's exist
if original_exists:

    # if exclude_backup is specified without arguments, don't perform backup operation
    if args.exclude_backup == []:
        logging.info("Skipping Backup.")
    else:
        start = perf_counter()

        copytree(original_path, duplicate_path, ignore=ignore, dirs_exist_ok=True)

        end = perf_counter()

        logging.info(f"Backup finished in {round(end-start, ndigits=2)} seconds")    # output time taken for backup

    if args.check_backup:
        check_backup()
else:
    logging.warning(f"Input path {str(original_path)} doesn't exist.")
