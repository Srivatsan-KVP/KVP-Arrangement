from django.shortcuts import render, redirect
from django.http.response import HttpResponseBadRequest, JsonResponse
from django.contrib.auth import authenticate, logout as auth_logout, login as auth_login
from django.contrib.auth.decorators import login_required

from . import models
from . import forms

import datetime, random, uuid, json

def __parseDate(req):
    ds = [int(i) for i in req.GET['date'].split('-')]
    return datetime.date(year=ds[-1], month=ds[-2], day=ds[-3])

# Create your views here.
def index(req):
    if req.method == 'POST':
        form = forms.LoginForm(req.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['login_username'], 
                password=form.cleaned_data['login_password']
            )
            if user is not None:
                auth_login(req, user)
                return JsonResponse({'redirect': '/upload/'})
            return JsonResponse({'valid': False, 'message': 'Invalid credentials!'})
        
        return HttpResponseBadRequest()
    
    if req.user.is_authenticated:
        return redirect('/upload/')
    return render(req, 'app/index.html')
    
def logout(req):
    auth_logout(req)
    return redirect('/')

@login_required
def master(req):
    if req.method == 'POST':
        if req.POST['method'] == 'update':
            uid = ''
            if len(req.POST['uid']) > 0:
                models.Teacher.objects.filter(uid=uuid.UUID(req.POST['uid'])).update(
                    name=req.POST['name'],
                    post=req.POST['post']
                )
                uid = req.POST['uid']
            else:
                t = models.Teacher(
                    name=req.POST['name'],
                    post=req.POST['post']
                )
                t.save()
                t.refresh_from_db()
                for i in range(6):
                    models.Table(teacher=t, day=i).save()
                uid = str(t.uid)

            return JsonResponse({'valid': True, 'uid': uid})
        
        elif req.POST['method'] == 'remove':
            models.Teacher.objects.filter(uid=uuid.UUID(req.POST['uid'])).delete()
            return JsonResponse({})
        
        elif req.POST['method'] == 'updateTT':
            periods = json.loads(req.POST['periods'])
            models.Table.objects.filter(day=req.POST['day'], teacher__uid=req.POST['uid']).update(
                p1=periods[0],
                p2=periods[1],
                p3=periods[2],
                p4=periods[3],
                p5=periods[4],
                p6=periods[5],
                p7=periods[6],
                p8=periods[7]
            )
            return JsonResponse({})

    context = {'tt': [], 'teachers': [teacher for teacher in models.Teacher.objects.all()]}
    for day in range(6):
        table = {}
        for t in models.Table.objects.filter(day=day):
            table[t.teacher] = t.get_classes()
        context['tt'].append(table)

    return render(req, 'app/master.html', context)

@login_required
def upload(req):
    if req.method == 'POST':
        if req.POST['method'] == 'add':
            models.Absent(date=__parseDate(req), teacher=models.Teacher.objects.get(uid=req.POST['uid'])).save()
            return JsonResponse({ 'valid': True })
        
        elif req.POST['method'] == 'remove':
            models.Absent.objects.filter(date=__parseDate(req), teacher=models.Teacher.objects.get(uid=req.POST['uid'])).delete()
            return JsonResponse({})

    context = {'teachers': [teacher for teacher in models.Teacher.objects.all()]}
    if req.GET.get('date', False):
        context['absent'] = [entry.teacher for entry in models.Absent.objects.filter(date=__parseDate(req))]

    return render(req, 'app/upload.html', context)

@login_required
def arrangement(req):
    if not req.GET.get('date', False):
        return HttpResponseBadRequest()
    
    d = __parseDate(req)

    absent = [entry.teacher for entry in models.Absent.objects.filter(date=d)]
    teachers = [t for t in models.Teacher.objects.all()]
    free, res = {}, {}

    for teacher in absent:
        classes = models.Table.objects.get(day=d.weekday(), teacher=teacher).get_classes()
        print(classes)
        res[teacher] = ['' for _ in range(8)]

        for i in range(8):
            if (classes[i] == 'F'): continue

            pgt_req = False
            if int(classes[i][:-1]) >= 11: pgt_req = True

            free_av, available = False, []

            for t in teachers:
                if not free.get(t.uid): free[t.uid] = [0 for _ in range(8)]
                if pgt_req and t.post != 'P': continue

                if models.Table.objects.get(day=d.weekday(), teacher=t).get_classes()[i] == 'F' \
                    and t not in absent and free[t.uid][i] < 2:
                    available.append(t)
                    if free[t.uid][i] == 0:
                        free_av = True

            if free_av:
                deleted = 0
                for idx in range(len(available)):
                    if free[available[idx - deleted].uid][i] > 0:
                        available.pop(idx)
                        deleted += 1

            res[teacher][i] = classes[i] + '\n\n'
            if len(available) >= 1:
                t = random.choice(available)
                free[t.uid][i] += 1
                res[teacher][i] += t.name
            else:
                res[teacher][i] += 'Not available'


    return render(req, 'app/arrangement.html', {'arr': res})