import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from datetime import datetime
import time as tm
import numpy as np
from scipy.interpolate import interp1d


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


class GcEvent(object):
    def __init__(self, time, event):
        self.time = time
        self.event = event

    def __str__(self):
        return "time：%s\t event：%s" % (self.time, self.event)


MB = 1024 * 1024

GetBytesAllocated = "GetBytesAllocated:"
old_native_bytes = "old_native_bytes:"
new_native_bytes = "new_native_bytes:"
time_format = "%Y-%m-%d %H:%M:%S.%f"


def parseDataFromFile(file_path):
    parsed_data = []
    with open(file_path, 'r') as file:
        for line in file:
            if GetBytesAllocated in line:
                time = "2023-" + line.split(" ")[0] + " " + line.split(" ")[1]
                datetime_obj = datetime.strptime(time, time_format)
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
            if "com.miui.home: NativeAlloc concurrent copying" in line:
                time = "2023-" + line.split(" ")[0] + " " + line.split(" ")[1]
                datetime_obj = datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f")
                timestamp = datetime_obj.timestamp()
                parsed_data.append(GcEvent(timestamp, "NativeAlloc"))
            if "com.miui.home: Explicit concurrent copying GC" in line:
                time = "2023-" + line.split(" ")[0] + " " + line.split(" ")[1]
                datetime_obj = datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f")
                timestamp = datetime_obj.timestamp()
                parsed_data.append(GcEvent(timestamp, "Explicit"))
    return parsed_data


def drawFigure(file_path):
    plt.figure(file_path)
    print("plt.figure")
    parsed_data = parseDataFromFile(file_path)
    time = []
    timeLabel = []
    for record in parsed_data:
        time.append(record.time)
        formatted_time = tm.strftime(time_format, tm.localtime(record.time * 1000))
        timeLabel.append(formatted_time)
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
    plt.plot(x, y_curNative, linewidth=0.5)
    yCurNativeMaxIndex = np.argmax(y_curNative)
    plt.scatter(x[yCurNativeMaxIndex], y_curNative[yCurNativeMaxIndex], color='red')
    plt.annotate(
        f'max:{y_curNative[yCurNativeMaxIndex]:.0f}M',
        xy=(x[yCurNativeMaxIndex], y_curNative[yCurNativeMaxIndex]),
        xytext=(x[yCurNativeMaxIndex], y_curNative[yCurNativeMaxIndex]))
    yCurNativeMinIndex = np.argmin(y_curNative)
    plt.scatter(x[yCurNativeMinIndex], y_curNative[yCurNativeMinIndex], color='red')
    plt.annotate(
        f'min:{y_curNative[yCurNativeMinIndex]:.0f}M',
        xy=(x[yCurNativeMinIndex], y_curNative[yCurNativeMinIndex]),
        xytext=(x[yCurNativeMinIndex], y_curNative[yCurNativeMinIndex]))
    # plt.xticks(time, timeLabel, rotation=90)
    x2 = []
    y2 = []
    lifeCount = 0
    for record in parsed_data:
        if isinstance(record, LifeEvent):
            x2.clear()
            y2.clear()
            x2.append(record.time)
            y2.append(-20)
            x2.append(record.time)
            y2.append(maxY + 20)
            lifeCount = lifeCount + 1
            if "wm_on_resume_called" in record.event:
                plt.plot(x2, y2, linestyle='dotted', color='r')
            else:
                plt.plot(x2, y2, linestyle='dotted', color='b')
    x3 = []
    y3 = []
    gcCount = 0
    for record in parsed_data:
        if isinstance(record, GcEvent):
            x3.clear()
            y3.clear()
            x3.append(record.time)
            y3.append(0)
            x3.append(record.time)
            y3.append(maxY)
            gcCount = gcCount + 1
            if "NativeAlloc" in record.event:
                plt.plot(x3, y3, color='r', linewidth=2)
            else:
                plt.plot(x3, y3, color='b', linewidth=2)
    yCurNativeAverage = np.average(y_curNative)
    maxTime = np.max(x)
    minTime = np.min(x)
    timeElapse = maxTime - minTime
    info = f'Native avg:{yCurNativeAverage:.1f}M  GcCount:{gcCount}  LifeCount:{lifeCount / 2}  Time:{timeElapse:.1f}s'
    plt.text(x[0], y_curNative[yCurNativeMaxIndex] + 60, info, fontdict={'size': 12, 'color': 'red'})


if __name__ == '__main__':
    file_path = 't/log.txt'
    drawFigure(file_path)
    file_path = 'u/log2.txt'
    drawFigure(file_path)
    plt.show()
