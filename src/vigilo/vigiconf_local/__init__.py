"""
Composant local de VigiConf

Il est installé sur les serveur de supervision qui sont téléadministrés par
VigiConf
"""

import optparse

from vigilo.vigiconf_local.commands import COMMANDS

def main():
    parser = optparse.OptionParser("Usage: %prog [options] command [arguments]")
    parser.add_option("-n", "--dry-run", action="store_true" dest="dryrun",
                      help="Only print the command that would be run")
    opts, args = parser.parse_args()
    if not args:
        parser.error("No command selected. Available commands: %s"
                     % ", ".join(COMMANDS.keys()))

    cmd_name = args[0]
    if cmd_name not in COMMANDS:
        parser.error("Unknown command. Available commands: %s"
                     % ", ".join(COMMANDS.keys()))

    cmd = COMMANDS[cmd_name](args[1:])

    if opts.dryrun:
        cmd.debug = True

    cmd.run()


if __name__ == "__main__":
    main()
