#!/usr/bin/python3
""" Vritten by Vladimir Rainish"""

from sortedcontainers import SortedDict
import PrintDS as p


class Tags():

    def __init__(self, debug, opt, stat):
        self.tags = {}
        #self_last_add = []
        #self.tags = SortedDict()
        self.DEBUG, self.OPT, self.STAT = debug, opt, stat

        if self.STAT:
            self.line_num = 0
            self.live_tag = {}
        return

    #
    # Add Tag
    #
    def add(self, tag, amount, side, price):

        self.tags[tag] = [side, price, int(amount)]

        if self.STAT:
            self.add_tag_live(tag, amount)

        return

    #
    # Remove tag
    #
    def rem(self, tag, amount):

        side, price, tag_amount = self.tags[tag]  # must be in Tags
        if int(amount) == tag_amount:
            del self.tags[tag]
        else:
            self.tags[tag][2] -= int(amount)

        if self.STAT:
            self.rem_tag_live(tag, amount)

        return side, price

    # for statistics only
    def add_tag_live(self, tag, amount):
        p.s('Tags_number ', len(self.tags))  # stat for number of tags

        self.line_num += 1
        #self.last_add = [self.line_num,int(amount)]
        self.live_tag[tag] = [self.line_num, int(amount)]
        #self.live_tag[tag] = self.last_add
        #.p.d("ID",id(self.last_add), "-> ", id(self.live_tag[tag]))
        return

    # for statistics only
    def rem_tag_live(self, tag, amount):
        p.s('Tags_number ', len(self.tags))  # stat for number of tags

        self.line_num += 1
        if tag in self.live_tag.keys():
            if self.live_tag[tag][1] == int(amount):
                p.s('TagLive', tag, self.line_num - self.live_tag[tag][0])
                del self.live_tag[tag]
            else:
                self.live_tag[tag][1] -= int(amount)
        return

    def print_tags(self):
        p.d("Tags")
        for tag, val in sorted(self.tags.items()):
            p.d(tag, " -> ", val)
        p.d("-----------")
        return

# end class Tags;


def main():
    t = Tags(True, False, False)

    t.add('add-only', 10, 'B', 4486)
    t.print_tags()

    t.add('add--rem', 15, 'S', 3386)
    t.print_tags()

    side, price = t.rem('add--rem', 6)
    p.d("restored side : ", side, "restored price : ", price)
    t.print_tags()

    side, price = t.rem('add-only', 10)
    p.d("restored side : ", side, "restored price : ", price)
    t.print_tags()
    return

if __name__ == '__main__':
    main()
