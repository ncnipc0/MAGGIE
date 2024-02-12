import copy
import re
from datetime import datetime
from loguru import logger

from PrivacyDB import info

char_record_type = ["Email", "Sex", "Age", "Birth", "Addr"]
range_record_type = ["Name", "ID", "PNum", "BNum"]
default_value = {"PNum": "(0,0)", "Name": "(0,0)", "ID": "(0,0)", "BNum": "(0,0)", "Email": "N", "Sex": "N", "Age": "N",
                 "Birth": "N", "Addr": "N"}


class Detector:
    def __init__(self):
        self.suspect_REs = {
            "Name": [
                info["Name"],
                # X*X
                info["Name"][:1] + "\\*+" + info["Name"][-1:],
                #X**
                info["Name"][:1] + "\\*+",
                #**X
                "\\*\\*+" + info["Name"][-1:],
                     ],

            "Name_py": [
                r"\b[A-Z][a-z*]{1,19}\b"
                # info['Name_py'],
                # info['Name_py'][:1] + "\\*+" + info['Name_py'][-1:]  # Z******n
                        ],

            "Age": ["^" + info["Age"] + "$",
                    "^" + info["Age"] + "岁" + "$",
                    # "^"+str(int(info["Age"])+1)+"$"
                    ],

            "Sex": ["^" + info["Sex"] + "$",
                    info["Sex"] + "$"
                    ],

            "ID/PNum/BNum": [
                r"[\d\*xX]{3,19}",
                # r"[\dxX]{11,}",
                #              r"[\dxX]+\*+[\dxX]*",  # 1****(*/9)
                #              r"[\dxX]*\*+[\dxX]+",  # (*/1)****9
                #              r"\*+[\dxX]+\*+",  # ***456***
                #              r"[\d]{4,}"
                             ],

            "Email": [
                r"([a-zA-Z0-9._%+-]|\*)+@([a-zA-Z0-9.-]|\*)+\.[a-zA-Z]{2,}"
            ],

            "Birth": [
                # YYYY-MM-DD, YYYY/MM/DD, YYYY.MM.DD
                r"(?<![0-9A-Za-z\u4e00-\u9fa5])\d{4}[-/.](0?[1-9]|1[0-2])[-/.](0?[1-9]|[12][0-9]|3[01])(?![0-9A-Za-z\u4e00-\u9fa5])",
                # MM-DD-YYYY, MM/DD/YYYY, MM.DD.YYYY
                r"(?<![0-9A-Za-z\u4e00-\u9fa5])(0?[1-9]|1[0-2])[-/.](0?[1-9]|[12][0-9]|3[01])[-/.]\d{4}(?![0-9A-Za-z\u4e00-\u9fa5])",
                # YYYY年MM月DD日
                r"(?<![0-9A-Za-z\u4e00-\u9fa5])\d{4}年(0?[1-9]|1[0-2])月(0?[1-9]|[12][0-9]|3[01])日(?![0-9A-Za-z\u4e00-\u9fa5])",
                # MM月DD日YYYY年
                r"(?<![0-9A-Za-z\u4e00-\u9fa5])(0?[1-9]|1[0-2])月(0?[1-9]|[12][0-9]|3[01])日\d{4}年(?![0-9A-Za-z\u4e00-\u9fa5])",
                # YYYY年MM月
                r"(?<![0-9A-Za-z\u4e00-\u9fa5])\d{4}年(0?[1-9]|1[0-2])月(?![0-9A-Za-z\u4e00-\u9fa5])",
                # YYYY-MM, YYYY/MM, YYYY.MM
                r"(?<![0-9A-Za-z\u4e00-\u9fa5])\d{4}[-/.](0?[1-9]|1[0-2])(?![0-9A-Za-z\u4e00-\u9fa5])",
                # MM月YYYY年
                r"(?<![0-9A-Za-z\u4e00-\u9fa5])(0?[1-9]|1[0-2])月\d{4}年(?![0-9A-Za-z\u4e00-\u9fa5])",
                # MM-YYYY, MM/YYYY, MM.YYYY
                r"(?<![0-9A-Za-z\u4e00-\u9fa5])(0?[1-9]|1[0-2])[-/.]\d{4}(?![0-9A-Za-z\u4e00-\u9fa5])",
                # MM月DD日
                r"(?<![0-9A-Za-z\u4e00-\u9fa5])(0?[1-9]|1[0-2])月(0?[1-9]|[12][0-9]|3[01])日(?![0-9A-Za-z\u4e00-\u9fa5])",
                # MM-DD, MM/DD, MM.DD
                r"(?<![0-9A-Za-z\u4e00-\u9fa5])(0?[1-9]|1[0-2])[-/.](0?[1-9]|[12][0-9]|3[01])(?![0-9A-Za-z\u4e00-\u9fa5])"
            ],

            "Addr":[
                info["Addr"][0],
                info["Addr"][1],
                    ]
        }
        self.single_display = {}
        self.history_display = copy.deepcopy(default_value)


    def __match_REs(self, info_name, text, all_text):

        if info_name == "Sex":
            if info["Sex"] in all_text and "性" in all_text:
                return info["Sex"]

        elif info_name == "Birth":
            for each_re in self.suspect_REs[info_name]:
                tmp = re.search(each_re, text)
                if tmp :
                    return tmp.group(0)
        else:
            res = []
            for each_re in self.suspect_REs[info_name]:
                if isinstance(each_re, str):
                    tmp = re.search(each_re, text, re.I)
                    if tmp:
                        res.append(tmp.group(0))
                elif isinstance(each_re, list):
                    for item in each_re:
                        tmp = re.search(item, text, re.I)
                        if tmp:
                            res.append(tmp.group(0))
                            logger.info("Addr:",text)
            if len(res) != 0:
                return max(res, key=lambda x: len(x))
            else:
                return None

    def record(self, info_name, info_content):
        def get_format_record(forward, backward, length):
            if forward + 1 >= backward:
                return "(C)"
            ret_str = "("
            ret_str += str(forward + 1)
            ret_str += ","
            ret_str += str(length - backward)
            ret_str += ")"

            return ret_str

        def match_from_two_sides(text, target):
            initial_forward = -1
            initial_backward_target = len(target)
            initial_backward_text = len(text)

            forward = initial_forward
            backward_target = initial_backward_target
            backward_text = initial_backward_text

            while forward + 1 != backward_text and forward < len(text) - 1 and backward_text > 0:
                if text[forward + 1] == target[forward + 1]:
                    forward += 1
                elif text[backward_text - 1] == target[backward_target - 1]:
                    backward_text -= 1
                    backward_target -= 1
                else:
                    break

            count = forward + 1 + len(target) - backward_target

            if count != len([char for char in text if char != '*']):
                forward = initial_forward
                backward_target = initial_backward_target
                backward_text = initial_backward_text
                count = 0

            return count, forward, backward_text

        def check_Birth(info_content, birth_from_database, birth_regexes):
            birth_date = datetime.strptime(birth_from_database, '%Y-%m-%d')
            birth_year = birth_date.year
            birth_month = birth_date.month
            birth_day = birth_date.day
            match_found = False
            for each_re in birth_regexes:
                match_res = re.search(each_re, info_content)
                if match_res:
                    date_str = info_content
                    try:
                        for fmt in ('%Y-%m-%d', '%m-%d-%Y', '%Y/%m/%d', '%m/%d/%Y', '%Y.%m.%d', '%m.%d.%Y',
                                    '%Y年%m月%d日', '%m月%d日%Y年', '%Y年%m月', '%m月%Y年', '%m月%d日', '%m-%d',
                                    '%m/%d', '%m.%d'):
                            try:
                                date = datetime.strptime(date_str, fmt)
                                break
                            except ValueError:
                                pass
                        else:
                            continue

                        if (date.year != 1900) and date.month == birth_month and date.day == birth_day:
                            match_found = True
                            break
                        elif (date.year == 1900) and date.month == birth_month and date.day == birth_day:
                            match_found = True
                            break
                    except Exception as e:
                        print(f"An error occurred: {e}")  # 或其他错误处理

                if match_found:
                    break

            if match_found:
                return True
            else:
                return False

        if info_content in ["", None]:
            return False

        if info_name in ["Age", "Sex"]:
            self.single_display[info_name] = "C"
        elif info_name in ["Addr"]:
            for each_addr in info["Addr"]:
                if each_addr in info_content:
                    self.single_display[info_name] = "C"

        elif info_name in ["Birth"]:
            if check_Birth(info_content, info[info_name], self.suspect_REs["Birth"]):
                self.single_display[info_name] = "C"

        elif info_name in ["Email"]:
            if info_content in info[info_name]:
                self.single_display[info_name] = "C"

        elif info_name in ["ID/PNum/BNum"]:

            final_count = 0
            final_forward = None
            final_backward = None
            final_name = None

            for name in ['ID', 'PNum', "BNum"]:
                if final_name:
                    break
                if isinstance(info[name], list):
                    for pnum in info[name]:
                        if pnum :
                            count, forward, backward_target = match_from_two_sides(info_content, pnum)
                            if (count > final_count) :
                                final_count = count
                                final_forward = forward
                                final_backward = backward_target
                                final_name = name

                else:
                    count, forward, backward_target = match_from_two_sides(info_content, info[name])

                    if count > final_count:
                        final_count = count
                        final_forward = forward
                        final_backward = backward_target
                        final_name = name

            if final_count <= 1:
                return False

            # assert final_count <= len(info[final_name]), "final_count <= len(info[final_name])"
            if final_name in ["PNum", "BNum"]:
                # logger.info(type(info[final_name][0]))
                s = get_format_record(final_forward, final_backward, len(info_content))
                self.single_display[final_name] = s
            else:
                s = get_format_record(final_forward, final_backward, len(info_content))
                self.single_display[final_name] = s

        else:
            extra_chars = [char for char in info_content if
                           char >= '\u4e00' and char <= '\u9fa5' and char not in info["Name"]]

            if not extra_chars:
                count, forward, backward_target = match_from_two_sides(info_content, info["Name"])
                s = get_format_record(forward, backward_target, len(info["Name"]))
                self.single_display["Name"] = s

        return True

    def detect(self, page_texts : [str]):
        res = False
        self.single_display = {}
        escape_sequences = ["\xa0", "\xa0", "\\x0a", "\\x0b", "\\x0c", "\\x0d", "\\x1b", "\\t", "\\r", "\\n", "\\f", "\\v"]
        page_texts = [s.replace(" ", "") for s in page_texts]
        page_texts = [s.replace("+86", "") for s in page_texts]
        page_texts = [s.replace("+86-", "") for s in page_texts]
        page_texts = [s.replace("姓名", "") for s in page_texts]
        page_texts = [s.replace(":", "") for s in page_texts]
        for seq in escape_sequences:
            page_texts = [s.replace(seq, "") for s in page_texts]
        all_text = "".join(page_texts)

        for text in page_texts:
            for info_name in ["Age", "Sex", "Birth", "Addr", "Email", "ID/PNum/BNum", "Name"]:
                raw_match = self.__match_REs(info_name, text, all_text)
                if self.record(info_name, raw_match):
                    res = True

        logger.info("current page info：{}", self.single_display)
        return res

    def merge_display(self):

        def bigger(s1, s2):
            if s1 == "C" or s2 == "C":
                return "C"
            elif s1 == "P" or s2 == "P":
                return "P"
            else:
                return "N"

        def get_two_sides_index(length, info_display):
            info_display = info_display[1:-1]
            if info_display == "C":
                return int(length), 0
            else:
                tmp = info_display.split(",")
                return int(tmp[0]), int(tmp[1])

        for k, v in self.single_display.items():
            if k in ["Email", "Sex", "Age", "Birth", "Addr"]:
                self.history_display[k] = bigger(v, self.history_display[k])
            else:
                if isinstance(info[k], list):
                    length = len(info[k][0])
                else:
                    length = len(info[k])

                front1, back1 = get_two_sides_index(length, v)
                front2, back2 = get_two_sides_index(length, self.history_display[k])

                front_count = max(front1, front2)
                back_count = max(back1, back2)

                s = "(C)" if back_count + front_count >= length else "(" + str(front_count) + "," + str(
                    back_count) + ")"
                self.history_display[k] = s

        logger.info("after merging：{}", self.history_display)

    def get_history_record_str(self):
        res = ""
        for k, v in self.history_display.items():
            res += k
            res += " >> "
            res += v
            res += "\n"
        return res

def count_hidden_chars(text, target):
    forward = -1
    backward_target = len(target)
    backward_text = len(text)

    while forward + 1 != backward_text and forward < len(text) - 1 and backward_text > 0:
        if text[forward + 1] == target[forward + 1] or target[forward + 1] == '*':
            forward += 1
        elif text[backward_text - 1] == target[backward_target - 1] or target[backward_target - 1] == '*':
            backward_text -= 1
            backward_target -= 1

        else:
            break

    count_forward = forward + 1
    count_backward = len(target) - backward_target

    return count_forward, count_backward




