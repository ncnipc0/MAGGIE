import uiautomator2 as u2
import config
from loguru import logger
from enum import Enum
import xml.etree.ElementTree as ET

from CompareAlgorithm import sim_tree


class WidgetType(Enum):
    Ability = "Ability"
    Image = "Image"
    Text = "Text"
    Normal = "Normal"
    WebView = "WebView"


def get_node_type(old_node: ET.Element):
    """
    Set node type: Ability、Pict、Text、Normal
    """
    if "WebView" in old_node.attrib["class"] and len(old_node) == 0:
        return WidgetType.WebView
    # Ability node: has checkable and clickable capabilities
    elif old_node.attrib["checkable"] == "true" or old_node.attrib["clickable"] == "true":
        return WidgetType.Ability
    # Image node: class is image
    elif old_node.attrib["class"] == "android.widget.ImageView":
        return WidgetType.Image
    # Text node: Non webview node with non empty text
    elif old_node.attrib["text"] != "" and old_node.attrib["class"] != "android.webkit.WebView":
        return WidgetType.Text
    else:
        return WidgetType.Normal


class STElement:
    def __init__(self, old_node):
        if isinstance(old_node, ET.Element):
            # Corresponding ETElement
            self.node = old_node
            # Parent
            self.parent = None
            # child node
            self.children = []
            self.index = 1
            # type
            self.widget_type = get_node_type(old_node)
            # The text corresponding to the ETree subtree, including the text of this node
            self.texts = []
            if old_node.attrib["text"] != "":
                self.texts.append(old_node.attrib["text"])
            if old_node.attrib["content-desc"] != "":
                self.texts.append(old_node.attrib["content-desc"])
            # The resourceId of the corresponding Etree subtree, including the resourceId of this node
            self.resource_id = []
            if old_node.attrib["resource-id"] != "":
                self.resource_id.append(old_node.attrib["resource-id"])
            # PictureNode corresponding to Etree subtree
            self.subPicture = []
            # The number of nodes in a subtree
            self.subTreeCount = 1
            self.occupy_area = []
        if isinstance(old_node, STElement):
            self.node = old_node.node
            self.parent = None
            self.children = []
            self.index = 1
            self.widget_type = old_node.widget_type
            self.texts = old_node.texts
            self.resource_id = old_node.resource_id
            self.subPicture = old_node.subPicture
            self.subTreeCount = 1
            self.occupy_area = old_node.occupy_area

    @property
    def all_text(self):
        return "".join(self.texts)

    @property
    def all_resourceID(self):
        return "".join(self.resource_id)

    def __str__(self):
        return '(widget_type:' + str(self.widget_type)[11:] + ', text:' + str(self.texts) + ', occupy:' + \
               self.node.attrib["bounds"] + ', resourceID:' + str(self.resource_id) + ')'

    def log(self, indent=0, stack_mode=False):
        if not stack_mode:
            logger.debug('\t' * (indent + 2) + "===========Page Tree===========")
        self.__log_sense_tree(self, indent, stack_mode)
        if not stack_mode:
            logger.debug('\t' * (indent + 2) + "======== Tree END ========")

    @staticmethod
    def __log_sense_tree(tree, indent, stack_mode):
        if stack_mode:
            logger.log("STACK", '\t' * (indent + 1) + "{}", str(tree))
        else:
            logger.debug('\t' * (indent + 1) + "{}", str(tree))
        for child in tree.children:
            tree.__log_sense_tree(child, indent + 1, stack_mode)


