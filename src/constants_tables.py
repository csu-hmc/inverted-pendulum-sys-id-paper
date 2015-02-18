#!/usr/bin/env python

import os

import sympy as sm
from sympy.physics.vector import vlatex

from model import QuietStandingModel
import utils

paths = utils.config_paths()

m = QuietStandingModel()
m.derive()

# Generate the equations of motion: fr + fr*
fr_plus_frstar = sm.trigsimp(m.fr_plus_frstar)

template = \
r"""\begin{{bmatrix}}
  0 \\
  0 \\
  0 \\
  0
\end{{bmatrix}}
=
\begin{{bmatrix}}
{rows}
\end{{bmatrix}}"""

rows = []
for row in m.kin_diff_eqs + tuple(fr_plus_frstar):
    rows.append(vlatex(row))

with open(os.path.join(paths['project_root'], 'eoms.tex'), 'w') as f:
    f.write(template.format(rows='\\\\\n'.join(rows)))

# Generate a table for the open loop model constants. This should have three
# columns: latex variable name, value, units

units = {'d': r'\si{\meter}',
         'l': r'\si{\meter}',
         'm': r'\si{\kilogram}',
         'I': r'\si{\kilogram\meter\squared}',
         'g': r'\si{\meter\per\second\squared}'}

template = \
r"""
\begin{{tabular}}{{llll}}
  \toprule
  Variable & Description & Value & Units \\
  \midrule
{rows}
  \bottomrule
\end{{tabular}}"""

rows = []
for var, val in m.open_loop_par_map.items():

    row_tmp = r'${}$ & {} & {:1.3f} & {} \\'
    rows.append(row_tmp.format(vlatex(var), 'booger', val, units[str(var)[0]]))

with open(os.path.join(paths['tables_dir'], 'constants-table.tex'), 'w') as f:
    f.write(template.format(rows='\n'.join(rows)))

# Generate a table of the known gains.
