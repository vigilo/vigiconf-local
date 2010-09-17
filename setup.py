#!/usr/bin/env python
# vim: set fileencoding=utf-8 sw=4 ts=4 et :
import os, sys
from glob import glob
from setuptools import setup, find_packages

sysconfdir = os.getenv("SYSCONFDIR", "/etc")
localstatedir = os.getenv("LOCALSTATEDIR", "/var")

tests_require = [
    'nose',
    'coverage',
]

def get_data_files():
    files = []
    for d in ["new", "prod", "tmp"]:
        files.append((os.path.join(sysconfdir, "vigilo/vigiconf", d), []))
    files.append((os.path.join(sysconfdir, "vigilo/vigiconf"), ["settings-local.ini"]))
    files.append((os.path.join(localstatedir, "lib/vigilo/vigiconf"), []))
    return files


setup(name='vigilo-vigiconf-local',
        version='2.0.0',
        author='Vigilo Team',
        author_email='contact@projet-vigilo.org',
        url='http://www.projet-vigilo.org/',
        description='vigilo configuration local component',
        license='http://www.gnu.org/licenses/gpl-2.0.html',
        long_description='The Vigilo configuration system generates\n'
        +'configuration for every other component in Vigilo, distributes\n'
        +'it and restarts the services.\n',
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
        packages=find_packages("src"),
        entry_points={
            'console_scripts': [
                'vigiconf-local = vigilo.vigiconf_local:main',
                ],
            },
        package_dir={'': 'src'},
        data_files=get_data_files(),
        )

