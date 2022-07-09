from copy import copy
from pathlib import Path
# compare modified dates to see if an already backed up file needs to be overwritten
# https://docs.python.org/3/library/shutil.html
# https://docs.python.org/3/library/shutil.html?#shutil.copytree

import shutil
import pathlib

# original = pathlib.PurePath("D:/coding projects/Projects/BackupManager/temp/[Cleo]Citrus_-_01_(10bit_BD1080p_x265).mkv")
# duplicate = pathlib.PurePath("D:/coding projects/Projects/BackupManager/temp/test.mkv")

# shutil.copy2(original, duplicate)

original_tree = pathlib.PurePath("D:/coding projects/Projects/BackupManager/temp/[Cleo] Citrus")
duplicate_tree = pathlib.PurePath("D:/coding projects/Projects/BackupManager/temp/test")

shutil.copytree(original_tree, duplicate_tree)
# test too see if actually overwrites same name stuff if data different, and if data the same. Then check to see if creating an ignore funct is necissary.
# test with over 260 character paths copying to external drive (maybe create a thing to detect if it's necissary for those ones and notify to transfer by self)