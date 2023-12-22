import sys

import matplotlib.pyplot as plt
from datetime import datetime
import time as tm
import numpy as np


class CheckGCEvent(object):
    def __init__(self, time, old_native_bytes, new_native_bytes, java_alloc, java_gc_start_bytes, adj_start_bytes):
        self.time = time
        self.oldNativeBytes = old_native_bytes
        self.newNativeBytes = new_native_bytes
        self.javaAlloc = java_alloc
        self.javaGcStart = java_gc_start_bytes
        self.adjStartBytes = adj_start_bytes

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


class GetTaskShapShotEvent(object):
    def __init__(self, time):
        self.time = time


class CreateTaskEvent(object):
    def __init__(self, time):
        self.time = time


class GetTaskEvent2(object):
    def __init__(self, time):
        self.time = time


class BackgroundEvent(object):
    def __init__(self, time):
        self.time = time


MB = 1024 * 1024

GetBytesAllocated = "GetBytesAllocated:"
old_native_bytes = "old_native_bytes:"
new_native_bytes_str = "new_native_bytes:"
java_gc_start_bytes_str = "java_gc_start_bytes:"
adj_start_bytes_str = "adj_start_bytes:"
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

                numberStr = line.split(new_native_bytes_str)[1].strip().split(" ")[0]
                integer_number = 0
                try:
                    integer_number = int(numberStr) / MB
                except ValueError:
                    print(f"Cannot convert '{numberStr}' to an integer.")
                newNativeBytes = integer_number

                numberStr = line.split(java_gc_start_bytes_str)[1].strip().split(" ")[0]
                integer_number = 0
                try:
                    integer_number = int(numberStr) / MB
                except ValueError:
                    print(f"Cannot convert '{numberStr}' to an integer.")
                java_gc_start_bytes = integer_number

                numberStr = line.split(adj_start_bytes_str)[1].strip().split(" ")[0]
                integer_number = 0
                try:
                    integer_number = int(numberStr) / MB
                except ValueError:
                    print(f"Cannot convert '{numberStr}' to an integer.")
                adj_start_bytes = integer_number

                parsed_data.append(
                    CheckGCEvent(
                        timestamp, oldNativeBytes, newNativeBytes, javaAlloc, java_gc_start_bytes, adj_start_bytes
                    )
                )
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
            elif "getTaskSnapshotInstance" in line:
                time = "2023-" + line.split(" ")[0] + " " + line.split(" ")[1]
                datetime_obj = datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f")
                timestamp = datetime_obj.timestamp()
                parsed_data.append(GetTaskShapShotEvent(timestamp))
            elif "createTaskSnapshot" in line:
                time = "2023-" + line.split(" ")[0] + " " + line.split(" ")[1]
                datetime_obj = datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f")
                timestamp = datetime_obj.timestamp()
                parsed_data.append(CreateTaskEvent(timestamp))
            elif "getTaskSnapshot:" in line:
                time = "2023-" + line.split(" ")[0] + " " + line.split(" ")[1]
                datetime_obj = datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f")
                timestamp = datetime_obj.timestamp()
                parsed_data.append(GetTaskEvent2(timestamp))
            elif "onTaskStackChangedBackground" in line:
                time = "2023-" + line.split(" ")[0] + " " + line.split(" ")[1]
                datetime_obj = datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f")
                timestamp = datetime_obj.timestamp()
                parsed_data.append(BackgroundEvent(timestamp))
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
    global lineResumeEvent
    global linePauseEvent
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
    y_newNative = []
    y_Adj = []
    maxY = 0.0
    for record in parsed_data:
        if isinstance(record, CheckGCEvent):
            checkGCCount = checkGCCount + 1
            x.append(record.time - minTime)
            y.append(record.javaAlloc)
            y_curNative.append(record.currentNativeByte())
            y_newNative.append(record.newNativeBytes)
            y_Adj.append(record.adjStartBytes)
            curBytes = record.currentNativeByte()
            if curBytes > maxY:
                maxY = curBytes
    lineJava, = ax1.plot(x, y)
    lineAdj, = ax1.plot(x, y_Adj)
    lineNewNative, = ax1.plot(x, y_newNative)
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
                lineResumeEvent, = ax1.plot(x2, y2, linestyle='dotted', color='r')
            else:
                linePauseEvent, = ax1.plot(x2, y2, linestyle='dotted', color='b')
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

    getTaskCount = 0
    getTaskCount2 = 0
    createTaskCount = 0
    backCount = 0
    for record in parsed_data:
        if isinstance(record, GetTaskShapShotEvent):
            getTaskCount = getTaskCount + 1
        elif isinstance(record, GetTaskEvent2):
            getTaskCount2 = getTaskCount2 + 1
        elif isinstance(record, BackgroundEvent):
            backCount = backCount + 1
        elif isinstance(record, CreateTaskEvent):
            createTaskCount = createTaskCount + 1

    yCurNativeAverage = np.average(y_curNative)
    yNewNativeAverage = np.average(y_newNative)
    yCurAdjAverage = np.average(y_Adj)
    yCurJavaAverage = np.average(y)
    timeElapse = maxTime - minTime
    info = f'Native :{yCurNativeAverage:.1f}M  newNative :{yNewNativeAverage:.1f}M Java :{yCurJavaAverage:.1f}M Adj :{yCurAdjAverage:.1f}M CheckGC:{checkGCCount:.0f}' \
           f'\nGc:{gcCount}  request:{requestCount} urgency:{urgencyCount} LifeEvent:{lifeCount / 2}  getTask:{getTaskCount:.1f} getTaskCount2:{getTaskCount2:.1f} createTask:{createTaskCount:.1f} back:{backCount:.1f}  Time:{timeElapse:.1f}s'
    ax1.text(x[0], y_curNative[yCurNativeMaxIndex] + 40, info, fontdict={'size': 12, 'color': 'red'})
    # ax1.legend(
    #     [lineNative, lineNewNative, lineAdj, lineJava, lineNativeAllocGc, lineResumeEvent, linePauseEvent],
    #     ["native", "NewNative", "adjStart", "java", "NativeAllocGc", "home resume", "home pause"],
    #     bbox_to_anchor=(1, 1), loc=1, borderaxespad=0)
    plt.grid()


