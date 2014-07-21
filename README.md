diary
=====

A diary for console cowboys/cowgirls, written in python 3.

Every time you run `./diary.py write` it creates a diary entry for  
the current date and opens it in your favorite editor.

Diary entries can have sections and todos:
You can use sections to break your diary entries into specific subjects,
so you can find them more easily later on.
The todo entries have a similar purpose:
They're meant to remind you to do something.

New diary entries are initialized with section headers
and todo entries of the previous diary entry.

I made this, because I wanted to live a more conscious life.
And I think writing diary entries daily or at least regulary helps a lot,
since you need to recapitulate what you did and felt that day.

May someone else find this useful. :)


## Configuration

First you need to create the configuration file.
Take your time here, since you don't want to change the values later on.
(Already created diary entries are not adapted automatically.)

The file should look like this:

    [diary]
    locale=de_DE
    file_mode=700
    file_format=%Y/%B/%d.md
    section_pattern=^## (?P<name>.+)$
    todo_pattern=\[(?P<state>.)\] (?P<name>.+)
    todo_replacement=[{state}] {name}
    todo_empty= 
    todo_checked=x

*locale*:  
Can be left out.
Comes handy if you need specific time formatting,
which is different to the rest of your system.
Same result as running `LC_ALL=<locale> ./diary.py`.

*file_mode*:  
Can be left out.
Files and directories created by diary.py have the permission flags,
defined in `file_mode`. Defaults to `0755`.

*file_format*:  
Used to create file names from dates.

*section_pattern*:  
RegEx pattern used to detect section headers.
It needs a `name` group.

*todo_pattern*:  
RegEx pattern used to detect todo entries.
It needs a `name` and a `section` group.

*todo_replacement*:  
Python format string used to modify todo entries.
It needs a `name` and a `section` placeholder.

*todo_empty*:  
String used if a todo entry is unchecked.

*todo_checked*  
String used if a todo entry is checked.


## Usage

`./diary.py <command> <args>`

*Commands:*

*help*: Prints a short text, that describes the commands.

*create*: Prepare new diary entry and print its file name.

*write*: Opens todays diary entry with `$EDITOR` or `nano`.
