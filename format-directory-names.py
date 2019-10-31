#!/usr/bin/python

from datetime import datetime

import sys
import os
import re
import time
import random
import json
import shutil

# importing the requests library
import requests

dirDictList = {'format': [], 'skip': [], 'error': []}


def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100*iteration / float(total))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


def writeLogFile(path):
    currTimestamp = datetime.now(tz=None).strftime("%Y_%b_%d_%H%M%S%f")
    logPath = path + ("/format_log_%s.log" % (currTimestamp))
    f = open(logPath, "w+")
    f.write("# Logfile generated from \"format-directory-names.py\" from %s\n" % (currTimestamp))
    f.write("## Skipped directorys:\n")
    for skippedDir in dirDictList['skip']:
        f.write("%s\n" % (skippedDir['originalDirName']))
    f.write("## Failed to format directorys:\n")
    for errDir in dirDictList['error']:
        f.write("%s\n" % (str(errDir)))
    f.write("## Successfully formated directorys:\n")
    for formatedDir in dirDictList['format']:
        f.write("%s --> %s\n" % (str(formatedDir['originalDirName']), str(formatedDir['targetDirName'])))
    f.close()
    return logPath

def main():
    regExPattern=re.compile(r"\(\b(19|20)\d{2}\b\)")
    for arg in sys.argv[1:]:
        basepath=os.getcwd()+"/"+arg
        print("Processing files in directory: \"%s\"" % (basepath))
        print("================================")
        cntItemsProcessed=0
        totalEntrys=len(os.listdir(basepath))
        for fname in os.listdir(basepath):
            # ITERATING OVER DIRECTORY CONTENT
            fpath=os.path.join(basepath, fname)
            if os.path.isdir(fpath):
                # process directories
                if regExPattern.search(fname):
                    # dir is allready tagged
                    dirDictList['skip'].append({'originalDirName': fpath})
                else:
                    # dir is not tagged
                    queryString=fname.replace(" ", "_")
                    queryString=queryString.lower()
                    endpoint="https://v2.sg.media-imdb.com/suggestion/" + \
                        queryString[0] + "/" + queryString + ".json"
                    response=requests.get(endpoint)
                    if response.status_code == 200:
                        data=response.json()
                        try:
                            fetchedYear=data['d'][0]['y']
                            targetDir=fpath + " (" + str(fetchedYear) + ")"
                            dirDictList['format'].append({'originalDirName': fpath, 'targetDirName': targetDir})
                        except:
                            dirDictList['error'].append({'originalDirName': fpath, 'errorType': 'Invalid JSON response', 'endpoint': endpoint})
                    else:
                        dirDictList['error'].append({'originalDirName': fpath, 'errorType': 'HTTP Failure', 'httpStatus': response.status_code, 'endpoint': endpoint})
                    time.sleep(random.randrange(40, 200, 10)/1000)
            cntItemsProcessed += 1
            printProgressBar(cntItemsProcessed, totalEntrys, prefix='Fetching Meta:', suffix='Fetched', length=70)
        print("================================")
        totalDirsToFormat=len(dirDictList['format'])
        cntDirsFormated=0
        for dirToFormat in dirDictList['format']:
            # FORMAT DIRECTORYS
            shutil.move(dirToFormat['originalDirName'], dirToFormat['targetDirName'])
            cntDirsFormated += 1
            printProgressBar(cntDirsFormated, totalDirsToFormat, prefix='Formating Directorys:', suffix='Formated', length=70)
        print("================================")
        print("Total skipped directorys: %d" % (len(dirDictList['skip'])))
        print("Total API errors: %d" % (len(dirDictList['error'])))
        print("Total formated directorys: %d" % (len(dirDictList['format'])))
        print("Check out logfile:", writeLogFile(basepath))

if __name__ == "__main__":
    main()
