from processor.simple import Discussion
from plotly import offline, graph_objs


class CommentChartBuilder:
    TIMEZONE_OFFSET = 8

    def graph(self, timeline):
        raise NotImplementedError


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
    def __init__(self, word_list: list):
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
