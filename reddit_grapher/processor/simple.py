import nltk
import re
import peakutils
import numpy
from datetime import datetime, timedelta
from collections import Counter

PRONOUNS = "he"
SPECIAL_IGNORE_WORDS = ["n't", "'s", "..."]
IGNORE_LIST = nltk.corpus.stopwords.words() + SPECIAL_IGNORE_WORDS

ROOT_COMMENTS_KEY = 'comments'
CREATED_COMMENTS_KEY = 'created'

TIME_INTERVAL = 20
CUTOFF_TIME = 600

TIMEZONE_OFFSET = 8


def clean_token_list(token_list):
    new_list = []
    for tkn in token_list:
        filter_pattern = re.compile("[^a-zA-z]")
        new_word = filter_pattern.sub('', tkn)
        new_word = new_word.lower()
        if new_word and len(new_word) > 1 and new_word not in IGNORE_LIST:
            new_list.append(new_word)
    return new_list


class DiscussionOld:
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
        self.latest_time = self.earliest_time + CUTOFF_TIME * TIME_INTERVAL

    def _build_timeline(self):
        for comment in self.comments[ROOT_COMMENTS_KEY]:
            timeline_address = float(comment[CREATED_COMMENTS_KEY])//TIME_INTERVAL * TIME_INTERVAL
            self.comment_list.setdefault(timeline_address, []).append(comment)
            # TODO: Find more dynamic way to cutoff trivial comment data
            if timeline_address > self.latest_time:
                break

    @property
    def word_count_local_maximas(self):
        timestamp_lst, comment_counts = zip(*[(timestamp, len(comment))
                                              for timestamp, comment in self.comment_list.items()])
        data_array = numpy.array(comment_counts)
        return peakutils.indexes(data_array)


def convert_timestamp_to_time(timestamp):
    comment_time = datetime.fromtimestamp(timestamp)
    tz_comment_time = comment_time + timedelta(hours=TIMEZONE_OFFSET)
    return tz_comment_time


class WordCount:
    word = None
    count = None

    def __init__(self, word, count):
        self.word = word
        self.count = count


class DiscussionInterval:
    timestamp = -1
    raw_comment_data = None
    is_local_maxima = True

    def __init__(self, min_timestamp: float):
        self.timestamp = convert_timestamp_to_time(min_timestamp)
        self.raw_comment_data = []
        self.word_count = None

    def process(self):
        self.word_count = sorted(
            [WordCount(word, count) for word, count in self._get_word_count().items()],
            key=lambda x: x.count, reverse=True)

    def add_comment_data(self, comment: dict):
        self.raw_comment_data.append(comment)

    def _get_word_count(self):
        tokens = []
        for cmt in self.raw_comment_data:
            formatted_words = self.format_words(nltk.word_tokenize(cmt['body']))
            filtered_tokens = self.filter_words(formatted_words)
            tokens += filtered_tokens

        return Counter(tokens)

    @property
    def popular_words(self, top_n: int =20):
        return self.word_count[:top_n]

    @property
    def comment_count(self) -> int:
        return len(self.raw_comment_data)

    def __str__(self) -> str:
        return f"{self.timestamp}: {self.comment_count}"

    @staticmethod
    def format_words(word_list) -> list:
        return [w.lower() for w in word_list]

    @staticmethod
    def filter_words(word_list) -> list:
        return [w for w in word_list if w not in IGNORE_LIST and len(w) > 1]


class Discussion:
    earliest_time = -1
    latest_time = 2 ** 31

    def __init__(self, data):
        self.init_time_ranges(data)
        self.comments = data
        self._comment_list = {}
        self._comment_count_local_maxima_indices = None
        self._build_timeline()

    def init_time_ranges(self, data):
        time = [t for t in map(lambda x: x[CREATED_COMMENTS_KEY], data[ROOT_COMMENTS_KEY])]
        self.earliest_time = float(min(time))
        self.latest_time = self.earliest_time + CUTOFF_TIME * TIME_INTERVAL

    def get_timeline_attrib_array(self, attribute_name, only_local_maxima=False, as_string=False):
        res = [getattr(cmt, attribute_name) for cmt in self._comment_list.values()]
        if only_local_maxima:
            res = [res[x] for x in self._comment_count_local_maxima_indices]

        if as_string:
            res = list(map(str, res))
        return res

    def _build_timeline(self):
        for comment in self.comments[ROOT_COMMENTS_KEY]:
            interval_min_timestamp = float(comment[CREATED_COMMENTS_KEY]) // TIME_INTERVAL * TIME_INTERVAL
            if interval_min_timestamp not in self._comment_list.keys():
                disc_int = DiscussionInterval(interval_min_timestamp)
                self._comment_list[interval_min_timestamp] = disc_int

            self._comment_list[interval_min_timestamp].add_comment_data(comment)
            # TODO: Find more dynamic way to cutoff trivial comment data
            if interval_min_timestamp > self.latest_time:
                break

        comments, comment_counts = zip(*[(x, x.comment_count) for x in self._comment_list.values()])
        data_array = numpy.array(comment_counts)
        self._comment_count_local_maxima_indices = peakutils.indexes(data_array, thres=0.1)
        for ci in self._comment_list.values():
            ci.process()
