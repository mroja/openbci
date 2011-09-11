#!/usr/bin/env python
# -*- coding: utf-8 -*-


number_of_decisions = 6
number_of_states = 77
states_configs = ['screen', 'graphics', 'graphics_solver', 'actions', 'actions_solver']
other_configs = []




screen = number_of_states * [number_of_decisions * [0]]
screen[0]  = [ 1, 1, 1, 1, 0, 0]
screen[1]  = [ 1, 0, 0, 0, 0,11]
screen[11] = [16,12,11,31, 0, 0]
screen[12] = [11,13,12,41, 0, 0]
screen[13] = [12,14,13,51, 0, 0]
screen[14] = [13,15,14,61, 0, 0]
screen[15] = [14,16,15,71, 0, 0]
screen[16] = [15,11,16,16, 0, 0]
screen[21] = [26,22,12,21, 0, 0]
screen[22] = [21,23,13,22, 0, 0]
screen[23] = [22,24,14,23, 0, 0]
screen[24] = [23,25,15,24, 0, 0]
screen[25] = [24,26,16,25, 0, 0]
screen[26] = [25,21,11,26, 0, 0]
screen[31] = [36,32,12,31, 0, 0]
screen[32] = [31,33,13,32, 0, 0]
screen[33] = [32,34,14,33, 0, 0]
screen[34] = [33,35,15,34, 0, 0]
screen[35] = [34,36,16,35, 0, 0]
screen[36] = [35,31,11,36, 0, 0]
screen[41] = [46,42,12,41, 0, 0]
screen[42] = [41,43,13,42, 0, 0]
screen[43] = [42,44,14,43, 0, 0]
screen[44] = [43,45,15,44, 0, 0]
screen[45] = [44,46,16,45, 0, 0]
screen[46] = [45,41,11,46, 0, 0]
screen[51] = [56,52,12,51, 0, 0]
screen[52] = [51,53,13,52, 0, 0]
screen[53] = [52,54,14,53, 0, 0]
screen[54] = [53,55,15,54, 0, 0]
screen[55] = [54,56,16,55, 0, 0]
screen[56] = [55,51,11,56, 0, 0]
screen[61] = [66,62,12,61, 0, 0]
screen[62] = [61,63,13,62, 0, 0]
screen[63] = [62,64,14,63, 0, 0]
screen[64] = [63,65,15,64, 0, 0]
screen[65] = [64,66,16,65, 0, 0]
screen[66] = [65,61,11,66, 0, 0]
screen[71] = [76,72,12,71, 0, 0]
screen[72] = [71,73,13,72, 0, 0]
screen[73] = [72,74,14,73, 0, 0]
screen[74] = [73,75,15,74, 0, 0]
screen[75] = [74,76,16,75, 0, 0]
screen[76] = [75,71,11,76, 0, 0]




