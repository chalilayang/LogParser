import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from datetime import datetime


# 将文本形式的时间转换为datetime对象
# datetime_obj = datetime.strptime(text_time, "%m-%d %H:%M:%S")

class CheckGCEvent(object):
    def __init__(self, time, current_native):
        self.time = time  # 实例属性
        self.currentNative = current_native  # 实例属性

    def __str__(self):
        return "time：%s\t currentNative：%s" % (self.time, self.currentNative)


class LifeEvent(object):
    def __init__(self, time, event):
        self.time = time  # 实例属性
        self.event = event  # 实例属性

    def __str__(self):
        return "time：%s\t event：%s" % (self.time, self.event)


MB = 1024 * 1024


def parse_numbers_after_keyword(file_path, keyword):
    parsed_data = []
    with open(file_path, 'r') as file:
        for line in file:
            if keyword in line:
                time = "2023-" + line.split(" ")[0] + " " + line.split(" ")[1]
                datetime_obj = datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f")
                timestamp = datetime_obj.timestamp()
                numberStr = line.split(keyword)[1].strip().split(" ")[0]
                integer_number = 0
                try:
                    integer_number = int(numberStr) / MB
                except ValueError:
                    print(f"Cannot convert '{numberStr}' to an integer.")
                parsed_data.append(CheckGCEvent(timestamp, integer_number))
            if "wm_on_resume_called" in line and "com.miui.home" in line:
                time = "2023-" + line.split(" ")[0] + " " + line.split(" ")[1]
                datetime_obj = datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f")
                timestamp = datetime_obj.timestamp()
                parsed_data.append(LifeEvent(timestamp, "wm_on_resume_called"))
            if "wm_on_paused_called" in line and "com.miui.home" in line:
                time = "2023-" + line.split(" ")[0] + " " + line.split(" ")[1]
                datetime_obj = datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f")
                timestamp = datetime_obj.timestamp()
                parsed_data.append(LifeEvent(timestamp, "wm_on_paused_called"))
    return parsed_data


def parse_text_file(file_path):
    parsed_data = parse_numbers_after_keyword(file_path, "GetBytesAllocated:")
    x = []
    y = []
    maxY = 0
    for record in parsed_data:
        if isinstance(record, CheckGCEvent):
            x.append(record.time)
            y.append(record.currentNative)
            if record.currentNative > maxY:
                maxY = record.currentNative
    plt.plot(x, y)
    x2 = []
    y2 = []
    for record in parsed_data:
        if isinstance(record, LifeEvent):
            x2.clear()
            y2.clear()
            x2.append(record.time)
            y2.append(0)
            x2.append(record.time)
            y2.append(maxY)
            if "wm_on_resume_called" in record.event:
                plt.plot(x2, y2, linestyle='dotted', color='r')
            else:
                plt.plot(x2, y2, linestyle='dotted', color='b')
    plt.show()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    file_path = 'log.txt'  # 替换为你的文本文件路径
    parse_text_file(file_path)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
