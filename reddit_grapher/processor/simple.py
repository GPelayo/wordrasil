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


def clean_token_list(token_list: list) -> list:
    new_list = []
    for tkn in token_list:
        filter_pattern = re.compile("[^a-zA-z]")
        new_word = filter_pattern.sub('', tkn)
        new_word = new_word.lower()
        if new_word and len(new_word) > 1 and new_word not in IGNORE_LIST:
            new_list.append(new_word)
    return new_list


def convert_timestamp_to_time(timestamp: float) -> datetime:
    comment_time = datetime.fromtimestamp(timestamp)
    tz_comment_time = comment_time + timedelta(hours=TIMEZONE_OFFSET)
    return tz_comment_time


class WordCount:
    word = None
    count = None

    def __init__(self, word: str, count: int):
        self.word = word
        self.count = count


class DiscussionInterval:
    timestamp = -1
    raw_comment_data = None
    is_local_maxima = True
    _word_count_map = None

    def __init__(self, min_timestamp: float):
        self.timestamp = convert_timestamp_to_time(min_timestamp)
        self.raw_comment_data = []
        self.word_count = None

    def process(self):
        self.word_count = sorted(
            [WordCount(word, count) for word, count in self._get_all_word_counts().items()],
            key=lambda x: x.count, reverse=True)
        self._word_count_map = {wc.word: wc for wc in self.word_count}

    def add_comment_data(self, comment: dict):
        self.raw_comment_data.append(comment)

    def get_word_count(self, word: str) -> int:
        try:
            return self._word_count_map[word].count
        except KeyError:
            return 0

    def _get_all_word_counts(self):
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

    def __init__(self, data: dict):
        self.init_time_ranges(data)
        self.comments = data
        self._comment_list = {}
        self._comment_count_local_maxima_indices = None
        self._build_timeline()

    def init_time_ranges(self, data: dict):
        time = [t for t in map(lambda x: x[CREATED_COMMENTS_KEY], data[ROOT_COMMENTS_KEY])]
        self.earliest_time = float(min(time))
        self.latest_time = self.earliest_time + CUTOFF_TIME * TIME_INTERVAL

    def get_timeline_attrib_array(self, attribute_name: str,
                                  only_local_maxima: bool=False, as_string: bool=False) -> list:
        res = [getattr(cmt, attribute_name) for cmt in self._comment_list.values()]
        if only_local_maxima:
            res = [res[x] for x in self._comment_count_local_maxima_indices]

        if as_string:
            res = list(map(str, res))
        return res

    def get_single_word_count_array(self, word: str) -> list:
        return [cmt.get_word_count(word)for cmt in self._comment_list.values()]

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
