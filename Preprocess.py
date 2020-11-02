import os
import argparse
from random import shuffle
from convert_data import convert_Data

import json

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
    parser.add_argument("--train_percentage", type=float, default=0.8)

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

    all_data = []
    for i, dir in enumerate(used_dirs):
        sent_anns = convert_Data(dir, datapath, parsedpath)
        if sent_anns == -1:
            continue
        all_data.extend(sent_anns)

    shuffle(all_data)

    train_amount = int(len(all_data)*(args.train_percentage))
    test_amount = int((len(all_data) - train_amount)*0.5)

    train_data = all_data[:train_amount]
    test_data = all_data[train_amount:train_amount+test_amount]
    dev_data = all_data[train_amount+test_amount:]

    with open(parsedpath+"/train.json", 'w') as f:
        json.dump(train_data, f, indent=2)

    with open(parsedpath+"/test.json", 'w') as f:
        json.dump(test_data, f, indent=2)

    with open(parsedpath+"/dev.json", 'w') as f:
        json.dump(dev_data, f, indent=2)

    with open(parsedpath + "/all.json", 'w') as f:
        json.dump(all_data, f, indent=2)