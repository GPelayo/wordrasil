import json
import nltk
import re
import collections
import datetime
import tqdm
from word_timeline.models import *


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


class WordCountChunker:
    def __init__(self, thread_id, increment, chunk_size, earliest_time: datetime=None):
        self.earliest_time = earliest_time
        self.increment_size = increment
        self.thread_id = thread_id
        self.chunk_size = chunk_size

    def get_comment_interval(self):
        if self.earliest_time:
            interval_start = self.earliest_time
        else:
            interval_start = Post.objects.filter(thread_id=self.thread_id).earliest('date_created').date_created
        latest_time = Post.objects.filter(thread_id=self.thread_id).latest('date_created').date_created
        interval_end = interval_start + datetime.timedelta(seconds=self.chunk_size)
        interval_cmts = Post.objects.filter(date_created__range=[interval_start, interval_end])

        interval = 0
        sh = SettingHistory()
        sh.interval_size = self.increment_size
        sh.start_time = interval_start
        sh.thread_id = self.thread_id
        sh.save()

        while interval_start < latest_time:
            for cmt in interval_cmts:
                snt_list = nltk.sent_tokenize(cmt.text)
                for snt in snt_list:
                    for word in clean_token_list(nltk.word_tokenize(snt)):
                        chunk_data_list = PostWordValueChunk.objects.filter(thread_id=self.thread_id,
                                                                            word=word,
                                                                            iteration=interval,
                                                                            setting_id=sh)
                        if chunk_data_list:
                            chunk_data = chunk_data_list[0]
                        else:
                            chunk_data = PostWordValueChunk()
                            chunk_data.thread_id = self.thread_id
                            chunk_data.word = word
                            chunk_data.setting_id = sh
                            chunk_data.iteration = interval
                            chunk_data.start_time = interval_start
                            chunk_data.end_time = interval_end

                        chunk_data.value += 1
                        chunk_data.save()
            interval += 1
            interval_start += datetime.timedelta(seconds=self.increment_size)
            interval_end += datetime.timedelta(seconds=self.increment_size)
            interval_cmts = Post.objects.filter(date_created__range=[interval_start, interval_end])
