#!/usr/bin/python

import re
import getopt, sys

##=======================================================================================================
##  Define variables
##=======================================================================================================

# lib dependent parameter
lef_name = "CDK_R256X16"  # change here
output_file_name = "RAMB4_S16"  # "RAMB4_S16"
address_pins = 8
data_in_pins = 16
data_out_pins = 16


# configurable parameters for widths and heights
x_init = 12.00
y_init = 12.00
x_max = 12.00
y_max = 12.00

x1_x2_delta = 0.66
y1_y2_delta = 0.66
pin_to_pin_x_delta = 7
pin_to_pin_y_delta = 7
lineWidth = 5
offsetVss = 5
offsetVdd = 13


# extension = .lef
CONST_IN = 100
CONST_OUT = 101
CONST_INOUT = 102


rectangle_format = "\tRECT {current_x1} {current_y1} {current_x2} {current_y2} ;"

pins_list = [
    "ADDRESS",
    "DATA_IN",
    "DATA_OUT",
    "CLOCK",
    "WR_ENABLE",
    "ENABLE",
    "VDD",
    # "VSS",
]

pins = {
    "ADDRESS": [CONST_IN, address_pins],
    "DATA_IN": [CONST_IN, data_in_pins],
    "DATA_OUT": [CONST_OUT, data_out_pins],
    "CLOCK": [CONST_IN, 1],
    "WR_ENABLE": [CONST_IN, 1],
    "ENABLE": [CONST_IN, 1],
    "VDD": [CONST_INOUT, 1],
    # "VSS": [CONST_INOUT, 1],
}


rectLocation = dict()
rectLocation['current_x1'] = x_max
rectLocation['current_x2'] = x_max + x1_x2_delta
rectLocation['current_y1'] = y_max
rectLocation['current_y2'] = y_max + y1_y2_delta


##=======================================================================================================
##  Define variables
##=======================================================================================================






def main(**kwargs):
    ""
    global outfile,tempFile
    global out_dict, in_dict, clk_dict, false_path_list, false_path_dict, files_dict
    import glob, os
    path = os.getcwd()

    # get files list
    import os
    files_dict = dict()
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".txt"):
                file_name = file.replace(".txt", "")
                files_dict[file_name] = open(file, 'r')
    if not os.path.exists("./lef"):
        os.makedirs("./lef/")
    dir_output_file = "./lef/" + output_file_name

    outfile = open(dir_output_file + ".lef", "w")
    tempFile = open(dir_output_file+ "temp.lef", "w")

    #wringing the rest of the file
    goOverPins()
    tempFile.close()
    copyFile()
    print "max_x = {} max_y = {}".format(x_max, y_max)
    outfile.close()



def copyFile():

    import os
    tempFileName = outfile.name.replace(".lef", "temp.lef")
    tempFile = open(tempFileName, "r")
    start_block(files_dict['start_block'])
    # restart The tempFile
    for line in tempFile:
        outfile.write(line)
    tempFile.close()
    os.remove(tempFileName)




def start_block(myfile):
    orig_line_name = "CDK_R512x16"
    rigths = """##
##  Automaticly created by Ofir Even-chen and Yogev Laks Script
##"""
    #outfile.write(rigths)
    for line in myfile:
        if orig_line_name in line:
            outfile.write(line.replace(orig_line_name, lef_name))
        elif "SIZE" in line:
            myMatch = re.sub(r'\d+[.,]?\d+ (\w+) \d+[.,]?\d+', r'{} \1 {}'.format(x_max,y_max), line)
            if myMatch:
                outfile.write(myMatch)
            else:
                raise Exception("parseError")
        else:
            outfile.write(line)


def goOverPins():
    global x_max, y_max
    for blockName in pins_list:
        blockDirection = pins[blockName][0] #in out or inout
        blockNuberOfPins = pins[blockName][1]
        for pin in range(blockNuberOfPins):# - 1, -1, -1):  # count down to zero
            CreateRECT(blockName, pin)
            current_string = blockString(blockName, blockDirection, pin, blockNuberOfPins)
            tempFile.write(current_string)
            #get max values
            if blockName is not ("VSS" or "VDD"):
                if x_max < rectLocation['current_x2']:
                    x_max = rectLocation['current_x2']
                if y_max < rectLocation['current_y2']:
                    y_max = rectLocation['current_y2']




