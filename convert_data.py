import os
import json
import nltk

def replace_special_tokens(str_):
    special_tokens = [".", ",", "?", "/", ";", ":", "<", ">", "[", "]", "/", "|", "'", '"', "{", "}",
                      "-", "+", ")", "(", "_", "=", "!", "*", "&", "^", "%", "$", "#", "@", "~", "`",
                      "’", "“", "”", "–", "—"]
    for token_ in special_tokens:
        str_ = str_.replace(token_, " ")
    return str_.strip().replace("  ", " ")

class AnnSent():
    def __init__(self, sent):
        self.sent = sent
        self.pre_atts = []

    def annotate_part(self, text, att_type, source):
        self.pre_atts.append((text,att_type,source))


    def process_data(self):
        self.sent = replace_special_tokens(self.sent)
        self.attitudes = []
        for att in self.pre_atts:
            text, att_type, source = att
            text = replace_special_tokens(text)
            attitude_info = {"att_type": att_type, "source": source}
            tokens = nltk.word_tokenize(self.sent)
            tokens = nltk.word_tokenize(text)
            if self.sent.count(text) == 1:
                trigger = {"text": text}
            elif self.sent.count(text) == 0:
                assert False
            else:
                print("duplicates")
                print(text)
                print(self.sent)
                print("_____")


def find_the_sent(indexes_list, start_index):
    # finds the sentence an annotated part belongs to, using the start index
    for i in range(len(indexes_list)):
        if(start_index < indexes_list[i]):
            break
        else:
            continue
    if start_index>=indexes_list[-1]:
        return len(indexes_list)-1
    return i -1


def convert_Data(dir, datapath, targetpath):
    annpath = os.path.join(datapath, "man_anns")
    docpath = os.path.join(datapath, "docs")
    dir = dir.strip()
    with open(os.path.join(annpath, dir, "gateman.mpqa.lre.2.0"), 'r') as f:
        anns = f.readlines()
    with open(os.path.join(annpath, dir, "gatesentences.mpqa.2.0"), 'r') as f:
        sent_anns = f.readlines()
    with open(os.path.join(docpath, dir), 'r') as f:
        doc = f.read()


    sents = {}
    annsents = []

    for sent_ann in sent_anns:
        splitted = sent_ann.split('\t')
        assert len (splitted)==4
        start, end = splitted[1].split(',')
        start = int(start)
        end = int(end)
        sents[start] = (start, end)

    sent_starts = list(sents.keys())
    sent_starts.sort()

    for sent_start in sent_starts:
        start,end = sents[sent_start]
        sentence = doc[start:end]
        annsents.append(AnnSent(sentence))

    ds_atts = [] # tuples of attitude link and nested source
    att_dict = {}
    for annotation in anns:
        parts = annotation.split("\t")
        if "GATE_direct-subjective" in annotation:
            assert parts[3] =='GATE_direct-subjective'
            attributes = parts[4]

            #links are a list, source a string
            if "attitude-link=" not in attributes or "nested-source=" not in attributes:
                continue
            attitude_links = attributes.split("attitude-link=")[1]
            attitude_links = attitude_links.split('"')[1]
            attitude_links = attitude_links.split(',')
            nested_source = attributes.split("nested-source=")[1].split('"')[1]

            for alink in attitude_links:
                ds_atts.append((alink.strip(),nested_source))

        elif "GATE_attitude" in annotation:
            assert parts[3] == 'GATE_attitude'
            if 'id="' not in annotation:
                print("id not detected for annotation", dir, annotation)
                continue
            id = annotation.split('id="')[1].split('"')[0]
            assert "," not in id
            att_dict[id] = annotation
        elif "GATE_intention" in annotation:
            id = annotation.split('id="')[1].split('"')[0]
            assert "," not in id
            att_dict[id] = annotation

    for alink, source in ds_atts:
        if alink == "":
            continue
        if not alink in att_dict:
            continue

        att_ann = att_dict[alink]
        att_type = att_ann.split("attitude-type=")[1].split('"')[1]
        start, end = att_ann.split("\t")[1].split(',')
        start = int(start)
        end = int(end)

        att_text = doc[start:end]

        sent_num = find_the_sent(sent_starts, start)
        if att_text in annsents[sent_num].sent:
            annsents[sent_num].annotate_part(att_text, att_type, source)
        elif att_text in annsents[sent_num].sent+'"': #one error due to quotation mark being outside
            annsents[sent_num].sent= annsents[sent_num].sent + '"'
            annsents[sent_num].annotate_part(att_text, att_type, source)
        else:
            print("skipping due to sentence split error") #4 errors because missplit sentence



    for annsent in annsents:
        annsent.process_data()











