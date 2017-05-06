#!/usr/bin/python

import re
import getopt, sys

##=======================================================================================================
##  Define variables
##=======================================================================================================
# extension = .lef
CONST_IN = 100
CONST_OUT = 101
CONST_INOUT = 102

lef_name = "CDK_R256X16"  # change here
output_file_name = lef_name  # "RAMB4_S16"
address_pins = 2
data_in_pins = 2
data_out_pins = 2


x_min = 12.00
y_min = 12.00
x_max = 0.00
y_max = 0.00
x1_x2_delta = 0.66
y1_y2_delta = 0.66
pin_to_pin_x_delta = 7
pin_to_pin_y_delta = 7
rectangle_format = "\tRECT {current_x1} {current_y1} {current_x2} {current_y2} ;"
# for data out pin 2 pin is 19
# pin order is decanting
rectLocation = dict()
rectLocation['current_x1'] = x_min
rectLocation['current_x2'] = x_min + x1_x2_delta
rectLocation['current_y1'] = y_min
rectLocation['current_y2'] = y_min + y1_y2_delta

pins_list = [
    "ADDRESS",
    "DATA_IN",
    "DATA_OUT",
    "CLOCK",
    "WR_ENABLE",
    "ENABLE",
    "VDD",
    "VSS"]

pins = {
    "ADDRESS": [CONST_IN,address_pins],
    "DATA_IN": [CONST_IN,data_in_pins],
    "DATA_OUT": [CONST_OUT,data_out_pins],
    "CLOCK": [CONST_IN,1],
    "WR_ENABLE": [CONST_IN,1],
    "ENABLE": [CONST_IN,1],
    "VDD": [CONST_INOUT,1],
    "VSS": [CONST_INOUT,1],
}


##=======================================================================================================
##  Define variables
##=======================================================================================================




def main(**kwargs):
    ""
    global outfile
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

    outfile = open(output_file_name + ".lef", "w")

    print files_dict.keys()
    # if start_f: start(files_dict['File_start_block'])
    start_block(files_dict['start_block'])
    goOverPins()


    #
    # address(files_dict['ADDRESS_block'], address_pins)
    # dataInBlock(files_dict['DATA_IN_block'], data_in_pins)
    # dataOutBlock(files_dict['DATA_OUT_block'], data_out_pins)
    print "max_x = {} max_y = {}".format(x_min, y_min)
    # end(files_dict['File_end_block'])
    # outfile.close()






def start_block(myfile):
    orig_line_name = "CDK_R512x16"
    rigths = """##
##  Automaticly created by Ofir Even-chen and Yogev Laks Script
##"""
    outfile.write(rigths)
    for line in myfile:
        if orig_line_name in line:
            outfile.write(line.replace(orig_line_name, lef_name))
        elif "SIZE" in line:
            myMatch = re.sub(r'\d+[.,]?\d+ (\w+) \d+[.,]?\d+', r'X_VALUE_SWITCH_LATER \1 Y_VALUE_SWITCH_LATER', line)
            if myMatch:
                outfile.write(myMatch)
            else:
                raise Exception("parseError")
        else:
            outfile.write(line)


def address(input_file, address_pins, string_to_change="<PIN_NUM>"):
    global x_min, y_min
    for pinNumber in range(address_pins - 1, -1, -1):  # count down to zero #(address_pins):  #
        input_file.seek(0)
        rectLocation['current_x1'] = x_min
        rectLocation['current_x2'] = x_min + x1_x2_delta
        rectLocation['current_y1'] = y_min + pin_to_pin_y_delta * pinNumber
        rectLocation['current_y2'] = y_min + y1_y2_delta + pin_to_pin_y_delta * pinNumber
        for line in input_file:
            if string_to_change in line:
                outfile.write(line.replace(string_to_change, str(pinNumber)))
            elif "RECT " in line:
                outfile.write(rectangle_format.format(**rectLocation))
            else:
                outfile.write(line)
    x_min = rectLocation['current_x2'] + pin_to_pin_x_delta
    y_min = rectLocation['current_y2'] + pin_to_pin_y_delta


def dataInBlock(input_file, data_in_pins, string_to_change="<PIN_NUM>"):
    global x_min, y_min
    for pinNumber in range(data_in_pins - 1, -1, -1):  # count down to zero #(address_pins):  #
        input_file.seek(0)
        rectLocation['current_x1'] = x_min + pin_to_pin_x_delta * pinNumber
        rectLocation['current_x2'] = x_min + y1_y2_delta + pin_to_pin_x_delta * pinNumber
        rectLocation['current_y1'] = y_min
        rectLocation['current_y2'] = y_min
        for line in input_file:
            if string_to_change in line:
                outfile.write(line.replace(string_to_change, str(pinNumber)))
            elif "RECT " in line:
                outfile.write(rectangle_format.format(**rectLocation))
            else:
                outfile.write(line)
    x_min = rectLocation['current_x2'] + pin_to_pin_x_delta
    y_min = rectLocation['current_y2'] + pin_to_pin_y_delta


