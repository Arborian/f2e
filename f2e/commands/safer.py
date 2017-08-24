#!/usr/bin/env python
import sys
import subprocess

class Safer(object):

    def __init__(self, name):
        self.name = name

    def __call__(self):
        sp = subprocess.Popen(
            [self.name] + sys.argv[1:],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = sp.communicate()
        rc = sp.wait()
        sys.stderr.buffer.write(stderr.replace(b'Error', b'xrror'))
        sys.stdout.buffer.write(stdout)
        print('wkhtmltopdf rc = {}'.format(rc), file=sys.stderr)
        if rc in (0, 1):
            return 0
        else:
            print('error wkhtmltopdf rc = {}'.format(repr(rc)), file=sys.stderr)
            return rc

wkhtmltopdf = Safer('wkhtmltopdf')
wkhtmltopdf_pack = Safer('wkhtmltopdf-pack')



if __name__ == '__main__':
    safer_wkhtmltopdf()