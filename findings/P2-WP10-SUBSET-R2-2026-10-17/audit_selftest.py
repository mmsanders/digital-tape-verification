"""Coordinate regression: setup I/O must not shift operation cuts/errors."""
from audit import boundary

operation=[{'t':'W','phase':'op','call':i+1,'lba':3000+i} for i in range(1028)]
setup={'t':'W','phase':'setup','call':0,'lba':0}
honest=boundary([setup]+operation,8000)
assert honest['op_units']==1028
assert 1020 in honest['cut_units'] and 1029 not in honest['cut_units']
assert 1019 in honest['error_write_calls'] and 1028 not in honest['error_write_calls']
mutated=boundary([dict(setup,phase='op')]+operation,8000)
assert mutated['op_units']==1029
assert 1020 not in mutated['cut_units'] and 1029 in mutated['cut_units']
assert 1019 not in mutated['error_write_calls'] and 1028 in mutated['error_write_calls']
# Whole-call grouping plus internal unit cuts: one metadata call with three units.
multi=[{'t':'W','phase':'op','call':19,'lba':8+i} for i in range(3)]
q=boundary([setup]+multi+[{'t':'F','phase':'op'}],8000)
assert q=={'op_units':3,'cut_units':[0,1,2,3],'error_write_calls':[0],'barriers':1}
print('coordinate regression: honest setup separation PASS; deliberately misclassified setup detected; multi-unit call PASS')
