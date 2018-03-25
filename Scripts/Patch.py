import sys
import os
import tempfile
import shutil
import time
import Run
import Utils
import datetime

class Patch:

    def __init__(self):

        # Check the OS first
        if not str(sys.platform) == "darwin":
            self.head("Incompatible System")
            print(" ")
            print("This script can only be run from macOS/OS X.")
            print(" ")
            print("The current running system is \"{}\".".format(sys.platform))
            print(" ")
            self.grab("Press [enter] to quit...")
            print(" ")
            exit(1)
        # Init some vars
        self.apfs        = self.apfs_path = "/usr/standalone/i386/apfs.efi"
        self.hex_find    = "00 74 07 B8 FF FF"
        self.hex_replace = "00 90 90 B8 FF FF"

        self.hex_digits  = "0123456789ABCDEF"
        # Credit to PMHeart for the hex patch
        self.r = Run.Run()
        self.u = Utils.Utils("APFS Non Verbose")

    def check_dir(self, build):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        os.chdir("../")
        if not os.path.exists("APFS"):
            os.mkdir("APFS")
        os.chdir("APFS")
        if not os.path.exists(build):
            os.mkdir(build)
        os.chdir(build)
        return os.getcwd()

    def get_md5(self, path):
        if not os.path.exists(path):
            return None
        out = self.r.run({"args" : ["md5", "-q", path]})
        if out[2] == 0:
            return out[0].replace("\n", "")
        else:
            return out[1]

    def check_md5(self):
        self.u.head("Get MD5")
        print(" ")
        print("M. Main Menu")
        print("Q. Quit")
        print(" ")
        menu = self.u.grab("Drag and drop an apfs.efi file to get its md5:  ")
        if not len(menu):
            self.check_md5()
            return
        if menu.lower() == "m":
            return
        elif menu.lower() == "q":
            self.u.custom_quit()
        menu = self.u.check_path(menu)
        if not menu:
            self.check_md5()
            return
        self.u.head("Get MD5")
        print(" ")
        print("Checking md5...")
        md = self.get_md5(menu)
        self.u.head("MD5 Results")
        print(" ")
        print(menu)
        print(" ")
        print("MD5:  {}".format(md))
        print(" ")
        self.u.grab("Press [enter] to return to the MD5 menu...")
        self.check_md5()
        return

    def patch(self, path, temp):
        self.u.head()
        print(" ")
        print("Copying to temp dir...")
        name = os.path.basename(path)
        self.r.run({"args" : ["cp", path, os.path.join(temp, name)]})
        # Get start md5
        m1 = self.get_md5(os.path.join(temp, name))
        print("\nStarting MD5:  {}".format(m1))
        print("\nAttempting to patch \"{}\"...".format(os.path.basename(path)))
        print(" - Patch courtesy of PMHeart -")
        # Check the hex
        if any(x for x in "".join((self.hex_find+self.hex_replace).split()) if x.upper() not in self.hex_digits.upper()):
            print("\nHex patch is malformed!")
            time.sleep(5)
            return
        # Build our command
        h_patch = 's|\\x{}|\\x{}|sg'.format(
            "\\x".join(self.hex_find.split()),
            "\\x".join(self.hex_replace.split())
        )
        out = self.r.run({"args" : ["perl", "-i", "-pe", h_patch, os.path.join(temp, name)]})
        # Get end md5
        m2 = self.get_md5(os.path.join(temp, name))
        print("\nEnding MD5:  {}".format(m2))
        if m1 == m2:
            print(" - No change in MD5!  Patch NOT Successful.\n")
            self.u.grab("Press [enter] to return to the main menu...")
            return

        print(" - MD5 changed!  Patch SUCCESSFUL.")
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        os.chdir("../")
        a_path = os.path.join(os.getcwd(), "APFS-Patched")
        if not os.path.exists(a_path):
            os.mkdir(a_path)
        print("\nCopying patched apfs to:\n - {}...".format(a_path))
        parts = name.split(".")
        new_name = ""
        if len(parts) < 2:
            new_name = name+"-{:%Y-%m-%d %H.%M.%S}".format(datetime.datetime.now())
        else:
            n = ".".join(parts[:-1])
            new_name = n+"-{:%Y-%m-%d %H.%M.%S}".format(datetime.datetime.now())+"."+parts[-1]
        
        self.r.run({"args":["cp", os.path.join(temp, name), os.path.join(a_path, new_name)]})
        self.r.run({"args":["open", a_path]})

        print("\nDone!\n")
        self.u.grab("Press [enter] to return to the main menu...")
        return

    def main(self):
        self.u.head()
        print(" ")
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        if os.path.exists(self.apfs_path):
            print("Found apfs.efi at: {}\n >>>--------> MD5: {}".format(self.apfs_path, self.get_md5(self.apfs_path)))
            print(" ")
        print("Drag and drop apfs.efi to patch, or:")
        print("")

        if os.path.exists(self.apfs_path):
            print("P. Patch Local")
        print("M. Get MD5")
        print("Q. Quit")
        print(" ")

        menu = self.u.grab("Please make a selection:  ")

        if not len(menu):
            return

        if menu.lower() == "q":
            self.u.custom_quit()
        elif menu.lower() == "m":
            self.check_md5()
        elif menu.lower() == "p" and os.path.exists(self.apfs_path):
            menu = self.apfs_path
        
        menu = self.u.check_path(menu)
        if not menu or os.path.isdir(menu):
            return
        # Got a path to a file - try to patch, and delete the temp regardless of success
        temp = tempfile.mkdtemp()
        try:
            self.patch(menu, temp)
        except:
            pass
        if os.path.exists(temp):
            shutil.rmtree(temp)
        return
        

p = Patch()

while True:
    try:
        p.main()
    except Exception as e:
        print(e)
        time.sleep(5)
