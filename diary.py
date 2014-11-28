#!/usr/bin/env python3

import datetime

file_mode = 0o755
file_format = None
section_pattern = None
todo_pattern = None
todo_replacement = None
todo_empty = None
todo_checked = None

def read_config():
    import re
    import configparser
    import locale

    global file_mode
    global file_format
    global section_pattern
    global todo_pattern
    global todo_replacement
    global todo_empty
    global todo_checked

    config = configparser.ConfigParser(interpolation=None)
    if not config.read('diary.ini'):
        raise RuntimeError('can\'t find diary.ini in current directory')
    if not config.has_section('diary'):
        raise RuntimeError('diary section missing in config')

    locale_name = config['diary']['locale']
    if locale_name:
        locale.setlocale(locale.LC_ALL, locale_name)

    file_mode_str = config['diary']['file_mode']
    if file_mode_str:
        file_mode = int(file_mode_str, base=8)

    file_format = config['diary']['file_format']
    if not file_format:
        raise RuntimeError('file_format missing in config')

    section_pattern = re.compile(config['diary']['section_pattern'])
    if not 'name' in section_pattern.groupindex:
        raise RuntimeError('section_pattern needs a "name" group')

    todo_pattern = re.compile(config['diary']['todo_pattern'])
    if not 'name' in todo_pattern.groupindex:
        raise RuntimeError('todo_pattern needs a "name" group')
    if not 'state' in todo_pattern.groupindex:
        raise RuntimeError('todo_pattern needs a "state" group')

    todo_replacement = config['diary']['todo_replacement']
    todo_empty = config['diary']['todo_empty']
    if todo_empty == '':
        todo_empty = ' '
    todo_checked = config['diary']['todo_checked']

def read_diary_entry( stream ):
    for line in stream:
        if line[-1] == '\n':
            line = line[:-1] # remove newline
        match = section_pattern.search(line)
        if match:
            yield dict(type='section',
                       line=line,
                       match=match,
                       name=match.group('name'))
            continue
        match = todo_pattern.search(line)
        if match:
            state_char = match.group('state')
            state = None
            if state_char == todo_checked:
                state = True
            elif state_char == todo_empty:
                state = False

            yield dict(type='todo',
                       line=line,
                       match=match,
                       name=match.group('name'),
                       state=state)
            continue
        yield dict(type='line',
                   line=line)


def date_to_entry_file_name( date ):
    return date.strftime(file_format)

def entry_file_name_to_date( file_name ):
    try:
        return datetime.datetime.strptime(file_name, file_format)
    except ValueError:
        return None

def get_previous_entry_date( end_date ):
    import os.path
    max_days = 14
    for i in range(1, max_days+1): # limit the amount of days we can go back
        previous_date = end_date - datetime.timedelta(days=i)
        file_name = date_to_entry_file_name(previous_date)
        if os.path.isfile(file_name):
            return previous_date
    return None

def copy_entry( istream, ostream ):
    for token in read_diary_entry(istream):
        if token['type'] == 'section':
            ostream.write(token['line'])
            ostream.write('\n')
        elif token['type'] == 'todo':
            match = token['match']
            line = token['line']
            ostream.write(line[:match.start()])
            ostream.write(todo_replacement.format(name=token['name'],
                                                  state=todo_empty))
            ostream.write(line[match.end():])
            ostream.write('\n')

def create_new():
    import os
    import os.path

    today = datetime.date.today()
    file_name = date_to_entry_file_name(today)

    if not os.path.exists(file_name):
        file_dir = os.path.dirname(file_name)
        os.makedirs(file_dir, mode=file_mode, exist_ok=True)
        previous = get_previous_entry_date(today)
        if previous:
            previous_file_name = date_to_entry_file_name(previous)
            # TODO: Support file_mode here!
            with open(previous_file_name, 'r', encoding='UTF-8') as previous_file:
                with open(file_name, 'w', encoding='UTF-8') as file:
                    copy_entry(previous_file, file)

    return file_name

def edit_new():
    import os
    import subprocess

    file_name = create_new()
    editor = os.getenv('EDITOR', 'nano')
    subprocess.check_call([editor, file_name])

def print_usage():
    print('Usage: {} <command> <args>'.format(sys.argv[0]))
    print('Commands:')
    print('  help: Prints this text.')
    print('  create: Prepare new diary entry and print its file name.')
    print('  write: Opens todays diary entry with $EDITOR.')

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print_usage()
    else:
        command = sys.argv[1]
        args = sys.argv[2:]
        if command == 'help':
            print_usage()
        elif command == 'create':
            read_config()
            print(create_new())
        elif command == 'write':
            read_config()
            edit_new()
