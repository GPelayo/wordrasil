import json
import threading
import os
import time
from praw import Reddit
from praw.models import MoreComments, Submission
from prawcore.exceptions import RequestException
from reddit_grapher.utils.wc_log import logger

from reddit_grapher import settings


class RedditThread(threading.Thread):
    def __init__(self, comment_tree, max_attempts, callback):
        super(RedditThread, self).__init__()
        self.comment_tree = comment_tree
        self.max_attempts = max_attempts
        self.callback = callback
        self.comment_list = []

    def run(self):
        attempts = 0
        while attempts < self.max_attempts:
            try:
                if isinstance(self.comment_tree, Submission):
                    self.comment_list = self.comment_tree.comments
                elif isinstance(self.comment_tree, MoreComments):
                    self.comment_list = self.comment_tree.comments()

            except RequestException:
                attempts += 1
                self.callback.set_description('{:30}'.format("Failed Connection. Attempts: {}".format(attempts)))
            else:
                break

CACHE_FOLDER = "cache"
CACHED_COMMENTS_FOLDER = "comments"
COMMENT_IDS_FILE_NAME = "comment-ids"
COMMENT_ID_FIELD_NAME = "id"

COMMENT_IDS_FILEPATH = os.path.join(CACHE_FOLDER, COMMENT_IDS_FILE_NAME)
COMMENT_CACHE_FOLDER = os.path.join(CACHE_FOLDER, CACHED_COMMENTS_FOLDER)


class SubmissionCommentCollector:
    def __init__(self, submission_id, fields, filestream, cache_location=CACHE_FOLDER):
        logger.info("Authenticating Reddit...")
        user_agent = settings.user_agent
        client_id = settings.Reddit.client_id
        client_secret = settings.Reddit.client_secret
        username = settings.Reddit.username
        password = settings.Reddit.password

        if not os.path.exists(CACHE_FOLDER):
            os.mkdir(CACHE_FOLDER)
        if not os.path.exists(COMMENT_CACHE_FOLDER):
            os.mkdir(COMMENT_CACHE_FOLDER)

        self.cache_location = cache_location
        self.api_wrapper = Reddit(user_agent=user_agent, client_id=client_id,
                                  client_secret=client_secret,
                                  username=username, password=password)

        if os.path.exists(COMMENT_IDS_FILEPATH):
            with open(COMMENT_IDS_FILEPATH, 'r') as cif_file:
                self.saved_comment_ids = cif_file.readlines()
        else:
            self.saved_comment_ids = []

        self.submission_id = submission_id
        self.stream = filestream
        self.fields = fields
        self.comment_data = []
        self.__more_comment_queue = []
        self.max_attempts = 3
        self.max_threads = 100
        self.thread_list = []

    # def add_filter(self, author_flair_text=None):
    #     if author_flair_text:

    def write_comments(self, roots_only=False, callback=None):
        if callback is not None:
            callback.set_description('Getting comments...')
        else:
            logger.info('Getting comments...')
        submission = self.api_wrapper.submission(id=self.submission_id)
        self.__more_comment_queue.append(submission)

        cmt_tree = self.__more_comment_queue.pop(0)
        callback.set_description('{:30}'.format(str((len(self.__more_comment_queue), len(self.__more_comment_queue)))))
        new_thread = RedditThread(cmt_tree, self.max_attempts, callback)
        new_thread.run()
        self.thread_list.append(new_thread)

        while len(self.thread_list) > 0:
            # while len(self.thread_list) >= self.max_threads:
            callback.set_description('{:30}'.format(str((len(self.thread_list),
                                                         len(self.__more_comment_queue)))))
            for t in self.thread_list:
                if not t.is_alive():
                    self.__get_comments(t.comment_list, callback)
                    self.thread_list.remove(t)

            # callback.set_description('{:30}'.format([at.is_alive() for at in self.thread_list]))
            # print(len(self.thread_list) < self.max_threads, len(self.__more_comment_queue) > 0)

            while len(self.thread_list) < self.max_threads and len(self.__more_comment_queue) > 0:
                cmt_tree = self.__more_comment_queue.pop(0)
                new_thread = RedditThread(cmt_tree, self.max_attempts, callback)
                new_thread.run()
                self.thread_list.append(new_thread)
            time.sleep(2)

        logger.info("Writing JSON...")
        json.dump({"comments": self.comment_data}, self.stream)

    def __get_comments(self, comment_forest, callback=None):
        for c in comment_forest:
            if isinstance(c, MoreComments):
                self.__more_comment_queue.append(c)
            else:
                if callback is not None:
                    callback.update(1)
                commend_id = getattr(c, COMMENT_ID_FIELD_NAME)
                self.write_comment_ids(commend_id)
                self.save_comments(commend_id, {f: str(getattr(c, f)) for f in self.fields})

    def write_comment_ids(self, comment_id):
        with open(COMMENT_IDS_FILEPATH, 'a') as cif:
            self.saved_comment_ids.append(comment_id)
            cif.write("{}\n".format(comment_id))
        # print("\n".join([str(type(cd)) for cd in self.__more_comment_queue]))

    def save_comments(self, comment_id, comment_data):
        self.comment_data.append(comment_data)
        with open(os.path.join(CACHE_FOLDER, CACHED_COMMENTS_FOLDER, '{}.json'.format(comment_id)),
                  'w+') as ccf:
            json.dump(comment_data, ccf)


# try:
#     mcmt = c.comments()
#     comment_text += self.__get_comments(mcmt, callback)
# except AssertionError as e:
#     logger.error(e)
