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

    def annotate_part(self, text, att_type, source, offset):
        self.pre_atts.append((text,att_type,source, offset))


    def process_data(self):
        clean_sent = replace_special_tokens(self.sent)
        attitudes = []
        for att in self.pre_atts:
            text, att_type, source, offset = att
            clean_text = replace_special_tokens(text)

            tokens = nltk.word_tokenize(clean_sent)
            trigger_tokens = nltk.word_tokenize(clean_text)

            new_start = len(nltk.word_tokenize(replace_special_tokens(self.sent[:offset])))
            trigger = {"text": clean_text, "start": new_start, "end": new_start+len(trigger_tokens)}
            if not tokens[new_start:new_start+len(trigger_tokens)] == trigger_tokens:
                # 4 cases skipped due to annotation errors
                continue
                # print(tokens[new_start:new_start+len(trigger_tokens)])
                # print(trigger_tokens)
                # print(text)
                # print(self.sent)
                # print(clean_sent)
                # input('error')
            attitude_info = {"att_type": att_type, "source": source, "trigger": trigger}
            attitudes.append(attitude_info)
        return {"sentence": clean_sent, "attitudes": attitudes}



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
    # broken sentence annotations
    if dir.strip() == 'xbank/wsj_0583':
        return -1
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
        offset = start - sent_starts[sent_num]
        if att_text in annsents[sent_num].sent:
            annsents[sent_num].annotate_part(att_text, att_type, source, offset)
        elif att_text in annsents[sent_num].sent+'"': #one error due to quotation mark being outside
            annsents[sent_num].sent= annsents[sent_num].sent + '"'
            annsents[sent_num].annotate_part(att_text, att_type, source, offset)
        else:
            print("skipping due to sentence split error") #4 errors because missplit sentence


    results = []
    for annsent in annsents:
        sentence = annsent.process_data()
        results.append(sentence)
    return results











