from time import perf_counter
# compare modified dates to see if an already backed up file needs to be overwritten
# https://docs.python.org/3/library/shutil.html
# https://docs.python.org/3/library/shutil.html?#shutil.copytree

import shutil
import pathlib

# original = pathlib.PurePath("D:/coding projects/Projects/BackupManager/temp/[Cleo]Citrus_-_01_(10bit_BD1080p_x265).mkv")
# duplicate = pathlib.PurePath("D:/coding projects/Projects/BackupManager/temp/test.mkv")

# shutil.copy2(original, duplicate)

original_tree = "D:\\coding projects\\Projects\\BackupManager\\temp\\[Cleo] Citrus"
duplicate_tree = "D:\\coding projects\\Projects\\BackupManager\\temp\\test"

original_path = pathlib.PurePath(original_tree)
duplicate_path = pathlib.PurePath(duplicate_tree)

def ignore(visiting, contents):
    exclude = []

    for item in contents:
        file = pathlib.Path(visiting+'/'+item)
        if file.is_file():
            extension = visiting.replace(original_tree, "")
            dupe_file = pathlib.Path(duplicate_tree + extension + "\\" + item)
            if dupe_file.exists() and dupe_file.stat().st_mtime == file.stat().st_mtime:
                exclude.append(item)
    return exclude

start = perf_counter()

shutil.copytree(original_path, duplicate_path, ignore=ignore, dirs_exist_ok=True)
# test too see if actually overwrites same name stuff if data different, and if data the same. Then check to see if creating an ignore funct is necissary.
# test with over 260 character paths copying to external drive (maybe create a thing to detect if it's necissary for those ones and notify to transfer by self)

end = perf_counter()

print(end-start)