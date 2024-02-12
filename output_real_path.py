import os
from copy import deepcopy


def get_way_string(way: str, i, dir_name):
    import os
    way = way[:way.index(" {")]
    file_name_list = os.listdir(dir_name)
    file_name = None
    for fn in file_name_list:
        if "code" + str(i) + "-8bit" in fn and "out" not in fn:
            file_name = fn
    with open(dir_name + file_name, "r") as f:
        for line in f.readlines():
            # print(line)
            if "-- LoginWay" in line and " " + way + " " in line:
                return line[line.index("{'") + 2:line.index("',")]
    print("Err", way, i, dir_name)
    exit(1)


def get_cond(dir_name, filename=None, file_index=None):
    if filename is None and file_index == None: exit(1)
    if filename is None:
        file_name_list = os.listdir(dir_name)

        for fn in file_name_list:
            if "code" + str(file_index) + "-8bit" in fn and "out" not in fn:
                filename = fn
    assert filename is not None
    res = dict()
    flag = False

    with open(dir_name + filename, "r") as f:
        for line in f.readlines():
            # print(line)
            if "next(knowledgements):=" in line:
                flag = True
                continue
            if flag and line.startswith("			app_list = "):
                index1 = line.find("&((")
                if index1 == -1: continue
                index0 = line.index("app_list = ")
                index0 += 11
                index3 = line.index("&0b8_") + 5
                index4 = index3 + 8
                res[line[index0:index1]] = int(line[index3:index4], 2)
            if "CTLGRADSPEC AG" in line:
                index = line.index("&0b8_") + 5
                real_target = line[index:index + 8]
                return res, real_target
    print("Err")
    exit(1)

def is_real_path(s: str, cond_dict, real_target, init_factor=0):
    tmp = s.split(" ")
    input_list = []
    for i in range(0, len(tmp), 2):
        input_list.append((tmp[i], int(tmp[i + 1])))

    real_get = []
    for i, tp in enumerate(input_list):
        if i == 0:

            real_get.append((tp[0], tp[1] & (~(1 << (7 - init_factor)))))
        else:
            real_get.append((tp[0], tp[1] ^ input_list[i - 1][1]))

    cond_and_real_get = []
    for tp in real_get:
        list1 = []
        for i in range(8):
            if (cond_dict[tp[0]] >> i) & 1 == 1:
                list1.append(7 - i)
        list2 = []
        for i in range(8):
            if (tp[1] >> i) & 1 == 1:
                list2.append(7 - i)

        cond_and_real_get.append((cond_dict[tp[0]], list1, tp[0], tp[1], list2))

    # build graph
    g = Graph(8)
    for index, tp in enumerate(cond_and_real_get):
        real_get = tp[4]
        for node1 in real_get:
            for tp in cond_and_real_get[index + 1:]:
                if node1 in tp[1]:  # PII_GOT in COND
                    for node2 in tp[4]: g.add_edge(node1, node2)

    # Traverse each operation, return false if any operation is meaningless
    for tp in cond_and_real_get:
        res_list = [g.is_reachable(node1, node2) for node2 in real_target for node1 in tp[4]]
        if not any(res_list):
            # print("False")
            return False

    return True


def generate_path(l_t, end_state, a: str, cond_dict, real_target):
    print("real_target", real_target)
    tmp = int(real_target, 2)
    real_target = []
    for i in range(8):
        if (tmp >> i) & 1 == 1:
            real_target.append(7 - i)
    print(real_target)
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
            # print("knowledgements-" + knowledgements, "app_list-" + app_list, "state-" + str(state))
            res[state]["app_list"] = app_list
            res[state]["knowledgements"] = knowledgements
            res[state]["depth"] = int(str(state).split(".")[1])
        if line[:length3] == "app_list = ":
            app_list = line[length3:]
            # print("knowledgements-" + knowledgements, "app_list-" + app_list, "state-" + str(state))
            res[state]["app_list"] = app_list
            res[state]["knowledgements"] = knowledgements
            res[state]["depth"] = int(str(state).split(".")[1])

    res = [i for i in res.items()]
    res.sort(key=lambda x: float(x[0]))

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
    i = ss
    length = len(l_t)
    input_list = []
    tmp = i.split(" ")
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

    if not is_real_path(ss, cond_dict, real_target):
        res = ["FAKE PATH {}"] + res

    return res


class Graph:
    def __init__(self, node_size):
        self.node_size = node_size
        self.edges = [set() for i in range(node_size)]
        self.record = [[None] * node_size for i in range(node_size)]

        for i in range(len(self.record)):
            self.edges[i].add(i)

    def add_edge(self, node1, node2):

        self.edges[node1].add(node2)
        self.record[node1][node2] = True

    def is_reachable(self, node1, node2, visited=None):
        if self.record[node1][node2] is not None:
            return self.record[node1][node2]
        if visited is None:
            visited = [False] * self.node_size

        visited[node1] = True  # Avoiding rings
        res = False
        for next_node in self.edges[node1]:
            if next_node == node2 or (visited[next_node] == False and self.is_reachable(next_node, node2, visited)):
                res = True
                break

        self.record[node1][node2] = res
        return self.record[node1][node2]


if __name__ == "__main__":
    MAX_END = 313  # Maximum End State
    MAX_FILE_INDEX = 1

    l_t = [('SMS', 1), ('bnum', 1), ('Name', 1), ('IDp1', 1), ('IDp2', 1), ('IDp3', 1), ('enum', 1), ('Ecode', 1)]
    l_t = list(list(zip(*l_t))[0])

    for i in range(1, MAX_FILE_INDEX + 1):
        SMV_code_dir = "./../SMV_code_file/"
        file_name = SMV_code_dir + "code" + str(i) + ".txt"
        cond_dict, real_target = get_cond(SMV_code_dir, file_index=i)

        with open(file_name, "r") as f:
            file_data = f.read()
            res_list = []
            for end in range(1, MAX_END):
                res_list.append(generate_path(l_t, end, file_data, cond_dict, real_target))

            out_str = ""
            fake = 0
            real = 0
            app = 0
            for res in res_list:
                if "FAKE" in res[0]:
                    fake += 1
                else:
                    real += 1
                    app += len(res)
                res2 = deepcopy(res)

                out_str += "-->".join(res) + "\n"
                for index in range(len(res2)):
                    if "LoginWay" in res2[index]:
                        res2[index] = get_way_string(res2[index], i, SMV_code_dir)
                    if "{" in res2[index]:
                        res2[index] = res2[index][:res2[index].index("{")]
                    res2[index] = res2[index].replace(" ", "")
                    if "ResetBy" in res[index]:
                        res2[index] += "(RL)"
                    else:
                        res2[index] += "(DL)"
                out_str += ",".join(res2) + "\n"

            out_str = "Fake path number:" + str(fake) + " Real:" + str(real) + "APP:" + str(app / real) + "\n" + out_str
            with open(SMV_code_dir + "code" + str(i) + "-realpath.txt", "w") as f2:
                f2.write(out_str)
