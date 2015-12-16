#!/usr/bin/env python
from __future__ import print_function
import argparse
import gzip
import json
import os
import pandas as pd
import re
import sys

rep = {
    'change': 'Change',
    'data': 'Raw',
    'last': 'Last',
}


def main():
    args = parseArgs(sys.argv)
    data = {
        'A': [],
        'B': [],
        'C': [],
    }
    pattern = r'([a-z]+)_([ABC])((?:change)|(?:last)|(?:data))(\.|\d|_)'
    for r, dns, fns in os.walk(args.metricDir):
        for fn in sorted(fns):
            match = re.search(pattern, fn)
            if match:
                try:
                    int(match.group(4))
                    continue
                except:
                    pass
                '''
                print('"{}" "{}" "{}" "{}"'.format(match.group(1),
                                                   match.group(2),
                                                   match.group(3),
                                                   match.group(4)))
                '''
                house = match.group(2)
                row = {}
                row['Model'] = match.group(1).upper()
                row['Feature'] = rep[match.group(3)]
                with gzip.open(os.path.join(r, fn), 'rb') as f:
                    m = json.load(f)
                row['Precision'] = m['precision_score']*100
                row['Recall'] = m['recall_score']*100
                row['F-Measure'] = m['f1_score']*100
                row['Accuracy'] = m['accuracy_score']*100
                # row['CV_Accuracy'] = u'{:.1f}\u00B1{:.1f}'.format(
                row['CV_Accuracy'] = '${:.1f}\pm{:.1f}$'.format(
                    m['cv_acc_mean']*100, m['cv_acc_std']*100)
                # row['CV_Accuracy'] = '{:.1f}'.format(
                #     m['cv_acc_mean']*100)
                data[house].append(row)
            else:
                print('Invalid file name: {}'.format(os.path.join(r, fn)))
    with open(args.latexFile, 'w') as f:
        f.write('\documentclass{article}\n')
        f.write('\usepackage{booktabs}\n')
        f.write('\\begin{document}\n')
        for house, rowList in data.items():
            f.write('\\textbf{{House {}}}\\\\\n'.format(house))
            f.write('\\vspace{1cm}\\\\\n')
            df = pd.DataFrame(rowList, columns=['Model', 'Feature', 'Precision',
                                                'Recall', 'F-Measure',
                                                'Accuracy', 'CV_Accuracy'])
            df.set_index(['Model', 'Feature'], inplace=True)
            tex = df.to_latex(float_format=lambda x: '{:.1f}'.format(x))
            tex = tex.replace('textbackslash', '')
            tex = tex.replace('\$', '$')
            f.write('{}'.format(tex))
            f.write('\\vspace{1cm}\\\\\n')
            # df.to_latex(f, formatters={'CV_Accuracy': lambda x: x})
            # df.to_latex(f, formatters={'CV_Accuracy': lambda x: u'{}'.format(x)})
        f.write('\end{document}')


def parseArgs(args):
    parser = argparse.ArgumentParser(
        description=('Create CSV for results table. '
                     'Written in Python 2.7.'),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('metricDir',
                        help='Directory containing calculated metrics.')
    parser.add_argument('latexFile',
                        help='Name of LaTeX file to save tables.')
    return parser.parse_args()


if __name__ == '__main__':
    main()
