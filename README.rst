Introduction
============

This is the source repository for the paper:

   Moore, J.K. and van den Bogert, A. "Quiet Standing Controller Parameter
   Identification: A Comparison of Methods", 2015.

This repository contains or links to all of the information needed to reproduce
the results in the paper.

The latest rendered version of the PDF can be viewed via the ShareLaTeX_ CI
system:

.. image:: https://www.sharelatex.com/github/repos/csu-hmc/inverted-pendulum-sys-id/builds/latest/badge.svg
   :target: https://www.sharelatex.com/github/repos/csu-hmc/inverted-pendulum-sys-id/builds/latest/output.pdf

.. _ShareLaTeX: http://sharelatex.com

License and Citation
====================

The contents of this repository is licensed under the `Creative Commons
Attribution 4.0 International License`_.

.. image:: https://i.creativecommons.org/l/by/4.0/80x15.png
   :target: http://creativecommons.org/licenses/by/4.0

.. _Creative Commons Attribution 4.0 International License: http://creativecommons.org/licenses/by/4.0

If you make use of our work we ask that you cite us.

Get the source
==============

First, navigate to a desired location on your file system and either clone the
repository with Git [#]_ and change into the new directory::

   $ git clone https://github.com/csu-hmc/inverted-pendulum-sys-id-paper.git
   $ cd inverted-pendulum-sys-id-paper

or download with wget, unpack the zip file, and change into the new directory::

   $ wget https://github.com/csu-hmc/inverted-pendulum-sys-id-paper/archive/master.zip
   $ unzip inverted-pendulum-sys-id-paper-master.zip
   $ cd inverted-pendulum-sys-id-paper-master

.. [#] Please use Git if you wish to contribute back to the repository. See
   CONTRIBUTING.rst for information on how to contribute.

Basic LaTeX Build Instructions
==============================

To build the pdf from the LaTeX source using the pre-generated figures and
tables in the repository, make sure you have an up-to-date LaTeX distribution
installed and run ``make`` from within the repository. The default ``make``
target will build the document, i.e.::

   $ make

You can then view the document with your preferred PDF viewer. For example,
Evince can be used::

   $ evince paper.pdf

Software
========

The scripts used for the analysis is available in the ``src`` directory of this
repository and depend primarily on the open source Python package opty
developed for this paper.
