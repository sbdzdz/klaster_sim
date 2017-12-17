# -*- coding: utf-8 -*-
"""
Created on Mon Jul 17 12:36:04 2017

@author: Ines.Moskal
"""
import subprocess
import os
import glob
import numpy as np
from tkinter import *
from userbin import USRBIN
from matplotlib import pyplot as plt 
import shutil
#energy changing function
def change_e(line, energia):
    source, beamenergy, l_square, spacing, spotsize = line.split()
    beamenergy = ("{0:.4f}".format(energia))
    print(beamenergy)
    #line="{}       {}        {}       {}       {}\n".format(source, beamenergy, l_square, spacing, spotsize) for rpp_mouse
    #for steps object
    line="{}   {}       {}      {}       {}\n".format(source, beamenergy, l_square, spacing, spotsize)
    return line
    

#changing the position of object
def move_z(line, delta):
    #linie dzielimy na zmienne (odzielone spacją sa kolumny, * oznacza resztę)
    shape, name, *dimensions = line.split() 
    #konwertujemy dimensions ze stringow na liczby
    dimensions = [float(dim) for dim in dimensions]
    #zmieniamy ostatnie dwa elementy (-1 ostatni, -2 przedostatni)
    dimensions[-1] += delta 
    dimensions[-2] += delta 
    #laczymy dimensions w jeden string 
    #(w join tworzenie listy nie wymaga [], bo wystarczy mu cokolwiek iterującego)
    dimensions = ' '.join(str(dim) for dim in dimensions)
    #sklejamy linijke (\t tabulator, \n koniec linijki)
    line = "{} {}      {}\n".format(shape, name, dimensions)
    return line

#changing the position of the detector
def move_det(line, delta, mouse_pos):
    #linie dzielimy na zmienne (odzielone spacją sa kolumny, * oznacza resztę)
    shape, name, *dimensions = line.split() 
    #konwertujemy dimensions ze stringow na liczby
    dimensions = [float(dim) for dim in dimensions]
    #zmieniamy ostatnie dwa elementy (-1 ostatni, -2 przedostatni)
    #zmiana odległości detektora od końca myszy
    dimensions[-1] += (mouse_pos + delta)
    dimensions[-1] = ("{0:.4f}".format(dimensions[-1]))
    dimensions[-2] += (mouse_pos + delta)
    dimensions[-2] = ("{0:.4f}".format(dimensions[-2]))
    
    #laczymy dimensions w jeden string 
    #(w join tworzenie listy nie wymaga [], bo wystarczy mu cokolwiek iterującego)
    dimensions = ' '.join(str(dim) for dim in dimensions)
    #sklejamy linijke (\t tabulator, \n koniec linijki)
    line = "{} {}   {}\n".format(shape, name, dimensions)
    return line
    
#changing the position of the USRBIN  
def move_usrbin(line, deltao, deltad, mouse_pos):
    #zmieniamy podkreslenie na spacje
    line = line.replace("_", " ")
    #linie dzielimy na zmienne 
    usrbin, val1, val2, pos1, pos2, pos3, pos4, name = line.split() 
    #zmiana odległości detektora od końca myszy
    bin_name = ('PROTON', "ENERGY")
    if val2.startswith(bin_name):
        #zmieniam pozycje na float a potem spowrotem na string
        pos4 = float(pos4)
        pos4 += (mouse_pos + deltad) 
        pos4 = ("{0:.4f}".format(pos4))
        pos4 = str(pos4)
        print(pos4)
        #sklejamy linijke (\t tabulator, \n koniec linijki)
        line = "{}           {}    {}      {}       {}      {}    {}_{}\n".format(usrbin, val1, val2, pos1, pos2, pos3, pos4, name)
    elif val2.startswith("DOSE"):
        #zmieniam pozycje na float a potem spowrotem na string
        print(pos4)
        pos4 = float(pos4)
        pos4 += deltao 
        pos4 = ("{0:.3f}".format(pos4))
        pos4 = str(pos4)
        print(pos4)
        #sklejamy linijke (\t tabulator, \n koniec linijki)
        line = "{}           {}      {}      {}      {}     {}     {}_{}\n".format(usrbin, val1, val2, pos1, pos2, pos3, pos4, name)
    elif val1.startswith("-1.25"): 
        pos1 = float(pos1)
        pos1 += deltao
        pos1 = ("{0:.3f}".format(pos1))
        pos1 = str(pos1)
        print(pos1)
        line = "{}         {}     {}     {}       {}       {}      {} {}\n".format(usrbin, val1, val2, pos1, pos2, pos3, pos4, name)
    else: 
        pos1 = float(pos1)
        pos1 += (mouse_pos + deltad)
        pos1 = ("{0:.3f}".format(pos1))
        pos1 = str(pos1)
        print(pos1)
        line = "{}          {}     {}     {}     {}      {}        {} {}\n".format(usrbin, val1, val2, pos1, pos2, pos3, pos4, name)
    return line
    
#finds the end of the object (to move the detector respectively)
def get_end(dimensions, delta): 
    dimensions = [float(dim) for dim in dimensions]
    position = dimensions[-1] + delta
    return position

#checks if the resultsfolder already exists    
def ensure_dir(file_path):
    #directory = os.path.dirname(file_path)
    if not os.path.exists(file_path):
        os.mkdir(file_path)
    
    
