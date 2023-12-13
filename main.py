import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from datetime import datetime


class CheckGCEvent(object):
    def __init__(self, time, old_native_bytes, new_native_bytes, java_alloc):
        self.time = time
        self.oldNativeBytes = old_native_bytes
        self.newNativeBytes = new_native_bytes
        self.javaAlloc = java_alloc

    def currentNativeByte(self):
        return self.oldNativeBytes + self.newNativeBytes

    def __str__(self):
        return "time：%s\t currentNative：%s" % (self.time, self.currentNativeByte())


class LifeEvent(object):
    def __init__(self, time, event):
        self.time = time
        self.event = event

    def __str__(self):
        return "time：%s\t event：%s" % (self.time, self.event)


MB = 1024 * 1024

GetBytesAllocated = "GetBytesAllocated:"
old_native_bytes = "old_native_bytes:"
new_native_bytes = "new_native_bytes:"


def parse_numbers_after_keyword(file_path):
    parsed_data = []
    with open(file_path, 'r') as file:
        for line in file:
            if GetBytesAllocated in line:
                time = "2023-" + line.split(" ")[0] + " " + line.split(" ")[1]
                datetime_obj = datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f")
                timestamp = datetime_obj.timestamp()

                numberStr = line.split(GetBytesAllocated)[1].strip().split(" ")[0]
                integer_number = 0
                try:
                    integer_number = int(numberStr) / MB
                except ValueError:
                    print(f"Cannot convert '{numberStr}' to an integer.")
                javaAlloc = integer_number

                numberStr = line.split(old_native_bytes)[1].strip().split(" ")[0]
                integer_number = 0
                try:
                    integer_number = int(numberStr) / MB
                except ValueError:
                    print(f"Cannot convert '{numberStr}' to an integer.")
                oldNativeBytes = integer_number

                numberStr = line.split(new_native_bytes)[1].strip().split(" ")[0]
                integer_number = 0
                try:
                    integer_number = int(numberStr) / MB
                except ValueError:
                    print(f"Cannot convert '{numberStr}' to an integer.")
                newNativeBytes = integer_number

                parsed_data.append(CheckGCEvent(timestamp, oldNativeBytes, newNativeBytes, javaAlloc))
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
    parsed_data = parse_numbers_after_keyword(file_path)
    x = []
    y = []
    y_curNative = []
    maxY = 0.0
    for record in parsed_data:
        if isinstance(record, CheckGCEvent):
            x.append(record.time)
            y.append(record.javaAlloc)
            y_curNative.append(record.currentNativeByte())
            curBytes = record.currentNativeByte()
            if curBytes > maxY:
                maxY = curBytes
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


if __name__ == '__main__':
    file_path = 'log.txt'  # 替换为你的文本文件路径
    parse_text_file(file_path)