# works well for ADDRESS and DATA pins

def CreateRECT(BlockName, pinNumber):
    if BlockName == "ADDRESS":
        rectLocation['current_x1'] = x_init
        rectLocation['current_y1'] = y_max + (pin_to_pin_y_delta if pinNumber is not 0 else 0)
        rectLocation['current_x2'] = x_init + x1_x2_delta
        rectLocation['current_y2'] = y_max + y1_y2_delta + (pin_to_pin_y_delta if pinNumber is not 0 else 0)
    # elif "DATA" in BlockName:
    #     rectLocation['current_x1'] = x_max + pin_to_pin_x_delta * pinNumber
    #     rectLocation['current_y1'] = y_init
    #     rectLocation['current_x2'] = x_max + x1_x2_delta + pin_to_pin_x_delta
    #     rectLocation['current_y2'] = y_init + y1_y2_delta
    else:
        rectLocation['current_x1'] = x_max + pin_to_pin_x_delta
        rectLocation['current_y1'] = y_init
        rectLocation['current_x2'] = x_max + x1_x2_delta + pin_to_pin_x_delta
        rectLocation['current_y2'] = y_init + y1_y2_delta


def blockString(block_type, direction, pin_number, blockPinNumber):
    if direction is CONST_IN:
        direction_str = "INPUT"
    elif direction is CONST_OUT:
        direction_str = "OUTPUT"
    elif direction is CONST_INOUT:
        direction_str = "INOUT"
    else:
        raise ValueError

    parameters = dict()
    parameters['block_type'] = block_type
    parameters['direction'] = direction_str
    parameters['rect_string'] = rectangle_format.format(**rectLocation)
    parameters['pin_number'] = pin_number
    if block_type == "VSS" or block_type == "VDD":
        return VddVssString()


    # opening the block accoding to number of ports
    if blockPinNumber is 1:
        pin_string = """\
  PIN {block_type}""".format(**parameters)
    else:  # more than 1 pin
        pin_string = """\
  PIN {block_type}[{pin_number}]""".format(**parameters)

    # this part is the same for all ports
    pin_string += """
    DIRECTION {direction} ;
    USE SIGNAL ;
  PORT
      LAYER M5 ;
{rect_string}
      LAYER M6 ;
{rect_string}
      LAYER M3 ;
{rect_string}
      LAYER M4 ;
{rect_string}
    END""".format(**parameters)

    # same as before closing the port
    if blockPinNumber is 1:
        pin_string += """
  END {block_type}\n""".format(**parameters)
    else:
        pin_string += """
  END {block_type}[{pin_number}]\n""".format(**parameters)

    return pin_string

def VddVssString():

    return VddString() + VssString() + OBSString()

def VddString():
    # defining the parameters
    vddRectLocation = dict()
    # defining rectangle upeer left upper right
    #M1
    #top line
    vddRectLocation['m1_top_xll'] = 0
    vddRectLocation['m1_top_yll'] = y_max + offsetVdd
    vddRectLocation['m1_top_xur'] = x_max + offsetVdd
    vddRectLocation['m1_top_yur'] = y_max + lineWidth + offsetVdd
    #bottom line
    vddRectLocation['m1_bottom_xll'] = 0
    vddRectLocation['m1_bottom_yll'] = 0
    vddRectLocation['m1_bottom_xur'] = x_max + offsetVdd
    vddRectLocation['m1_bottom_yur'] = lineWidth
    #M2
    #right line
    vddRectLocation['m2_right_xll'] = x_max + offsetVdd - lineWidth
    vddRectLocation['m2_right_yll'] = y_max + lineWidth + offsetVdd
    vddRectLocation['m2_right_xur'] = x_max + offsetVdd
    vddRectLocation['m2_right_yur'] = lineWidth
    #left
    vddRectLocation['m2_left_xll'] = 0
    vddRectLocation['m2_left_yll'] = 0
    vddRectLocation['m2_left_xur'] = lineWidth
    vddRectLocation['m2_left_yur'] = y_max + lineWidth + offsetVdd

    vddString = """  PIN VDD
    DIRECTION INOUT ;
    USE POWER ;
    SHAPE RING ;
    PORT
      LAYER M1 ;
        RECT {m1_top_xll} {m1_top_yll} {m1_top_xur} {m1_top_yur} ;
        RECT {m1_bottom_xll} {m1_bottom_yll} {m1_bottom_xur} {m1_bottom_yur} ;
      LAYER M2 ;
        RECT {m2_right_xll} {m2_right_yll} {m2_right_xur} {m2_right_yur} ;
        RECT {m2_left_xll} {m2_left_yll} {m2_left_xur} {m2_left_yur} ;
    END
  END VDD""".format(**vddRectLocation)
    return vddString



