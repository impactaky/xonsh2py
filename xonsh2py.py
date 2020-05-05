import subprocess
import re

def search_correspond_bracket(target, pos="("):
    level = 0
    for i, c in enumerate(target[pos:]):
        if c == '(':
            level += 1
        elif c == ')':
            level -= 1
            if level == 0:
                return i+pos

def get_min(string, start_pos=0):
    pos = {
        ('shell_pipe', 2): string[start_pos:].find('$('),
        ('python', 2): string[start_pos:].find('@('),
        ('shell_pipe', 3): string[start_pos:].find('@$('),
    }
    min_pos = len(string)
    min_key = ('', 0)
    for k, v in pos.items():
        if v < 0:
            continue
        if v <= min_pos:
            min_pos = v
            min_key = k
    return (start_pos+min_pos if min_key[0] else min_pos, min_key)

class SplitInfo():
    def __init__(self, prev_end, start, end, type_):
        self.prev_end = prev_end
        self.start = start
        self.end = end
        self.type_ = type_

def find_child(string):
    ret = []
    start_pos = 0
    while 1:
        min_pos, min_key = get_min(string, start_pos)
        if min_pos == len(string):
            break
        end_pos = search_correspond_bracket(string, min_pos) if min_key[1] else len(string)
        ret.append(SplitInfo(min_pos, min_pos+min_key[1], end_pos, min_key[0]))
        start_pos = end_pos
    return ret

def convert(string, type=''):
    if not type:
        target = string.split()
        if '=' in target[:2]:
            type = 'python'
        elif re.match(string, '^[./]'):
            type = 'shell'
        elif subprocess.run(['which', target[0]], stdout=subprocess.DEVNULL).returncode == 0:
            type = 'shell'
        else :
            type = 'python'
    # print("parse ({}):".format(type), string)
    children = find_child(string)
    ret = ''
    pos = 0
    if type == 'python':
        for split_info in children:
            ret += string[pos:split_info.prev_end]
            ret += convert(string[split_info.start:split_info.end], split_info.type_)
            pos = split_info.end+1
        ret += string[pos:]
    else:
        if type == 'shell_pipe':
            ret += 'subprocess.check_output("'
        elif type == 'shell' :
            ret += 'subprocess.call("'
        if children:
            for split_info in children:
                ret += string[pos:split_info.prev_end]
                ret += '{}'
                pos = split_info.end+1
            ret += '".format('
            for i, split_info in enumerate(children):
                if i:
                    ret += ', '
                ret += convert(string[split_info.start:split_info.end], split_info.type_)
            ret += ')'
        else:
            ret += string + '"'
        ret += ', shell=True)'
        if type == 'shell_pipe':
            ret += '.decode()'
    # print('->', ret)
    return ret
