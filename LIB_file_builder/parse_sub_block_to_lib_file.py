#!/usr/bin/python
# import re
import getopt, sys

##=======================================================================================================
##  Define variables
##=======================================================================================================

output_file_name="RAMB4_S1"
lib_name = "CDK_R4096X1"
address_pins = 12
data_in_pins = 1
data_out_pins = 1


# output_related_pins = {"DATA_IN": data_in_pins, "ADDRESS": address_pins, "CLOCK":1}
output_related_pins = {"CLOCK":1}


##=======================================================================================================
##  Define variables
##=======================================================================================================




def main(**kwargs):
    ""
    global outfile
    global out_dict, in_dict, clk_dict, false_path_list, false_path_dict, files_dict
    import glob, os
    path = os.getcwd()

    # ## handle command line arguments:
    # try:
    #     opts, args = getopt.getopt(sys.argv[1:], "ho:v", ["help", "output="])
    # except getopt.GetoptError as err:
    #     # print help information and exit:
    #     print str(err)  # will print something like "option -a not recognized"
    #     sys.exit(2)
    # output = None
    # start_f = False
    # for o, a in opts:
    #
    #     if o in ("-h", "--help"):
    #         sys.exit()
    #     elif o in ("-s", "--start"):
    #         start_f = True
    #     elif o in ("-o", "--output"):
    #         output = a
    #     else:
    #         assert False, "unhandled option"
    # # ...
    # ## handle command line arguments:

    print path
    # if "\\tutorial_RTL\\LIB" not in path:
    #     path = path + "\\tutorial_RTL\\LIB"
    #     os.chdir(path)
    print path

    # if len(kwargs)<1:
    #     print "wrong input"
    files_dict = {}
    if not os.path.exists(path+"\out/"):
        os.mkdir(path+"/out/")


    outfile = open(path+"/out/"+output_file_name+".lib", "w")
    for myfile in glob.glob("*.lib"):
        files_dict[myfile.replace(".lib", "")] = open(myfile, "r")

    print files_dict.keys()
    # if start_f: start(files_dict['File_start_block'])
    start(files_dict['File_start_block'])
    open_cell()
    start_bus("ADDRESS", bus_number=0, bit_width=address_pins, bit_from=address_pins - 1)
    address(files_dict['ADDRESS_block'], address_pins)
    start_bus("DATA_IN", bus_number=1, bit_width=data_in_pins, bit_from=data_in_pins - 1)
    inblock(files_dict['DATA_IN_block'], data_in_pins)
    start_bus("DATA_OUT", bus_number=2, bit_width=data_out_pins, bit_from=data_out_pins - 1)
    outblock(files_dict['DATA_OUT_block'], data_out_pins, output_related_pins)
    end(files_dict['File_end_block'])
    outfile.close()


def start(myfile):
    orig_line_name = "CDK_S256x16"
    for line in myfile:
        if orig_line_name in line:
            outfile.write(line.replace(orig_line_name, lib_name))
        else:
            outfile.write(line)


def open_cell():
    output_string = """  cell ({}) {{
    area :  0.0000;
    dont_touch : true ;
    dont_use : true ;
    timing_model_type : extracted ;
    interface_timing : true ;\n""".format(lib_name)
    outfile.write(output_string)


def start_bus(bus_name, bus_number, bit_width, bit_from, bit_to=0):
    output_sting = """    type (bus{}){{
      base_type : array ;
      data_type : bit ;
      bit_width :  {};
      bit_from :  {};
      bit_to :  {};
      downto : true ;
    }}
    bus ({} ){{
      bus_type :  bus{} ;\n""".format(bus_number, bit_width, bit_from, bit_to, bus_name,bus_number)
    outfile.write(output_sting)

def close_block():
    outfile.write("      \n    }\n")  #close block

def address(input_file, address_pins, string_to_change="<ADDRESS_NUM>"):
    for num in range(address_pins - 1, -1, -1):  # count down to zero #(address_pins):  #
        input_file.seek(0)
        for line in input_file:
            if string_to_change in line:
                outfile.write(line.replace(string_to_change, str(num)))
            else:
                outfile.write(line)
    close_block()


