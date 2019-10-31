#!/usr/bin/python

import sys
import os
import shutil

def main():
    for arg in sys.argv[1:]:
        basepath = os.getcwd()+"/"+arg
        print("Processing files in directory: \"%s\"" % (basepath))
        print("================================")
        cntDirSkipped = 0
        cntFileProcessed = 0
        cntFileDeleted = 0
        for fname in os.listdir(basepath):
            # ITERATING OVER DIRECTORY CONTENT
            fpath = os.path.join(basepath, fname)
            if os.path.isdir(fpath):
                # skip directories
                cntDirSkipped += 1
                continue
            else:
                # process files
                cntFileProcessed += 1
                if fname[:2] == "._":
                    os.remove(fpath)
                    print("Removed hidden file: \"%s\"" % (fname))
                    cntFileDeleted += 1
                else:
                    # create directory for current file
                    dirName = fname.rsplit('.', 1)[0]
                    destDirPath = os.path.join(basepath, dirName)
                    try:
                        os.mkdir(destDirPath)
                        print("Created directory: \"%s\"" % dirName) 
                    except FileExistsError:
                        print("Failed creating directory: \"%s\"" % dirName)
                    # move file to fresh directory
                    shutil.move(fpath, os.path.join(destDirPath, fname))
                    print("Moved \"%s\" into new directory" % fname)
                continue

        print("================================")
        print("Total Skipped %d directorys" % (cntDirSkipped))
        print("Total Processed %d files" % (cntFileProcessed))
        print("Total Removed %d hidden files" % (cntFileDeleted))

if __name__ == "__main__":
    main()