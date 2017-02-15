from django.shortcuts import render
from django.http import HttpResponse
from word_timeline.models import Post
from django.core import serializers
from django.http import JsonResponse


def test_api_call(request, comment_id):
    cmt = Post.objects.get(pk=comment_id)
    cmt_json = serializers.serialize('json', cmt)
    return JsonResponse(cmt_json)

