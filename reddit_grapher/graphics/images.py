from datetime import datetime, timedelta
from processor.simple import DiscussionOld, Discussion
from plotly import offline, graph_objs
import peakutils
import numpy


class CommentChartBuilder:
    TIMEZONE_OFFSET = 8

    def _convert_timestamp_to_time(self, timestamp):
        comment_time = datetime.fromtimestamp(timestamp)
        tz_comment_time = comment_time + timedelta(hours=self.TIMEZONE_OFFSET)
        return tz_comment_time

    def graph(self, timeline):
        raise NotImplementedError


class CommentCountChartBuilder(CommentChartBuilder):
    def graph(self, timeline: DiscussionOld):
        timestamp_lst, comment_counts = zip(
            *[(timestamp, len(comment)) for timestamp, comment in timeline.comment_list.items()])
        timestamp_lst = list(map(self._convert_timestamp_to_time, timestamp_lst))

        data = [graph_objs.Scatter(x=timestamp_lst, y=comment_counts)]
        offline.plot(data, image='png')


class PeakWordCountGraphBuilder(CommentChartBuilder):
    def graph(self, timeline: DiscussionOld):
        timestamp_lst, comment_counts = zip(
            *[(timestamp, len(comment)) for timestamp, comment in timeline.comment_list.items()])
        timestamp_lst = list(map(self._convert_timestamp_to_time, timestamp_lst))

        data_array = numpy.array(comment_counts)
        peak_data = peakutils.indexes(data_array)
        data = [graph_objs.Scatter(x=timestamp_lst, y=comment_counts),
                graph_objs.Scatter(x=[timestamp_lst[i] for i in peak_data],
                                   y=[comment_counts[i] for i in peak_data],
                                   mode='markers',
                                   marker=dict(symbol='cross',
                                               color='rgb(0,255,0)'))]
        offline.plot(data, image='png')


class PeakPopularWordsGraphBuilder(CommentChartBuilder):
    def graph(self, timeline: Discussion):
        timestamps = timeline.get_timeline_attrib_array('timestamp')
        comment_counts = timeline.get_timeline_attrib_array('comment_count')
        peak_timestamps = timeline.get_timeline_attrib_array('timestamp', only_local_maxima=True)
        peak_comment_counts = timeline.get_timeline_attrib_array('comment_count', only_local_maxima=True)
        peak_popular_words = timeline.get_timeline_attrib_array('popular_words', only_local_maxima=True)

        prettified_ppw = ['<br>'.join([f'{i+1}. {wc.word} ({wc.count})'
                                      for i, wc in enumerate(wc_list)]) for wc_list in peak_popular_words]

        data = [graph_objs.Scatter(x=timestamps, y=comment_counts, hoverinfo='none'),
                graph_objs.Scatter(x=peak_timestamps,
                                   y=peak_comment_counts,
                                   mode='markers',
                                   marker=dict(symbol='cross',
                                               color='rgb(0,255,0)'),
                                   name='',
                                   text=prettified_ppw)]
        layout = graph_objs.Layout(showlegend=False)
        fig = graph_objs.Figure(data=data, layout=layout)
        offline.plot(fig, image='png')


class SingleWordCountGraphBuilder(CommentChartBuilder):
    def __init__(self, word_list):
        self.word_list = word_list

    def graph(self, timeline: Discussion):
        timestamps = timeline.get_timeline_attrib_array('timestamp')
        data = []
        for word in self.word_list:
            comment_counts = timeline.get_single_word_count_array(word)
            data.append(graph_objs.Scatter(name=word, x=timestamps, y=comment_counts, hoverinfo='none', mode='line'))
        layout = graph_objs.Layout()
        fig = graph_objs.Figure(data=data, layout=layout)
        offline.plot(fig, image='png')
