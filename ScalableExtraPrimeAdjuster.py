# Copyright (c) 2018 Pheneeny
# The ScalableExtraPrime plugin is released under the terms of the AGPLv3 or higher.

from math import sqrt
from collections import namedtuple

Point = namedtuple('Point', 'x y')
GCodeArg = namedtuple('GCodeArg', 'name value')


def parse_and_adjust_gcode(gcode_layers:[[str]], min_travel:float, max_travel:float, min_prime:float, max_prime:float, extra_prime_without_retraction:bool=True)->([str], float):

    last_point = None

    last_e = 0
    adjusted_e = 0

    current_travel = 0
    current_retraction = 0

    if min_travel > max_travel:
        min_travel, max_travel = max_travel, min_travel

    if min_prime > max_prime:
        min_prime, max_prime = max_prime, min_prime

    for layer, gcode_layer in enumerate(gcode_layers):
        # gcode_list[2] is the first layer, after the preamble and the start gcode
        if layer < 2:
            continue
        lines = gcode_layer.split("\n");
        for (line_nr, line) in enumerate(lines):

            # Check if line is empty or a comment
            if len(line.strip()) == 0 or line.strip()[0] == ';':
                continue

            split_g = split_gcode(line)
            command, command_value = split_g[0]

            # Handle movement command
            if command == 'G':
                #Handle resetting E position
                if command_value == '92':
                    e_val = get_e_from_split(split_g)
                    if e_val is not None:
                        last_e = e_val
                        adjusted_e = e_val
                        continue
                # Handle travel
                if command_value == '0':
                    current_point = get_point_from_split(split_g)
                    if current_point is None:
                        continue
                    if last_point is None:
                        last_point = current_point
                    current_travel += get_distance(last_point, current_point)
                    last_point = current_point

                # Handle extrude
                elif command_value == '1':
                    current_point = get_point_from_split(split_g)
                    if last_point is None:
                        last_point = current_point
                    current_e = get_e_from_split(split_g)
                    if current_point is not None:
                        last_point = current_point

                    #No extrusion on this G1?
                    if current_e is None:
                        continue


                    e_diff = current_e - last_e

                    adjustment_message = None
                    extra_move = None

                    #Check if this is the first extrude after a travel
                    if current_travel != 0 and (current_retraction != 0 or extra_prime_without_retraction):
                        #Calculate extra prime based on travel distance
                        extra_e = round(get_extra_e(min_travel, max_travel, min_prime, max_prime, current_travel), 5)
                        adjusted_e += extra_e;

                        if extra_e != 0:
                            adjustment_message = "Adjusted e by {}mm".format(extra_e);

                            #If this move wasn't a prime after a retraction, create a move that we will inject later
                            if current_retraction == 0 and get_point_from_split(split_g) is not None:
                                extra_move = "G1 E{} ;{}\n".format(round(adjusted_e, 5), adjustment_message)
                                adjustment_message = None

                    #Adjust for current move extrusion
                    adjusted_e += e_diff

                    #Set adjusted value for the current move
                    set_e_in_split(split_g, adjusted_e)

                    #Generate new gcode
                    new_gcode = combine_gcode(split_g, adjustment_message);

                    #If we created an extra move before, prepend it to the generated gcode
                    if extra_move:
                        new_gcode = extra_move + new_gcode

                    lines[line_nr] = new_gcode

                    current_travel = 0
                    if e_diff < 0:
                        current_retraction = e_diff
                    else:
                        current_retraction = 0

                    last_e = current_e
        gcode_layers[layer] = "\n".join(lines)
    return gcode_layers


def get_extra_e(min_travel:float, max_travel:float, min_prime:float, max_prime:float, actual_travel:float)->float:

    #If we didn't travel at least the min distance, return 0 extra e
    if actual_travel == 0 or actual_travel < min_travel:
        return 0

    #If actual travel is min_travel, return min_prime.
    if actual_travel == min_travel:
        return min_prime

    #If we traveled further than our max, return max_prime. This also avoid divide by 0 if min_travel == max_travel
    if actual_travel > max_travel:
        return max_prime

    possible_travel_range = max_travel - min_travel
    actual_travel = actual_travel - min_travel;

    travel_percent = actual_travel / possible_travel_range;

    possible_prime_range = max_prime - min_prime

    extra_e = (travel_percent * possible_prime_range) + min_prime
    return extra_e


def split_gcode(g_command:str)->[GCodeArg]:
    if ';' in g_command:
        comment_index = g_command.find(';')
        if comment_index > 0 and g_command[comment_index-1] != " ":
            g_command = g_command.replace(";", " ;")
    args = g_command.strip().split(" ");
    parsed = [];
    for arg in args:
        if len(arg) > 1:
            parsed.append(GCodeArg(arg[0], arg[1:]))
    return parsed


def combine_gcode(args:[GCodeArg], comment:str=None)-> [str]:
    gcode_line = ""
    for arg in args:
        gcode_line += arg.name + str(arg.value) + " "
    gcode_line = gcode_line.strip()
    if comment:
        gcode_line += " ;" + comment
    return gcode_line;


def get_point_from_split(args:[GCodeArg])->Point:
    x = None;
    y = None;
    for arg in args:
        attr, value = arg
        if attr == 'X':
            x = float(value)
        elif attr == 'Y':
            y = float(value)
        elif attr == ';':
            break;

    if x is None or y is None:
        return None;

    return Point(x, y)


def get_e_from_split(args:[GCodeArg])->float:
    for arg in args:
        attr, value = arg
        if attr == 'E':
            return float(value)

    return None


def set_e_in_split(args:[GCodeArg], e_value:float)->[GCodeArg]:
    e_value = round(e_value, 5)
    adjusted_arg = GCodeArg("E", str(e_value))
    for arg_n, arg in enumerate(args):
        if arg.name == "E":
            args[arg_n] = adjusted_arg

    return args


def get_distance(point1:Point, point2:Point):
    return sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2);

