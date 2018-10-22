import os
import subprocess

EBOOK_CONVERT = os.getenv('EBOOK_CONVERT')


def convert(input_filepath, output_filepath):
    print("%s -> %s" % (input_filepath, output_filepath))
    p = subprocess.Popen([EBOOK_CONVERT, input_filepath, output_filepath])
    r = p.wait()
    print("exit code", r)
    return r
