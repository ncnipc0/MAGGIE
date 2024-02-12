# coding:utf-8
import os.path
import traceback
from collections import defaultdict
from copy import copy, deepcopy
from pypinyin import lazy_pinyin
import openpyxl

# index name in excel file
col_index = ["APP类别", "APP名称", "备注", "注册条件（需要哪些认证因子）", "pnum&SMS", "pnum&Pwd", "ID&Pwd", "enum&Pwd", "Una&Pwd", "第三方登录",
             "其他登录", "其他登录", "RSPWD_pnum&SMS", "RSPWD_enum&验证码", "安全问题", "其他", "如果强制开启请标注,若果未强制开启,默认不开启",
             "查看敏感信息的二次认证条件",
             "二次认证后能查看", "是有绑定银行卡,如果有,支付条件", "重置支付密码条件", "是有转账功能,如果有,转账条件", "是有借贷功能", "其他重要信息", "Name", "age", "sex",
             "birth", "addr", "enum", "ID", "pnum", "bnum"]

filename = r"Result.xlsx"
output_file_name = r"out.txt"
output_file_name2 = None
sheet_name = "Sheet1"
third_login_flag = False
# Factors involved and corresponding lengths
l = [('SMS', 1), ('bnum', 1), ('Name', 1), ('IDp1', 1), ('IDp2', 1), ('IDp3', 1), ('enum', 1), ('Ecode', 1)]
length_dict = dict()
# Total length of factors
total_len = 0
third_Login_APP = []
third_Ligin_APP_name = dict()  # The app name corresponding to the third-party login method
manual = True
if manual:
    third_Ligin_APP_name = {'百度': '百度v13.14.0.11', 'YY': 'YYv8.11.1', '抖音': '抖音(优价好物)v21.5.0',
                            'QQ': 'QQv8.8.98.8410', '京东': '京东v11.1.2', '微博': '微博v12.7.0',
                            '淘宝': '淘宝v10.14.0', '支付宝': '支付宝v10.2.76', '今日头条': '今日头条v8.8.8', '微信': '微信v8.0.24'}

Email_app = ["QQ邮箱v6.3.5", "139邮箱v9.3.3", "网易邮箱大师v7.10.1", "网易邮箱v7.9.5"]
MIN_ROW = 4
MIN_COL = 1
MAX_ROW = 237
MAX_COL = 33
Var_name = "knowledgements"  # Variable names for SVM code
N = 0


def init_global(cond, data, dir_index, init_code_index, PART_index):
    global N
    if init_code_index: N = 0

    global COND
    COND = cond
    global total_len
    total_len = 0
    global DIR_INDEX
    DIR_INDEX = dir_index

    for _, length in l:
        total_len += length

    # 输出文件以因子长度加攻击条件命名
    global output_file_name2
    N += 1
    output_file_name2 = "./SMV_code_file/" if PART_index is None else "./SMV_code_file-" + str(PART_index) + "/"

    if DIR_INDEX != None:
        output_file_name2 += str(DIR_INDEX) + "/"

    output_file_name2 += "code" + str(N) + "-" + str(total_len) + "bit" + "".join(COND) + ".smv"

    global length_dict
    length_dict = dict()
    for tp in l:
        length_dict[tp[0]] = tp[1]

    init_third_Login_APP(data)


def init_third_Login_APP(data):
    s = set()
    for i in data:
        if i["第三方登录"] is None:
            continue
        tmp = i["第三方登录"].split(",")
        for j in tmp:
            s.add(j)
    print(s)
    global third_Login_APP
    third_Login_APP = list(s)

    if not manual:
        global third_Ligin_APP_name
        third_Ligin_APP_name = dict()
        for APP in third_Login_APP:
            for row in data:
                appname = row["APP名称"]
                if APP in appname:
                    third_Ligin_APP_name[APP] = appname
                    break

    # print(third_Ligin_APP_name)


