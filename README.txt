VigiConf Local
==============

VigiConf-Local est le composant de Vigilo_ qui permet de valider et d'activer
la configuration distribuée par VigiConf.

Pour les détails du fonctionnement de VigiConf, se reporter à la
`documentation officielle`_.


Dépendances
-----------
Vigilo nécessite une version de Python supérieure ou égale à 2.5. Le chemin de
l'exécutable python peut être passé en paramètre du ``make install`` de la
façon suivante::

    make install PYTHON=/usr/bin/python2.6

VigiConf a besoin des modules Python suivants :

- setuptools (ou distribute)
- vigilo-common


Installation
------------
L'installation se fait par la commande ``make install`` (à exécuter en
``root``).


License
-------
VigiConf est sous licence `GPL v2`_.


.. _documentation officielle: Vigilo_
.. _Vigilo: http://www.projet-vigilo.org
.. _GPL v2: http://www.gnu.org/licenses/gpl-2.0.html

.. vim: set syntax=rst fileencoding=utf-8 tw=78 :


