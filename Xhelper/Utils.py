import re
import time
import os
import config


def find_same_widget(widget, root_widget):
    if widget == root_widget:
        return root_widget

    for child in root_widget.children:
        result = find_same_widget(widget, child)
        if result is not None:
            return result

    return None


def calculate_operation_point(area, occupy_areas):
    x1, y1, x2, y2 = get_points(area)
    x_min = x2
    x_max = x1
    y_min = y2
    y_max = y1
    for j in range(len(occupy_areas)):
        bound = occupy_areas[j]
        x1_, y1_, x2_, y2_ = get_points(bound)
        x_min = x_min if x_min < x1_ else x1_
        y_min = y_min if y_min < y1_ else y1_
        x_max = x_max if x_max > x2_ else x2_
        y_max = y_max if y_max > y2_ else y2_

    if len(occupy_areas) == 0 or (
            len(occupy_areas) == 1 and x1 == x1_ and x2 == x2_ and y1 == y1_ and y2 == y2_):
        x0 = (x1 + x2) / 2
        y0 = (y1 + y2) / 2
    elif (x1 != x1_ or x2 != x2_) and (y1 != y1_ or y2 != y2_):
        x0 = (x1 + x1_) / 2 if x1_ != x1 else (x2 + x2_) / 2
        y0 = (y1 + y1_) / 2 if y1_ != y1 else (y2 + y2_) / 2
    else:
        x0 = x_min
        y0 = y_min
    return int(x0), int(y0)


def get_points(area):
    res = re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', area)
    x1 = int(res.group(1))
    y1 = int(res.group(2))
    x2 = int(res.group(3))
    y2 = int(res.group(4))
    return x1, y1, x2, y2


def get_auth_code(msg):
    res = re.search(r"(\d+)", msg)
    return res.group(0)


def reverse_dict(dict):
    result = {}
    for i in dict:
        if dict[i] in result:
            result[dict[i]].append(i)
        else:
            result[dict[i]] = [i]
    return result


def get_screen_size():
    result = os.popen('adb -s ' + config.serials[config.CONFIG['phone_no']] + ' shell wm size').read()
    size = result.split('Physical size: ')[1].split('\n')[0]
    width, height = size.split('x')
    return int(width), int(height)


def locate_screenshot_area(left, top, width, height):
    os.system('adb -s ' + config.serials[config.CONFIG['phone_no']] + ' shell input tap %s %s' % (left, top))
    os.system('adb -s ' + config.serials[config.CONFIG['phone_no']] + ' shell input swipe %s %s %s %s' % (
    left, top, left + width, top + height))


def take_screenshot(file_name):
    os.system('adb -s ' + config.serials[config.CONFIG['phone_no']] + ' shell screencap -p /sdcard/%s' % file_name)


def save_screenshot(file_name, save_path):
    os.system('adb -s ' + config.serials[config.CONFIG['phone_no']] + ' pull /sdcard/%s %s' % (file_name, save_path))


def take_screenshot_for_all_screen_and_save(dir):
    TimeName = time.strftime("%Y%m%d%H%M%S", time.localtime())
    path = dir + str(TimeName) + '.png'
    take_screenshot(str(TimeName))
    save_screenshot(str(TimeName), path)


def del_files(path_file):
    ls = os.listdir(path_file)
    for i in ls:
        f_path = os.path.join(path_file, i)
        if os.path.isdir(f_path):
            del_files(f_path)
        else:
            os.remove(f_path)