def read_data(worksheet, used_apps=None):
    data = []
    # 将excel数据读入data
    for row in worksheet.iter_rows(min_row=MIN_ROW, min_col=MIN_COL, max_row=MAX_ROW, max_col=MAX_COL):
        d = dict()
        for index, cell in enumerate(row):
            # print(index,cell.value)
            # print(d)
            # if "中国建设银行v5.7.4" == cell.value:
            #     print("123")

            if (col_index[index] == "其他登录") and ("其他登录" in d) and (d["其他登录"] is not None):
                if (cell.value is not None):
                    d["其他登录"] += ", "
                    d["其他登录"] += cell.value
                else:
                    continue
            else:
                d[col_index[index]] = cell.value

            print(cell.value, end=" ")
        print()
        data.append(d)

    # APP过滤
    name_fix_dict = {
        r'“T3”出行': r'T3出行',
        r'微信': r'微信v',
        r'QQ': r'QQv',
        r'京东': r'京东v',
        r'美团-美好生活小帮手': r'美团美好生活小帮手',
        r'携程旅行-订酒店机票火车票': r'携程旅行',
        r'“58”同城': r'58同城',
        r'今日头条': r'今日头条v',
        r'百度': r'百度v',
        r'爱彼迎china': '爱彼迎',
        r'移动云盘': '移动云盘',
        r'中国移动': '中国移动v',
        r'抖音好物': '抖音优价好物',
        r'网易邮箱': '网易邮箱v',
        r'快手': '快手v',
        r'百度输入法': '百度输入法v',
        r'百度CarLife+': '百度CarLife'
    }
    if used_apps is not None:
        data_used_apps = []
        for app in used_apps:
            # 名称修正
            if app in name_fix_dict:
                app = name_fix_dict[app]
            app = app.replace(r'"', "")
            app = app.replace(r'“', "")
            app = app.replace(r"”", "")
            app = app.replace(r'-', "")
            if app in ["桌子", "苹果", "草莓", '都没使用过', '中国国航', '中国人保', '招联金融', '钱站']:
                continue

            index = -1
            count = 0
            for vindex, row in enumerate(data):
                if app in row["APP名称"]:
                    assert count == 0, app + " " + row["APP名称"]
                    count += 1
                    index = vindex
            assert count == 1 and index != -1, app + str(count)
            data_used_apps.append(data[index])
        data = data_used_apps

    # print(len(used_apps),len(data),data)
    # exit(1)

    name_to_index_of_data = dict()
    for index, row in enumerate(data):
        name_to_index_of_data[row["APP名称"]] = index

    return name_to_index_of_data, data


def get_01string_by_text_CNP(s: str) -> str:
    assert s in ["C", "P", "N"], s
    if s == "C":
        return "1"
    else:
        return "0"


def get_01string_by_text_n1n2(s: str, len) -> str:
    if s == "C":
        return "1" * len
    elif s == "N":
        return "0" * len

    assert "," in s, s
    n1, n2 = int(s.split(",")[0]), int(s.split(",")[1])
    assert n1 + n2 < len, s
    return n1 * '1' + '0' * (len - n1 - n2) + n2 * '1'


def get_01string_by_name(info_name, info_text):
    info_len = length_dict[info_name]
    if info_len != 1:
        if info_text == "C":
            return "1" * info_len
        elif info_text == "N":
            return "0" * info_len
        assert "," in info_text, info_text
        n1, n2 = int(info_text.split(",")[0]), int(info_text.split(",")[1])
        assert n1 + n2 < info_len, info_text
        return n1 * '1' + '0' * (info_len - n1 - n2) + n2 * '1'
    else:
        # assert info_text in ["C", "P", "N"], info_text
        if info_text == "C":
            return "1"
        else:
            return "0"


def get_01string_by_list(l_condition) -> str:
    """
    Input factors and return the 01 string representing these factors
    """
    s = "0b" + str(total_len) + "_"

    if len(l_condition) == 0:
        return s + "0" * total_len

    if isinstance(l_condition[0], str):
        for key, length in l:
            if key not in l_condition:
                s += "0" * length
            else:
                s += "1" * length
        return s
    else:
        tmp1, _ = zip(*l_condition)
        k_list = list(tmp1)
        for key, length in l:
            if key not in k_list:
                s += "0" * length
            else:
                for name, text in l_condition:
                    if name == key:
                        s += get_01string_by_name(name, text)
                        break
        assert len(s) == len("0b" + str(total_len) + "_") + total_len
        return s


