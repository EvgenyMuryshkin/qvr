import os

def uptime():
    return float(os.popen("awk '{print $1}' /proc/uptime").readline())