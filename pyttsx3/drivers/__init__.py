'''
Speech driver implementations.

Copyright (c) 2009, 2013 Peter Parente

Permission to use, copy, modify, and distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
'''

'''
Utility functions to help with Python 2/3 compatibility
'''
from .. import six

def toUtf8(value):
    '''
    Takes in a value and converts it to a text (unicode) type.  Then decodes that
    type to a byte array encoded in utf-8.  In 2.X the resulting object will be a
    str and in 3.X the resulting object will be bytes.  In both 2.X and 3.X any
    object can be passed in and the object's __str__ will be used (or __repr__ if
    __str__ is not defined) if the object is not already a text type.
    '''
    return six.text_type(value).encode('utf-8')

def fromUtf8(value):
    '''
    Takes in a byte array encoded as utf-8 and returns a text (unicode) type.  In
    2.X we expect a str type and return a unicde type.  In 3.X we expect a bytes
    type and return a str type.
    '''
    return value.decode('utf-8')
