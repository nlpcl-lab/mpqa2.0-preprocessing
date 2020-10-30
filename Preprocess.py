import os
import argparse
from convert_data import convert_Data

datapath = os.getcwd() + "/mpqa2"
parsedpath = os.getcwd() + "/ParsedData"

assert os.path.exists(datapath)
if not os.path.exists(parsedpath):
    os.makedirs(parsedpath)

# The subsets according to doclist. Note that opqa subset is a subset of mpqaOriginal subset, so it is not looked for.
# Set use_ulas argument to true to use the last two subsets.

subsets = ['mpqaOriginal', 'xbank', 'ula-lu', 'ula']

def get_subset_dirs(keyword):
    fname = os.path.join(datapath, "doclist." + keyword + "Subset")
    assert os.path.exists(fname)

    with open(fname, 'r') as f:
        dirs = f.readlines()

    return dirs

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--use_ulas", type=bool, default=False)

    args = parser.parse_args()
    if not args.use_ulas:
        subsets = subsets[:-2]

    all_dirs = []
    for subset in subsets:
        subdirs = get_subset_dirs(subset)
        all_dirs.extend(subdirs)

    # Some do not have attitude annotations, and should not be used
    atts = get_subset_dirs("attitude")

    used_dirs = [x for x in all_dirs if x in atts]

    print("Total number of documents to be used : ", len(used_dirs))

    for dir in used_dirs:
        convert_Data(dir, datapath, parsedpath)