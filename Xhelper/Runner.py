import re
import traceback
from copy import copy
import time
from loguru import logger
import uiautomator2 as u2
import xml.etree.ElementTree as ET
import config
from CompareAlgorithm import sim_tree, sim_text, is_same_kind_page, is_same_page
from PageStorage import Page
from Utils import get_points
from SenseTree import STElement, WidgetType
from config import CONFIG
import Utils


class StackFrame:
    def __init__(self, page, unvisited, forward_widget, black_list):
        self.black_list = black_list
        self.page = page
        self.unvisited = unvisited
        self.forward_widget = forward_widget
        self.delete_duplicate_widget(unvisited)
        self.__delete_blacklist(page)
        self.__delete_back(page)
        self.__delete_input()

    def delete_duplicate_widget(self, unvisited: [STElement]):
        no_text_widges = []
        w: STElement = None
        for w in unvisited:
            if w.texts == []:
                no_text_widges.append((w, get_points(w.node.attrib["bounds"])))
        to_del = set()
        # x1 y1 x2 y2
        for index1, item1 in enumerate(no_text_widges):
            for index2, item2 in enumerate(no_text_widges):
                w1, tp1 = item1[0], item1[1]
                w2, tp2 = item2[0], item2[1]
                if index1 == index2: continue
                if tp1 == tp2:
                    if index1 < index2:
                        to_del.add(w2)
                    else:
                        to_del.add(w1)
                elif tp1[0] <= tp2[0] <= tp1[2] and tp1[0] <= tp2[2] <= tp1[2] and tp1[1] <= tp2[1] <= tp1[3] and tp1[
                    1] <= tp2[3] <= tp1[3]:
                    to_del.add(w1)

        for each in to_del:
            self.unvisited.remove(each)

    def __delete_blacklist(self):
        tmp_set = set()
        for widget in self.unvisited:
            for btext in config.APP["black_texts"] + self.black_list:
                if btext in widget.all_text.replace(" ", ""):
                    logger.info("delete  <{}>", widget.texts)
                    tmp_set.add(widget)

            for bid in config.APP['black_ids']:
                for id in widget.resource_id:
                    res = re.search(':id/([\w_]+)', id)
                    if res is None:
                        continue
                    id = res.group(1)
                    if bid == id:
                        logger.info("remove <{}>", id)
                        tmp_set.add(widget)
        for each in tmp_set:
            self.unvisited.remove(each)

    def __delete_input(self):
        tmplist = []
        for widget in self.unvisited:
            if widget.node.attrib["class"] == "android.widget.EditText":
                logger.info("remove EditText <{}>", widget.texts)
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


class PageStack(list[StackFrame]):

    def __init__(self):
        super().__init__()

    def push(self, stackFrame: StackFrame):
        self.append(stackFrame)

    def pop_back(self):
        return self.pop(-1)

    def top(self):
        return self[-1]

    def contains(self, page, hold=0.75):
        index = self.get_max_sim_index(page, hold)
        if index >= 0:
            return True
        else:
            return False

    def get_max_sim_index(self, page: Page, hold=0.4):
        same_index = -1
        max_sim = 0
        for i in range(0, len(self)):
            if page is None or self[i].page is None: continue
            sim = sim_tree(self[i].page.sense_root, page.sense_root, 0)

            sim2 = 0.5 * sim_tree(self[i].page.sense_root, page.sense_root, 1) + 0.5 * sim_text(self[i].page.texts,
                                                                                                page.texts)
            sim = max(sim2, sim)
            if sim > max_sim:
                max_sim = sim
                same_index = i

        if max_sim > hold:
            return same_index
        else:
            return -1

    def get_index(self, page: Page, diretion="Forward"):
        same_index = -1
        if diretion == "Forward":
            for i in range(0, len(self)):
                logger.debug("Comparing with Page :{}", i)

                if is_same_page(page, self[i].page, 0.7) or is_same_kind_page(page,
                                                                              self[i].page):
                    same_index = i
                    break
        else:
            for i in range(len(self) - 1, -1, -1):
                logger.debug("Comparing with Page :{}", i)
                if is_same_page(page, self[i].page, 0.7) or is_same_kind_page(page,
                                                                              self[i].page):
                    same_index = i
                    break
        return same_index

    def __contains__(self, page: Page):
        index = self.get_index(page)
        if index >= 0:
            return True
        else:
            return False

    def log(self):
        logger.log("STACK", "\t\t========PageStack========")
        for i in range(len(self)):
            logger.log("STACK", "\t\t\t({}) Page:", i)
            self[i].page.sense_root.log(indent=2, stack_mode=True)
            logger.log("STACK", "\t\t\t    Widget:")
            if i == 0:
                logger.log("STACK", "\t" * 5 + "None")
            else:
                logger.log("STACK", "\t" * 5 + "{}", self[i].page.texts)
        logger.log("STACK", "\t\t========Stack END========")


