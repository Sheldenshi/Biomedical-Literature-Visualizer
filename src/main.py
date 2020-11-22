"""
This script parses the CORD-19 dataset, annotates sentences with Named Entities, and 
saves the annotated sentences.

Usage with default options: 
python main.py --data-dir /path/to/CORD_19_RC/

Usage with manually set options: 
python main.py --config /path/to/config.yaml --data-dir /path/to/CORD_19_RC/ --bern False --stanza True --num-batches 10

Author - Tornike Tsereteli
"""

import os
import json

import re
import stanza
import sentence_splitter
import yalafi
import pandoc
from pandoc.types import Space, Str
from collections import defaultdict

import requests
import logging
import argparse
import configparser
from tqdm import tqdm


def tex2str(sentence):
    doc = pandoc.read(sentence)

    tokens = []

    for t in doc[1][0][0]:
        if isinstance(t, Space):
            tokens.append(" ")
        elif isinstance(t, Str):
            tokens.append(str(t[0]))

    return "".join(tokens)


def print_entities(sentence):
    for ner in ners:
        doc = ner(sentence)
        # print out all entities
        for ent in doc.entities:
            print(f"{ent.text}\t{ent.type}")


def get_entities(text, ners):
    entities = []
    for ner in ners:
        doc = ner(text)
        for ent in doc.entities:
            entities.append([ent.text, ent.type, ent.start_char, ent.end_char])
    return entities


def has_latex(sentence):
    commands = ["\\usepackage", "\\begin", "\\end", "\\setlength"]

    for c in commands:
        if c in sentence:
            return True
    return False


def query_raw(text, url="https://bern.korea.ac.kr/plain"):
    return requests.post(url, data={"sample_text": text}).json()


def get_datafiles(path_dir):
    assert os.path.isdir(path_dir)
    datafiles = []
    for dirname, _, filenames in os.walk(path_dir):
        for filename in filenames:
            ifile = os.path.join(dirname, filename)
            if ifile.split(".")[-1] == "json":
                datafiles.append(ifile)
    return datafiles


def map_ners_to_sentences(sentences, entities):
    res = defaultdict(list)
    c = 0
    incorrect = 0
    correct = 0
    for word, ent, start, end in tqdm(entities):
        l_start = 0
        for sent in sentences:
            l_end = l_start + len(sent)
            if start >= l_start and end <= l_end:
                if sent[start - l_start : end - l_start] != word:
                    print(c, sent, start - l_start, end - l_start, word, ent)
                    incorrect += 1
                    continue
                res[sent] += [[word, ent, start - l_start, end - l_start]]
                correct += 1
            l_start = l_end + 1
            c += 1

    print(correct, incorrect)
    return res


def load_ners(
    pack="mimic",
    anatem=True,
    bc5cdr=True,
    bc4chemd=True,
    bionlp13cg=True,
    jnlpba=True,
    linnaeus=True,
    s800=True,
    i2b2=True,
    radiology=True,
):
    procs = []

    if anatem:
        procs.append("anatem")
    if bc5cdr:
        procs.append("bc5cdr")
    if bc4chemd:
        procs.append("bc4chemd")
    if bionlp13cg:
        procs.append("bionlp13cg")
    if jnlpba:
        procs.append("jnlpba")
    if linnaeus:
        procs.append("linnaeus")
    if s800:
        procs.append("s800")
    if i2b2:
        procs.append("i2b2")
    if radiology:
        procs.append("radiology")

    ners = []

    for proc in procs:
        stanza.download("en", package=pack, processors={"ner": proc})
        ner = stanza.Pipeline("en", package=pack, processors={"ner": proc})
        ners.append(ner)

    return ners


def get_datafiles(path_dir):
    assert os.path.isdir(path_dir)
    datafiles = []
    for dirname, _, filenames in os.walk(path_dir):
        for filename in filenames:
            ifile = os.path.join(dirname, filename)
            if ifile.split(".")[-1] == "json":
                datafiles.append(ifile)
    return datafiles


def make_batches(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last) : int(last + avg)])
        last += avg

    return out