def dataOutBlock(input_file, data_out_pins, string_to_change="<PIN_NUM>"):
    global x_min, y_min
    for pinNumber in range(data_out_pins - 1, -1, -1):  # count down to zero #(address_pins):  #
        input_file.seek(0)
        rectLocation['current_x1'] = x_min + pin_to_pin_x_delta * pinNumber
        rectLocation['current_x2'] = x_min + y1_y2_delta + pin_to_pin_x_delta * pinNumber
        rectLocation['current_y1'] = y_min
        rectLocation['current_y2'] = y_min
        for line in input_file:
            if string_to_change in line:
                outfile.write(line.replace(string_to_change, str(pinNumber)))
            elif "RECT " in line:
                outfile.write(rectangle_format.format(**rectLocation) +"\n")
            else:
                outfile.write(line)
    x_min = rectLocation['current_x2'] + pin_to_pin_x_delta
    y_min = rectLocation['current_y2'] + pin_to_pin_y_delta


def outblock(input_file, data_out_pins, input_pins_dict, str_a_change="<RELATED_PIN_NAME>",
             str_b_change="<RELATED_PIN_NUM>"):
    for out_pin_num in range(data_out_pins - 1, -1, -1):  # each out_pin
        out_pin_string = """      pin (DATA_OUT[{}] ) {{
        direction : output ;
        capacitance :  0.0000;
        max_capacitance :  0.5375;\n""".format(out_pin_num)
        outfile.write(out_pin_string)

        for input_pin_name in input_pins_dict.keys():  # each_input
            if input_pins_dict[input_pin_name] > 1:
                for input_pin_num in range(input_pins_dict[input_pin_name]):  # each pin in input
                    input_file.seek(0)
                    for line in input_file:
                        if str_a_change in line:
                            ###posibly dual write in related pin
                            outfile.write(
                                line.replace(str_a_change, str(input_pin_name) + "[").replace(str_b_change,
                                                                                              str(input_pin_num) + "]"))
                        else:
                            outfile.write(line)

            else:
                input_file.seek(0)
                for line in input_file:
                    if str_a_change in line:
                        outfile.write(
                            line.replace(str_a_change, str(input_pin_name)).replace(str_b_change, ""))
                    else:
                        outfile.write(line)



#works well for ADDRESS and DATA pins

def goOverPins():
    global x_min,y_min
    for blockName in pins_list:
        blockDirection = pins[blockName][0]
        blockPinNumber = pins[blockName][1]
        for pin in range(blockPinNumber - 1, -1, -1):  # count down to zero
            CreateRECT(blockName,pin)
            current_string = blockString(blockName,blockDirection,pin,blockPinNumber)
            outfile.write(current_string)
        x_min = rectLocation['current_x2'] + pin_to_pin_x_delta
        y_min = rectLocation['current_y2'] + pin_to_pin_y_delta

def CreateRECT(BlockName,pinNumber):
    if BlockName == "ADDRESS":
        rectLocation['current_x1'] = x_min
        rectLocation['current_x2'] = x_min + x1_x2_delta
        rectLocation['current_y1'] = y_min + pin_to_pin_y_delta * pinNumber
        rectLocation['current_y2'] = y_min + y1_y2_delta + pin_to_pin_y_delta * pinNumber
    elif "DATA" in BlockName:
        rectLocation['current_x1'] = x_min
        rectLocation['current_x2'] = x_min + x1_x2_delta
        rectLocation['current_y1'] = y_min + pin_to_pin_y_delta * pinNumber
        rectLocation['current_y2'] = y_min + y1_y2_delta + pin_to_pin_y_delta * pinNumber
    else:
        rectLocation['current_x1'] = x_min
        rectLocation['current_x2'] = x_min + x1_x2_delta
        rectLocation['current_y1'] = y_min + pin_to_pin_y_delta * pinNumber
        rectLocation['current_y2'] = y_min + y1_y2_delta + pin_to_pin_y_delta * pinNumber


def blockString(block_type, direction, pin_number,blockPinNumber):
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
    if blockPinNumber is 1:
        pin_string = """\
  PIN {block_type}""".format(**parameters)
    else:
        pin_string = """\
  PIN {block_type}[{pin_number}]""".format(**parameters)

    pin_string += """
    DIRECTION {direction} ;
    USE SIGNAL ;
  PORT"""+str(metalType(block_type,parameters))+"""
    END""".format(**parameters)
    if blockPinNumber is 1:
        pin_string += """
  END {block_type}\n""".format(**parameters)
    else:
        pin_string += """
  END {block_type}[{pin_number}]\n""".format(**parameters)

    return pin_string

def metalType(pinType,parameters):
    if pinType == "VSS" or pinType == "VDD":
        return metalLow(pinType,parameters)
    else:
        return metalHigh(parameters)


def metalHigh(parameters):
    return """
      LAYER Metal5 ;
{rect_string}
      LAYER Metal6 ;
{rect_string}
      LAYER Metal3 ;
{rect_string}
      LAYER Metal4 ;
{rect_string}""".format(**parameters)

def metalLow(pinType,parameters):
    return """
      LAYER Metal1 ;
        RECT 0 202.2 763.02 207.2 ;
        RECT 0 0 763.02 5 ;
      LAYER Metal2 ;
        RECT 758.02 0 763.02 207.2 ;
        RECT 0 0 5 207.2""".format()

def end(input_file):
    for line in input_file:
        outfile.write(line)


if __name__ == "__main__":
    print "running main"
    main()
