import sys
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedSeq as cs
from ruamel.yaml.comments import TaggedScalar as ts
from ruamel.yaml.scalarstring import SingleQuotedScalarString as sq
from ruamel.ordereddict import ordereddict


yaml_doc = """\
version: 0
projects:
  - name: A1
    dir: B1
    wflow: l
"""
yaml = YAML()
# yaml.preserve_quotes = True
# yaml.width = 4096
data = yaml.load(yaml_doc)
print(data)

ref = data['projects']
print(ref)
# record_to_add = dict(name='A2', dir='B2', aplan=dict(when=["X", "Y", "Z"]), wflow='l')
# ref.append(record_to_add)
#
record_to_add_2 = ordereddict([('name', 'A3'), ('dir', 'B3'), ('aplan', ordereddict([('when', ['X', 'Y', 'Z'])])), ('wflow', 'l')])
ref.append(record_to_add_2)

yaml.dump(data, sys.stdout)