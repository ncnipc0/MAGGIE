import pickle
import sys
from loguru import logger
import random
import time
import Utils
import config
from Utils import get_points, del_files
from config import CONFIG, LOG_CONFIG
from Runner import AppRunner
from Detector import Detector
from SenseTree import STElement
from PageStorage import PageStorage


class Scanner:
    def __init__(self, package, main_activity, recoverMode=False):
        if not recoverMode: del_files("./img/phone" + str(CONFIG["phone_no"]) + "/")
        self.detector = Detector()
        # blacklist initialization
        self.black_list = []
        with open("blacklist.txt", "r", encoding='UTF-8') as f:
            for line in f:
                self.black_list.append(line.rstrip('\n'))
        # blackPageList initialization
        self.black_page_list = []
        with open("blackPageList.txt", "r", encoding='UTF-8') as f:
            for line in f:
                tmp_set = line.rstrip('\n').split()
                self.black_page_list.append(tmp_set)
        self.black_page_list += config.APP['black_pages']
        # Page library initialization
        self.runner = AppRunner(package, self.black_list)

        self.pageStorage = PageStorage()
        if recoverMode:
            with open('./storage/phone' + str(CONFIG["phone_no"]) + '/pageStorage', 'rb') as f:
                self.pageStorage = pickle.load(f)
            with open('./storage/phone' + str(CONFIG["phone_no"]) + '/pageStack', 'rb') as f:
                self.runner.pageStack = pickle.load(f)

        logger.configure(**LOG_CONFIG)
        self.package = package
        self.main_activity = main_activity
        self.xmax, self.ymax = Utils.get_screen_size()



    def get_spw_index(self):
        res = -1
        if "我的" in self.runner.page.all_text and len(self.runner.pageStack) == 2:
            for i, w in enumerate(self.runner.pageStack.top().unvisited):
                if w.all_text != "": continue
                x1, y1, x2, y2 = get_points(w.node.attrib["bounds"])
                x = (x1 + x2) / 2
                y = (y1 + y2) / 2
                if x > self.xmax * 0.9 and y < self.ymax * 0.1:
                    res = i
                    break
        return res

    def scan_app(self, recoverMode=False):
        logger.info("Start exploring")
        t0 = time.perf_counter()

        def back():
            if len(self.runner.pageStack) == 1:
                logger.info("Page depth traversal completed")
                logger.info("Explored pages：{}", len(self.pageStorage))
                logger.info("The detected display of personal information is：{}", self.detector.history_display)
                exit(0)
            logger.info("go back")
            success = self.runner.back_to_last_page()

            if not success:
                logger.error("Page rollback failed")
                time.sleep(1)

        def out_recover():
            self.runner.restart()
            assert self.runner.page is not None
            if not self.runner.click_along_the_stack(cur_index=0):
                back()

        # start app
        if not recoverMode:
            self.runner.start_app(self.package, self.main_activity)
            self.pageStorage.append(self.runner.page)
        if recoverMode:
            self.runner.restart()
            if not self.runner.click_along_the_stack(cur_index=0):
                back()
        if CONFIG["special_detect"]:
            self.detect_special_operation()
            self.runner.go_to_init_page()

        try:
            while True:
                if len(self.runner.pageStack) == 0: break

                if self.runner.page is None or len(self.runner.pageStack.top().unvisited) == 0:
                    logger.info("Page has no widget")
                    back()
                    continue

                if time.perf_counter() - self.pageStorage.last_update >= 300:
                    self.pageStorage.last_update = time.perf_counter()
                    logger.info("No new pages found for a long time")
                    back()
                    continue

                logger.debug("current page:")
                self.runner.page.sense_root.log()
                logger.debug("The number of controls to be accessed on the current page：{}", len(self.runner.pageStack.top().unvisited))
                logger.debug('Unaccessed widget List：{}', [each.texts for each in self.runner.pageStack.top().unvisited])
                select_widget = select_one_widget(self.runner.pageStack.top().unvisited,
                                                  stack_size=len(self.runner.pageStack), index=self.get_spw_index())
                is_success = self.runner.click(select_widget)

                if not is_success:
                    if self.runner.page is None:
                        out_recover()
                    continue

                if self.__is_black_page():
                    logger.info("Recognize black page")
                    back()
                    continue

                if self.runner.page in self.pageStorage or self.pageStorage.same_kind_page_num(
                        self.runner.page) > 3 and not self.is_interested_page(self.runner.page):
                    logger.info("There are already 5 identical or greater pages of the same type")
                    back()
                    continue

                # take_screenshot_for_all_screen_and_save('.\\img\\')
                self.pageStorage.append(self.runner.page)

                if len(self.runner.pageStack) > 4 and not self.is_interested_page(self.runner.page):
                    logger.info("The stack depth is too deep and not the page of interest")
                    back()
                    continue

                if time.perf_counter() - t0 >= 300:
                    t0 = time.perf_counter()
                    with open('./storage/phone' + str(CONFIG["phone_no"]) + '/pageStorage', "wb") as f:
                        pickle.dump(self.pageStorage, f, pickle.HIGHEST_PROTOCOL)
                    with open('./storage/phone' + str(CONFIG["phone_no"]) + '/pageStack', "wb") as f:
                        pickle.dump(self.runner.pageStack, f, pickle.HIGHEST_PROTOCOL)
        except BaseException as e:
            print("BaseException dumping..")
            with open('./storage/phone' + str(CONFIG["phone_no"]) + '/pageStorage', "wb") as f:
                pickle.dump(self.pageStorage, f, pickle.HIGHEST_PROTOCOL)
            with open('./storage/phone' + str(CONFIG["phone_no"]) + '/pageStack', "wb") as f:
                pickle.dump(self.runner.pageStack, f, pickle.HIGHEST_PROTOCOL)
            raise

    def detect_special_operation(self):
        if "order" in config.APP:
            for text in config.APP["order"]:
                tmp = text if text[0] != "#" else text[1:]
                if tmp not in self.runner.page.all_text:
                    logger.debug("loading...")
                    time.sleep(5)
                    self.runner.handle_page_after_loading()

                for w in self.runner.page.clickable:
                    if (text[0] == "#" and text[1:] == w.all_text) or (text[0] != "#" and text in w.all_text):
                        self.runner.click(w)
                        break

            if CONFIG['always_detection']:
                if self.detector.detect(self.runner.page.texts):
                    self.detector.merge_display()

    def __is_black_page(self):
        for each_list in self.black_page_list:
            if all([btext in self.runner.page.all_text for btext in each_list]):
                logger.debug(each_list)
                return True
        return False

    def clear(self):
        self.tab_view_widgets = {}
        self.pageStorage.clear()
        self.runner.pageStack.clear()

    def is_interested_page(self, page):
        logger.debug("stack depth：{}", len(self.runner.pageStack))
        if any([text in t for t in page.texts for text in config.APP["white_texts"]]):
            page.isInterested = True
            logger.debug("Discover pages of interest：{}", page.texts)

        elif self.detector.detect(page.texts):
            page.isInterested = True
            logger.debug("Discover pages of interest：{}", page.texts)

        return page.isInterested