def get_info_after_login(data) -> dict:
    info_after_login = {}
    for row in data:
        try:
            tmp_list = []
            for i in l:
                #  不考虑生日 因为与身份证的第二部分重复
                if i[0] in ["birth"]:
                    continue
                # 登陆后看不到短信验证码
                elif i[0] in ["SMS"]:
                    tmp_list.append((i[0], "N"))
                # 如果是邮箱app 登陆后可以看到Ecode
                elif i[0] in ["Ecode"]:
                    if row["APP名称"] in Email_app:
                        tmp_list.append((i[0], "C"))
                    else:
                        tmp_list.append((i[0], "N"))
                elif i[0] in ["IDp1"]:
                    id_info = row["ID"]
                    if id_info in ["C", "N"]:
                        tmp_list.append(("IDp1", id_info))
                        tmp_list.append(("IDp2", id_info))
                        tmp_list.append(("IDp3", id_info))
                    else:
                        assert "," in id_info
                        n1 = int(id_info.split(",")[0])
                        n2 = int(id_info.split(",")[1])
                        IDp1_n1 = n1 if n1 >= 0 else 0
                        IDp1_n2 = n2 - 12 if n2 - 12 >= 0 else 0
                        IDp2_n1 = n1 - 6 if n1 - 6 >= 0 else 0
                        IDp2_n2 = n2 - 4 if n2 - 4 >= 0 else 0
                        IDp3_n1 = n1 - 14 if n1 - 14 >= 0 else 0
                        IDp3_n2 = n2 if n2 >= 0 else 0
                        res = []
                        for index, tp in enumerate(
                                [(IDp1_n1, IDp1_n2, 6), (IDp2_n1, IDp2_n2, 8), (IDp3_n1, IDp3_n2, 4)]):

                            n1 = tp[0]
                            n2 = tp[1]
                            length = tp[2]

                            n1 = min(length, n1)
                            n2 = min(length, n2)
                            if n1 + n2 >= length or (index == 0 and n1 >= 2):
                                res.append("C")
                            elif n1 == n2 == 0:
                                res.append("N")
                            else:
                                res.append(str(n1) + "," + str(n2))

                        if row["birth"] == "C":
                            res[1] = "C"

                        for name, value in zip(["IDp1", "IDp2", "IDp3"], res):
                            # print(name,value)
                            tmp_list.append((name, value))

                elif i[0] in ["IDp2", "IDp3"]:
                    continue
                else:
                    tmp_list.append((i[0], row[i[0]]))
            s = get_01string_by_list(tmp_list)
            print(tmp_list)
        except Exception as e:
            print(traceback.format_exc())
            exit(1)
        print(s)

        info_after_login[row["APP名称"]] = s
    return info_after_login


def get_login_way(data) -> dict:
    login_condition = dict()
    for row in data:
        assert row["Name"] is not None
        assert row["APP名称"] is not None
        app_name = row["APP名称"]
        login_condition[app_name] = [[], [], [], None, None]
        # SMS login method
        if row["pnum&SMS"] == 1:
            login_condition[app_name][0].append("SMS")
        if third_login_flag:
            # Third party login method
            if row["第三方登录"] is not None:
                for s in third_Login_APP:
                    if s in row["第三方登录"]:
                        login_condition[app_name][1].append(s)

        # Reset login password login
        if row["RSPWD_pnum&SMS"] == 1:
            login_condition[app_name][2].append("SMS")
        if row["RSPWD_enum&验证码"] == 1:
            login_condition[app_name][2].append("enum")

        def get_reset_pwd_condition(row):
            res = []
            if row["RSPWD_pnum&SMS"] == 1:
                res.append(["SMS"])
            if row["RSPWD_enum&验证码"] == 1:
                res.append(["enum", "Ecode"])
            if row["其他"] != "" and row["其他"] != None:
                ways = row["其他"].split(",")
                for way in ways:
                    res.append(way.split("&"))
            print(row)
            print("res：", res)
            return res

        def get_login_condition(row):
            res = []
            if row["pnum&SMS"] == 1:
                res.append(["SMS"])
            if row["pnum&Pwd"] == 1:
                res.append(["Pwd"])
            if row['ID&Pwd'] == 1:
                res.append(["IDp1", "IDp2", "IDp3", "Pwd"])
            if row["enum&Pwd"] == 1:
                res.append(["enum", "Pwd"])

            if row["其他登录"] != "" and row["其他登录"] != None:
                ways = row["其他登录"].split(",")
                for way in ways:
                    res.append(way.split("&"))
            print(row)
            print("res：", res)
            return res

        login_ways = get_login_condition(row)
        reset_ways = get_reset_pwd_condition(row)
        login_condition[app_name][3] = login_ways
        login_condition[app_name][4] = reset_ways

    return login_condition


