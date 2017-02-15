from django.db import models

MAX_STRING_LENGTH = 100


class Thread(models.Model):
    thread_id = models.CharField(max_length=10)
    text = models.CharField(max_length=35)
    url = models.CharField(max_length=100)


class Post(models.Model):
    post_id = models.CharField(max_length=10)
    thread_id = models.CharField(max_length=10)
    author = models.CharField(max_length=35)
    date_created = models.DateTimeField()
    text = models.CharField(max_length=500)
    url = models.CharField(max_length=300)

    def __str__(self):
        return "{} - {}".format(self.date_created,
                                str(self.text)[0: MAX_STRING_LENGTH],
                                "..." if len(str(self.text)) < MAX_STRING_LENGTH else "")


class SettingHistory(models.Model):
    interval_size = models.IntegerField()
    start_time = models.DateTimeField()
    thread_id = models.CharField(max_length=10)


class PostWordValueChunk(models.Model):
    thread_id = models.CharField(max_length=10)
    word = models.CharField(max_length=35)
    value = models.DecimalField(max_digits=6, decimal_places=1, default=0)
    setting_id = models.ForeignKey(SettingHistory)
    iteration = models.IntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return "{}-{}: {}".format(self.iteration, self.word, self.value)


class PostTag(models.Model):
    original_post = models.ForeignKey(Post)
    tag = models.CharField(max_length=35)
