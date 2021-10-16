import json

from bs4 import BeautifulSoup
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render


# Create your views here.


def index(request):
    return render(request, 'test1/index.html')


def html_dom_ajax(request):
    jsonObject = json.loads(request.body)
    soup = BeautifulSoup(jsonObject.get('content'), 'html.parser')
    totCnt = soup.select_one(".prdCount strong").text
    return JsonResponse(jsonObject)
