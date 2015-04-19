#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from blackhole.app.engine import Blackhole


def main():
    app = Blackhole()
    app.run()

if __name__ == "__main__":
    main()
