#!/usr/bin/env python
import curses
import curses.textpad
import os
import logging
import locale

from slack import Slack


locale.setlocale(locale.LC_ALL, "")


LOGGER = logging.getLogger(__name__)
LOG_FORMAT = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


def rel(path):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), path)


def set_color_pairs():
    # based on the colors of pyradio
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
    curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(8, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(9, curses.COLOR_BLACK, curses.COLOR_GREEN)


class Skin(object):
    startPos = 0

    def __init__(self):
        self.stdscr = None
        # instantiate a Slack client
        self.slack_client = Slack()
        # print(self.slack_client.get_channels())
        # print(self.slack_client.get_ims())

        self.contact_list = self.slack_client.get_contacts_names()
        self.showing = 0
        self.selection = 0
        # proportion of the left panel body, to the chat panel
        self.body_proportion = 0.20
        # vertical proportion of text area against chat window
        self.text_area_proportion = 0.20

    def setup(self, stdscr):
        self.stdscr = stdscr
        # define curses color pairs
        set_color_pairs()
        # set getch to blocking
        self.stdscr.nodelay(0)
        # don't echo key strokes on the screen
        curses.noecho()
        # read keystrokes instantly, without waiting for enter to be pressed
        curses.cbreak()
        # enable keypad mode
        self.stdscr.keypad(1)
        # draw the main frame
        self.setup_draw()
        self.run()

    def setup_draw(self):
        # get screen dimensions
        self.maxY, self.maxX = self.stdscr.getmaxyx()
        # n_lines, n_cols, begin_y, begin_x
        self.headWin = curses.newwin(1, self.maxX, 0, 0)
        # left panel, contacts
        self.bodyWin = curses.newwin(
            self.maxY - 1,
            int(self.maxX * self.body_proportion),
            1,
            0)
        # right chat window
        self.chat_win = curses.newwin(
            self.maxY - 1 - int(self.maxY * self.text_area_proportion),
            self.maxX - int(self.maxX * self.body_proportion),
            1,
            int(self.maxX * self.body_proportion))
        # bottom textarea window
        self.text_win = curses.newwin(
            int(self.maxY * self.text_area_proportion),
            self.maxX - int(self.maxX * self.body_proportion),
            self.maxY - int(self.maxY * self.text_area_proportion),
            int(self.maxX * self.body_proportion))
        self.init_head()
        self.init_body()
        self.init_chat()
        self.init_textbox()
        self.bodyWin.keypad(1)
        curses.doupdate()

    def init_head(self):
        name = "Slacky"
        middle_pos = int(self.maxX/2 - len(name)/2)
        self.headWin.addstr(0, middle_pos, name, curses.color_pair(2))
        self.headWin.bkgd(' ', curses.color_pair(7))
        self.headWin.noutrefresh()

    def init_body(self):
        """
        Initializes the body/story window
        """
        self.bodyMaxY, self.bodyMaxX = self.bodyWin.getmaxyx()
        self.bodyWin.noutrefresh()
        self.refresh_body()

    def init_chat(self):
        """
        Draw the initial chat window
        """
        self.chat_max_y, self.chat_max_x = self.chat_win.getmaxyx()
        self.bodyWin.noutrefresh()
        self.refresh_chat()

    def init_textbox(self):
        """
        Draws the textbox under the chat window
        """
        self.text_max_y, self.text_max_x = self.text_win.getmaxyx()
        self.textbox = curses.textpad.Textbox(self.text_win)

        self.text_win.refresh()
        self.refresh_textbox()

    def set_body_selection(self, number):
        """
        Select chat
        """
        self.selection = number
        maxDisplayedItems = self.bodyMaxY - 2
        if self.selection - self.startPos >= maxDisplayedItems:
            self.startPos = self.selection - maxDisplayedItems + 1
        elif self.selection < self.startPos:
            self.startPos = self.selection

    def refresh_body(self):
        self.bodyWin.erase()
        self.bodyWin.box()
        maxDisplay = self.bodyMaxY - 1
        for lineNum in range(maxDisplay - 1):
            i = lineNum + self.startPos
            if i < len(self.contact_list):
                self.__display_body_line(lineNum, self.contact_list[i])
        self.bodyWin.refresh()

    def __display_body_line(self, lineNum, station):
        col = curses.color_pair(5)

        if lineNum + self.startPos == self.selection and self.selection == self.showing:
            col = curses.color_pair(9)
            self.bodyWin.hline(lineNum + 1, 1, ' ', self.bodyMaxX - 2, col)
        elif lineNum + self.startPos == self.selection:
            col = curses.color_pair(6)
            self.bodyWin.hline(lineNum + 1, 1, ' ', self.bodyMaxX - 2, col)
        elif lineNum + self.startPos == self.showing:
            col = curses.color_pair(4)
            self.bodyWin.hline(lineNum + 1, 1, ' ', self.bodyMaxX - 2, col)
        line = "{0}. {1}".format(lineNum + self.startPos + 1, station)
        self.bodyWin.addstr(lineNum + 1, 1, line, col)

    def refresh_chat(self):
        self.chat_win.box()
        self.chat_win.refresh()

    def refresh_textbox(self):
        self.text_win.box()
        start_text = self.text_win.getparyx()
        # self.text_win.addstr(1, 1, "Typed text goes here")
        self.text_win.refresh()

    def run(self):
        self.refresh_body()
        while True:
            try:
                c = self.bodyWin.getch()
                ret = self.keypress(c)
            except KeyboardInterrupt:
                break

    def keypress(self, char):
        # right arrow select a user/group to chat with
        if char == curses.KEY_RIGHT:
            self.showing = self.selection
            self.refresh_body()
            self.setup_draw()
            return

        # moves to the user/group below current selection
        elif char == curses.KEY_DOWN:
            if self.selection < len(self.contact_list) - 1:
                self.set_body_selection(self.selection + 1)
            self.refresh_body()
            return

        # move cursor one position up
        elif char == curses.KEY_UP:
            if self.selection > 0:
                self.set_body_selection(self.selection - 1)
            self.refresh_body()
            return

        # send the char to textbox area
        # else:
            # self.


# This method is callable for testing porpuses only
if __name__ == "__main__":
    slack = Skin()
    curses.wrapper(slack.setup)
