import sys

import matplotlib.pyplot as plt
from datetime import datetime
import time as tm
import numpy as np


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


class GcUrgencyEvent(object):
    def __init__(self, time, urgency):
        self.time = time
        self.urgency = urgency

    def __str__(self):
        return "time：%s\t urgency：%s" % (self.time, self.urgency)


class RequestEvent(object):
    def __init__(self, time):
        self.time = time


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
            elif "gc_urgency" in line:
                time = "2023-" + line.split(" ")[0] + " " + line.split(" ")[1]
                datetime_obj = datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f")
                timestamp = datetime_obj.timestamp()
                numberStr = line.split("gc_urgency")[1].strip().split(" ")[0]
                urgency_number = 0
                try:
                    urgency_number = float(numberStr)
                except ValueError:
                    print(f"Cannot convert '{numberStr}' to an float.")
                urgency = urgency_number
                parsed_data.append(GcUrgencyEvent(timestamp, urgency))
            elif "CheckGCForNative requested" in line:
                time = "2023-" + line.split(" ")[0] + " " + line.split(" ")[1]
                datetime_obj = datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f")
                timestamp = datetime_obj.timestamp()
                parsed_data.append(RequestEvent(timestamp))
            elif "wm_on_resume_called" in line and "com.miui.home" in line:
                time = "2023-" + line.split(" ")[0] + " " + line.split(" ")[1]
                datetime_obj = datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f")
                timestamp = datetime_obj.timestamp()
                parsed_data.append(LifeEvent(timestamp, "wm_on_resume_called"))
            elif "wm_on_paused_called" in line and "com.miui.home" in line:
                time = "2023-" + line.split(" ")[0] + " " + line.split(" ")[1]
                datetime_obj = datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f")
                timestamp = datetime_obj.timestamp()
                parsed_data.append(LifeEvent(timestamp, "wm_on_paused_called"))
            elif "com.miui.home: NativeAlloc concurrent copying" in line:
                time = "2023-" + line.split(" ")[0] + " " + line.split(" ")[1]
                datetime_obj = datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f")
                timestamp = datetime_obj.timestamp()
                parsed_data.append(GcEvent(timestamp, "NativeAlloc"))
            elif "com.miui.home: Explicit concurrent copying GC" in line:
                time = "2023-" + line.split(" ")[0] + " " + line.split(" ")[1]
                datetime_obj = datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f")
                timestamp = datetime_obj.timestamp()
                parsed_data.append(GcEvent(timestamp, "Explicit"))
    return parsed_data


def drawFigure(file_path):
    global lineNativeAllocGc
    plt.figure(file_path)
    ax1 = plt.subplot()
    parsed_data = parseDataFromFile(file_path)
    time = []
    timeLabel = []
    minTime = sys.maxsize
    maxTime = -1
    checkGCCount = 0
    for record in parsed_data:
        time.append(record.time)
        formatted_time = tm.strftime(time_format, tm.localtime(record.time * 1000))
        timeLabel.append(formatted_time)
        if record.time < minTime:
            minTime = record.time
        if record.time > maxTime:
            maxTime = record.time
    x = []
    y = []
    y_curNative = []
    maxY = 0.0
    for record in parsed_data:
        if isinstance(record, CheckGCEvent):
            checkGCCount = checkGCCount + 1
            x.append(record.time - minTime)
            y.append(record.javaAlloc)
            y_curNative.append(record.currentNativeByte())
            curBytes = record.currentNativeByte()
            if curBytes > maxY:
                maxY = curBytes
    lineJava, = ax1.plot(x, y)
    lineNative, = ax1.plot(x, y_curNative, linewidth=0.5, color='green')

    yCurNativeMaxIndex = np.argmax(y_curNative)
    ax1.scatter(x[yCurNativeMaxIndex], y_curNative[yCurNativeMaxIndex], color='green')
    ax1.annotate(
        f'max:{y_curNative[yCurNativeMaxIndex]:.0f}M',
        xy=(x[yCurNativeMaxIndex], y_curNative[yCurNativeMaxIndex]),
        xytext=(x[yCurNativeMaxIndex], y_curNative[yCurNativeMaxIndex]), color='green')

    yCurNativeMinIndex = np.argmin(y_curNative)
    ax1.scatter(x[yCurNativeMinIndex], y_curNative[yCurNativeMinIndex], color='green')
    ax1.annotate(
        f'min:{y_curNative[yCurNativeMinIndex]:.0f}M',
        xy=(x[yCurNativeMinIndex], y_curNative[yCurNativeMinIndex]),
        xytext=(x[yCurNativeMinIndex], y_curNative[yCurNativeMinIndex]), color='green')

    x1 = []
    y1 = []
    minUrgency = sys.maxsize
    maxUrgency = 0.0
    urgencyCount = 0
    for record in parsed_data:
        if isinstance(record, GcUrgencyEvent):
            x1.append(record.time - minTime)
            y1.append(record.urgency)
            if record.urgency >= 1.0:
                urgencyCount = urgencyCount + 1
            if record.urgency < minUrgency:
                minUrgency = record.urgency
            elif record.urgency > maxUrgency:
                maxUrgency = record.urgency
    ax2 = ax1.twinx()
    ax2.plot(x1, y1, color='blue', linestyle='dotted', marker='.', linewidth=0.5)

    requestCount = 0
    for record in parsed_data:
        if isinstance(record, RequestEvent):
            requestCount = requestCount + 1

    # plt.xticks(time, timeLabel, rotation=90)
    x2 = []
    y2 = []
    lifeCount = 0
    for record in parsed_data:
        if isinstance(record, LifeEvent):
            x2.clear()
            y2.clear()
            x2.append(record.time - minTime)
            y2.append(-20)
            x2.append(record.time - minTime)
            y2.append(maxY + 20)
            lifeCount = lifeCount + 1
            if "wm_on_resume_called" in record.event:
                ax1.plot(x2, y2, linestyle='dotted', color='r')
            else:
                ax1.plot(x2, y2, linestyle='dotted', color='b')
    x3 = []
    y3 = []
    gcCount = 0
    for record in parsed_data:
        if isinstance(record, GcEvent):
            x3.clear()
            y3.clear()
            x3.append(record.time - minTime)
            y3.append(0)
            x3.append(record.time - minTime)
            y3.append(maxY)
            gcCount = gcCount + 1
            if "NativeAlloc" in record.event:
                lineNativeAllocGc, = ax1.plot(x3, y3, color='r', linewidth=2)
            else:
                ax1.plot(x3, y3, color='b', linewidth=2)
    yCurNativeAverage = np.average(y_curNative)
    yCurJavaAverage = np.average(y)
    timeElapse = maxTime - minTime
    info = f'Native avg:{yCurNativeAverage:.1f}M  Java avg:{yCurJavaAverage:.1f}M CheckGC:{checkGCCount:.0f}' \
           f'\nGc:{gcCount}  request:{requestCount} urgency:{urgencyCount} LifeEvent:{lifeCount / 2}  Time:{timeElapse:.1f}s'
    ax1.text(x[0], y_curNative[yCurNativeMaxIndex] + 40, info, fontdict={'size': 12, 'color': 'red'})
    ax1.legend(
        [lineNative, lineJava, lineNativeAllocGc],
        ["native", "java", "NativeAllocGc"],
        bbox_to_anchor=(1, 1), loc=1, borderaxespad=0)


if __name__ == '__main__':
    # drawFigure('t/log.txt')
    # drawFigure('t/log2.txt')
    # drawFigure('u/log2.txt')
    drawFigure('u/log3.txt')
    plt.show()