class AppRunner:
    def __init__(self, package, black_list):

        self.device = u2.connect(CONFIG['serial'])
        self.device.implicitly_wait(CONFIG['ui_wait_timeout'])
        self.pageStack = PageStack()
        self.init_page = None
        self.page: Page = None
        self.pre_page: Page = None
        self.package = package
        self.black_list = black_list

    def parse_page(self):
        t = self.device.dump_hierarchy()
        root_node = ET.fromstring(t)

        origin_root = root_node.find(".//*[@package='" + self.package + "']")
        if origin_root is None:
            origin_root = root_node.find(".//*[@package='" + "com.huawei.hwid" + "']")

        if origin_root is None:
            logger.error("origin_root is None")
            time.sleep(1)
            root_node = ET.fromstring(self.device.dump_hierarchy())
            origin_root = root_node.find(".//*[@package='" + self.package + "']")

        if origin_root is None:
            logger.warning("The current page does not belong to the APP")
            self.device.press('back')
            return None

        actName = self.device.app_current()['activity']
        page: Page = Page(origin_root, actName)
        return page

    def start_app(self, package: str, main_activity: str):
        """
        Start the MainActivity of the APP with the specified package name
        """
        self.clear()

        logger.info("start APP")
        logger.debug("target APP package name：{}", package)
        logger.debug("target Activity：{}", main_activity)

        # time.sleep(3)
        logger.info("start..." + config.APP["activity"])
        self.device.app_start(package_name=package, use_monkey=True)
        self.device.wait_activity(main_activity, timeout=5)
        if "init_oper" in config.APP:
            for op, t in config.APP["init_oper"]:
                self.device(textContains=op).click()
                time.sleep(t)

        self.handle_page_after_loading(wait_time=1)
        self.init_page = self.page
        self.pageStack.push(StackFrame(self.page, copy(self.page.clickable), None, self.black_list))

    def restart(self):
        logger.info("restart APP")
        self.device.app_stop(self.package)
        time.sleep(1)
        logger.info("start..." + self.package)
        self.device.app_start(package_name=self.package, use_monkey=True)
        logger.info("wait for..." + config.APP["activity"])
        self.device.wait_activity(config.APP["activity"], timeout=5)
        time.sleep(1)
        if "init_oper" in config.APP:
            for op, t in config.APP["init_oper"]:
                self.device(textContains=op).click()
                time.sleep(t)
        self.handle_page_after_loading()

    def handle_page_after_loading(self, wait_time=1):

        page: Page = self.parse_page()
        uistr = self.device.dump_hierarchy()


        if page is None:
            if "允许" in uistr and "拒绝" in uistr:
                try:
                    self.device(textContains="拒绝").click()
                except Exception as e:
                    print(e)
                time.sleep(1)
                page = self.parse_page()
            if "允许" in uistr:
                try:
                    self.device(textContains="允许").click()
                except Exception as e:
                    print(e)
                time.sleep(1)
                page = self.parse_page()

        # Page not fully rendered
        retry_C1 = CONFIG['no_page_retry']
        while page is None and retry_C1 > -1:
            retry_C1 -= 1
            logger.warning("{} Waiting for reload, the root node of the page does not contain nodes with package={}", CONFIG['no_page_retry'] - retry_C1, self.package)
            if retry_C1 == 0:
                logger.warning("Waiting for page rendering failed")
                self.press_back()
            time.sleep(wait_time)
            page = self.parse_page()

        retry_C2 = CONFIG['no_data_retry']
        while page is not None and (len(page.clickable) <= 5 and len(page.texts) < 5 or "加载中" in page.all_text):
            retry_C2 -= 1
            logger.warning("{}Waiting for load", CONFIG['no_data_retry'] - retry_C2)
            for i in range(3):
                logger.debug("{}s", 3 - i)
                time.sleep(1)
            if retry_C2 <= 0:
                logger.debug("Reparse the current page")
                page = self.parse_page()
                logger.warning("Reached maximum number of attempts")
                break
            logger.debug("Reparse the current page")
            page = self.parse_page()

        self.page = page

    def click_along_the_stack(self, target_index=-1, cur_index=-1):
        """
        Restore to the specified page in stack
        """
        try:
            logger.debug("click along the stack")
            if target_index < 0:
                target_index = len(self.pageStack) + target_index

            index = self.pageStack.get_max_sim_index(self.page) if cur_index == -1 else cur_index
            assert index >= 0, "confirm that the current page is on the stack"

            if target_index == index:
                logger.debug("The current page is the target page")
                return True

            for i in range(index, target_index):
                expect_page, click_widget = self.pageStack[i + 1].page, self.pageStack[i + 1].forward_widget
                self.click_once_without_changing_stack(click_widget)
                self.handle_page_after_loading()
                logger.info("Click on the widget on the current page<{}>", click_widget)
                logger.debug("The page that jumps to after clicking is：")
                self.page.sense_root.log()
                if not is_same_kind_page(self.page, expect_page, hold=0.4):
                    time.sleep(2)
                    self.handle_page_after_loading()

                if is_same_kind_page(self.page, expect_page, hold=0.4):
                    logger.debug("Jump to expiration page")
                else:
                    logger.error("Page recovery failed")
                    if is_same_kind_page(self.page, expect_page, hold=0.4):
                        logger.error("This page is of the same type")
                    else:
                        logger.error("Expected page：")
                        expect_page.sense_root.log()
                        logger.error("This page is not of the same type")
                    return False
            return True
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print("Exception")
            traceback.format_exc()
            if self.pageStack[0].page: self.pageStack[0].page.sense_root.log()
            if self.page: self.page.sense_root.log()
            return False


    def back_to_last_page(self):
        """
        Return to the previous page on the stack and push the current page out of the stack
        """
        cur_page = self.pageStack.top().page
        logger.debug("current page：")
        cur_page.sense_root.log()
        self.pageStack.pop()
        logger.debug("The current page is out of stack")
        last_page = self.pageStack.top().page
        logger.debug("The top page of the stack has been updated to：")
        last_page.sense_root.log()
        logger.log("STACK", "The current page stack is：")
        self.pageStack.log()
        is_success = True
        if not self.pageStack.contains(self.page, hold=0.9):
            self.press_back()
            self.handle_page_after_loading()

        count = 0
        while not self.pageStack.contains(self.page, hold=0.75):
            if count == 5:
                is_success = False
                break
            count += 1
            self.press_back()
            self.handle_page_after_loading()
            if self.page is None:
                is_success = False
                break

        if self.page is None: is_success = False

        if is_success:
            same_index = self.pageStack.get_max_sim_index(self.page)
            assert same_index >= 0
            logger.debug("Find the same page on the stack,index:{}", same_index)
            is_success = self.click_along_the_stack()

        def handle_failurev2():
            while len(self.pageStack) > 1:
                self.restart()
                res = self.click_along_the_stack(cur_index=0)
                if res:
                    print("click along success")
                    break
                else:
                    print("click along fail")
                    print("pop")
                    self.pageStack.pop()

            if len(self.pageStack) == 1 and not (is_same_page(self.pageStack.top().page, self.page,
                                                              0.4) or is_same_kind_page(
                self.pageStack.top().page, self.page, hold=0.4)):
                self.restart()

        if not is_success:
            handle_failurev2()

        return True

    def go_to_init_page(self):
        logger.debug("Return to the initial page")
        self.restart()
        while len(self.pageStack) > 1:
            self.pageStack.pop()
        return

    def press_back(self, sleeptime=1):
        logger.debug("==press back==")
        self.device.press("back")
        time.sleep(sleeptime)

    def click(self, selected_widget: STElement) -> bool:
        if selected_widget is None: return False
        logger.info("click<'{}', res-id={} bounds={}>widget", selected_widget.texts, selected_widget.all_resourceID,
                    selected_widget.node.attrib["bounds"])
        assert isinstance(selected_widget, STElement), type(selected_widget)
        self.pre_page = self.page
        self.click_once_without_changing_stack(selected_widget)
        self.handle_page_after_loading()
        retry_times = CONFIG["max_retry_times"]
        while is_same_page(self.pre_page, self.page):
            if retry_times > 0:
                logger.debug("Page not redirected, try clicking again")
                retry_times -= 1
                self.click_once_without_changing_stack(selected_widget)
                self.handle_page_after_loading()
            else:
                logger.error("Reached maximum number of attempts, failed")
                logger.debug("current page：")
                self.pre_page.sense_root.log()
                logger.debug("current page：")
                self.page.sense_root.log()
                return False


        if self.page is not None:
            self.pageStack.push(StackFrame(self.page, copy(self.page.clickable), selected_widget, self.black_list))
            return True
        else:
            logger.error("Clicking on the widget does not respond or the app pops up")
            return False


    def click_once_without_changing_stack(self, widget: STElement):
        try:
            node = widget.node
            occupy_area = widget.occupy_area

            point = Utils.calculate_operation_point(node.attrib["bounds"], occupy_area)
            ui_obj = self.get_ui_obj(node)
            if ui_obj.count == 1:
                ui_obj.click()
                time.sleep(1)
                return

            for text in widget.texts:
                ui_obj = self.device(text=text)
                if ui_obj.count == 1:
                    ui_obj.click()
                    time.sleep(1)
                    return
            self.device.click(point[0], point[1])
            time.sleep(1)

        except KeyboardInterrupt as e:
            print("KeyboardInterrupt")
            raise
        except Exception:
            pass

    def set_text(self, widget: STElement, set_text):
        """"""
        node = widget.node
        occupy_area = widget.occupy_area
        ui_obj = self.get_ui_obj(node)
        if ui_obj.count == 1:
            ui_obj.set_text(set_text)
            return

        for text in widget.texts:
            ui_obj = self.device(text=text)
            if ui_obj.count == 1:
                ui_obj.set_text(set_text)
                time.sleep(1)
                return
        print("Unable to locate widget")
        exit(-1)

    def get_ui_obj(self, node: ET.Element):
        if node.attrib["content-desc"] == "" and node.attrib["resource-id"] == "":
            return self.device(
                className=node.attrib["class"],
                packageName=node.attrib["package"],
                checkable=node.attrib["checkable"],
                clickable=node.attrib["clickable"],
                longClickable=node.attrib["long-clickable"],
                scrollable=node.attrib["scrollable"],
                enabled=node.attrib["enabled"],
                focusable=node.attrib["focusable"],
                index=node.attrib["index"]
            )
        elif node.attrib["content-desc"] == "" and node.attrib["resource-id"] != "":
            return self.device(
                className=node.attrib["class"],
                packageName=node.attrib["package"],
                resourceId=node.attrib["resource-id"],
                checkable=node.attrib["checkable"],
                clickable=node.attrib["clickable"],
                longClickable=node.attrib["long-clickable"],
                scrollable=node.attrib["scrollable"],
                enabled=node.attrib["enabled"],
                focusable=node.attrib["focusable"],
                index=node.attrib["index"]
            )
        elif node.attrib["content-desc"] != "" and node.attrib["resource-id"] == "":
            return self.device(
                className=node.attrib["class"],
                packageName=node.attrib["package"],
                description=node.attrib["content-desc"],
                checkable=node.attrib["checkable"],
                clickable=node.attrib["clickable"],
                longClickable=node.attrib["long-clickable"],
                scrollable=node.attrib["scrollable"],
                enabled=node.attrib["enabled"],
                focusable=node.attrib["focusable"],
                index=node.attrib["index"]
            )
        else:
            return self.device(
                className=node.attrib["class"],
                packageName=node.attrib["package"],
                resourceId=node.attrib["resource-id"],
                description=node.attrib["content-desc"],
                checkable=node.attrib["checkable"],
                clickable=node.attrib["clickable"],
                longClickable=node.attrib["long-clickable"],
                scrollable=node.attrib["scrollable"],
                enabled=node.attrib["enabled"],
                focusable=node.attrib["focusable"],
                index=node.attrib["index"]
            )

    def clear(self):
        self.pageStack.clear()
