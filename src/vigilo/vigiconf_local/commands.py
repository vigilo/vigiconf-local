# vim:set expandtab tabstop=4 shiftwidth=4:
# -*- coding: utf-8 -*-
################################################################################
#
# VigiConf local component
# Copyright (C) 2010-2011 CS-SI
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
################################################################################

"""
Commandes autorisées
"""

import os
import shutil
import subprocess

from vigilo.common.conf import settings
try:
    settings.load_module("vigilo.vigiconf")
except IOError:
    settings.load_module("vigilo.vigiconf", "settings-local.ini")


class CommandError(Exception):
    pass
class CommandExecError(CommandError):
    pass
class CommandPrereqError(CommandError):
    pass


class Command(object):


    def __init__(self, name):
        self.name = name
        self.debug = False

    def run(self):
        raise NotImplementedError


class ReceiveConf(Command):

    def __init__(self, archive):
        self.basedir = settings["vigiconf"].get("targetconfdir")
        self.archive = archive
        super(ReceiveConf, self).__init__(name="receive")

    def check(self):
        if not os.path.exists(self.archive):
            raise CommandPrereqError("The archive '%s' does not exist, "
                                      % self.archive +
                                     "copy it first.")

    def run(self):
        self.check()
        if os.path.isdir(os.path.join(self.basedir, "new")):
            shutil.rmtree(os.path.join(self.basedir, "new"))
        os.makedirs(os.path.join(self.basedir, "new"))
        os.chdir(os.path.join(self.basedir, "new"))
        command = ["tar", "-xf", self.archive]
        if self.debug:
            print " ".join(command)
            return
        proc = subprocess.Popen(command, stdout=subprocess.PIPE,
                                         stderr=subprocess.STDOUT)
        output = proc.communicate()[0]
        if proc.returncode != 0:
            os.remove(self.archive)
            raise CommandExecError("Validation failed for app %s. "
                                    % self.appname +
                                   "Output: %s" % output)
        self.chmod()
        os.remove(self.archive)

    def chmod(self):
        subprocess.call(["chmod", "-R", "o-w",
                         os.path.join(self.basedir, "new")])


class ValidateConf(Command):

    def __init__(self, appname):
        self.basedir = settings["vigiconf"].get("targetconfdir")
        self.appname = appname
        self.valid_script = os.path.join(self.basedir, "new", "apps",
                                         self.appname, "validation.sh")
        super(ValidateConf, self).__init__(name="validate")

    def check(self):
        if not self.appname:
            raise CommandPrereqError("Please specify an app name to validate")
        if not os.path.exists(self.valid_script):
            print "No validation script: %s" % self.valid_script
            return False
        return True

    def run(self):
        if not self.check():
            return # pas de script de validation, on a rien à faire
        os.chdir(os.path.join(self.basedir, "new"))
        command = ["sh", self.valid_script, os.path.join(self.basedir, "new")]
        if self.debug:
            print " ".join(command)
            return
        proc = subprocess.Popen(command, stdout=subprocess.PIPE,
                                         stderr=subprocess.STDOUT)
        output = proc.communicate()[0]
        if proc.returncode != 0:
            raise CommandExecError("Validation failed for app %s. "
                                    % self.appname +
                                   "Output: %s" % output)


class ActivateConf(Command):

    def __init__(self):
        self.basedir = settings["vigiconf"].get("targetconfdir")
        super(ActivateConf, self).__init__(name="activate")

    def check(self):
        if not os.path.isdir(os.path.join(self.basedir, "new")):
            raise CommandPrereqError("The 'new' directory does not exist. "
                               "Deploy the configuration first.")

    def run(self):
        self.check()
        if self.debug:
            print "backuping directory 'prod' to 'old', " \
                 +"and renaming 'new' to 'prod'"
            return
        if not os.path.isdir(os.path.join(self.basedir, "prod")):
            os.makedirs(os.path.join(self.basedir, "prod"))
        try:
            shutil.rmtree(os.path.join(self.basedir, "old"))
            os.rename(os.path.join(self.basedir, "prod"),
                      os.path.join(self.basedir, "old"))
            os.rename(os.path.join(self.basedir, "new"),
                      os.path.join(self.basedir, "prod"))
            os.makedirs(os.path.join(self.basedir, "new"))
            shutil.copy(os.path.join(self.basedir, "prod", "revisions.txt"),
                        os.path.join(self.basedir, "new", "revisions.txt"))
        except OSError, e:
            msg = "Configuration activation failed: %s." % e
            if not os.access(self.basedir, os.W_OK):
                msg += " The '%s' user must have write access to '%s'." \
                        % (os.getlogin(), self.basedir)
            raise CommandExecError(msg)


