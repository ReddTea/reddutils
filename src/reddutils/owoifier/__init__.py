#!/usr/bin/env python
# -*- coding: utf-8 -*-

def pwint(sentence):
    '''
    Euthanize me senpai
    '''
    s = sentence.replace('r', 'w').replace('l', 'w')
    s = s.replace('na', 'nya').replace('ne', 'nye').replace('ni', 'nyi')
    s = s.replace('no', 'nyo').replace('nu', 'nyu')
    if len(s) > 25:
        s ='UwU whats this?? ' + s
    elif len(s) > 10:
        s += ' OwO'

    print(s)
    pass
