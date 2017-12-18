from os import system
from pwd import getpwuid

tmp_name    = 'tmp'
status_name = 'status'

tmp_path    = './' + tmp_name
status_path = tmp_name + '/' + status_name

read_keys   = ['Name', 'State', 'Pid', 'Uid', 'VmSize'] # keys in reading order
line_keys   = ['Pid', 'Name', 'Uid', 'State', 'VmSize'] # keys in printing order

header  = {'Name': 'NAME', 'State': 'STATE', 'Pid': 'PID', 'Uid': 'USER', 'VmSize': 'VIRT'}
widths  = {'Name': 20, 'State': 5, 'Pid': 3, 'Uid': 3, 'VmSize': 10}

def just(value, width):
    return str(value)[:width].rjust(width)

def line(values):
    line = ''
    for key in line_keys:
        line += ' ' + just(values[key], widths[key])
    return line

class Process:

    def __init__(self, status):
        self.values = {}
        for key in read_keys:
            for line in status.lines[status.index:]:
                tokens = line.split()
                if tokens[0] == key + ':':
                    if key == 'State':
                        self.values[key] = tokens[2][1:-1]
                    elif key == 'Uid':
                        self.values[key] = getpwuid(int(tokens[1]))[0]
                    elif key == 'VmSize':
                        self.values[key] = tokens[1] + ' ' + tokens[2]
                    else:
                        self.values[key] = tokens[1]
                    break
                status.index += 1

    def __str__(self):
        return line(self.values)

    def empty(self):
        return len(self.values) == 0

class Status:

    def __init__(self):
        self.index = 0
        self.lines = open(status_path, 'r').readlines()
        self.list = []
        while self.index < len(self.lines):
            process = Process(self)
            if not process.empty():
                self.list.append(process)

    def order(self):
        self.list = sorted(self.list, key = lambda p: int(p.values['Pid']))

    def width(self):
        for process in self.list:
            for key in read_keys:
                if widths[key] < len(process.values[key]):
                    widths[key] = len(process.values[key])

    def __str__(self):
        print(line(header))
        for process in self.list:
            print(process)
        return ''

def main():
    system('mkdir ' + tmp_name)
    system('cat /proc/*/status > ' + status_path + ' && clear')

    status = Status()
    status.order()
    status.width()
    print(status)

    system('rm -r ' + tmp_name)

if __name__ == '__main__':
    main()