def VssString():
    vssRectLocation = dict()

    # M1
    # top line
    vssRectLocation['m1_top_xll'] = 5.6
    vssRectLocation['m1_top_yll'] = y_max + offsetVss
    vssRectLocation['m1_top_xur'] = x_max + offsetVss
    vssRectLocation['m1_top_yur'] = y_max + lineWidth + offsetVss
    # bottom line
    vssRectLocation['m1_bottom_xll'] = 5.6
    vssRectLocation['m1_bottom_yll'] = 5.6
    vssRectLocation['m1_bottom_xur'] = x_max + offsetVss
    vssRectLocation['m1_bottom_yur'] = lineWidth
    # M2
    # right line
    vssRectLocation['m2_right_xll'] = x_max + offsetVss - lineWidth
    vssRectLocation['m2_right_yll'] = y_max + lineWidth + offsetVss
    vssRectLocation['m2_right_xur'] = x_max + offsetVss
    vssRectLocation['m2_right_yur'] = lineWidth
    # left
    vssRectLocation['m2_left_xll'] = 5.6
    vssRectLocation['m2_left_yll'] = 5.6
    vssRectLocation['m2_left_xur'] = lineWidth
    vssRectLocation['m2_left_yur'] = y_max + lineWidth + offsetVss
    # defining the parameters

    vssString = """    
  PIN VSS
    DIRECTION INOUT ;
    USE GROUND ;
    SHAPE RING ;
    PORT
      LAYER M1 ;
        RECT {m1_top_xll} {m1_top_yll} {m1_top_xur} {m1_top_yur} ;
        RECT {m1_bottom_xll} {m1_bottom_yll} {m1_bottom_xur} {m1_bottom_yur} ;
      LAYER M2 ;
        RECT {m2_right_xll} {m2_right_yll} {m2_right_xur} {m2_right_yur} ;
        RECT {m2_left_xll} {m2_left_yll} {m2_left_xur} {m2_left_yur} ;
    END
  END VSS""".format(**vssRectLocation)

    return vssString

def OBSString():
    obsRectLocation = dict()

    obsRectLocation['xLowerLeft'] = x_init
    obsRectLocation['yLowerLeft'] = y_init
    obsRectLocation['xUpperRight'] = x_max
    obsRectLocation['yUpperRight'] = y_max
    obsRectLocation['lef_name'] = lef_name
    obsString="""
  OBS
    LAYER M1 ;
      RECT {xLowerLeft} {yLowerLeft} {xUpperRight} {yUpperRight} ;
    LAYER M2 ;
      RECT {xLowerLeft} {yLowerLeft} {xUpperRight} {yUpperRight} ;
    LAYER M3 ;
      RECT {xLowerLeft} {yLowerLeft} {xUpperRight} {yUpperRight} ;
    LAYER M4 ;
      RECT {xLowerLeft} {yLowerLeft} {xUpperRight} {yUpperRight} ;
    LAYER M5 ;
      RECT {xLowerLeft} {yLowerLeft} {xUpperRight} {yUpperRight} ;
    LAYER M6 ;
      RECT {xLowerLeft} {yLowerLeft} {xUpperRight} {yUpperRight} ;
  END
END {lef_name}

END LIBRARY
    """.format(**obsRectLocation)
    return obsString

def end(input_file):
    for line in input_file:
        outfile.write(line)


if __name__ == "__main__":
    print "running main"
    main()
