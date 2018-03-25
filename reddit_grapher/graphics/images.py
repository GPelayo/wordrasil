from reddit_grapher.extractor.reddit import SubmissionCommentCollector
from reddit_grapher.processor.simple import build_wc_matrix
import tqdm

GAME_NAME = 'nfc_div'
SUBREDDIT = 'nfl'

#TODO Current, fix progress bar



with open('{}-{}.txt'.format(GAME_NAME, SUBREDDIT), 'w') as tfile:
    scc = SubmissionCommentCollector('7vb5tk', ['body', 'created'], tfile)
    max_comments = 43233
    with tqdm.tqdm(total=max_comments) as pbar:
        scc.write_comments(callback=pbar)

with open('{}-{}.txt'.format(GAME_NAME, SUBREDDIT), 'r') as tfile:
    build_wc_matrix(tfile)


# offline.plot([graph_objs.Scatter(x=[1, 2, 3], y=[3, 1, 6])])