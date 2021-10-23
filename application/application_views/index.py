# -*- coding: utf-8 -*-
import json
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
def test(request):
    if request.method == 'GET':
        content = "application test"
        content = json.dumps(content, ensure_ascii=False)
        response = HttpResponse(content=content, content_type='application/json', charset='utf-8')
        response.status_code = 200
        return response