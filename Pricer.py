#!/usr/bin/python3

import PrintDS as p
#import Stat as s
from Tags import Tags
from Chunks import Chunks
import sys
from enum import Enum


class Pricer():

    def __init__(self, size, stat, debug, opt, step, out):
        self.msize = size
        self.STAT, self.DEBUG, self.OPT  = stat , debug, opt
        self.step = step
        self.out = out
        return

    def launch_pricer(self):
        tags = Tags(self.DEBUG, self.OPT, self.STAT)
        sells = Chunks('S', 'B', self.msize, self.DEBUG, self.OPT, self.STAT)
        buys = Chunks('B', 'S', self.msize, self.DEBUG, self.OPT, self.STAT)
        # Action = Enum('Action', 'Add Remove') Enum is very slow

        # if self.STAT: line_num = 0
        # iterate over lines
        # step for debugging only
        if self.step > 0:
            cstep = 0
        if self.out > 0:
            outcount = 0
        for line in sys.stdin:
            # if self.STAT: line_num +=1
            if self.DEBUG:
                p.d('', '+++++++++++++++++++++++++++++++++++++++++++++++\n', '*', line)

            if self.STAT:
                p.s('Line ', line.strip())
            # process line
            '''
            mil, action, tag, rem = line.split(' ', 3)
            # action =  Action.Add if action == 'A' else Action.Remove
            # if action == Action.Remove:
            if action == 'R':
                amount = rem
            else:
                side, price, amount = rem.split(' ')
                # works only because there is ALWAYS two digits after dot even
                # 1.00
                price = price.replace(".", "")
                price = int(price)
            '''
            # much faster, may be because split is called only once
            # alo list slicing slows things a little
            l = line.split(' ')
            # first 3 is fixed, it's milliseconds,R/A for action and tag
            # if action is A then it's B/S for side, price and amount
            #
            # 12345 A abc B 44.33 100
            #
            # if action is R it's only amount
            #
            # 12345 R abc 100
            mil, action, tag, amount = l[0:4] # if action is R it's enough
            if action == 'A':
                side,price,amount = l[3:6]
                # works only because there is ALWAYS two digits after dot even
                # 1.00 or 0.50
                # price = int(price.replace(".", ""))
                price = int(price[:-3] + price[-2:])
            amount = int(amount)

            # add tag or
            # remove tag completely or partually and
            # retrive its side and price
            # process prices (side and price has been restored in case of 'R'
            if action == 'A': # if action == Action.Add:  # Enum is very slow
                tags.add(tag, amount, side, price)
                prices = sells if side == 'S' else buys
                prices.add(price, amount)
            else:
                side, price = tags.rem(tag, amount)
                prices = sells if side == 'S' else buys
                prices.rem(price, amount)

            #if action == 'A': # if action == Action.Add: # Enum is slow
            #else:

            # recompute price
            #Status is True if we need to print or False if not
            # if Status is True and price is 0 we print NA

            # print results
            # insert dot in second position from right  not sure this works if
            # msize_price is less the 1

            #need_to_print = prices.recompute()
            #if need_to_print :
            if prices.recompute():
                if prices.size_value != 0:
                    print_price = abs(prices.size_value) # need to change the name
                    # reinsert decimal dot
                    to_print = str(print_price)[:-2] + '.' + str(print_price)[-2:]
                    print(mil, " ", prices.side_for_print, " ", to_print, sep="")
                else:
                    print(mil, " ", prices.side_for_print, " NA", sep="")
                if self.out > 0:
                    outcount += 1
                    if outcount == self.out:
                        break

            if self.step > 0:
                cstep += 1
                if self.step == cstep:
                    break
        # end loop over lines
        return
    # end launch_pricer()
# end class Pricer

import argparse


def main():
    parser = argparse.ArgumentParser(
        description='RGM Advisors challenge.\nSubmitted to RGM March 2011 by Vladimir Rainish',
        usage='\n%(prog)s [optional arguments] size < input_file > output_file')
    parser.add_argument(
        '-S', '--stat', action='store_true', help='Print statistics. False by default')
    parser.add_argument(
        '-D', '--debug', action='store_true', help='Print Debug info, False by default')
    parser.add_argument(
        '-N', '--noopt', action='store_false', help='Cancel performance optimisations')
    parser.add_argument(
        '--step', help='Performs n steps only', type=int, default=0)
    parser.add_argument(
        '--out', help='Print n output', type=int, default=0)
    parser.add_argument(
        'size', help='Defines size, must be a positive interger. No default', type=int)

    args = parser.parse_args()

    pricer = Pricer(
        args.size, args.stat, args.debug, args.noopt, args.step, args.out)
    pricer.launch_pricer()
    return

if __name__ == "__main__":
    main()