def get_condition_expresssion(login_way: list):
    res = "((" + Var_name + "&"
    res += get_01string_by_list(login_way)
    res += ")="
    res += get_01string_by_list(login_way)
    res += ")"
    return res


def generate_expression(login_condition, info_after_login, data):
    res = dict()

    for row in data:
        try:
            appname = row["APP名称"]
            res[appname] = []
            if appname not in login_condition:
                continue
            list1 = login_condition[appname][0]  # SMS

            # Generate SMS login expression
            if len(list1) != 0:
                login_condition_expresssion = get_condition_expresssion(["SMS"])
                s = row["pinyin"] + ".Login(SMS)"
                s += "&"
                s += login_condition_expresssion
                s += ":" + Var_name + "|"
                s += info_after_login[appname]
                res[appname].append(s)

        except Exception as e:
            print(traceback.format_exc())

    return res


def generate_pinyin(data):
    for row in data:
        try:
            appname: str = row["APP名称"]
            if appname is None:
                continue

            assert "v" in appname, appname
            chinese_name = appname.split("v")[0]
            pinyin = "".join(lazy_pinyin(chinese_name))

            s_builder = ""
            for index, c in enumerate(pinyin):
                if c not in [chr(i) for i in range(ord('a'), ord('z') + 1)] + [str(i) for i in range(0, 10)] + [chr(i)
                                                                                                                for i in
                                                                                                                range(
                                                                                                                    ord(
                                                                                                                        "A"),
                                                                                                                    ord("Z") + 1)]:
                    continue
                s_builder += c
            pinyin = s_builder
            assert len(pinyin) > 0, row["APP名称"]
            if '0' <= pinyin[0] <= '9':
                row["pinyin"] = "App" + pinyin
            else:
                row["pinyin"] = pinyin

        except Exception as e:
            print(traceback.format_exc())


def get_operation_and_condition(data, f=True):
    res = dict()
    for row in data:
        if "login_way" not in row:
            continue
        appname = row["APP名称"]
        tmp = []
        list1 = row["login_way"][0]  # SMS
        list2 = row["login_way"][1]  # third
        list3 = row["login_way"][2]  # resetPWD
        list4 = row["login_way"][3]
        list5 = row["login_way"][4]

        res[appname] = tmp

        for login_way in list4:
            if "Pwd" not in login_way:
                tmp.append(("LoginBy" + "".join(login_way), get_condition_expresssion(login_way)))
            else:
                for reset_way in list5:
                    assert "Pwd" not in reset_way
                    tmp_set = set(login_way)
                    tmp_set.remove("Pwd")
                    tmp_set = tmp_set.union(set(reset_way))
                    tmp.append(("LoginBy" + "".join(login_way) + "ResetBy" + "".join(reset_way),
                                get_condition_expresssion(list(tmp_set))))

        to_del = set()
        for name1, cond_str in tmp:
            tmp_cond1 = int(cond_str[cond_str.index("_") + 1:cond_str.index("_") + 1 + total_len], base=2)
            for name2, cond_str2 in tmp:
                tmp_cond2 = int(cond_str2[cond_str2.index("_") + 1:cond_str2.index("_") + 1 + total_len],
                                base=2)
                if name1 != name2 and tmp_cond1 != tmp_cond2 and tmp_cond1 | tmp_cond2 == tmp_cond2:
                    to_del.add((name2, cond_str2))

        n = 0
        for item in to_del:
            tmp.remove(item)
            n += 1
            print("test", n, item)

        def is_in_list(l, s):
            for item in [tp[1] for tp in l]:
                if s == item:
                    return True
            return False

        # third part
        for APP in list2:
            if APP in third_Ligin_APP_name:
                conditions = get_login_condition(third_Ligin_APP_name[APP], data)
                for condition in conditions:
                    if not is_in_list(tmp, condition):
                        tmp.append(("Login" + "".join(lazy_pinyin(APP)), condition))

    return res


