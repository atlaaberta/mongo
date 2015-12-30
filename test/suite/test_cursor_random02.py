#!/usr/bin/env python
#
# Public Domain 2014-2015 MongoDB, Inc.
# Public Domain 2008-2014 WiredTiger, Inc.
#
# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.
#
# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

import wiredtiger, wttest
from helper import complex_populate, simple_populate
from helper import key_populate, value_populate
from wtscenario import check_scenarios, multiply_scenarios, number_scenarios

# test_cursor_random02.py
#    Cursor next_random operations
class test_cursor_random02(wttest.WiredTigerTestCase):
    type = 'table:random'
    config = [
        ('not-sample', dict(config='next_random=true'))
    ]
    records = [
        ('1', dict(records=1)),
        ('250', dict(records=250)),
        ('500', dict(records=500)),
        ('5000', dict(records=5000)),
        ('10000', dict(records=10000)),
        ('50000', dict(records=50000)),
    ]
    scenarios = number_scenarios(multiply_scenarios('.', config, records))

    # Check that next_random works in the presence of a larger set of values,
    # where the values are in an insert list.
    def test_cursor_random_reasonable_distribution(self):
        uri = self.type
        num_entries = self.records

        # Set the leaf-page-max value, otherwise the page might split.
        simple_populate(self, uri,
            'leaf_page_max=100MB,key_format=S', num_entries)
        # Setup an array to track which keys are seen
        visitedKeys = [0] * (num_entries + 1)

        cursor = self.session.open_cursor(uri, None, 'next_random=true')
        for i in range(0, num_entries):
            self.assertEqual(cursor.next(), 0)
            current = cursor.get_key()
            current = int(current)
            visitedKeys[current] = visitedKeys[current] + 1

        differentKeys = sum(x > 0 for x in visitedKeys)

        #print visitedKeys
        #print differentKeys
        '''
        self.tty('differentKeys: ' + str(differentKeys) + ' of ' + \
            str(num_entries) + ', ' + \
            str((int)((differentKeys * 100) / num_entries)) + '%')
        '''

        self.assertGreater(differentKeys, num_entries / 4,
            'next_random random distribution not adequate')

if __name__ == '__main__':
    wttest.run()
