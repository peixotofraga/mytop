import subprocess
from pwd import getpwuid

tmp_name    = 'tmp'
status_name = 'status'
time_name   = 'time'
etime_name  = 'etime'

tmp_path    = './' + tmp_name
status_path = tmp_name + '/' + status_name
time_path   = tmp_name + '/' + time_name
etime_path  = tmp_name + '/' + etime_name

commands    = ['filter', 'help', 'kill', 'sort', 'quit']

status_keys = ['name', 'state', 'pid', 'user', 'virt'] # keys in reading order
table_keys  = ['pid', 'name', 'user', 'state', 'time', 'etime', 'virt'] # keys in printing order

status_fields   = {'Name': 'name', 'State': 'state', 'Pid': 'pid', 'Uid': 'user', 'VmSize': 'virt'}
table_fields    = {'name': 'NAME', 'state': 'STATE', 'pid': 'PID', 'user': 'USER', 'virt': 'VIRT', 'etime': 'EXECTIME', 'time': 'CPUTIME'}

width_values    = {'name': 10, 'state': 5, 'pid': 3, 'user': 10, 'virt': 5, 'etime': 15, 'time': 15}

help    = ('\'filter\' + field + list of strings: show only the processes which have any of the strings in the respective field' + '\n'
        + '\'kill\' + field + list of strings: kill only the processes which have any of the strings in the respective field' + '\n'
        + '\'sort\' + list of fields: sort the processes by fields' + '\n' + '\n'
        + 'Available commands \t= ' + str(commands) + '\n'
        + 'Available fields \t= ' + str(table_keys) + '\n')

def breakLine(line):
    return list(map(lambda token: token.replace(':', ''), line.split()))

class Status:

    def __init__(self):
        self.index = 0
        self.lines = subprocess.check_output('cat /proc/*/status', shell = True, universal_newlines = True).split('\n')
        self.lines = list(map(lambda line: breakLine(line), self.lines[:-1]))
        self.list = []
        while self.index < len(self.lines):
            process = Process(self)

    def filter(self, key, list):
        list_aux = []
        if key in status_keys and len(list) > 0:
            for process in self.list:
                for string in list:
                    if process.filter(key, string):
                        list_aux.append(process)
                        break
        self.list = list_aux

    def kill(self):
        for process in self.list:
            subprocess.call('kill ' + process.values['pid'], shell = True)

    def sort(self, key_list):
        for key in key_list:
            if key in table_keys:
                if key == 'pid':
                    self.list = sorted(self.list, key = lambda p: int(p.values[key]))
                elif key == 'virt':
                    self.list = sorted(self.list, key = lambda p: int(p.values[key][:-3]))
                else:
                    self.list = sorted(self.list, key = lambda p: p.values[key])

    def width(self):
        for key in table_keys:
            width_values[key] = 0
        for process in self.list:
            for key in table_keys:
                if width_values[key] < len(process.values[key]):
                    width_values[key] = len(process.values[key])

    def __str__(self):
        if len(self.list) > 0:
            table = formatLine(table_fields) + '\n'
            for process in self.list:
                table += str(process) + '\n'
            return table
        else:
            return 'No process found' + '\n'

def justify(value, width):
    return str(value)[:width].rjust(width)

def formatLine(values):
    line = ''
    for key in table_keys:
        line += ' ' + justify(values[key], width_values[key])
    return line

class Process:

    def __init__(self, status):
        self.values = {}
        for line in status.lines[status.index:]:
            if line[0] in status_fields:
                key = status_fields[line[0]]
                if key in self.values:
                    break
                elif key == 'state':
                    value = line[2][1:-1]
                elif key == 'user':
                    value = getpwuid(int(line[1]))[0]
                elif key == 'virt':
                    value = line[1] + ' ' + line[2]
                else:
                    value = line[1]
                self.values[key] = value
            status.index += 1
        #self.values['time'] = str(subprocess.check_output('ps -p ' + self.values['pid'] + ' -o time=; exit 0', shell = True, stderr = subprocess.STDOUT).strip())[2:-1]
        #self.values['etime'] = str(subprocess.check_output('ps -p ' + self.values['pid'] + ' -o etime=; exit 0', shell = True, stderr = subprocess.STDOUT).strip())[2:-1]
        if len(self.values.values()) > 0:
            for key in table_keys:
                if key not in self.values:
                    if key == 'virt':
                        self.values[key] = '0 kB'
                    else:
                        self.values[key] = ''
            status.list.append(self)

    def filter(self, key, string):
        return self.values[key].find(string) >= 0

    def __str__(self):
        return formatLine(self.values)

def main():
    #subprocess.call('mkdir ' + tmp_name, shell = True)

    status = Status()
    status.sort(['pid'])
    status.width()
    print(status)

    while True:
        token = input('Type a command: ').split()

        status = Status()
        status.sort(['pid'])
        status.width()

        if token[0] == 'filter':
            status.filter(token[1], token[2:])
            print(status)
        elif token[0] == 'help':
            print(help)
        elif token[0] == 'kill':
            status.filter(token[1], token[2:])
            status.kill()
        elif token[0] == 'sort':
            status.sort(token[1:])
            print(status)
        elif token[0] == 'quit':
            break
        else:
            print(status)

    #subprocess.call('rm -r ' + tmp_name, shell = True)

if __name__ == '__main__':
    main()
