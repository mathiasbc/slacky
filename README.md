Slacky
======

This is a weekend project that started for me as a way to learn
how to write old style command line interfaces. Slack is a tool
a lot of programmers use today so I thought a lot of you would 
have interest in contributing to this effor.

![Looking nice!](https://github.com/mathiasbc/slacky/blob/master/img/slacky.jpg)

Status
------

This is a minimal working version, will surely have several bugs
and many features are missing but I hope I find time to continue
the effort to develop this project and hopefully some of you might
show interest in contributing with this.

Development
-----------

First you'll need to get yourself a Slack API Token, which you
can get at: https://api.slack.com/tokens

Then clone this repo, `cd` and get a python environment setup:

    $ git clone https://github.com/mathiasbc/slacky
    $ cd slacky
    $ python install -r requirements.txt

Then you need to set the Slack API Token in the Environment like:

    $ export SLACK_TOKEN=<my_slack_token_here>;

Finally the fun:

    $ python slacky/skin.py


Commands
--------

The idea is for Slacky to be as intuitive as the Slack original
client, but we are far from that, for the moment.

    Up/Down arrows: navigate contacts section.
    Right arrow: Access a chat, load messages from it
    Enter: Send the message typed in the textarea below.


