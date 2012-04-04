# vim:set expandtab tabstop=4 shiftwidth=4:
# -*- coding: utf-8 -*-
################################################################################
#
# VigiConf local component
# Copyright (C) 2010-2012 CS-SI
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
import re

from vigilo.common.gettext import translate

from vigilo.common.conf import settings

_ = translate(__name__)


class CommandError(Exception):
    """Classe de base pour les erreurs dans les commandes"""
    def __str__(self):
        msg = unicode(self.args[0]
                      if len(self.args) <= 1
                      else self.args)
        return msg.encode("utf-8")

class CommandExecError(CommandError):
    """Erreur à l'exécution de la commande"""
    pass

class CommandPrereqError(CommandError):
    """
    Erreur signalant que les conditions ne sont pas remplies pour exécuter la
    commande
    """
    pass


class Command(object):
    """
    Classe de base (abstraite) pour les commandes disponibles
    """

    def __init__(self, name):
        """
        @param name: nom de la commande
        @type  name: C{str}
        """
        self.name = name
        self.debug = False

    def check(self):
        """
        Vérifie que toutes les conditions sont remplies pour pouvoir exécuter
        la commande.
        @return: C{True}, C{False} ou C{None} suivant l'implémentation dans
            la sous-classe
        @raise CommandPrereqError: si les conditions d'exécution ne sont
            pas remplies
        """
        return True

    def run(self):
        """
        Méthode principale: exécute la commande
        """
        raise NotImplementedError


class ReceiveConf(Command):
    """
    Réceptionne la configuration télédéployée et la détarre dans le bon
    dossier.
    @ivar archive: le chemin vers l'archive télédéployée
    """

    def __init__(self, archive):
        """
        @param archive: le chemin vers l'archive télédéployée
        """
        self.basedir = settings["vigiconf"].get("targetconfdir")
        self.archive = archive
        super(ReceiveConf, self).__init__(name="receive")

    def check(self):
        """Vérifie que l'archive existe bel et bien"""
        if not os.path.exists(self.archive):
            raise CommandPrereqError(_("The archive '%s' does not exist, "
                                        "copy it first") % self.archive)

    def run(self):
        """Détarre l'archive et règle les droits"""
        self.check()
        if os.path.isdir(os.path.join(self.basedir, "new")):
            shutil.rmtree(os.path.join(self.basedir, "new"))
        os.makedirs(os.path.join(self.basedir, "new"))
        os.chdir(os.path.join(self.basedir, "new"))
        command = ["tar", "-pxf", self.archive]
        if self.debug:
            print " ".join(command)
            return
        proc = subprocess.Popen(command, stdout=subprocess.PIPE,
                                         stderr=subprocess.STDOUT)
        output = proc.communicate()[0]
        if proc.returncode != 0:
            os.remove(self.archive)
            raise CommandExecError(_("Can't untar the configuration: "
                                     "%(output)s")
                                   % {'output': output.decode("utf-8")})
        self.chmod()
        os.remove(self.archive)

    def chmod(self):
        """Règle quelques droits par défaut pour un peu de sécurité"""
        subprocess.call(["chmod", "-R", "o-w",
                         os.path.join(self.basedir, "new")])


class ValidateConf(Command):
    """
    Validation de la configuration

    @ivar location: C{local} si la validation est faite sur le serveur de
        destination, et C{central} si la validation est faite sur le serveur
        VigiConf.
    @type location: C{local} ou C{central}
    """

    def __init__(self, appname, basedir=None):
        self.appname = appname
        self.basedir = basedir
        targetconfdir = settings["vigiconf"].get("targetconfdir")
        if self.basedir is None:
            self.basedir = os.path.join(targetconfdir, "new")
        if self.basedir.startswith(targetconfdir):
            self.location = "local"
        else:
            self.location = "central"
        self.valid_script = os.path.join(self.basedir, "apps",
                                         self.appname, "validation.sh")
        super(ValidateConf, self).__init__(name="validate")

    def check(self):
        """
        Vérifie qu'il y a bien un script de validation pour l'application
        demandée
        """
        if not self.appname:
            raise CommandPrereqError(_("Please specify an application "
                                        "name to validate"))
        if not os.path.exists(self.valid_script):
            print _("No validation script: %s") % self.valid_script
            return False
        return True

    def run(self):
        """Valide la configuration de l'application"""
        if not self.check():
            return # pas de script de validation, on a rien à faire
        os.chdir(self.basedir)
        command = ["sh", self.valid_script, self.basedir, self.location]
        if self.debug:
            print " ".join(command)
            return
        proc = subprocess.Popen(command, stdout=subprocess.PIPE,
                                         stderr=subprocess.STDOUT)
        output = proc.communicate()[0]
        if proc.returncode != 0:
            raise CommandExecError(_("Validation failed for application "
                                    "'%(app)s'. Output: %(output)s") % {
                                        'app': self.appname,
                                        'output': output.decode('utf-8')
                                    })


