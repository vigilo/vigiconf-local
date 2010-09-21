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

def main():
    parser = optparse.OptionParser("Usage: %prog [options] command [arguments]")
    parser.add_option("-n", "--dry-run", action="store_true", dest="dryrun",
                      help="Only print the command that would be run")
    opts, args = parser.parse_args()
    if not args:
        parser.error("No command selected. Available commands: %s"
                     % ", ".join(COMMANDS.keys()))

    cmd_name = args[0]
    if cmd_name not in COMMANDS:
        parser.error("Unknown command. Available commands: %s"
                     % ", ".join(COMMANDS.keys()))

    cmd_args = inspect.getargspec(COMMANDS[cmd_name].__init__)[0]

    if len(args) != len(cmd_args):
        parser.error("%d argument(s) required: %s" % (len(cmd_args) - 1, ", ".join(cmd_args[1:])))

    cmd = COMMANDS[cmd_name](*args[1:])

    if opts.dryrun:
        cmd.debug = True

    try:
        cmd.run()
    except CommandPrereqError, e:
        print >>sys.stderr, "Setup error: %s" % e
        sys.exit(11)
    except CommandExecError, e:
        print >>sys.stderr, "Error: %s" % e
        sys.exit(10)


if __name__ == "__main__":
    main()