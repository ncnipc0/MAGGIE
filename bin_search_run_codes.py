import os
import re


def set_target_number_in_file(filename, number):
    file_data = ""
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            # print(line,end="")
            if "CTLGRADSPEC " in line:
                index1 = line.index("AG ") + 3
                index2 = line.index(" (")
                line = line[:index1] + str(number) + line[index2:]
            file_data += line
    with open(filename, "w", encoding="utf-8") as f:
        f.write(file_data)


def run_smv(filename, number):
    print("execute smv code:", filename, "number:", number)
    set_target_number_in_file(filename, number)
    f = os.popen("./NuSMV " + filename)
    f.readline()
    f.readline()
    f.readline()
    f.readline()
    f.readline()
    try:
        s = f.readline()
        print(s, end="")
        if "true" in s:
            res = True
        else:
            res = False
    except:
        res = False
    print("finish", "Test value is too high" if res else "Test values are either too small or correct")
    return res


def bin_search_run_smv_code(file_name):
    left = 0
    right = None
    print("bin search begin：", file_name, "left:", left, "right", right)

    while right is None:
        test_number = left * 3 if left != 0 else 1
        res = run_smv(file_name, test_number)
        if res == False:
            left = test_number
            print("interval update：", left, right)
        else:
            right = test_number
            print("interval update：", left, right)

    while left < right:
        mid = left + (right - left) // 2
        res = run_smv(file_name, mid)
        if res is True:
            right = mid
        else:
            left = mid + 1
        print("left", left, "mid", mid, "right", right)
    print("res", right)
    return right


if __name__ == "__main__":
    path_number_res = dict()
    path_root = "../tmp/SMV_code_file/"
    file_name_list = os.listdir(path_root)
    sub_dir = []
    for name in file_name_list:
        if not os.path.isdir(path_root + name) and re.match(r'\d+', name) is None:
            continue
        sub_dir.append((re.match(r'\d+', name).group(0), path_root + name))

    total_num = 0
    attack_success_num = 0
    for queryId, dir in sub_dir:
        result = False
        total_num += 1
        complete_file_name_list = []
        smv_file_name_list = os.listdir(dir)
        for smv_file_name in smv_file_name_list:
            # print(smv_file_name)
            complete_file_name = dir + "/" + smv_file_name
            res = bin_search_run_smv_code(complete_file_name)
            if res > 0: result = True
            path_number_res[complete_file_name] = res
            print("res update", path_number_res)
        if result: attack_success_num += 1

    print("total_num：", total_num)
    print("successful_attack_num：", attack_success_num)