class SenseTree:
    def __init__(self, old_root: ET.Element):
        self.clickable = []
        self.texts = []
        self.webview_flag = False
        self.root = self.__build_sense_tree(old_root)

        if self.root is None:
            logger.warning("root node is none")
            self.type_dict = {}
            self.clickable = []
            self.root = STElement(old_root)
        else:
            self.type_dict = self.__get_type_dict()

    def __build_ability_tree(self, ability_node: STElement, cur_node: STElement, old_node: ET.Element):
        # dfs
        for child in old_node:
            if get_node_type(child) == WidgetType.WebView:
                self.webview_flag = True
            elif get_node_type(child) == WidgetType.Text:
                ability_node.texts.append(child.attrib["text"])
                tmp_resource_id = child.attrib["resource-id"]
                if tmp_resource_id != "":
                    cur_node.resource_id.append(tmp_resource_id)
            elif get_node_type(child) == WidgetType.Image:
                ability_node.subPicture.append(child)
                tmp_resource_id = child.attrib["resource-id"]
                if tmp_resource_id != "":
                    cur_node.resource_id.append(tmp_resource_id)
            elif get_node_type(child) == WidgetType.Ability:
                new_ability_node = STElement(child)
                cur_node.children.append(new_ability_node)
                self.clickable.append(new_ability_node)
                ability_node.occupy_area.append(child.attrib["bounds"])
                self.__build_ability_tree(new_ability_node, new_ability_node, child)
                self.texts.extend(new_ability_node.texts)
                cur_node.resource_id.extend(new_ability_node.resource_id)
                ability_node.occupy_area.extend(new_ability_node.occupy_area)
            else:
                new_node = STElement(child)
                cur_node.children.append(new_node)
                self.__build_ability_tree(ability_node, new_node, child)
                cur_node.resource_id.extend(new_node.resource_id)
                if len(new_node.children) == 0:
                    del cur_node.children[-1]
                if len(new_node.children) == 1:
                    cur_node.children[-1] = new_node.children[0]

        for i in range(0, len(cur_node.children)):
            cur_node.children[i].parent = cur_node
            cur_node.children[i].index = i + 1
            cur_node.subTreeCount += cur_node.children[i].subTreeCount

    def __build_sense_tree(self, old_node: ET.Element):
        """
        build sense tree
        """
        new_node = STElement(old_node)
        # dfs
        child_list = []
        for child in old_node:
            # WebView
            if get_node_type(child) == WidgetType.WebView:
                self.webview_flag = True
            # Text
            if get_node_type(child) == WidgetType.Text:
                # new_node.children.append(Widget(children))
                self.texts.append(child.attrib["text"])
                child_list.append(STElement(child))
            # Image
            elif get_node_type(child) == WidgetType.Image:
                child_list.append(STElement(child))
                if child.attrib["text"] != '':
                    self.texts.append(child_list[-1].texts)
            # Ability
            elif get_node_type(child) == WidgetType.Ability:
                ability_node = STElement(child)
                self.clickable.append(ability_node)
                self.__build_ability_tree(ability_node, ability_node, child)
                self.texts.extend(ability_node.texts)
                child_list.append(ability_node)
            else:
                sub_sense_tree = self.__build_sense_tree(child)
                if sub_sense_tree is not None:
                    child_list.append(sub_sense_tree)
                    assert new_node.widget_type == WidgetType.Normal, "father is not L node"
                    if len(child_list[-1].children) == 1:
                        new_node.resource_id.extend(child_list[-1].resource_id)
                        child_list[-1] = child_list[-1].children[0]
                        continue
                else:
                    continue

            new_node.resource_id.extend(child_list[-1].resource_id)

        if len(child_list) == 0 and new_node.widget_type == WidgetType.Normal:

            return None
        elif len(child_list) == 1 and child_list[
            0].widget_type == WidgetType.Normal and new_node.widget_type == WidgetType.Normal:

            child_list = child_list[0].children
        elif len(child_list) == 2 and new_node.widget_type == WidgetType.Normal:

            if (child_list[0].widget_type == WidgetType.Text
                    and child_list[1].node.attrib["class"] == "android.widget.EditText"
                    and child_list[1].node.attrib["text"] == ""
                    and len(child_list[1].texts) == 0):
                child_list[1].texts.append(child_list[0].node.attrib["text"])
                tmp_resource_id = child_list[0].node.attrib["resource-id"]
                if tmp_resource_id != "":
                    child_list[1].resource_id.append(tmp_resource_id)
                del child_list[0]
            elif (child_list[1].widget_type == WidgetType.Text
                  and child_list[0].node.attrib["class"] == "android.widget.EditText"
                  and child_list[0].node.attrib["text"] == ""
                  and len(child_list[0].texts) == 0):
                child_list[0].texts.append(child_list[1].node.attrib["text"])
                tmp_resource_id = child_list[1].node.attrib["resource-id"]
                if tmp_resource_id != "":
                    child_list[0].resource_id.append(tmp_resource_id)
                del child_list[1]

        new_node.children = child_list

        for i in range(0, len(child_list)):
            child_list[i].parent = new_node
            child_list[i].index = i + 1
            new_node.subTreeCount += child_list[i].subTreeCount


        return new_node

    def __is_same_ETtree(self, root1: ET.Element, root2: ET.Element):
        if sim_tree(root1, root2, 0) >= 0.9:
            return True
        else:
            return False

    def __get_type_dict(self):
        ability_stack = []

        stack = [[self.root]]
        assert self.root is not None, 'SenseTree root is None'
        assert isinstance(self.root, STElement), 'err node type'

        while len(stack) != 0:
            # 出栈
            tmp_list = stack.pop()

            assert len(tmp_list) > 0, 'stack is empty'
            if tmp_list[0].widget_type == WidgetType.Ability:
                ability_stack.append(tmp_list)
                continue

            new_list = []
            for node in tmp_list:
                for child in node.children:
                    flag = True
                    for child_list in new_list:
                        if child.widget_type == child_list[0].widget_type and child.subTreeCount == child_list[
                            0].subTreeCount:

                            child_list.append(child)
                            flag = False
                            break
                    if flag:
                        new_list.append([child])
            stack.extend(new_list)

        type_count = 0
        type_dict = {}
        for child_list in ability_stack:
            new_list = []
            for child in child_list:
                flag = True
                for new_child_list in new_list:
                    if self.__is_same_ETtree(child.node, new_child_list[0].node):
                        # if True:
                        new_child_list.append(child)
                        type_dict[child] = type_dict[new_child_list[0]]
                        flag = False
                        break
                if flag:
                    new_list.append([child])
                    type_count += 1
                    type_dict[child] = type_count

        if len(self.clickable) != len(type_dict):
            for child in self.clickable:
                if child not in type_dict.keys():
                    type_count += 1
                    type_dict[child] = type_count

        return type_dict


