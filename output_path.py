# This script is used to read/ Nusmv output named code [number]. txt in the SMV_code_file directory, and format the attack path displayed in the output codeXX.txt
from copy import deepcopy


def generate_path(l_t, end_state, a: str):
    string_list = a.split("\n")
    def get_end_state(end_state):
        res = None
        if isinstance(end_state, str):
            return end_state
        else:
            for line in string_list:
                if " " + str(end_state) + "." in line and "State:" in line:
                    res = line[len("-> State: "):].split(" ")[0]
        assert isinstance(res, str)
        return res

    end_state = get_end_state(end_state)
    app_list = ""
    res = {}
    knowledgements = ""
    for line in string_list:
        length1 = len("-> State: ")
        length2 = len("knowledgements = ")
        length3 = len("app_list = ")
        if line[:length1] == "-> State: ":
            state = line[length1:].split(" ")[0]
            res[state] = {}
        if line[:length2] == "knowledgements = ":
            knowledgements = line[length2 + 4:]
            res[state]["app_list"] = app_list
            res[state]["knowledgements"] = knowledgements
            res[state]["depth"] = int(str(state).split(".")[1])
        if line[:length3] == "app_list = ":
            app_list = line[length3:]
            res[state]["app_list"] = app_list
            res[state]["knowledgements"] = knowledgements
            res[state]["depth"] = int(str(state).split(".")[1])

    res = [i for i in res.items()]
    res.sort(key=lambda x: float(x[0]))
    # print(res)

    index = 0
    for index_tmp, i in enumerate(res):
        if i[0] == end_state:
            index = index_tmp
    depth = int(str(end_state).split(".")[1]) + 1
    path = []
    for i in range(index, -1, -1):
        if res[i][1]["depth"] < depth:
            depth -= 1
            path.append(res[i])
    path.reverse()
    ss = ""
    for i in range(1, len(path)):
        if i % 2 == 0:
            ss += path[i][1]["knowledgements"] + " "
        else:
            ss += path[i][1]["app_list"] + " "
    ss = ss[:-1]

    length = len(l_t)
    input_list = []

    tmp = ss.split(" ")
    for i in range(0, len(tmp), 2):
        input_list.append((tmp[i], int(tmp[i + 1])))

    res = []
    for name, value in input_list:
        state = bin(value)[2:]
        state = "0" * (length - len(state)) + state
        tl = []

        for index, c in enumerate(state):
            if c == '1':
                tl.append(l_t[index])
        res.append(name + " {" + ",".join(tl) + "}")

    return res


def get_way_string(way: str, i, dir_name):
    import os
    way = way[:way.index(" {")]

    file_name_list = os.listdir(dir_name)
    file_name = None

    for fn in file_name_list:
        if "code" + str(i) + "-" in fn and "out" not in fn:
            file_name = fn

    with open(dir_name + file_name, "r") as f:
        for line in f.readlines():
            if "-- LoginWay" in line and " " + way + " " in line:
                return line[line.index("{'") + 2:line.index("',")]
    # print("Err",way,i,dir_name)
    exit(1)


if __name__ == "__main__":
    l_t = [('SMS', 1), ('Name', 1), ('IDp1', 1), ('IDp2', 1), ('IDp3', 1), ('bnum', 1), ('enum', 1), ('Ecode', 1)]
    l_t = list(list(zip(*l_t))[0])

    for i in range(1, 12):
        file_name = "./SMV_code_file/code" + str(i) + ".txt"
        with open(file_name, "r") as f:
            file_data = f.read()
            res_list = []
            for end in range(2, 300):
                res_list.append(generate_path(l_t, end, file_data))
            # print(res_list)
            # print("res_list:----------")
            end = 2
            out_str = ""
            for res in res_list:
                res2 = deepcopy(res)
                # print("-->".join(res))
                out_str += "end:" + str(end) + "\n"
                end += 1

                out_str += "-->".join(res) + "\n"
                for index in range(len(res2)):
                    if "LoginWay" in res2[index]:
                        ##print("LoginWay:",res2[index])
                        res2[index] = get_way_string(res2[index], i, "../tmp/SMV_code_file/")

                    if "{" in res2[index]:
                        res2[index] = res2[index][:res2[index].index("{")]
                    res2[index] = res2[index].replace(" ", "")
                    if "ResetBy" in res[index]:
                        res2[index] += "(RL)"
                    else:
                        res2[index] += "(DL)"

                out_str += ",".join(res2) + "\n"

            with open("./SMV_code_file/code" + str(i) + "-out.txt", "w") as f2:
                f2.write(out_str)
