#!/usr/bin/env python3
# coding=utf-8

import sys

def main():

    try:
        if len(sys.argv) != 2:
            raise ValueError
        sallary = int(sys.argv[1])
    except ValueError:
        print("Parameter Error")
        return -1

