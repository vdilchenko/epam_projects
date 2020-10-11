import os
from collections import defaultdict
import argparse


parser = argparse.ArgumentParser(description=u"""Allows to hardlink all the equal files in the directory""")
parser.add_argument('path', type=str, metavar="PATH", help=u"Path to the dir")


def main(path_dir):
    filenames = defaultdict(list)
    for path, subdirs, files in os.walk(path_dir):
        for name in files:
            filenames[name].append(os.path.join(path, name))

    if all(len(v) == 1 for v in filenames.values()):
        exit("No equal matches found")

    for k in filenames.keys():
        names = []
        if len(filenames[k]) > 1:
            lead = filenames[k][0]
            names.append(lead)
            for val in filenames[k]:
                if val not in names:
                    os.remove(val)
                    os.link(lead, val)
                    print(f"/{'/'.join(val.split('/')[-2:])} is hardlinked with /{'/'.join(lead.split('/')[-2:])}")


if __name__ == "__main__":
    path_dir = parser.parse_args().path
    if os.path.isdir(path_dir):
        main(path_dir)
    else:
        raise Exception("Wrong path!")
