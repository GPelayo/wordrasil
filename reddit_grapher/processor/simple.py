import nltk
import re
import peakutils
import numpy


IGNORE_LIST = nltk.corpus.stopwords.words() + ['nt']

ROOT_COMMENTS_KEY = 'comments'
CREATED_COMMENTS_KEY = 'created'

TIME_INTERVAL = 30
CUTOFF_TIME = 400


def clean_token_list(token_list):
    new_list = []
    for tkn in token_list:
        filter_pattern = re.compile("[^a-zA-z]")
        new_word = filter_pattern.sub('', tkn)
        new_word = new_word.lower()
        if new_word and len(new_word) > 1 and new_word not in IGNORE_LIST:
            new_list.append(new_word)
    return new_list


class WordrasilCommentArrays:
    timestamp_list = []
    comment_count_list = []


class Discussion:
    earliest_time = -1
    latest_time = 2**31

    def __init__(self, data):
        self.init_time_ranges(data)
        self.comments = data
        self.comment_list = {}
        self._build_timeline()

    def init_time_ranges(self, data):
        time = [t for t in map(lambda x: x[CREATED_COMMENTS_KEY], data[ROOT_COMMENTS_KEY])]
        self.earliest_time = float(min(time))
        # self.latest_time = float(max(time))
        self.latest_time = self.earliest_time + CUTOFF_TIME * TIME_INTERVAL

    def _build_timeline(self):
        for comment in self.comments[ROOT_COMMENTS_KEY]:
            timeline_address = float(comment[CREATED_COMMENTS_KEY])//TIME_INTERVAL * TIME_INTERVAL
            self.comment_list.setdefault(timeline_address, []).append(comment)
            # TODO: Find more dynamic way to cutoff trivial comment data
            if timeline_address > self.latest_time:
                break


# def build_wc_matrix(read_stream):
#     data = json.load(read_stream)
#     build_time_array(data)

    # start_index = 0
    # for c in range(len(comment_data)):
    #     if float(comment_data[c]['created']) >= earliest_time:
    #         start_index = c
    #         break
    # comment_data = comment_data[start_index:]
    # interval_end = earliest_time + SMALLEST_INTERVAL
    #
    # full_sect_word_list = []
    # sect_word_list = []
    # test_time = []
    # for i, cd in tqdm.tqdm(enumerate(comment_data)):
    #     if interval_end <= float(cd['created']):
    #         test_time.append(str(interval_end))
    #         interval_end += SMALLEST_INTERVAL
    #         full_sect_word_list.append(sect_word_list)
    #         sect_word_list = []
    #
    #     snt_tkns = nltk.sent_tokenize(cd['body'])
    #     for snt in snt_tkns:
    #         sect_word_list += clean_token_list(nltk.word_tokenize(snt))
    #
    # interval = 2
    # full_size = len(full_sect_word_list)
    # word_list = {}
    #
    # for i in tqdm.tqdm(range(full_size)):
    #     start_offset = i - int(interval/2 * 60/SMALLEST_INTERVAL)
    #     end_offset = i + int(interval/2 * 60/SMALLEST_INTERVAL)
    #
    #     if start_offset < 0:
    #         start_offset = 0
    #     if end_offset > full_size - 1:
    #         end_offset = end_offset
    #
    #     interval_list = [word for sect in full_sect_word_list[start_offset:end_offset] for word in sect]
    #     wrd_cnt_lst = collections.Counter(interval_list)
    #     for word in wrd_cnt_lst.keys():
    #         value = wrd_cnt_lst.get(word)
    #         word_list.setdefault(word, [0]*full_size)[i] = value
    #
    # with open('{}-matrix.txt'.format(read_stream.name.split('.')[0]), 'w') as output_file:
    #         output_file.write("\t" + "\t".join(test_time))
    #         for word in tqdm.tqdm(word_list.keys()):
    #             output_file.write("{}\t{}\n".format(word, "\t".join(map(str, word_list[word]))))
    #
    # with open('{}-wrdcnt.txt'.format(read_stream.name.split('.')[0]), 'w') as ttl_wrd_cnt_file:
    #     sorted_wordcount = sorted([(word, sum(word_list[word]))
    #                                for word in tqdm.tqdm(word_list.keys())], key=lambda x: x[1])
    #     for w in sorted_wordcount:
    #         ttl_wrd_cnt_file.write("{}: {}\n".format(w[0], w[1]))
