from datetime import datetime, timedelta
from processor.simple import Discussion
from plotly import offline, graph_objs
import peakutils
import numpy


class CommentChartBuilder:
    TIMEZONE_OFFSET = 8

    def _convert_timestamp_to_time(self, timestamp):
        comment_time = datetime.fromtimestamp(timestamp)
        tz_comment_time = comment_time + timedelta(hours=self.TIMEZONE_OFFSET)
        return tz_comment_time


class CommentCountChartBuilder(CommentChartBuilder):
    def build_comment_count_graph(self, timeline: Discussion):
        timestamp_lst, comment_counts = zip(
            *[(timestamp, len(comment)) for timestamp, comment in timeline.comment_list.items()])
        timestamp_lst = list(map(self._convert_timestamp_to_time, timestamp_lst))

        data = [graph_objs.Scatter(x=timestamp_lst, y=comment_counts)]
        offline.plot(data, image='png')


class PeakWordCountGraphBuilder(CommentChartBuilder):
    def with_peaks_build_comment_count_graph(self, timeline: Discussion):
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