graphics = number_of_states * [number_of_decisions * [""]]
graphics[0] = ['','','','','','',]
graphics[1] = ['','','','','','']
graphics[11] = ['clear','ABCDEX','FGHIJX','WYZXXX','PRSTUX','KLMNOX',]
graphics[12] = ['ABCDEX','FGHIJX','KLMNOX','clear','WYZXXX','PRSTUX',]
graphics[13] = ['FGHIJX','KLMNOX','PRSTUX','ABCDEX','clear','WYZXXX',]
graphics[14] = ['KLMNOX','PRSTUX','WYZXXX','FGHIJX','ABCDEX','clear',]
graphics[15] = ['PRSTUX','WYZXXX','clear','KLMNOX','FGHIJX','ABCDEX',]
graphics[16] = ['WYZXXX','clear','ABCDEX','PRSTUX','KLMNOX','FGHIJX',]
graphics[21] = ['','','','','','',]
graphics[22] = ['','','','','','',]
graphics[23] = ['','','','','','',]
graphics[24] = ['','','','','','',]
graphics[25] = ['','','','','','',]
graphics[26] = ['','','','','','',]
graphics[31] = ['A','B','C','<','E','D',]
graphics[32] = ['B','C','D','A','<','E',]
graphics[33] = ['C','D','E','B','A','<',]
graphics[34] = ['D','E','<','C','B','A',]
graphics[35] = ['E','<','A','D','C','B',]
graphics[36] = ['<','A','B','E','D','C',]
graphics[41] = ['F','G','H','<','J','I',]
graphics[42] = ['G','H','I','F','<','J',]
graphics[43] = ['H','I','J','G','F','<',]
graphics[44] = ['I','J','<','H','G','F',]
graphics[45] = ['J','<','F','I','H','G',]
graphics[46] = ['<','F','G','J','I','H',]
graphics[51] = ['K','L','M','<','O','N',]
graphics[52] = ['L','M','N','K','<','O',]
graphics[53] = ['M','N','O','L','K','<',]
graphics[54] = ['N','O','<','M','L','K',]
graphics[55] = ['O','<','K','N','M','L',]
graphics[56] = ['<','K','L','O','N','M',]
graphics[61] = ['P','R','S','<','U','T',]
graphics[62] = ['R','S','T','P','<','U',]
graphics[63] = ['S','T','U','R','P','<',]
graphics[64] = ['T','U','<','S','R','P',]
graphics[65] = ['U','<','P','T','S','R',]
graphics[66] = ['<','P','R','U','T','S',]
graphics[71] = ['W','Y','Z','<','<','<',]
graphics[72] = ['Y','Z','<','W','<','<',]
graphics[73] = ['Z','<','<','Y','W','<',]
graphics[74] = ['<','<','<','Z','Y','W',]
graphics[75] = ['<','<','W','<','Z','Y',]
graphics[76] = ['<','W','Y','<','<','Z',]




graphics_solver = number_of_states * [number_of_decisions * [""]]




actions = number_of_states * [number_of_decisions * [""]]
actions[0] = [u"msg(u'KALIBRACJA: Proszę mocno przewracać oczami.')","","","","",""]
actions[1] = ["","","","","","clear()"]
actions[11] = ["","","","","",""]
actions[12] = ["","","","","",""]
actions[13] = ["","","","","",""]
actions[14] = ["","","","","",""]
actions[15] = ["","","","","",""]
actions[16] = ["","","","clear()","",""]
actions[21] = ["","","","","",""]
actions[22] = ["","","","","",""]
actions[23] = ["","","","","",""]
actions[24] = ["","","","","",""]
actions[25] = ["","","","","",""]
actions[26] = ["","","","","",""]
actions[31] = ["","","",'msg("B")',"",""]
actions[32] = ["","","",'msg("C")',"",""]
actions[33] = ["","","",'msg("D")',"",""]
actions[34] = ["","","",'msg("E")',"",""]
actions[35] = ["","","","backspace()","",""]
actions[36] = ["","","",'msg("A")',"",""]
actions[41] = ["","","",'msg("G")',"",""]
actions[42] = ["","","",'msg("H")',"",""]
actions[43] = ["","","",'msg("I")',"",""]
actions[44] = ["","","",'msg("J")',"",""]
actions[45] = ["","","","backspace()","",""]
actions[46] = ["","","",'msg("F")',"",""]
actions[51] = ["","","",'msg("L")',"",""]
actions[52] = ["","","",'msg("M")',"",""]
actions[53] = ["","","",'msg("N")',"",""]
actions[54] = ["","","",'msg("O")',"",""]
actions[55] = ["","","","backspace()","",""]
actions[56] = ["","","",'msg("K")',"",""]
actions[61] = ["","","",'msg("R")',"",""]
actions[62] = ["","","",'msg("S")',"",""]
actions[63] = ["","","",'msg("T")',"",""]
actions[64] = ["","","",'msg("U")',"",""]
actions[65] = ["","","","backspace()","",""]
actions[66] = ["","","",'msg("P")',"",""]
actions[71] = ["","","",'msg("Y")',"",""]
actions[72] = ["","","",'msg("Z")',"",""]
actions[73] = ["","","","backspace()","",""]
actions[74] = ["","","","backspace()","",""]
actions[75] = ["","","","backspace()","",""]
actions[76] = ["","","",'msg("W")',"",""]




actions_solver = number_of_states * [number_of_decisions * [""]]