def get_login_condition(appname, data, exclude_third=False):
    res = []
    for row in data:
        if row["APP名称"] == appname:
            operation_and_condition = row["operation_and_condition"]
            for op, cond in operation_and_condition:
                exclude_third = True
                if exclude_third:
                    print(op, cond)
                    # continue
                res.append(cond)
            break
    return res


def get_nusmv_str(data):
    n = 0
    str_list = []
    res = ""
    for index, row in enumerate(data):

        # info_after_login 全零不考虑
        if row["info_after_login"] == get_01string_by_list([]):
            continue

        print(index, row["APP名称"])
        res += "-- " + str(index) + row["APP名称"] + "\n"

        try:
            for op, cond in row["operation_and_condition"]:
                tmp_cond = cond[cond.index("_") + 1:cond.index("_") + 1 + total_len]
                tmp_info_after_login = row["info_after_login"][
                                       row["info_after_login"].index("_") + 1:row["info_after_login"].index(
                                           "_") + 1 + total_len]
                tmp1 = int(tmp_cond, base=2)
                tmp2 = int(tmp_info_after_login, base=2)

                if tmp1 | tmp2 == tmp1:
                    n += 1
                    print(bin(tmp1), bin(tmp2))
                    print("hhh", n)
                    continue

                cond2 = "((" + Var_name + "|" + row["info_after_login"] + ")!=" + Var_name + ")"  # new
                s = row["pinyin"]
                # s += "_"
                s += op
                s += "&"
                s += cond
                s += "&"  # new
                s += cond2  # new
                s += ":" + Var_name + "|"
                s += row["info_after_login"]
                s += ";"
                print(s)
                res += s + "\n"
                str_list.append(s)
        except Exception as e:
            print(traceback.format_exc())
    return res, str_list


def dump_nusmv_01str_to_file(data, file_name):
    with open(file_name, "w", encoding="utf-8") as f:
        s, _ = get_nusmv_str(data)
        f.write(s)


def generate_nusmv_code(data, filename, merger_APP=True):
    _, s_list = get_nusmv_str(data)
    tmp = set()

    # merge apps
    if merger_APP:
        hashmap = defaultdict(set)
        for i, each in enumerate(s_list):
            index = each.find("&")
            name = each[:index]
            string = each[index + 1:]
            hashmap[string].add((i, name))

        hashmap2 = {}
        for index, s in enumerate(hashmap):
            if len(hashmap[s]) > 1:
                print(s, hashmap[s])
                hashmap2[s] = hashmap[s]

        d = {}
        count = 0
        for s in hashmap2.values():
            print(s)
            for index, name in s:
                d[index] = ("LoginWay" + str(count), name)
            count += 1

        for index, s in enumerate(s_list):
            if index in d:
                string = s[s.find("&") + 1:]
                s_list[index] = d[index][0] + "&" + string
                assert s.split("&")[0] == d[index][1]

        s_list = list(set(s_list))
        # print(s_list)
        # exit(1)

    # generate app_list
    for each in s_list:
        tmp.add(each.split("&")[0])
        if each == "tengxunshoujiguanjia—QQweixinbaohu_Login_SMS&((knowledgements&0b58_1111111111110000000000000000000000000000000000000000000000)=0b58_1111111111110000000000000000000000000000000000000000000000)&((knowledgements|0b58_0111000011110000000000000000000000000000000000000000000000)!=knowledgements):knowledgements|0b58_0111000011110000000000000000000000000000000000000000000000;":
            print(1)
            a = each.split("&")[0]

    cond = get_01string_by_list(COND)
    app_list = list(tmp)
    s = "-- " + str(l) + "\n"
    s += "MODULE main\n"
    s += "VAR " + Var_name + ": word[" + str(total_len) + "];\n"
    s += "VAR app_list : {no," + ",".join(app_list) + "};\n\n"
    s += "ASSIGN\n"
    # s += "\tinit(" + Var_name + "):=" + get_01string_by_list(["enum","Ecode"]) + ";\n"
    s += "\tinit(" + Var_name + "):=" + get_01string_by_list(["SMS"]) + ";\n"
    s += "\tinit(app_list):=no;\n"
    s += "\tnext(" + Var_name + "):=\n"
    s += "\t\tcase\n"
    s += "\t\t\tapp_list = no:" + Var_name + ";\n"
    s += "\t\t\t(knowledgements&" + cond + ")=" + cond + ":" + get_01string_by_list([]) + ";\n"
    for each in s_list:
        s += "\t\t\tapp_list = " + each + "\n"
    s += "\t\t\tTRUE: " + get_01string_by_list([]) + ";\n"
    s += "\t\tesac;\n"

    s += "\tnext(" + "app_list" + "):=\n"
    s += "\t\tcase\n"
    s += "\t\t\tapp_list!=no:no;\n"
    s += "\t\t\tTRUE: {" + ",".join(app_list) + "};\n"
    s += "\t\tesac;\n"
    s += "CTLGRADSPEC AG 0 " + "(((knowledgements&" + cond + ")!= " + cond + ")|app_list!=no" + ")\n"

    # l = [('SMS', 1) ,('Name',1),('IDp1', 1), ('IDp2', 1), ('IDp3', 1), ('bnum', 1),('enum', 1), ('Ecode', 1)]
    if merger_APP:
        tmp = defaultdict(set)
        for name1, name2 in d.values():
            tmp[name1].add(name2)
        for name, set1 in tmp.items():
            s += "-- " + name + " " + str(set1) + "\n"

    if not os.path.exists(filename[:filename.rindex("/")]):
        os.makedirs(filename[:filename.rindex("/")])
    with open(filename, "w", encoding="utf-8") as f:
        f.write(s)


