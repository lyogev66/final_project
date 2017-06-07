#!/usr/bin/python
import re
import getopt, sys

##=======================================================================================================
##  Define variables
##=======================================================================================================





def main(**kwargs):
    ""
    global outfile
    global out_dict, in_dict, clk_dict, false_path_list, false_path_dict, files_dict
    import glob, os
    path = os.getcwd() + "\\blocks_after_timing_change\\"

    if not os.path.exists(path + "\out/"):
        os.mkdir(path + "/out/")

    files_dict = {}
    out_dict = {}
    for myfile in glob.glob(path + "*.lib"):
        try:
            files_dict[myfile.replace(".lib", "").replace(path,"")] = open(myfile, "r")
            out_dict[myfile.replace(".lib", "").replace(path,"")] = open(myfile.replace(".lib", "")+"_new.lib", "w")
        except:
            pass

    print files_dict
    for fileName in files_dict.keys():
        currentFile = files_dict[fileName]
        outFile= out_dict[fileName]
        parseFile(currentFile,outFile)

    # if start_f: start(files_dict['File_start_block'])

def parseFile(file,outFile):
    flag = False
    for line in file:
        if "constraint" in line or "transition" in line:
            flag = True
        elif "}" in line:
            flag =False
        elif " values(\\" in line or ");" in line:
            pass
        elif flag:

            numberslist = re.findall(r"-*[0-1].\d+", line)
            if len(numberslist) > 0:
                # print line
                # numberslist = re.findall(r"[-|][0-1].\d+", result[0])
                divided = map(lambda x: x / 2, map(float, numberslist))
                print "line before " + line
                for i in range(len(numberslist)):
                    line = line.replace(str(numberslist[i]), str(divided[i]))

                print "line after " + line
                outFile.write(line)
                continue
        outFile.write(line)

if __name__ == "__main__":
    print "running main"
    main()