def select_one_widget(unvisited, stack_size=0, index=-1):
    """
    Randomly select a widget
    """
    if index != -1:
        w = unvisited[index]
        unvisited.remove(w)
        return w

    for text in config.APP["white_texts"]:
        if len(text) >= 2 and text[0] == "#" and text[-1] == "#":
            for w in unvisited[:]:
                for wtext in w.texts:
                    if wtext == text[1:-1]:
                        unvisited.remove(w)
                        return w
        else:
            for w in unvisited[:]:
                if (text != "" and text in w.all_text) or (text == "" and text == w.all_text):
                    unvisited.remove(w)
                    return w

    if stack_size > 6: unvisited.clear()

    length = len(unvisited)
    if length == 0:
        return None
    random.seed(2)
    random_index = random.randint(0, length - 1)
    widget = unvisited.pop(random_index)
    assert isinstance(widget, STElement)
    logger.debug("choose widget<'{}', res-id={} bounds={}>", widget.texts, widget.all_resourceID, widget.occupy_area)
    return widget


def unit_test():
    scanner = Scanner(config.APP['package'], config.APP['activity'])
    scanner.runner.start_app(scanner.package, scanner.main_activity)
    scanner.runner.restart()


def main(recoverMode=False):
    scanner = Scanner(config.APP['package'], config.APP['activity'], recoverMode)
    while True:
        try:
            scanner.scan_app(recoverMode)
        except BaseException as e:
            print(e)
            recoverMode = True


if __name__ == "__main__":
    # argv1：Test phone number argv2：App number
    print("phone " + sys.argv[1] + " starts testing")
    if not CONFIG["phone_no"]: CONFIG["phone_no"] = int(sys.argv[1])
    if not CONFIG["serial"]: CONFIG["serial"] = config.serials[CONFIG["phone_no"]]
    if len(sys.argv) >= 3: config.APP = config.appList[int(sys.argv[2]) - 1]
    i = input("recoverMode? Y/N\n")
    if i == "Y":
        main(recoverMode=True)
    elif i == "N":
        main(recoverMode=False)
