import re
import time
from copy import copy

import CompareAlgorithm

import config
from config import CONFIG
import Utils
import xml.etree.ElementTree as ET
from SenseTree import SenseTree
from SenseTree import STElement
from SenseTree import WidgetType
from loguru import logger
from Utils import take_screenshot_for_all_screen_and_save


class Page:
    def __init__(self, origin_root, actName):
        self.origin_root: ET.Element = origin_root
        self.actName = actName
        self.isInterested = False
        # 拿到感官树,并记录clickable
        sense_tree = SenseTree(origin_root)
        self.sense_root: STElement = sense_tree.root
        self.clickable: [STElement] = sense_tree.clickable
        self.texts = sense_tree.texts
        self.type_dict = sense_tree.type_dict
        self.r_type_dict = Utils.reverse_dict(self.type_dict)

    @property
    def all_text(self):
        return "".join(self.texts)

    def __str__(self):
        string = "{"
        for widget in self.clickable:
            string += str(widget)
        string += '}'
        return string

    def __hash__(self):
        return hash(id(self))


class PageStorage(list):

    def __init__(self):
        self.last_update = None

    def append(self, __object) -> None:
        self.last_update = time.perf_counter()
        super().append(__object)
        take_screenshot_for_all_screen_and_save("./img/phone" + str(CONFIG["phone_no"]) + "/")

    def has_same_kind_page(self, item: Page):
        page_count = 0
        for record in self:
            page_count += 1
            if CompareAlgorithm.is_same_kind_page(record, item):
                return True
        return False

    def same_kind_page_num(self, page: Page):
        res = 0
        page_count = 0
        for record in self:
            page_count += 1
            if CompareAlgorithm.is_same_kind_page(record, page):
                res += 1
        return res

    def __contains__(self, item: Page):
        page_count = 0
        for record in self:
            page_count += 1
            if CompareAlgorithm.is_same_page(record, item, 0.7):
                return True
        return False

    def __str__(self):
        string = "PageStorage:"
        for page in self:
            string += str(page) + "\n"
        return string

    def log(self):
        logger.log("DEBUG", "\t\t========Storage========")
        logger.log("DEBUG", self.__str__())
        logger.log("DEBUG", "\t\t========Storage========")


class VisitRecord:
    def __init__(self, page: Page, tab_view_widgets, blacklist):
        self.unvisited = copy(page.clickable)
        self.tab_view_widgets = tab_view_widgets
        self.black_texts = set(config.APP["black_texts"] + blacklist)
        self.black_ids = set(config.APP['black_ids'])

        # Remove components marked on the blacklist from the unverified list
        self.__delete_blacklist(page)
        # Delete EditText and checkbox from unvisited
        self.__delete_input()
        self.__delete_back(page)
        self.__delete_tabview(page)
        self.__delete_img_in_not_idconent_page(page)
        self.visited = {}
        self.type_dict = page.type_dict
        type_id = -1
        for i in self.unvisited:
            if i not in self.type_dict:
                self.type_dict[i] = type_id
                type_id -= 1

    def __delete_blacklist(self, page: Page):
        tmp_set = set()
        for widget in page.clickable:
            for btext in self.black_texts:
                if btext in widget.all_text:
                    logger.info("delete  <{}>", widget.texts)
                    tmp_set.add(widget)

            for bid in self.black_ids:
                for id in widget.resource_id:
                    res = re.search(':id/([\w_]+)', id)
                    if res is None:
                        logger.error("can not find res-id:{}", id)
                        continue
                    id = res.group(1)
                    if bid == id:
                        logger.info("remove  <{}>", id)
                        tmp_set.add(widget)
        for each in tmp_set:
            self.unvisited.remove(each)

    def __delete_input(self):
        tmplist = []
        for widget in self.unvisited:
            if widget.node.attrib["class"] == "android.widget.EditText":
                tmplist.append(widget)
        for each in tmplist:
            self.unvisited.remove(each)

    def __delete_back(self, page: Page):
        if len(page.sense_root.children) >= 1:
            child0 = page.sense_root.children[0]
        else:
            return
        if child0.widget_type == WidgetType.Normal:
            if len(child0.children) == 2:
                child1 = child0.children[0]
                child2 = child0.children[1]
                if child1.widget_type == WidgetType.Ability and child1.texts == [] and child2.widget_type == WidgetType.Text:
                    self.unvisited.remove(child1)

    def __delete_tabview(self, page: Page):
        if page.actName not in self.tab_view_widgets:
            return
        for widget in self.unvisited:
            if widget in self.tab_view_widgets[page.actName]:
                self.unvisited.remove(widget)

    def __delete_img_node(self, node, img_nodes):
        if node.widget_type == WidgetType.Image:
            img_nodes.append(node)
            return
        for child in node.children:
            self.__delete_img_node(child, img_nodes)

    def __delete_img_in_not_idconent_page(self, page):
        if page.origin_root.attrib['resource-id'] == 'android:id/content':
            return
        img_nodes = []
        self.__delete_img_node(page.sense_root, img_nodes)
