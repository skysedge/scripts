#!/bin/bash

mplayer -vf rotate=2  tv:// -tv device=/dev/video0 &
mplayer -vf rotate=2  tv:// -tv device=/dev/video2