def inblock(input_file, data_in_pins, string_to_change="<DATA_IN_NUM>"):
    for num in range(data_in_pins - 1, -1,-1):
                # (data_in_pins-1,-1,-1): #count down to zero      #counting up -> range(data_in_pins):
        input_file.seek(0)
        for line in input_file:
            if string_to_change in line:
                outfile.write(line.replace(string_to_change, str(num)))
            else:
                outfile.write(line)
    close_block()


def outblock(input_file, data_out_pins, input_pins_dict, str_a_change="<RELATED_PIN_NAME>",
             str_b_change="<RELATED_PIN_NUM>"):
    for out_pin_num in range(data_out_pins - 1, -1,-1): # each out_pin
        out_pin_string = """      pin (DATA_OUT[{}] ) {{
        direction : output ;
        capacitance :  0.0000;
        max_capacitance :  0.5375;\n""".format(out_pin_num)
        outfile.write(out_pin_string)

        for input_pin_name in input_pins_dict.keys():  # each_input
            # if "DATA_" in input_pin_name:
            #     continue
            if input_pins_dict[input_pin_name]>1:
                for input_pin_num in range(input_pins_dict[input_pin_name]):  # each pin in input
                    input_file.seek(0)
                    for line in input_file:
                        if str_a_change in line:
                            ###posibly dual write in related pin
                            outfile.write(
                                line.replace(str_a_change, str(input_pin_name)+"[").replace(str_b_change, str(input_pin_num)+"]"))
                        else:
                            outfile.write(line)

            else:
                input_file.seek(0)
                for line in input_file:
                    if str_a_change in line:
                        outfile.write(
                            line.replace(str_a_change, str(input_pin_name)).replace(str_b_change,""))
                    else:
                        outfile.write(line)
        close_block()
    close_block()


def end(input_file):
    for line in input_file:
        outfile.write(line)


if __name__ == "__main__":
    print "running main"
    main()



# "JTAG , TCB??"
#
#
# def find_clk(io_dict, clk_dict):
#     ""
#     for key in io_dict.keys():
#         if "clk" in key.lower():
#             clk_dict[key] = io_dict[key]
#             print key
#     return clk_dict
#
#
# def write_to_const_data(my_dict, string, output_file, clk_dict):
#     clk_key ="SI_ClkIn"
#
#     for key in my_dict.keys():
#
#         for ignore in false_path_list:
#             if ignore not in key:
#
#                 if my_dict[key] == 1:
#                     output_file.write(
#                         "set_%s_delay -clock [get_clocks %s] -add_delay 0.1 [get_ports %s]\n" % (string, clk_key, key))
#                 else:
#                     for bit in range(my_dict[key]):
#                         output_file.write(
#                             "set_%s_delay -clock [get_clocks %s] -add_delay 0.1 [get_ports {%s[%s]}]\n" % (
#                             string, clk_key, key, bit))
#
#
# def find_match(line, my_dict, string):
#     match = re.search(string + "\s+(\w+);", line)
#     if match:
#         print "single bit " + string + match.group(1)
#         my_dict.update({match.group(1): 1})
#     else:
#         match = re.search(string + "\s+\[(\d+):(\d+)\]\s+(\w+);", line)
#         if match:
#             print "multibit " + match.group(0)
#
#             bits = int(match.group(1)) - int(match.group(2)) + 1
#             my_dict[match.group(3)] = bits
#     return my_dict
#
# def write__const_file_begging(outfile):
#     ""
#     output_string =    """set sdc_version 1.4
# # Set the current design
# current_design m14k_top
# \ncreate_clock -name "SI_ClkIn" -add -period 16.0 -waveform {0.0 8.0} [get_ports SI_ClkIn]"""
#
#
# def write__const_file_ending(outfile):
#     ""
#     output_string =    """\nset_max_fanout 15.000 [current_design]
# set_max_transition 1.2 [current_design]\n"""
#     outfile.write(output_string)