def extract_ner_sentences(
    datafiles, parsed_papers, ners=None, bern=False, stanza=False, num_batches=10
):
    doc_entities = {}
    doc_counter = 0
    sent_counter = 0

    # split processing documents into batches
    batches = make_batches(datafiles, num_batches)

    for i, batch in tqdm(enumerate(batches)):
        logging.info(f"Processing batch {str(i)}.")
        docs = []

        for j, path in enumerate(batch):
            try:
                logging.info(
                    f"Processing document {str(j)} of {str(len(batch))} documents in batch {str(i)}."
                )
                # read file
                with open(path, "r") as infile:
                    paper_json = json.load(infile)

                paper_id = paper_json["paper_id"]

                # ignore already processed documents
                if paper_id in parsed_papers:
                    continue

                paper_title = paper_json["metadata"]["title"]
                bib_entries = paper_json["bib_entries"]

                doc = ""

                # aggregate all paragraphs for each document
                for text_json in paper_json["body_text"]:
                    text = text_json["text"]
                    section = text_json["section"]

                    doc += section + "\n" + text + "\n"

                # remove latex code from text
                text = tex2str(doc)

                if bern:
                    # process text with BERN NER model
                    res = query_raw(text)
                    doc_entities[paper_id] = res
                    parsed_papers.append(paper_id)

                elif stanza and ners:
                    # process text with stanza NER models
                    sentences = sentence_splitter.split_text_into_sentences(
                        text, language="en"
                    )
                    sent_entity_pairs = []
                    for sent in tqdm(sentences):
                        if not sent or sent == " ":
                            continue
                        try:
                            entities = get_entities(sent, ners)
                            if entities:
                                sent_entity_pairs.append([sent, entities])
                                sent_counter += 1
                        except:
                            logging.error(f'Could not process sentence: "{sent}"')
                    doc_entities[paper_id] = sent_entity_pairs
                    parsed_papers.append(paper_id)

                # save parsed NER sentences
                if j > 0 and j % 10 == 0:
                    doc_counter += 1

                    with open(f"./output/{str(doc_counter)}.json", "w") as f:
                        json.dump(doc_entities, f)
                    with open(f"./parsed_papers.txt", "a") as f:
                        for pid in parsed_papers:
                            f.write(pid + "\n")

                    doc_entities = {}

                    logging.info(
                        f"Saved processed sentences to: {str(doc_counter)}.json"
                    )
            except:
                logging.error(f"Could not process document {str(j)} in batch {str(i)}.")

    logging.info(
        f"Done!\nProcessed {str(doc_counter)} documents and {str(sent_counter)} sentences."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        required=False,
        default="./config.yaml",
        help="Path to config file.",
    )
    parser.add_argument(
        "--data-dir", required=True, help="Path to data directory.",
    )
    parser.add_argument(
        "--bern",
        required=False,
        default=False,
        help="Set to True if using the BERN NER model.",
    )
    parser.add_argument(
        "--stanza",
        required=False,
        default=True,
        help="Set to True if using stanza NER models.",
    )
    parser.add_argument(
        "--num-batches", required=False, default=10, help="Size of batch of documents.",
    )
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(args.config)
    config_ner = config["ners"]

    # read file locations
    data_dir = os.path.join(args.data_dir, "document_parses")
    assert os.path.isdir(data_dir)
    datafiles = get_datafiles(data_dir)

    # load NER models
    ners = load_ners(
        anatem=config_ner["anatem"],
        bc5cdr=config_ner["bc5cdr"],
        bc4chemd=config_ner["bc4chemd"],
        bionlp13cg=config_ner["bionlp13cg"],
        jnlpba=config_ner["jnlpba"],
        linnaeus=config_ner["linnaeus"],
        s800=config_ner["s800"],
        i2b2=config_ner["i2b2"],
        radiology=config_ner["radiology"],
    )

    # load already processed files
    parsed_papers = []

    parsed_papers_file = "./parsed_papers.txt"
    if os.path.isfile(parsed_papers_file):
        with open(parsed_papers_file, "r") as f:
            parsed_papers = f.read().split("\n")
    if not os.path.isdir("./output"):
        os.makedirs("./output")

    # parse sentences and extract sentences with NERs
    extract_ner_sentences(
        datafiles,
        parsed_papers,
        ners=ners,
        bern=args.bern,
        stanza=args.stanza,
        num_batches=args.num_batches,
    )
