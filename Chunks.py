#!/usr/bin/python3
""" Vritten by Vladimir Rainish"""

from sortedcontainers import SortedDict
import PrintDS as p


class Chunks():

    #
    #   __INIT__
    #
    def __init__(self, ids, side_for_print, msize, debug, opt, stat):

        self.ids = ids
        self.side_for_print = side_for_print
        self.msize = msize
        self.DEBUG, self.OPT, self.STAT = debug, opt, stat

        self.prices = SortedDict()  # self.prices = {}
        self.size_value = 0
        self.total_orders = 0
        self.state = 'NA'

        if self.OPT:
            self.last_op = 'R'
            self.lp_price = 0
            self.lp_free = 0
            self.lp_used = 0
            self.lm_price = 0
            self.last_amount = 0
            self.last_price = 0
        if self.STAT:
            self.min_val = 0
            self.max_val = 0
            self.no_recompute = 0
            self.do_recompute = 0
            self.chunk_size1 = 32
            self.chunk_map1 = self.chunk_size1 - 1
            self.key_map1 = ~ self.chunk_map1
        if self.DEBUG:
            self.chunk_size1 = 32
            self.chunk_map1 = self.chunk_size1 - 1
            self.key_map1 = ~ self.chunk_map1
        return
    # end def __init__

    #
    # ADD
    #
    def add(self, price, amount):
        if self.ids == 'B':
            price = -price

        if self.OPT:
            self.last_op, self.last_amount, self.last_price = 'A', amount, price

        self.total_orders += amount
        self.prices[price] = self.prices[price] + amount if price in self.prices else amount

        if self.OPT:
            self.lm_price = price

        if self.STAT:
            self.handle_add_stat(price)
            p.s('DiffPrice', self.ids, price, self.lm_price)
            sd, sz, k1, key_to_reach, step_to_reach = self.get_chunks_stat()
            p.s('DictStat ', sd, sz, k1, key_to_reach, step_to_reach)

        if self.DEBUG:
            self.print_chunks()
        return
    # end def add

    #
    # REMOVE
    #
    def rem(self, price, amount):
        if self.ids == 'B':
            price = -price

        if self.OPT:
            self.last_op, self.last_amount, self.last_price = 'R', amount, price

        self.total_orders -= amount
        if self.prices[price] == amount:
            del self.prices[price]
            if self.STAT:
                self.handle_rem_stat(price)
        else:
            self.prices[price] -= amount

        if self.OPT:
            self.lm_price = price

        if self.STAT:
            p.s('DiffPrice', self.ids, price, self.lm_price)
            sd, sz, k1, key_to_reach, step_to_reach = self.get_chunks_stat()
            p.s('DictStat ', sd, sz, k1, key_to_reach, step_to_reach)

        if self.DEBUG:
            self.print_chunks()
        return
    # end def rem

    #
    # RECOMPUTE
    #
    def recompute(self):
        # recompute also set state , not good for general case but OK for now
        if self.total_orders < self.msize:
            if self.state == 'AV':
                # AV -> NA
                self.state = 'NA'
                self.size_value = 0
                if self.OPT:
                    self.lp_price = 0
                return True
            else:
                # NA -> NA
                return False

        # if here
        # NA -> AV , AV -> AV

        if self.state == 'AV':
            if self.OPT:
                need_to_recompute, print_status = self.optimize_recompute()
                if need_to_recompute == False:
                    if self.DEBUG:
                        if print_status :
                            self.print_chunks()
                    return print_status
        else:
            # always recompute after NA->AV
            self.state = 'AV'

        if self.DEBUG:
            self.print_chunks()

        if self.STAT:
            p.s('Do rec')
            self.do_recompute += 1

        recomputed_price = 0
        amount_needed = self.msize
        if self.STAT:
            step = 0
        # loop over sorted dictionary
        # for bid_price,bid_amount in self.prices.items():
        # for bid_price,bid_amount in self.prices.iteritems():
        # to check why iter() is faster then methods above
        for bid_price in iter(self.prices):
            bid_amount = self.prices[bid_price]
            if bid_amount < amount_needed:
                recomputed_price += bid_price * bid_amount
                amount_needed -= bid_amount
                if self.STAT:
                    step += 1
            else:
                # need to handle equak case specially
                recomputed_price += bid_price * amount_needed
                if self.OPT:
                    self.lp_price = bid_price
                    self.lp_free = bid_amount - amount_needed
                    self.lp_used = amount_needed
                    if self.DEBUG:
                        self.print_fu("after recompute set lpp")
                if self.STAT:
                    step += 1
                    p.s("RecSteps", self.ids, " ", step,
                        self.prices.keys()[0], bid_price)
                    #if bid_amount - amount_needed < 500: print("Cushion ",self.ids," ", amount_needed, " ", bid_amount)
                break

        if recomputed_price != self.size_value:
            self.size_value = recomputed_price
            return True
        else:
            # no change in price after recompute
            return False
    # end def __invert__

    #
    # OPTIMIZE RECOMPUTE
    #
    def optimize_recompute(self):
        # to check why less or equal causes mistakes
        if self.lp_price < self.lm_price:
            if self.STAT:
                self.no_recompute += 1
            if self.DEBUG:
                p.d("NO RCMP/NO PRINT add/remove above lpp : ",
                    self.lp_price, "lmp ", self.lm_price)
            return False, False

        if self.lp_price == self.lm_price:
            if self.last_op == 'A':
                # only need to asjust free amount 
                self.lp_free += self.last_amount
                if self.DEBUG:
                    self.print_fu('NO RCMP/NO PRINT add at lpp')
                return False, False
            else:
                self.lp_free -= self.last_amount
                if self.lp_free >= 0:
                    # only need to adjust free amount 
                    if self.DEBUG:
                        self.print_fu("NO RCMP/NO PRINT rem at lpp")
                    return False, False
                else:
                    # need to recompute
                    # need specail handling if equal, since we neet to adjust
                    # cushion and lpp but price doesn't change
                    self.lp_used += self.lp_free
                    if self.DEBUG:
                        self.print_fu("RCMP/PRINT rem at lpp")
                    return True, 0

        # important when we add or remove at the lpp we need to recompute boundaries even if not printing
        # disable cushioning opt for now
        if self.lp_price > self.lm_price:
            # if we remove bids below last participating price ,msize_price
            # should go up
            if self.last_op == 'R':
                if self.lp_free >= self.last_amount:
                    if self.DEBUG:
                        self.print_fu("NO RCMP/PRINT rem below lpp before")
                    self.lp_free -= self.last_amount
                    self.lp_used += self.last_amount
                    self.size_value += (self.lp_price - self.last_price) * self.last_amount
                    if self.DEBUG:
                        self.print_fu("NO RCMP/PRINT rem below lpp after")
                    return False, True
                else:
                    if self.DEBUG:
                        self.print_fu("RCMP rem below lpp before")
                    self.lp_free -= self.last_amount
                    self.lp_used += self.last_amount
                    if self.DEBUG:
                        self.print_fu("RCMP rem below lpp after")
                    return True, 0
            else:
                # if we add bids below last participating price ,msize_price
                # should go down
                if self.lp_used >= self.last_amount:
                    if self.DEBUG:
                        self.print_fu("NO RCMP/Print add below lpp before")
                    self.size_value -= (self.lp_price - self.last_price) * self.last_amount
                    self.lp_free += self.last_amount
                    self.lp_used -= self.last_amount
                    # if self.lp_used == 0: # MUST handle this case
                       # need to set lpp correctly
                    if self.DEBUG:
                        self.print_fu("NO RCMP/Print add below lpp after")
                    return False, True
                else:
                    if self.DEBUG:
                        self.print_fu("RCMP/Print add below lpp before")
                    self.lp_free += self.last_amount
                    self.lp_used -= self.last_amount
                    if self.DEBUG:
                        self.print_fu("RCMP/Print add below lpp after")
                    return True, 0

        # can't be here
        return True, 0
    # end def optimize_recompute

    # called only if STAT

    #
    #   HANDLE_ADD_STAT
    #
    def handle_add_stat(self, price):
        if self.min_val == 0:
            self.min_val = price
            self.max_val = price
        else:
            if price < self.min_val:
                self.min_val = price
            if price > self.max_val:
                self.max_val = price
        p.s('Chains ', self.ids, " ", len(self.prices),
            " ", self.min_val, " ", self.max_val)
        return
    # end def habdle_add_stat

    # called only if STAT

    #
    #   HANDLE_REM_STAT
    #
    def handle_rem_stat(self, price):
        if int(price) == self.min_val:
            if len(self.prices.keys()) > 0:
                self.min_val = self.prices.keys()[0]
            else:
                self.min_val = 0

        if int(price) == self.max_val:
            if len(self.prices.keys()) > 0:
                self.max_val = self.prices.keys()[len(self.prices.keys()) - 1]
            else:
                self.max_val = 0

        if self.min_val > 0:
            p.s('Chains ', self.ids, " ", len(self.prices),
                " ", self.min_val, " ", self.max_val)
        return
    # end def handle_add_stat_

    #
    #   PRINT_FU
    #
    def print_fu(self, header):
        p.d(header, ' : ', "lpp :", self.lp_price, ":",
            self.lp_used, "/", self.lp_free, "used/free")
        return
    # end def print_fu

    #
    #   PRINT_CHUNKS
    #
    def print_chunks(self):
        if self.total_orders > 0:
            lng = len(self.prices)
            num_keys = 1
            init_key = (self.prices.keys()[0] & self.key_map1)
            for key in iter(self.prices):
                if init_key == (key & self.key_map1):
                    continue
                init_key = key & self.key_map1
                num_keys += 1
        else:
            num_keys = 0
            lng = 0
        p.d("Dict ", self.ids, self.total_orders, "keys", num_keys, "len", lng)
        if len(self.prices) > 0:
            num_keys = 1
            init_key = (self.prices.keys()[0] & self.key_map1)
            for bid_price in iter(self.prices):
                if self.OPT:
                    if init_key != bid_price & self.key_map1:
                        init_key = bid_price & self.key_map1
                        num_keys += 1
                    if bid_price == self.lp_price:
                        p.ds('* ', end='')
                    else:
                        p.ds('  ', end='')
                p.dm(bid_price & self.key_map1, (bid_price & self.key_map1)
                     >> 5, bid_price, " -> ", self.prices[bid_price], end='')
                if self.OPT:
                    if bid_price == self.lp_price:
                        p.dm(':', self.lp_used, '/', self.lp_free,
                             "used/free", "keys to reach", num_keys, end='')
                p.de("")
        return
    # end def print_chunks

    #
    #   GET_CHUNKS_STAT
    #
    def get_chunks_stat(self):
        if self.total_orders > 0:
            lng = len(self.prices)
            num_keys1 = 1
            init_key1 = (self.prices.keys()[0] & self.key_map1)
            amount_needed = self.msize
            key_to_reach = 0
            step_to_reach = 0
            step = 0
            for key in iter(self.prices):

                if init_key1 != (key & self.key_map1):
                    init_key1 = key & self.key_map1
                    num_keys1 += 1
                step += 1
                bid_amount = self.prices[key]
                if amount_needed > 0:
                    amount_needed -= bid_amount
                    if amount_needed <= 0:
                        key_to_reach = num_keys1
                        step_to_reach = step
        else:
            lng = 0
            num_keys1 = 0
            key_to_reach = 0
            step_to_reach = 0
        # return self.ids,lng,num_keys1,num_keys2,num_keys3,key_to_reach
        return self.ids, lng, num_keys1, key_to_reach, step_to_reach

    # end def print_chunks

# end class Chunks


def main():
    # set DEBUG to True
    c = Chunks('S', 'B', 10, True, False, False)

    c.add(-150, 9)
    c.print_chunks()
    print_status = c.recompute()
    p.d(print_status, c.size_value)

    c.add(-150, 1)
    c.print_chunks()
    print_status = c.recompute()
    p.d(print_status, c.size_value)

    c.rem(-150, 2)
    c.print_chunks()
    print_status = c.recompute()
    p.d(print_status, c.size_value)

    c.add(-150, 2)
    c.print_chunks()
    print_status = c.recompute()
    p.d(print_status, c.size_value)
    return

if __name__ == '__main__':
    main()
