#!/usr/bin/env python
import curses
import curses.textpad
import os
import locale

from slack import Slack


locale.setlocale(locale.LC_ALL, "")


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
        # find what's the erase character
        self.del_char = curses.erasechar()
        self.run()

    def setup_draw(self):
        # get screen dimensions
        self.maxY, self.maxX = self.stdscr.getmaxyx()
        # n_lines, n_cols, begin_y, begin_x
        self.head_win = curses.newwin(1, self.maxX, 0, 0)
        # left panel, contacts
        self.body_win = curses.newwin(
            self.maxY - 1,
            int(self.maxX * self.body_proportion),
            1,
            0)
        # left chat window
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

        self.textarea = curses.newwin(
            int(self.maxY * self.text_area_proportion) - 2,
            self.maxX - int(self.maxX * self.body_proportion) - 2,
            self.maxY - int(self.maxY * self.text_area_proportion) + 1,
            int(self.maxX * self.body_proportion) + 1)

        self.init_head()
        self.init_body()
        self.init_chat()
        self.init_textbox()
        self.init_textarea()
        self.body_win.keypad(1)
        curses.doupdate()

    def init_head(self):
        name = "Slacky (github.com/mathiasbc)"
        middle_pos = int(self.maxX/2 - len(name)/2)
        self.head_win.addstr(0, middle_pos, name, curses.color_pair(2))
        self.head_win.bkgd(' ', curses.color_pair(7))
        self.head_win.noutrefresh()

    def init_body(self):
        """
        Initializes the body/story window
        """
        self.bodyMaxY, self.bodyMaxX = self.body_win.getmaxyx()
        self.body_win.noutrefresh()
        self.refresh_body()

    def init_chat(self):
        """
        Draw the initial chat window
        """
        self.chat_max_y, self.chat_max_x = self.chat_win.getmaxyx()
        self.body_win.noutrefresh()
        self.chat_win.box()
        self.refresh_chat()

    def init_textbox(self):
        """
        Draws the textbox under the chat window
        """
        self.text_win.refresh()
        self.text_win.box()
        self.refresh_textbox()

    def init_textarea(self):
        # the current displayed text
        self.char_pos = [0, 0]
        self.text = ""
        self.textarea.refresh()
        self.refresh_textarea()

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
        self.body_win.erase()
        self.body_win.box()
        maxDisplay = self.bodyMaxY - 1
        for lineNum in range(maxDisplay - 1):
            i = lineNum + self.startPos
            if i < len(self.contact_list):
                self.__display_body_line(lineNum, self.contact_list[i])
        self.body_win.refresh()

    def __display_body_line(self, lineNum, station):
        col = curses.color_pair(5)

        # if the cursor is on the highligted chat/group
        is_current = self.selection == self.showing

        if lineNum + self.startPos == self.selection and is_current:
            col = curses.color_pair(9)
            self.body_win.hline(lineNum + 1, 1, ' ', self.bodyMaxX - 2, col)
        elif lineNum + self.startPos == self.selection:
            col = curses.color_pair(6)
            self.body_win.hline(lineNum + 1, 1, ' ', self.bodyMaxX - 2, col)
        elif lineNum + self.startPos == self.showing:
            col = curses.color_pair(4)
            self.body_win.hline(lineNum + 1, 1, ' ', self.bodyMaxX - 2, col)
        line = "{0}. {1}".format(lineNum + self.startPos + 1, station)
        self.body_win.addstr(lineNum + 1, 1, line, col)

    def refresh_chat(self):
        self.chat_win.refresh()

    def refresh_textbox(self, char=None):
        self.text_win.refresh()

    def refresh_textarea(self, char=None):
        # draws a border on the window
        self.textarea.addstr(0, 0, self.text)
        self.textarea.refresh()

    def backspace(self):
        self.text = self.text[:-1]
        self.textarea.clear()
        self.refresh_textarea()

    def run(self):
        self.refresh_body()
        while True:
            try:
                c = self.body_win.getch()
                ret = self.keypress(c)
            except KeyboardInterrupt:
                break

    def keypress(self, char):
        # right arrow select a user/group to chat with
        if char == curses.KEY_RIGHT:
            self.showing = self.selection
            self.refresh_body()
            return

        if char == curses.KEY_LEFT:
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

        # send the content on the textbox
        elif char == curses.KEY_ENTER or chr(char) == "\n":
            # make sure to clean the text
            self.char_pos = [1, 1]
            self.text = ""
            self.textarea.clear()
            self.refresh_textarea()
            return

        # delete a character
        elif chr(char) == self.del_char or chr(char) == "\x7f" or char == curses.KEY_BACKSPACE:
            self.backspace()
            return

        # send the char to textbox area
        else:
            self.text += chr(char)
            self.refresh_textarea(char)
            return


# This method is callable for testing porpuses only
if __name__ == "__main__":
    slack = Skin()
    curses.wrapper(slack.setup)
