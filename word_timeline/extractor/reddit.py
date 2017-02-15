from praw import Reddit
from praw.models import MoreComments
from word_timeline.utils.wc_log import logger
from word_timeline.extractor import CommentCollector, secrets
from word_timeline import settings


class SubmissionCommentCollector(CommentCollector):
    def __init__(self, url, fields):
        logger.info("Authenticating Reddit...")
        user_agent = settings.user_agent
        client_id = secrets.Reddit.client_id
        client_secret = secrets.Reddit.client_secret
        username = secrets.Reddit.username
        password = secrets.Reddit.password
        self.api_wrapper = Reddit(user_agent=user_agent, client_id=client_id,
                                  client_secret=client_secret,
                                  username=username, password=password)
        self.url = url
        self.fields = fields
        self.comment_data = []

    def get_comments(self, roots_only=False):
        logger.info("Getting comments...")
        submission = self.api_wrapper.submission(url=self.url)

        for cmt in self.__traverse_comment_tree(submission.comments):
            yield cmt

    def __traverse_comment_tree(self, comment_forest):
        for c in comment_forest:
            if isinstance(c, MoreComments):
                try:
                    mcmt = c.comments()
                    for more_cmt in self.__traverse_comment_tree(mcmt):
                        yield more_cmt
                except AssertionError as e:
                    print(e)
                    logger.error(e)
            else:
                yield {f: str(getattr(c, f)) for f in self.fields}
