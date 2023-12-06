from django.shortcuts import render, get_object_or_404, redirect
import os
from django.http import FileResponse
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.core.files.storage import FileSystemStorage
from pathlib import Path

# Create your views here.