#generating of the new inputs
#infile- original file, outfile- new generated file, delta-how much we want to move it
def generate_file(infile, outfile, delta1, delta2, energy):
    with open(infile, 'r') as inp, open(outfile, 'w') as out:
        mouse_end = 0.0
        for line in inp:
            if line.startswith('RPP'):
                shape, name, *dims = line.split()
                #change object position
                if name.startswith('step'):
                    line = move_z(line, delta1)
                    mouse_end = max(mouse_end, get_end(dims, delta1))
                #change detector position
                if name.startswith('detector'):
                    line = move_det(line, delta2, mouse_end)
            #change usrbin position (usrbin)
            elif line.startswith('USRBIN'):
            	line = move_usrbin(line, delta1, delta2, mouse_end)
            elif line.startswith('SOURCE'):
                line = change_e(line, energy)
            #jesli nie zaczyna się na RPP to przepisuje linijke z oryginalnego pliku    
            out.write(line)

#merges USRBIN
def merge_one_estimator(folder, nr, estimator, minfiles):
    files = glob.glob(os.path.join(folder,'*.'+nr))
    if len(files) < minfiles: 
        print('Not enough files to merge')
        exit()
    else:
        subprocess.call(['/project/med2/I.Moskal/sim/simulation_steps/merge_bash.sh', folder, nr, estimator])
    return
    
#merges USRBINs and creates ASCII
def merge_all_estimators(folder, infile, minfiles):
    #otworzyć inputfile by otrzymac wszystkie usbriny do zmergowania
    with open(os.path.join(folder, infile)) as fin: 
        all_lines = fin.readlines()

    #search input file line by line for string beginning with USR 
    for ll in all_lines:
        if ll.startswith('USRBIN') and ll.endswith('&\n')==False:
            nr = ll[37:39]
            estimator = 'USRBIN'
            merge_one_estimator(folder, nr, estimator, minfiles)
    return

#moves the simulation files into the respective folder
def move_files(folder, name, outfile_without_ext, path_out):
    ext = ('.out', '.err', '.19', '.log', '.24', '.inp', '.23','.21','.22','.25','.26','.27','.28','.29','.30','.31')
    for e in ext:
        files = glob.glob(os.path.join(folder,'{}_*'.format(name)+e))
        for file in files: 
            name_file = os.path.split(file)[1]
            name_path = os.path.join(path_out, name_file)
            os.rename(file, name_path)
        ranfiles = glob.glob(os.path.join(folder,'ran*'))
        for file in ranfiles: 
            os.remove(file)

def proces_usrbin(outfile):
    usrbins = sorted(glob.glob(os.path.join(folder, '*usrbin*')))
    for bin in usrbins:
        print(bin)
        proces = USRBIN(bin)
        outfile_cut_inp = os.path.splitext(outfile)[0]
        path_outfile = os.path.join(folder, name, outfile_cut_inp)
        ensure_dir(path_outfile)
        #addes png
        usrbinname = bin.split('/')[-1]
        namestr = (path_outfile, usrbinname)
        newname = ''.join(namestr)
        print(newname)
        #zmienia nazwe i wrzuca do katalogu o nazwie inputu
        move = os.rename(bin, newname)


        
          
#input file
name = 'steps'
infile = '{}.inp'.format(name)
#values for object and detector (o - obiekt, det - detector respectively to the object)
values_o = [2.0]
values_det = [0.2]
#number of cycles
minfiles = 5
#folder where the program is running, path - path to the file
folder = '/project/med2/I.Moskal/sim/simulation_steps'
path = os.path.join(folder, name)
#energia = [0.00679, 0.00801, 0.01009, 0.01188, 0.01346, 0.01491, 0.01626, 0.01752, 0.01870, 0.01984]
energia = np.arange(0.0174, 0.0185, 0.0001)
#energia = [0.0082]



for value_o in values_o:
    for value_det in values_det:
        for e in energia:
            #nazwa pliku wyjsciowego
            nazwae = ("{0:.3f}".format(e*1000))
            outfile = '{}/{}/{}_{}MeV_{}det.inp'.format(folder, name, name, nazwae, value_det)
            ensure_dir(path)
            #zmiana tdanych w inputfilu (zmiana pozycji detektora, obiektu oraz usrbin_fluence)
            generate_file(infile, outfile, value_o, value_det, e)
            #uruchomienie fluki

fluka_cluster = subprocess.call("/project/med2/I.Moskal/sim/runfluka_dclaster.sh", shell=True)

            

'''
            fluka = subprocess.Popen(['/software/opt/xenial/x86_64/fluka/2011.2c.5/flutil/rfluka', '-e', '/home/i/Ines.Moskal/Documents/mouse_fluka/execute_original', '-M5', outfile])
            #czeka do zakończeniu procesu by wykonać następny krok
            fluka.wait()
            #merge usrbin files
            merge_all_estimators(folder, outfile, minfiles)
            proces_usrbin(outfile)
            
            outfile_cut_inp = os.path.splitext(outfile)[0]
            path_outfile = os.path.join(folder, name, outfile_cut_inp)
            move_files(folder, name, outfile_cut_inp, path_outfile)
   ''' 
        
