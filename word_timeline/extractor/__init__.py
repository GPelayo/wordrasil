from word_timeline.models import Post
from word_timeline.utils.date import convert_to_datetime, DateFormatType
from django.db.models import DateTimeField


class APISettings:
    client_id = None
    client_secret = None
    username = None
    password = None


class CommentCollector:
    def get_comments(self, roots_only=False):
        raise NotImplementedError

    def __traverse_comment_tree(self, comment_forest):
        raise NotImplementedError


class CommentLoader:
    pass


class DjangoCommentLoader(CommentLoader):
    field_pairs = None
    date_formats = None
    format_methods = None

    def __init__(self, comment_collector: CommentCollector):
        self.comment_collector = comment_collector
        self.field_pairs = []
        self.date_formats = {}
        self.format_methods = {}

    def add_field_pair(self, db_field, api_field):
        self.field_pairs.append((db_field, api_field))

    def set_date_format(self, db_field, format_type: DateFormatType):
        self.date_formats[db_field] = format_type

    def set_format_method(self, db_field, method):
        self.format_methods[db_field] = method

    def save_comments(self):
        for api_cmt in self.comment_collector.get_comments():
            new_db_cmt = Post()
            for cmt_fld in self.field_pairs:
                db_field, api_field = cmt_fld
                field_type = new_db_cmt._meta.get_field(db_field).get_internal_type()
                raw_value = api_cmt[api_field]

                if db_field in self.format_methods.keys():
                    final_value = self.format_methods[db_field](raw_value)
                elif field_type in ['DateTimeField']:
                    format_type = self.date_formats[db_field]
                    final_value = convert_to_datetime(raw_value, format_type)
                else:
                    final_value = raw_value

                setattr(new_db_cmt, db_field, final_value)
            new_db_cmt.save()
