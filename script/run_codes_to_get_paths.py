import os


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


COND_list = [
    ["enum", "Ecode"],
    ["enum", "SMS"],
    ["IDp1", "IDp2", "IDp3", "SMS"],
    ["Name", "SMS"],
    ["bnum", "SMS"],
    ["Name", "SMS", "IDp1", "IDp2", "IDp3"],
    ["IDp1", "IDp2", "IDp3", "enum", "Ecode"],
    ["IDp1", "SMS"],
    ["IDp1", "IDp2", "IDp3", "enum", "Ecode", "bnum"],
    ["IDp1", "IDp2", "IDp3", "bnum", "SMS"],
    ["Name", "SMS", "IDp1", "IDp2", "IDp3", "bnum"],
    ["enum", "Ecode", "IDp1", "IDp2", "IDp3"],
    ["enum", "Ecode", "IDp1", "IDp2", "IDp3", "Name"]
]
N = 0
total_len = 8
paths = 1000
for c in COND_list:
    N += 1
    COND = c
    output_file_name2 = "code" + str(N) + "-" + str(total_len) + "bit" + "".join(COND) + ".smv"
    set_target_number_in_file(output_file_name2, paths)
    os.popen("./../NuSMV " + output_file_name2 + ">> code" + str(N) + ".txt")
