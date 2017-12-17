import os
import glob
import numpy as np

def pad(value):
    value = str(value)[:10]
    return str.ljust(value, 10)

def build_line(*values):
    line = ''.join(pad(value) for value in values) + '\n'
    return line

def change_energy(line, energy):
    source, beamenergy, l_square, spacing, spotsize = line.split()
    line = build_line(source, energy, l_square, spacing, spotsize)
    return line
    
def move_z(line, delta):
    shape, name, *dimensions = line.split() 
    dimensions = [float(dim) for dim in dimensions]
    dimensions[-1] += delta 
    dimensions[-2] += delta 
    line = build_line(shape, name, *dimensions)
    return line

def move_det(line, delta, mouse_pos):
    shape, name, *dimensions = line.split() 
    dimensions = [float(dim) for dim in dimensions]

    dimensions[-1] += (mouse_pos + delta)
    dimensions[-1] = ("{0:.4f}".format(dimensions[-1]))
    dimensions[-2] += (mouse_pos + delta)
    dimensions[-2] = ("{0:.4f}".format(dimensions[-2]))
    
    line = build_line(shape, name, *dimensions)
    return line
    
def move_usrbin(line, deltao, deltad, mouse_pos):
    line = line.replace("_", " ")
    values = line.split()
    bintype = values[2]

    if bintype.startswith(('PROTON', 'ENERGY')):
        values[6] = float(values[6]) + mouse_pos + deltad
    elif bintype.startswith('DOSE'):
        values[6] = float(values[6]) + deltao
    elif values[1].startswith('-2.5'):
        values[3] = float(values[3]) + mouse_pos + deltad
    else:
        values[3] = float(values[3]) + deltao

    line = build_line(*values)
    return line
    
def get_end(dimensions, delta): 
    dimensions = [float(dim) for dim in dimensions]
    position = dimensions[-1] + delta
    return position

def ensure_dir(file_path):
    if not os.path.exists(file_path):
        os.mkdir(file_path)
    
def generate_file(infile, outfile, delta1, delta2, energy):
    with open(infile, 'r') as inp, open(outfile, 'w') as out:
        mouse_end = 0.0
        for line in inp:
            if line.startswith('RPP'):
                shape, name, *dims = line.split()
                if name.startswith('step'):
                    line = move_z(line, delta1)
                    mouse_end = max(mouse_end, get_end(dims, delta1))
                if name.startswith('detector'):
                    line = move_det(line, delta2, mouse_end)
            elif line.startswith('USRBIN'):
            	line = move_usrbin(line, delta1, delta2, mouse_end)
            elif line.startswith('SOURCE'):
                line = change_energy(line, energy)
            out.write(line)

infile = 'steps.inp'
values_o = [2.0, 4.0, 6.0]
values_det = [0.2]
energy = [0.0082, 0.0083, 0.0084]
path = './steps'

for value_o in values_o:
    for value_det in values_det:
        for e in energy:
            outfile = '{}/o_{}d_{}e_{}.inp'.format(path, value_o, value_det, e)
            ensure_dir(path)
            generate_file(infile, outfile, value_o, value_det, e)
