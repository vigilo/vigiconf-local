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

from pkg_resources import working_set

from vigilo.common.conf import settings
settings.load_module(__name__)


class CommandError(Exception):
    pass
class CommandExecError(CommandError):
    pass
class CommandPrereqError(CommandError):
    pass


class Command(object):

    runas = None

    def __init__(self, name=None, args=[]):
        self.name = name
        self.args = args

    def run(self):
        raise NotImplementedError


class ShellCommand(Command):
    pass


class ValidateConf(Command):

    def __init__(self, appname=None):
        self.basedir = settings["vigiconf"].get("targetconfdir")
        self.appname = appname
        super(ValidateConf, self).__init__(name="validate")

    def check(self):
        if not self.appname:
            raise CommandPrereqError("Please specify an app name to validate")
        if not os.path.exists(os.path.join(
                    self.basedir, "validation", "%s.sh" % self.appname)):
            return False
        return True

    def run(self):
        if not self.check():
            return # pas de script de validation, on a rien à faire
        os.chdir(os.path.join(self.basedir, "new"))
        command = [os.path.join("validation", "%s.sh" % self.appname),
                   os.path.join(self.basedir, "new")]
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
                               "Depoy the configuration first.")

    def run(self):
        self.check()
        if not os.path.isdir(os.path.join(self.basedir, "prod")):
            os.makedirs(os.path.join(self.basedir, "prod"))
        shutil.rmtree(os.path.join(self.basedir, "old"))
        os.rename(os.path.join(self.basedir, "prod"),
                  os.path.join(self.basedir, "old"))
        os.rename(os.path.join(self.basedir, "new"),
                  os.path.join(self.basedir, "prod"))
        os.makedirs(os.path.join(self.basedir, "new"))
        shutil.copy(os.path.join(self.basedir, "prod", "revisions.txt"),
                    os.path.join(self.basedir, "new", "revisions.txt"))


class RevertConf(Command):

    def __init__(self):
        self.basedir = settings["vigiconf"].get("targetconfdir")
        super(RevertConf, self).__init__(name="revert")

    def check(self):
        if os.path.isdir(os.path.join(self.basedir, "undo-tmp")):
            raise CommandPrereqError("The 'undo-tmp' directory exists. "
                               "It looks like a previous undo failed.")
        if not os.path.isdir(os.path.join(self.basedir, "old")):
            raise CommandPrereqError("The 'old' directory does not exist, "
                               "can't revert to the previous config.")
        if not os.path.isdir(os.path.join(self.basedir, "prod")):
            raise CommandPrereqError("The 'prod' directory does not exist, "
                               "can't revert to the previous config.")

    def run(self):
        self.check()
        os.rename(os.path.join(self.basedir, "old"),
                  os.path.join(self.basedir, "undo-tmp"))
        os.rename(os.path.join(self.basedir, "prod"),
                  os.path.join(self.basedir, "old"))
        os.rename(os.path.join(self.basedir, "undo-tmp"),
                  os.path.join(self.basedir, "prod"))


class StartStopApp(Command):

    def __init__(self, appname=None, action=None):
        self.appname = appname
        self.action = action
        super(StartStopApp, self).__init__(name=action)

    def get_script(self):
        return os.path.join(settings["vigiconf"].get("targetconfdir"),
                            "prod", self.appname, "%s.sh" % self.action)

    def check(self):
        if not os.path.exists(self.get_script()):
            raise CommandPrereqError("The %s script does not exist for the "
                                        % self.get_script() +
                                     "application %s" % self.appname)

    def run(self):
        self.check()
        proc = subprocess.Popen([self.get_script()],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        output = proc.communicate()[0]
        if proc.returncode != 0:
            raise CommandExecError("Action %s failed for app %s. "
                                    % (self.action, self.appname) +
                                   "Output: %s" % output)


class StartApp(StartStopApp):
    def __init__(self, appname=None):
        super(StartApp, self).__init__(appname=appname, action="start")

class StopApp(StartStopApp):
    def __init__(self, appname=None):
        super(StopApp, self).__init__(appname=appname, action="stop")



COMMANDS = {
        "stop-app": StopApp,
        "start-app": StartApp,
        "validate-app": ValidateConf,
        "activate-conf": ActivateConf,
        "revert-conf": RevertConf,
}
