from django.contrib import admin
from word_timeline.models import *


class PostWordValueChunkAdmin(admin.ModelAdmin):
    search_fields = ['word']

admin.site.register(Post)
admin.site.register(SettingHistory)
admin.site.register(PostWordValueChunk, PostWordValueChunkAdmin)