if __name__ == '__main__':
    # drawFigure('t/log.txt')
    # drawFigure('t/log2.txt')
    # drawFigure('u/log2.txt')
    # drawFigure('u/log_16.txt')
    # drawFigure('t/log_16.txt')
    # drawFigure('u/log_16_8.txt')
    # drawFigure('t/log_16_8.txt')
    # drawFigure('t_uapk/log_16_1.txt')
    # drawFigure('t_uapk/log_16_2.txt')
    # drawFigure('t_uapk/log_16_3.txt')
    # drawFigure('t_uapk/log_16_4.txt')
    # drawFigure('t_uapk/log_16_5.txt')
    # drawFigure('u_tapk/log_16_1.txt')
    # drawFigure('u_tapk/log_16_2.txt')
    # drawFigure('u_tapk/log_16_3.txt')
    # drawFigure('u/log_16_1_ex.txt')
    # drawFigure('u/log_16_2_ext.txt')
    # drawFigure('u/log_16_3_ext.txt')
    # drawFigure('u/log_16_4_ext.txt')
    # drawFigure('u/log_16_5_ext.txt')

    # drawFigure('t_uapk/log_16_1_ext.txt')
    # drawFigure('t_uapk/log_16_2_ext.txt')
    # drawFigure('t_uapk/log_16_3_ext.txt')
    # drawFigure('t_uapk/log_16_4_ext.txt')
    # drawFigure('t_uapk/log_16_5_ext.txt')
    # drawFigure('u_uapk/log_16_1.txt')
    # drawFigure('u_uapk/log_16_2.txt')
    # drawFigure('u_uapk/log_16_3.txt')
    # drawFigure('u_uapk/log_16_4.txt')
    # drawFigure('u_uapk/log_16_5.txt')

    # drawFigure('u_tapk/log_16_1_ext.txt')
    # drawFigure('u_tapk/log_16_2_ext.txt')
    # drawFigure('u_tapk/log_16_3_ext.txt')
    # drawFigure('u_tapk/log_16_4_ext.txt')
    # drawFigure('u_tapk/log_16_5_ext.txt')
    # drawFigure('t_tapk/log_16_1.txt')
    # drawFigure('t_tapk/log_16_2.txt')
    # drawFigure('t_tapk/log_16_3.txt')
    # drawFigure('t_tapk/log_16_4.txt')
    # drawFigure('t_tapk/log_16_5.txt')
    # drawFigure('u_uapk/log_16_test4.txt')
    # drawFigure('test8.txt')
    # drawFigure('test7.txt')
    # drawFigure('test9.txt')
    # drawFigure('test19.txt')
    # drawFigure('test20.txt')
    # drawFigure('test21.txt')
    # drawFigure('test23.txt')
    # drawFigure('test25.txt')
    # drawFigure('test26.txt')
    # drawFigure('test_T.txt')
    # drawFigure('t/test_16_1_e.txt')
    # drawFigure('t/test_16_2_e.txt')
    # drawFigure('t/test_16_3_e.txt')
    # drawFigure('u/test_16_1_e.txt')
    # drawFigure('u/test_16_2_e.txt')
    # drawFigure('u/test_16_3_e.txt')
    # drawFigure('u/test_16_4_e.txt')
    # drawFigure('u/test_16_5_e.txt')
    # drawFigure('test6.txt')
    # drawFigure('test2.txt')
    # drawFigure('test3.txt')
    # drawFigure('test4.txt')
    # drawFigure('test5.txt')
    # drawFigure('test_U_1.txt')
    # drawFigure('test_U_2.txt')
    # drawFigure('test_U_3.txt')
    # drawFigure('test_U_4.txt')
    # drawFigure('test_U_5.txt')
    # drawFigure('test_U_1_e.txt')
    # drawFigure('test_U_2_e.txt')
    # drawFigure('test_U_3_e.txt')
    # drawFigure('test_U_4_e.txt')
    # drawFigure('test_U_5_e.txt')
    # drawFigure('t/test3.txt')
    # drawFigure('u/test2.txt')
    # drawFigure('u/test3.txt')
    # drawFigure('u/test4.txt')
    # drawFigure('u/test5.txt')
    # drawFigure('t_tapk/test_16_1.txt')
    # drawFigure('t_tapk/test_16_2.txt')
    # drawFigure('t_tapk/test_16_3.txt')
    # drawFigure('t_tapk/test_16_4.txt')
    # drawFigure('t_tapk/test_16_5.txt')
    drawFigure('u_new/test1.txt')
    drawFigure('u_new/test2.txt')
    drawFigure('u_new/test3.txt')
    drawFigure('u_new/test4.txt')
    drawFigure('u_new/test5.txt')

    # drawFigure('u_new/test1_e.txt')
    # drawFigure('u_new/test2_e.txt')
    # drawFigure('u_new/test3_e.txt')
    # drawFigure('u_new/test4_e.txt')
    # drawFigure('u_new/test5_e.txt')
    plt.show()
