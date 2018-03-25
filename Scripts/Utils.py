import sys
import os
import time
import tempfile
import shutil
import subprocess
import re
import threading
try:
    from Queue import Queue, Empty
except:
    from queue import Queue, Empty
# Python-aware urllib stuff
if sys.version_info >= (3, 0):
    from urllib.request import urlopen
else:
    from urllib2 import urlopen

class Utils:

    def __init__(self, name = "Python Script"):
        self.name = name
        
    def check_path(self, path):
        # Loop until we either get a working path - or no changes
        count = 0
        while count < 100:
            count += 1
            if not len(path):
                # We uh.. stripped out everything - bail
                return None
            if os.path.exists(path):
                # Exists!
                return os.path.abspath(path)
            # Check quotes first
            if (path[0] == '"' and path[-1] == '"') or (path[0] == "'" and path[-1] == "'"):
                path = path[1:-1]
                continue
            # Check for tilde
            if path[0] == "~":
                test_path = os.path.expanduser(path)
                if test_path != path:
                    # We got a change
                    path = test_path
                    continue
            # If we have no spaces to trim - bail
            if not (path[0] == " " or path[0] == "  ") and not(path[-1] == " " or path[-1] == " "):
                return None
            # Here we try stripping spaces/tabs
            test_path = path
            t_count = 0
            while t_count < 100:
                t_count += 1
                t_path = test_path
                while len(t_path):
                    if os.path.exists(t_path):
                        return os.path.abspath(t_path)
                    if t_path[-1] == " " or t_path[-1] == "    ":
                        t_path = t_path[:-1]
                        continue
                    break
                if test_path[0] == " " or test_path[0] == " ":
                    test_path = test_path[1:]
                    continue
                break
            # Escapes!
            test_path = "\\".join([x.replace("\\", "") for x in path.split("\\\\")])
            if test_path != path and not (path[0] == " " or path[0] == "  "):
                path = test_path
                continue
            if path[0] == " " or path[0] == "  ":
                path = path[1:]
        return None

    # Helper methods
    def grab(self, prompt):
        if sys.version_info >= (3, 0):
            return input(prompt)
        else:
            return str(raw_input(prompt))

    # Header drawing method
    def head(self, text = None, width = 55):
        if text == None:
            text = self.name
        os.system("clear")
        print("  {}".format("#"*width))
        len_text = text
        mid_len = int(round(width/2-len(len_text)/2)-2)
        middle = " #{}{}{}#".format(" "*mid_len, len_text, " "*((width - mid_len - len(len_text))-2))
        print(middle)
        print("#"*width)

    def custom_quit(self):
        self.head()
        print("by CorpNewt\n")
        print("Thanks for testing it out, for bugs/comments/complaints")
        print("send me a message on Reddit, or check out my GitHub:\n")
        print("www.reddit.com/u/corpnewt")
        print("www.github.com/corpnewt\n")
        print("Have a nice day/night!\n\n")
        exit(0)