#!/usr/bin/env python
"""A small wrapper around nosetests.
Turns down the iso8601 logging level-
this is otherwise disruptive when viewing error messages.
"""
import sys
import nose

if __name__ == "__main__":
    import logging
    logging.getLogger('iso8601').setLevel(logging.ERROR) #Suppress iso8601 debug log.
    logging.getLogger().setLevel(logging.ERROR)
    nose.run(argv=sys.argv)
