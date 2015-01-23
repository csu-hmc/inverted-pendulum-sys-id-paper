#!/usr/bin/env python

from prettytable import PrettyTable


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
