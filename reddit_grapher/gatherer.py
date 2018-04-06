from reddit_grapher.extractor import SubmissionCommentCollector

SUBMISSION_CODE = "5o6fc6"
COMMENT_DATA_FILENAME = "nfc-div-2017-all.json"

with open(COMMENT_DATA_FILENAME, 'w+') as test_file:
    cl = SubmissionCommentCollector(SUBMISSION_CODE, ['body', 'created'], test_file)
    cl.write_comments(roots_only=True)
