#!/usr/bin/python3
""" Vritten by Vladimir Rainish"""

from sortedcontainers import SortedDict
import sys


def main():
    msize = int(sys.argv[1])

    TOTAL_AMOUNT = 0
    CURRENT_STATE = 1
    TOTAL_PRICE = 2
    PRINT_SYMBOL = 3
    tags = {}
    sells = SortedDict()
    buys = SortedDict()
    sells_state = [0, 'NA', 0, 'B']  # amount, state total price , print
    buys_state = [0, 'NA', 0, 'S']

    for line in sys.stdin:
        l = line.split(' ')
        mil, action, tag, amount = l[0:4]
        if action == 'A':
            side, price, amount = l[3:6]
            # remove decimal dot
            #price = int(price.replace(".", ""))
            price = int(price[:-3] + price[-2:])
        amount = int(amount)

        if action == 'A':
            tags[tag] = (side, price, amount)
        else:
            side, price, tag_amount = tags[tag]
            if tag_amount == amount:
                del tags[tag]
            else:
                tags[tag] = (side,price,tag_amount - amount)

        if side == 'S':
            prices = sells
            state = sells_state
        else:
            prices = buys
            state = buys_state
            price = -price

        if action == 'A':
            state[TOTAL_AMOUNT] += amount
            prices[price] = prices[price] + \
                amount if price in prices else amount
        else:
            state[TOTAL_AMOUNT] -= amount
            if prices[price] == amount:
                del prices[price]
            else:
                prices[price] -= amount

        if state[TOTAL_AMOUNT] < msize:
            if state[CURRENT_STATE] == 'AV':
                # AV -> NA
                state[CURRENT_STATE] = 'NA'
                state[TOTAL_PRICE] = 0
                print(mil, " ", state[PRINT_SYMBOL], " NA", sep="")
            continue

        # NA -> AV , AV -> AV
        state[CURRENT_STATE] = 'AV'

        recomputed_price = 0
        amount_needed = msize
        for bid_price in iter(prices):
            bid_amount = prices[bid_price]
            if bid_amount < amount_needed:
                recomputed_price += bid_price * bid_amount
                amount_needed -= bid_amount
            else:
                recomputed_price += bid_price * amount_needed
                break

        if recomputed_price != state[TOTAL_PRICE]:
            state[2] = recomputed_price
            print_price = abs(state[TOTAL_PRICE])
            # reinsert decimal dot
            to_print = str(print_price)[:-2] + '.' + str(print_price)[-2:]
            print(mil, " ", state[PRINT_SYMBOL], " ", to_print, sep="")
    # end loop over lines
# end Pricer

if __name__ == "__main__":
    main()