class ActivateConf(Command):
    """
    Renomme les répertoires old, new et prod pour activer la configuration.
    """

    def __init__(self):
        self.basedir = settings["vigiconf"].get("targetconfdir")
        super(ActivateConf, self).__init__(name="activate")

    def check(self):
        """
        Vérifie que le répertoire "new" est bien en place pour procéder à
        l'activation
        """
        if not os.path.isdir(os.path.join(self.basedir, "new")):
            raise CommandPrereqError(_("The 'new' directory does not exist. "
                                       "Deploy the configuration first."))

    def run(self):
        """Active la configuration"""
        self.check()
        if self.debug:
            print _("Backing up the directory 'prod' to 'old', "
                    "and renaming 'new' into 'prod'")
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
            if not os.access(self.basedir, os.W_OK):
                msg = _("Configuration activation failed: %(error)s. "
                        "User '%(user)s' must have write access "
                        "to '%(dir)s'.") % {
                            'error': e,
                            'user': os.getlogin(),
                            'dir': self.basedir,
                        }
            else:
                msg = _("Configuration activation failed: %s.") % e
            raise CommandExecError(msg)


class StartStopApp(Command):
    """
    Démarre ou arrête une application, grâce aux scripts fournis.
    """

    def __init__(self, appname, action, subdir):
        self.appname = appname
        self.action = action
        self.subdir = subdir
        super(StartStopApp, self).__init__(name=action)

    def get_script(self):
        """Récupère le chemin du script à exécuter"""
        return os.path.join(settings["vigiconf"].get("targetconfdir"),
                            self.subdir, "apps", self.appname,
                            "%s.sh" % self.action)

    def check(self):
        """Vérifie que le script existe"""
        if not os.path.exists(self.get_script()):
            raise CommandPrereqError(_("The script '%(script)s' does not "
                                        "exist for application '%(app)s'") % {
                                            'script': self.get_script(),
                                            'app': self.appname,
                                        })

    def run(self):
        """Démarre ou arrête l'application"""
        self.check()
        confdir = os.path.join(settings["vigiconf"].get("targetconfdir"),
                               self.subdir)
        if self.debug:
            print "sh %s %s" % (self.get_script(), confdir)
            return
        proc = subprocess.Popen(["sh", self.get_script(), confdir],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        output = proc.communicate()[0]
        if proc.returncode != 0:
            raise CommandExecError(_("Action %(action)s failed for "
                                    "application %(app)s. "
                                    "Output: %(output)s") % {
                                        'action': self.action,
                                        'app': self.appname,
                                        'output': output.decode("utf-8"),
                                    })


class StartApp(StartStopApp):
    """Démarre une application"""

    def __init__(self, appname):
        super(StartApp, self).__init__(appname=appname, action="start",
                                       subdir="prod")

class StopApp(StartStopApp):
    """Arrête une application"""
    def __init__(self, appname):
        # subdir=new, parce que le process est :
        # 1. déploiement dans new
        # 2. arrêt des services
        # 3. new -> prod
        # 4. démarrage des services
        # donc la première fois, le dossier prod est vide quand on arrête les
        # services
        super(StopApp, self).__init__(appname=appname, action="stop",
                                      subdir="new")


class GetRevisions(Command):
    """
    Récupère et affiche les révisions SVN actuellement déployées dans les
    répertoires old, new et prod.
    """

    def __init__(self):
        self.basedir = settings["vigiconf"].get("targetconfdir")
        self.dirs = ["new", "prod", "old"]
        super(GetRevisions, self).__init__(name="get-revisions")

    def check(self):
        """Vérifie que les répertoires existent"""
        for d in self.dirs:
            if not os.path.isdir(os.path.join(self.basedir, d)):
                raise CommandPrereqError(
                        _("The directory '%s' does not exist.") % d)

    def run(self):
        """Récupère et affiche les révisions"""
        self.check()
        if self.debug:
            print _("Getting revisions from these directories: %s") % \
                    ", ".join(self.dirs)
            return
        rev_re = re.compile("^\s*Revision: (\d+)\s*$")
        for d in self.dirs:
            revision_file = os.path.join(self.basedir, d, "revisions.txt")
            if os.path.exists(revision_file):
                rev_file = open(revision_file)
                rev = rev_file.read().strip()
                rev_file.close()
                rev_match = rev_re.match(rev)
                if not rev_match:
                    rev = 0
                else:
                    rev = rev_match.group(1)
            else:
                rev = 0
            print "%s %s" % (d, rev)


class SetRevision(Command):
    """
    Affecte la révision SVN actuellement déployée.
    """

    def __init__(self, rev):
        self.basedir = os.path.join(settings["vigiconf"].get("targetconfdir"),
                                    "new")
        self.rev = rev
        super(SetRevision, self).__init__(name="set-revision")

    def check(self):
        """Vérifie que les répertoires existent"""
        if not os.path.isdir(self.basedir):
            raise CommandPrereqError(_("The directory 'new' does not exist."))

    def run(self):
        """Écrit la révision"""
        self.check()
        if self.debug:
            print _("Setting revision to: %s") % self.rev
            return
        rev_file = open(os.path.join(self.basedir, "revisions.txt"), "w")
        rev_file.write("Revision: %s\n" % self.rev)
        rev_file.close()



COMMANDS = {
        "stop-app": StopApp,
        "start-app": StartApp,
        "validate-app": ValidateConf,
        "activate-conf": ActivateConf,
        "receive-conf": ReceiveConf,
        "get-revisions": GetRevisions,
        "set-revision": SetRevision,
#        "revert-conf": RevertConf,
}
