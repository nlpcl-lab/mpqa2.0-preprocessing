import os
import json
import nltk

def convert_Data(dir, datapath, targetpath):
    annpath = os.path.join(datapath, "man_anns")
    docpath = os.path.join(datapath, "docs")
    dir = dir.strip()
    with open(os.path.join(annpath, dir, "gateman.mpqa.lre.2.0"), 'r') as f:
        anns = f.readlines()

    with open(os.path.join(docpath, dir), 'r') as f:
        doc = f.read()

    j_data = {}
    sents = []
    for sent in nltk.sent_tokenize(doc):
        sents.extend(sent.split("\n\n"))

    #sents = list(filter(lambda x : len(x) > 5, sents))

    sent_indexes =[]
    for i, sent in enumerate(sents):
        if i ==0:
            sent_indexes.append(len(sent))
        else:
            sent_indexes.append(len(sent)+sent_indexes[-1]+2)

    #sents = sents[1:]



    ds_atts = [] # tuples of attitude link and nested source
    att_dict = {}
    for annotation in anns:
        parts = annotation.split("\t")
        if "GATE_direct-subjective" in annotation:
            assert parts[3] =='GATE_direct-subjective'
            attributes = parts[4]

            #links are a list, source a string
            attitude_links = attributes.split("attitude-link=")[1].split('"')[1].split(',')
            nested_source = attributes.split("nested-source=")[1].split('"')[1]

            for alink in attitude_links:
                ds_atts.append((alink.strip(),nested_source))

        elif "GATE_attitude" in annotation:
            assert parts[3] == 'GATE_attitude'
            id = annotation.split('id="')[1].split('"')[0]
            assert "," not in id
            att_dict[id] = annotation

    for alink, source in ds_atts:
        if not alink in att_dict:
            print(alink)
            print("____\n", att_dict.keys())
        assert alink in att_dict
        att_ann = att_dict[alink]
        att_type = att_ann.split("attitude-type=")[1].split('"')[1]
        start, end = att_ann.split("\t")[1].split(',')
        start = int(start)
        end = int(end)
        att_text = doc[start:end]
        try_text = att_text
        candidates = [x for x in sents if try_text in x]
        while len(candidates)>1:
            print(att_text)
            print(candidates)
            print(doc[start-10:end+10])
            input()







