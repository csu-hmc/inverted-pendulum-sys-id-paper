#!/usr/bin/env python

# standard library
import os
import time

# external
import yaml

from prettytable import PrettyTable


def timeit(method):

    def timed(*args, **kw):

        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        t_delta = te - ts

        #print '%r (%r, %r) %2.2f sec' % \
              #(method.__name__, args, kw, t_delta)

        return (result, ) + (t_delta,)

    return timed


def print_gains(actual, *identified):
    """Prints an ASCII table of the provided gains."""
    table = PrettyTable()
    table.add_column('Gains', ['g_00', 'g_01', 'g_02', 'g_03', 'g_10',
                               'g_11', 'g_12', 'g_13'])
    table.add_column('Actual', ['{:1.3f}'.format(g) for g in actual])
    for i, gain_set in enumerate(identified):
        table.add_column('Set {}'.format(i),
                         ['{:1.3f}'.format(g) for g in gain_set])
    print(table)


def config_paths():
    """Returns the full paths to the directories specified in the config.yml
    file.

    Returns
    -------
    paths : dictionary
        Absolute paths to the various directories.

    """

    this_script_path = os.path.realpath(__file__)
    src_dir = os.path.dirname(this_script_path)
    root_dir = os.path.realpath(os.path.join(src_dir, '..'))

    try:
        with open(os.path.join(root_dir, 'config.yml'), 'r') as f:
            config = yaml.load(f)
    except IOError:
        with open(os.path.join(root_dir, 'default-config.yml'), 'r') as f:
            config = yaml.load(f)

    paths = {}
    for name, dir_name in config.items():
        dir_path = os.path.join(root_dir, dir_name)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        paths[name] = dir_path

    paths['project_root'] = root_dir

    return paths
