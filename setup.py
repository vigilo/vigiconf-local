#!/usr/bin/env python
# vim: set fileencoding=utf-8 sw=4 ts=4 et :
# Copyright (C) 2006-2020 CS GROUP - France
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

import os, sys
from setuptools import setup, find_packages

sysconfdir = os.getenv("SYSCONFDIR", "/etc")
localstatedir = os.getenv("LOCALSTATEDIR", "/var")

tests_require = [
    'nose',
    'coverage',
]

def install_i18n(i18ndir, destdir):
    data_files = []
    langs = []
    for f in os.listdir(i18ndir):
        if os.path.isdir(os.path.join(i18ndir, f)) and not f.startswith("."):
            langs.append(f)
    for lang in langs:
        for f in os.listdir(os.path.join(i18ndir, lang, "LC_MESSAGES")):
            if f.endswith(".mo"):
                data_files.append(
                        (os.path.join(destdir, lang, "LC_MESSAGES"),
                         [os.path.join(i18ndir, lang, "LC_MESSAGES", f)])
                )
    return data_files

def get_data_files():
    files = []
    for d in ["new", "prod", "tmp", "old"]:
        files.append((os.path.join(sysconfdir, "vigilo/vigiconf", d), []))
    files.append((os.path.join(sysconfdir, "vigilo/vigiconf"), ["settings-local.ini"]))
    files.append((os.path.join(localstatedir, "lib/vigilo/vigiconf"), []))
    return files


setup(name='vigilo-vigiconf-local',
        version='5.2.0b2',
        author='Vigilo Team',
        author_email='contact.vigilo@csgroup.eu',
        url='https://www.vigilo-nms.com/',
        license='http://www.gnu.org/licenses/gpl-2.0.html',
        description="Local client for VigiConf",
        long_description="This program installs the configuration pushed "
                         "by VigiConf.",
        install_requires=[
            "setuptools",
            "vigilo-common",
            ],
        extras_require={
            'tests': tests_require,
        },
        namespace_packages = [
            'vigilo',
            ],
        message_extractors={
            'src': [
                ('**.py', 'python', None),
            ],
        },
        packages=find_packages("src"),
        entry_points={
            'console_scripts': [
                'vigiconf-local = vigilo.vigiconf_local:main',
                ],
            },
        package_dir={'': 'src'},
        data_files=get_data_files() +
            install_i18n("i18n", os.path.join(sys.prefix, 'share', 'locale')),
        )
