#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import numpy as np
import obci.drivers.balance_xwiimote.wii_balance_board_xwiimote_dummy as wii_balance_board_xwiimote

def format_measurement(x):
    return "{0:.2f}".format(x/ 100.0)

def print_bboard_measurements(*args):
    sm = format_measurement(sum(args))
    tl, tr, bl, br = map(format_measurement, args)
    print "{}{}{}".format("┌","─" * 21, "┐")
    print "{}{}{}{}{}".format("│"," " * 8, "{:>5}".format(sm)," " * 8, "│")
    print "{}{}{}{}{}".format("├","─" * 10, "┬", "─" * 10, "┤")
    print "│{:^10}│{:^10}│".format(tl, tr)
    print "{}{}{}{}{}".format("│"," " * 10, "│", " " * 10, "│")
    print "{}{}{}{}{}".format("│"," " * 10, "│", " " * 10, "│")
    print "│{:^10}│{:^10}│".format(bl, br)
    print "{}{}{}{}{}".format("└","─" * 10, "┴", "─" * 10, "┘")
    print "{}".format('\n\n')

def main():
    wbb = wii_balance_board_xwiimote.WiiBalanceBoard()
    t = time.time()
    fs = []
    i = 0
    try:
        while True:
            m, m_t = wbb.measurement()
            if i:
                fs.append(1.0/(m_t-t_last))
            print 'time: {0:.2f} s'.format(m_t-t)
            print_bboard_measurements(*m)
            t_last = m_t
            i+=1

    except KeyboardInterrupt:
        print "\nestimate fs: {} +/- {} Hz".format(np.mean(fs), np.std(fs))

if __name__ == '__main__':
    main()