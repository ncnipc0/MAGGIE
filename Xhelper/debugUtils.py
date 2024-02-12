from loguru import logger

similarity = []


def print_sense_tree(widget, depth=0):
    print(depth * "   ", widget)
    for child in widget.children:
        print_sense_tree(child, depth + 1)


def printPath(path):
    string = "\n--------path-------\n"
    for page, widget in path:
        string = string + "Page:" + str(page) + '\n'
        string = string + "Widget: " + str(widget) + '\n\n'
    if string[-2:] == "\n\n":
        string = string[:-1]
    string = string + "------------------------"
    print(string)


def printTree(node, depth=0):
    print(depth * '   ', node.attrib)
    for child in node:
        printTree(child, depth + 1)


def logOriginTree(origin_root, indent=0):
    logger.debug('\t' * (indent + 2) + "===========ET Tree===========")
    __log_origin_tree(origin_root, indent)
    logger.debug('\t' * (indent + 2) + "========= Tree END =========")


def __log_origin_tree(node, indent):
    logger.debug('\t' * (indent + 1) + "{}", node.attrib)
    for child in node:
        __log_origin_tree(child, indent + 1)


def printinfo(info):
    print("info:")
    print("clickable:", end="")
    for i in info["clickable"]:
        print(i[0].attrib["text"], i[0].attrib["bounds"], i[0].attrib["class"], end="  |")
    print("")


def stack_or_path_to_string(s_or_p: []):
    s = "["
    for item in s_or_p:
        s += "(" + str(item[0]) + "," + str(item[1]) + "," + item[2][0].attrib["text"] + ") "
    s += "]"
    return s


def print_unvisited(unvisited):
    for widget in unvisited:
        print(widget, end=" | ")
    print("")
