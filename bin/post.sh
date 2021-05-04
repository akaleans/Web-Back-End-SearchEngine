#!/bin/sh

# TIMELINES METHODS
http --verbose POST localhost:5100/timelines/post_tweet/ username=kstensby text='Hello, this is my first post!'
http --verbose POST localhost:5100/timelines/post_tweet/ username=zjeffries text='Hello, my name is Zook! And this is my second post!'
http --verbose POST localhost:5100/timelines/post_tweet/ username=rwalls text='Hello, this is Richard Walls, and I will post third!'
http --verbose POST localhost:5100/timelines/post_tweet/ username=zjeffries text='Hello, this is Zook again, fourth post btw'

# SEARCH ENGINE
http GET localhost:5300/index/ id=1
http GET localhost:5300/index/ id=2
http GET localhost:5300/index/ id=3
http GET localhost:5300/index/ id=4

http GET localhost:5300/search/ kw=hello
http GET localhost:5300/any/ kw=richard+zook
http GET localhost:5300/all/ kw=hello+zook+fourth
http GET localhost:5300/exclude/ inc=hello exc=zook
