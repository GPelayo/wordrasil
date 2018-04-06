from datetime import datetime, timedelta
from processor.simple import Discussion
from plotly import offline, graph_objs


class CommentChartBuilder:
    TIMEZONE_OFFSET = 8

    def build_comment_count_graph(self, timeline: Discussion):
        timestamp_lst, comment_counts = zip(
            *[(timestamp, len(comment)) for timestamp, comment in timeline.comment_list.items()])
        timestamp_lst = list(map(self._convert_timestamp_to_time, timestamp_lst))
        data = [graph_objs.Scatter(x=timestamp_lst, y=comment_counts)]
        offline.plot(data, image='png')

    def _convert_timestamp_to_time(self, timestamp):
        comment_time = datetime.fromtimestamp(timestamp)
        tz_comment_time = comment_time + timedelta(hours=self.TIMEZONE_OFFSET)
        return tz_comment_time