#class RevertConf(Command):
#
#    def __init__(self):
#        self.basedir = settings["vigiconf"].get("targetconfdir")
#        super(RevertConf, self).__init__(name="revert")
#
#    def check(self):
#        if os.path.isdir(os.path.join(self.basedir, "undo-tmp")):
#            raise CommandPrereqError("The 'undo-tmp' directory exists. "
#                               "It looks like a previous undo failed.")
#        if not os.path.isdir(os.path.join(self.basedir, "old")):
#            raise CommandPrereqError("The 'old' directory does not exist, "
#                               "can't revert to the previous config.")
#        if not os.path.isdir(os.path.join(self.basedir, "prod")):
#            raise CommandPrereqError("The 'prod' directory does not exist, "
#                               "can't revert to the previous config.")
#
#    def run(self):
#        self.check()
#        if self.debug:
#            print "switching directories 'prod' and 'old'"
#            return
#        try:
#            os.rename(os.path.join(self.basedir, "old"),
#                      os.path.join(self.basedir, "undo-tmp"))
#            os.rename(os.path.join(self.basedir, "prod"),
#                      os.path.join(self.basedir, "old"))
#            os.rename(os.path.join(self.basedir, "undo-tmp"),
#                      os.path.join(self.basedir, "prod"))
#        except OSError, e:
#            msg = "Configuration rollback failed: %s." % e
#            if not os.access(self.basedir, os.W_OK):
#                msg += " The '%s' user must have write access to '%s'." \
#                        % (os.getlogin(), self.basedir)
#            raise CommandExecError(msg)


class StartStopApp(Command):

    def __init__(self, appname, action):
        self.appname = appname
        self.action = action
        super(StartStopApp, self).__init__(name=action)

    def get_script(self):
        return os.path.join(settings["vigiconf"].get("targetconfdir"),
                            "prod", "apps", self.appname,
                            "%s.sh" % self.action)

    def check(self):
        if not os.path.exists(self.get_script()):
            raise CommandPrereqError("The %s script does not exist for the "
                                        % self.get_script() +
                                     "application %s" % self.appname)

    def run(self):
        self.check()
        if self.debug:
            print "sh %s" % self.get_script()
            return
        proc = subprocess.Popen(["sh", self.get_script()],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        output = proc.communicate()[0]
        if proc.returncode != 0:
            raise CommandExecError("Action %s failed for app %s. "
                                    % (self.action, self.appname) +
                                   "Output: %s" % output)


class StartApp(StartStopApp):
    def __init__(self, appname):
        super(StartApp, self).__init__(appname=appname, action="start")

class StopApp(StartStopApp):
    def __init__(self, appname):
        super(StopApp, self).__init__(appname=appname, action="stop")


class GetRevisions(Command):

    def __init__(self):
        self.basedir = settings["vigiconf"].get("targetconfdir")
        self.dirs = ["new", "prod", "old"]
        super(GetRevisions, self).__init__(name="get-revisions")

    def check(self):
        for d in self.dirs:
            if not os.path.isdir(os.path.join(self.basedir, d)):
                raise CommandPrereqError(
                        "The '%s' directory does not exist." % d)

    def run(self):
        self.check()
        if self.debug:
            print "Getting revisions in directories %s" % ", ".join(self.dirs)
            return
        for d in self.dirs:
            revision_file = os.path.join(self.basedir, d, "revisions.txt")
            if os.path.exists(revision_file):
                rev_file = open(revision_file)
                rev = rev_file.read().strip().split(" ")[1]
                rev_file.close()
            else:
                rev = 0
            print "%s %s" % (d, rev)



COMMANDS = {
        "stop-app": StopApp,
        "start-app": StartApp,
        "validate-app": ValidateConf,
        "activate-conf": ActivateConf,
        "receive-conf": ReceiveConf,
        "get-revisions": GetRevisions,
#        "revert-conf": RevertConf,
}