def print_sense_tree_type(new_node: STElement, level):
    print('\t' * level, new_node.widget_type)
    for child in new_node.children:
        print_sense_tree_type(child, level + 1)


def print_sense_tree1(new_node: STElement, level):
    print('\t' * level, new_node.widget_type, new_node.subTreeCount, new_node.texts, sep=" ")
    for child in new_node.children:
        print_sense_tree1(child, level + 1)


def print_sense_tree2(new_node: STElement, level):
    print('\t' * level, new_node.widget_type, new_node.index, new_node.resource_id, sep=" ")
    for child in new_node.children:
        print_sense_tree2(child, level + 1)


def print_sense_tree3(new_node: STElement, level):
    print('\t' * level, new_node.widget_type, new_node, new_node.parent, sep=" ")
    for child in new_node.children:
        print_sense_tree3(child, level + 1)


def print_sense_tree4(new_node: STElement, level):
    print('\t' * level, new_node.widget_type, new_node.node.attrib["bounds"], new_node.occupy_area,
          new_node.subPicture, sep=" ")
    for child in new_node.children:
        print_sense_tree4(child, level + 1)


def print_sense_tree5(new_node, type_dict, level):
    print('\t' * level, new_node.widget_type, new_node.texts, type_dict.get(new_node, None), sep=" ")
    for child in new_node.children:
        print_sense_tree5(child, type_dict, level + 1)



