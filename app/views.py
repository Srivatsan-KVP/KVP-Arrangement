from django.shortcuts import render, redirect
from django.http.response import HttpResponseBadRequest, JsonResponse
from django.contrib.auth import authenticate, logout as auth_logout, login as auth_login
from django.contrib.auth.decorators import login_required

from . import models
from . import forms

import datetime, random, uuid, json

def __getTeacher(
    classReq: str, available: list[models.Teacher],
    alloted: dict[uuid.UUID, list[int]], day: int, period: int
) -> str:
    filtered: list[models.Teacher] = []
    allowed_posts = ['P']
    
    if int(classReq[:-1]) < 11: allowed_posts = ['T']
    if int(classReq[:-1]) == 12: allowed_posts.append('N')
    allowed_posts.append('C')

    free_av = False
    for teacher in available:
        if not alloted.get(teacher.uid, False): alloted[teacher.uid] = [0 for _ in range(8)]
        if teacher.post in allowed_posts and (teacher.post == 'N' or (
            classReq[-1] in teacher.sections and
            alloted[teacher.uid][period] < teacher.get_limit() and 
            models.Table.objects.get(teacher=teacher, day=day).get_classes()[period] == 'F'
        )): 
            if alloted[teacher.uid][period] == 0: free_av = True
            filtered.append(teacher)

    if free_av:
        deleted = 0
        for i in range(len(filtered)):
            if alloted[filtered[i-deleted].uid][period] > 0:
                filtered.pop(i-deleted)
                deleted += 1

    if len(available) >= 1:
        teacher = random.choice(filtered)
        alloted[teacher.uid][period] += 1
        return teacher.name
    return 'Not available'

def __parseDate(req) -> datetime.date:
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
                    post=req.POST['post'],
                    sections=req.POST['sections']
                )
                uid = req.POST['uid']
            else:
                t = models.Teacher(
                    name=req.POST['name'],
                    post=req.POST['post'],
                    sections=req.POST['sections']
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
            q = models.Table.objects.filter(day=req.POST['day'], teacher__uid=req.POST['uid'])
            q.update(
                p1=periods[0], p2=periods[1], p3=periods[2], p4=periods[3],
                p5=periods[4], p6=periods[5], p7=periods[6], p8=periods[7]
            )
            q[0].trim()
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
            models.Absent(
                date=__parseDate(req), teacher=models.Teacher.objects.get(uid=req.POST['uid']),
                exempt=req.POST['exempt'] == 'true',
                s1=req.POST['s1'] == 'true', s2=req.POST['s2'] == 'true'
            ).save()
            return JsonResponse({ 'valid': True })
        
        elif req.POST['method'] == 'remove':
            models.Absent.objects.filter(date=__parseDate(req), teacher=models.Teacher.objects.get(uid=req.POST['uid'])).delete()
            return JsonResponse({})

    context = {'teachers': [teacher for teacher in models.Teacher.objects.all()], 'absent': []}
    if req.GET.get('date', False):
        context['absent'] = [entry for entry in models.Absent.objects.filter(date=__parseDate(req))]

    return render(req, 'app/upload.html', context)

@login_required
def arrangement(req):
    if not req.GET.get('date', False):
        return HttpResponseBadRequest()
    
    d = __parseDate(req)

    ab_s1, ab_s2, exempt = [], [], []
    for entry in models.Absent.objects.filter(date=d):
        if entry.exempt:
            exempt.append(entry.teacher)
            continue
            
        if entry.s1: ab_s1.append(entry.teacher)
        if entry.s2: ab_s2.append(entry.teacher)

    self_study = models.Teacher(uid=uuid.uuid4(), name='Self Study', post='N')
    av_s1, av_s2 = [self_study], [self_study]
    for teacher in models.Teacher.objects.all():
        if teacher in exempt: continue
        if teacher not in ab_s1: av_s1.append(teacher)
        if teacher not in ab_s2: av_s2.append(teacher)

    alloted, res = {}, {}
    for teacher in ab_s1:
        res[teacher] = ['' for _ in range(8)]
        classes = models.Table.objects.get(day=d.weekday(), teacher=teacher).get_classes()
        for i in range(4):
            if classes[i] == 'F': continue
            if teacher.post == 'C':
                for c in classes[i].split():
                    res[teacher][i] += f'| {c} {__getTeacher(c, av_s1, alloted, d.weekday(), i)} |'
            else:
                res[teacher][i] = classes[i] + ' ' + __getTeacher(classes[i], av_s1, alloted, d.weekday(), i)

    for teacher in ab_s2:
        if not res.get(teacher, False): res[teacher] = ['' for _ in range(8)]
        classes = models.Table.objects.get(day=d.weekday(), teacher=teacher).get_classes()
        for i in range(4, 8):
            if classes[i] == 'F': continue
            if teacher.post == 'C':
                for c in classes[i].split():
                    res[teacher][i] += f'| {c} {__getTeacher(c, av_s2, alloted, d.weekday(), i)} |'
            else:
                res[teacher][i] = classes[i] + ' ' + __getTeacher(classes[i], av_s2, alloted, d.weekday(), i)

    return render(req, 'app/arrangement.html', {'arr': res})