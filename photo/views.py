from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, FileResponse, StreamingHttpResponse
from django.views import View
from photo.models import Account, Album
from photo.utils import handle
import copy
import json
from django.http import QueryDict
from django.views.decorators.csrf import csrf_exempt
# from django.contrib.auth.decorators import login_required


test_temp = {
    'id': int,
    'name': str,
    'public': bool,
    'cases': [{
        'id': int,
        'name': str,
        'label': [str]
    }],
    'data': {
        'course': [int],
        'value': float,
        'sub': {
            'name': str,
            'desc': str
        }
    }
}


class Test:
    def __init__(self, **kwargs):
        print(kwargs)

    @classmethod
    def api(cls,arg, **initkwargs):
        print("request", arg)
        print("INIT:", initkwargs)

        def get(request, *args, **kwargs):
            print(request, args, kwargs)
            return HttpResponse()

        return get




@csrf_exempt
def test(arg,*args,**kwargs):
    print(arg,args,kwargs)
    return HttpResponse(kwargs)
    # return JsonResponse(request.POST.dict())


class AlbumView(View):
    post_temp = {
        'name': str,
        'desc': str,
        'public': bool,
        'photos': [{
            'name': str,
            'desc': str,
            'can_download': bool,
        }],
        'cover': int,
    }
    put_temp = {
        'name': str,
        'desc': str,
        'public': bool,
        'photos': [{
            'name': str,
            'desc': str,
            'can_download': bool,
        }],
        'cover': int,
        'deletes': [int]
    }

    files_temp = {
        'file': list,
    }

    def fetch(self, request):
        return {
            'data': copy.deepcopy(request.DATA),
            'files': request.FILES.getlist('file')
        }

    @handle()   # (redirect('/me'))
    def get(self, request, aid):
        # aid = request.GET.get('id')
        print(request.get_full_path())
        return JsonResponse(Album.get(aid).get_data())

    @handle(post_temp, HttpResponse("0"))
    def post(self, request):
        data = self.fetch(request)
        data['data'].update({
            'creator': Account.get_user(request.session),
        })
        Album.create(**data)
        return HttpResponse('1')

    @handle(put_temp, HttpResponse("0"))
    def put(self, request, aid):
        data = self.fetch(request)
        Album.get(aid).modify(**data)
        return HttpResponse('1')

    @handle()
    def delete(self, request, aid):
        if 'user' in request.session:
            user = Account.get(request.session['user'])
            if user.own_album(aid):
                Album.get(aid).remove()
        return HttpResponse("0")

    @staticmethod
    @handle(None, HttpResponse("0"))
    def download(request, aid):
        if 'user' in request.session:
            user = Account.get(request.session['user'])
            if user.own_album(aid):
                return FileResponse(Album.get(aid).get_zip())
        return HttpResponse("0")


# def album(request):
#     if request.method == 'POST':
#         try:
#             user = Account.get_user(request.session)
#
#             aid = request.POST.get('id')
#             name = request.POST.get('name')
#             desc = request.POST.get('desc')
#             photos = request.FILES.getlist('file')
#             info = request.POST.get('info')
#
#             public = True if request.POST.get('type') == 'publish' else False
#             if aid == 0:
#                 Album.create(user, name, desc, public, photos, info)
#             else:
#                 deletes = request.POST.get('deletes')
#                 Album.get(aid).modify(name, desc, public, photos, deletes, info)
#             return HttpResponse('1')
#         except Exception as e:
#             print(e)
#             return HttpResponse('0')
#     if request.method == 'GET':
#         id = request.GET.get('id')
#         return JsonResponse(Album.get(id).get_data())


# @handle(redirect('/'))
def account(request, username):
    if request.method == 'GET' and request.is_ajax():
        if Account.get(username):
            return HttpResponse("0")
        return HttpResponse("1")
    return HttpResponse("0")


def join(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        in_type = request.POST.get('type')

        if in_type == 'login':
            if Account.login(username, password):
                request.session['user'] = username
                return HttpResponse("1")
        elif in_type == 'signup':
            if Account.signup(username, password):
                request.session['user'] = username
                return HttpResponse("1")
    return HttpResponse("0")





# @handle
def me(request):
    if 'user' in request.session:
        user = Account.get(request.session['user'])
        return render(request, 'me.html', user.get_data())
    return redirect('/')


def avatar(request):
    if 'user' not in request.session:
        return HttpResponse("0")
    user = Account.get(request.session['user'])
    if 'file' in request.FILES:
        file = request.FILES.get('file')
        user.avatar = file
        user.save()
        return HttpResponse("1")


def index(request):
    data = {'avatar': ''}
    if 'user' in request.session:
        data['avatar'] = Account.get(request.session['user']).avatar.name
    albums = Album.objects.filter(public=True).order_by('?')[:6]
    hot = []
    for a in albums:
        hot.append(a.get_data())
    data['albums'] = hot
    return render(request, 'index.html', data)


def like(request):
    if request.method == 'POST':
        aid = request.POST.get("id")
        a = Album.get(aid)
        a.likes += 1
        a.save()
        return HttpResponse("1")
    return HttpResponse("0")


