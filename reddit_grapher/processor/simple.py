import json
import nltk
import re
import collections
import datetime
import tqdm



IGNORE_LIST = nltk.corpus.stopwords.words() + ['nt']

SMALLEST_INTERVAL = 30
EARLIEST_TIME = 1484544784


def clean_token_list(token_list):
    new_list = []
    for tkn in token_list:
        filter_pattern = re.compile("[^a-zA-z]")
        new_word = filter_pattern.sub('', tkn)
        new_word = new_word.lower()
        if new_word and len(new_word) > 1 and new_word not in IGNORE_LIST:
            new_list.append(new_word)
    return new_list


def build_wc_matrix(read_stream):
    data = json.load(read_stream)

    comment_data = sorted(data['comments'], key=lambda x: x['created'])

    if EARLIEST_TIME:
        start_index = 0
        for c in range(len(comment_data)):
            if float(comment_data[c]['created']) >= EARLIEST_TIME:
                start_index = c
                break
        comment_data = comment_data[start_index:]
        interval_end = EARLIEST_TIME + SMALLEST_INTERVAL
    else:
        interval_end = float(comment_data[0]['created']) + SMALLEST_INTERVAL

    full_sect_word_list = []
    sect_word_list = []
    test_time = []
    for i, cd in tqdm.tqdm(enumerate(comment_data)):
        if interval_end <= float(cd['created']):
            test_time.append(str(interval_end))
            interval_end += SMALLEST_INTERVAL
            full_sect_word_list.append(sect_word_list)
            sect_word_list = []

        snt_tkns = nltk.sent_tokenize(cd['body'])
        for snt in snt_tkns:
            sect_word_list += clean_token_list(nltk.word_tokenize(snt))

    interval = 2
    full_size = len(full_sect_word_list)
    word_list = {}

    for i in tqdm.tqdm(range(full_size)):
        start_offset = i - int(interval/2 * 60/SMALLEST_INTERVAL)
        end_offset = i + int(interval/2 * 60/SMALLEST_INTERVAL)

        if start_offset < 0:
            start_offset = 0
        if end_offset > full_size - 1:
            end_offset = end_offset

        interval_list = [word for sect in full_sect_word_list[start_offset:end_offset] for word in sect]
        wrd_cnt_lst = collections.Counter(interval_list)
        for word in wrd_cnt_lst.keys():
            value = wrd_cnt_lst.get(word)
            word_list.setdefault(word, [0]*full_size)[i] = value

    with open('{}-matrix.txt'.format(read_stream.name.split('.')[0]), 'w') as output_file:
            output_file.write("\t" + "\t".join(test_time))
            for word in tqdm.tqdm(word_list.keys()):
                output_file.write("{}\t{}\n".format(word, "\t".join(map(str, word_list[word]))))

    with open('{}-wrdcnt.txt'.format(read_stream.name.split('.')[0]), 'w') as ttl_wrd_cnt_file:
        sorted_wordcount = sorted([(word, sum(word_list[word]))
                                   for word in tqdm.tqdm(word_list.keys())], key=lambda x: x[1])
        for w in sorted_wordcount:
            ttl_wrd_cnt_file.write("{}: {}\n".format(w[0], w[1]))
