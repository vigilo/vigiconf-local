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
Composant local de VigiConf

Il est installé sur les serveur de supervision qui sont téléadministrés par
VigiConf
"""

import sys
import optparse
import inspect

from vigilo.vigiconf_local.commands import \
        COMMANDS, CommandPrereqError, CommandExecError

from vigilo.common.gettext import translate, translate_narrow
_ = translate(__name__)
N_ = translate_narrow(__name__)

from vigilo.common.argparse import prepare_argparse

def main():
    # Chargement des traductions d'optparse.
    prepare_argparse()

    parser = optparse.OptionParser(
        _("Usage: %prog [options] command [arguments]"))
    parser.add_option("-n", "--dry-run", action="store_true", dest="dryrun",
                      help=_("Only print the command that would be run"))
    opts, args = parser.parse_args()
    if not args:
        parser.error(N_("No command selected. Available commands: %s") %
                        ", ".join(COMMANDS.keys()))

    cmd_name = args[0]
    if cmd_name not in COMMANDS:
        parser.error(N_("Unknown command. Available commands: %s") %
                        ", ".join(COMMANDS.keys()))

    cmd_args = inspect.getargspec(COMMANDS[cmd_name].__init__)
    cmd_min_args = len(cmd_args[0]) - 1
    if cmd_args[3]:
        cmd_min_args -= len(cmd_args[3])

    if len(args) < cmd_min_args or len(args) > len(cmd_args[0]):
        args_list = []
        for index, arg in enumerate(cmd_args[0][1:]):
            if index + 1 > cmd_min_args:
                arg = "[%s]" % arg
            args_list.append(arg)
        parser.error(N_("Wrong number of arguments. Expected: %s") %
                        " ".join(args_list))

    cmd = COMMANDS[cmd_name](*args[1:])

    if opts.dryrun:
        cmd.debug = True

    try:
        cmd.run()
    except CommandPrereqError, e:
        print >> sys.stderr, N_("Setup error: %s") % e
        sys.exit(11)
    except CommandExecError, e:
        print >> sys.stderr, N_("Error: %s") % e
        sys.exit(10)


if __name__ == "__main__":
    main()