worksheet = None


def main(cond, used_apps=None, dir_index=None, init_code_index=False, PART_index=None):

    # Read data into the data variable
    book = openpyxl.load_workbook(filename)
    global worksheet
    if worksheet is None: worksheet = book[sheet_name]
    name_to_index_of_data, data = read_data(worksheet, used_apps)
    init_global(cond, data, dir_index, init_code_index, PART_index)
    generate_pinyin(data)

    info_after_login = get_info_after_login(data)
    # Add data
    for k, v in info_after_login.items():
        data[name_to_index_of_data[k]]["info_after_login"] = v

    # Read login method
    login_condition = get_login_way(data)
    for k, v in login_condition.items():
        data[name_to_index_of_data[k]]["login_way"] = v

    for row in data:
        row["operation_and_condition"] = []

    tmp_data = None
    while tmp_data != data:
        tmp_data = deepcopy(data)
        operation_and_condition = get_operation_and_condition(data)
        for appname, tplist in operation_and_condition.items():
            for tp in tplist:
                if tp not in data[name_to_index_of_data[appname]]["operation_and_condition"]:
                    data[name_to_index_of_data[appname]]["operation_and_condition"].append(tp)
                    print("tp:", tp)

    dump_nusmv_01str_to_file(data, output_file_name)
    generate_nusmv_code(data, output_file_name2)


if __name__ == "__main__":

    COND_list = [
        ["enum", "Ecode"],
        ["enum"],
        ["IDp1", "IDp2", "IDp3"],
        ["bnum"],
        ["Name"],
        ["Name", "IDp1", "IDp2", "IDp3"],
        ["IDp2", "IDp3"],  # 5
        ["IDp3"],
        ["IDp1", "IDp3"],  # 6
        ["enum", "Ecode", "bnum", "IDp1", "IDp2", "IDp3"],
        ["Name", "bnum"],  # 16
        ["bnum", "IDp1", "IDp2", "IDp3"],
        ["Name", "bnum", "IDp1", "IDp2", "IDp3"],
        ["enum", "bnum", "IDp1", "IDp2", "IDp3"],
        ["enum", "Ecode", "IDp1", "IDp2", "IDp3"],
        ["enum", "Ecode", "IDp1", "IDp2", "IDp3", "Name"],
        ["enum", "Ecode", "IDp1", "IDp2", "IDp3", "bnum"],
        ["enum", "Ecode", "IDp1", "IDp2", "IDp3", "Name"],
        ["enum", "Ecode", "IDp1", "IDp2", "IDp3"],
        [""]
    ]

    for c in COND_list:
        main(c)
