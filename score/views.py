#coding:utf-8
from django.shortcuts import render
from django.http import HttpResponseRedirect,HttpResponse
from .models import record
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from operator import itemgetter
from re import findall,IGNORECASE
import os

def index(request):
    members = User.objects.all()
    line = int(User.objects.get(username='hiddenadmin').last_name)

    lis = []

    for man in members:
        #rs = record.objects.filter(who=man.username)
        rs = record.objects.all();
        s = 0
        for r in rs:
            if(r.who == man.username) or (('#'+man.username+'#') in r.who):
                s += r.soc

        if (s>0) or (man.email[0]=='0'):
            #print man.first_name
            if man.email[0] !='0':
                col = 'black'
            else:
                if s<line:
                    col = 'red'
                else:
                    col = 'green'

            lis.append({
                    'un' : man.username,
                    'name':man.first_name,
                    'sum': s,
                    'col': col
                })
        lis.sort(key=itemgetter('sum'),reverse=True)
        
        if request.user.is_authenticated:
            nam = request.user.first_name 
            un  = request.user.username
        else:
            nam = ''
            un = ''

    return render(request,'score/rank.html',{
        'list':lis,
        'name':nam,
        'un':un,
        'is_staff':request.user.is_staff
        })

@login_required
def add(request):
    
    nam = request.user.first_name 
    un  = request.user.username
    
    score = {
                'zs':10,
                'win':5,
                'best':3,
                'mb':5,
                'bys':8,
                'pw':2,
                'cw':5,
                'out':5,
                'other':0
                }
    kk = {
                'zs':"正赛",
                'win':"正赛胜利",
                'best':"最佳辩手",
                'mb':"模辩",
                'bys':"表演赛",
                'pw':"新生赛评委",
                'cw':"场务",
                'out':"外派",
                'other':"待填写"
            }
       
    k_list = ['zs','win','best','mb','bys','pw','cw','out','other']

    if request.POST:
        kind = request.POST['kind']
        title = request.POST['title']
        detail = request.POST['detail']
        date = request.POST['date']
         

        if kind not in kk or not (kind and title and detail and date):
            return HttpResponse("<h1>信息不全，返回重填</h1>")

        rc = record(
                kind = kk[kind],
                name = title,
                detail = detail,
                who = un,
                when = date,
                soc = score[kind]
                )
        rc.save();
        return HttpResponseRedirect("/score/")

    return render(request,'score/add.html',{
        'name':nam,
        'un':un,
        'k_list':k_list,
        'kk':kk,
        'ss':score
        })

@staff_member_required
def addGroup(request):
    nam = request.user.first_name 
    un  = request.user.username

    if request.POST:
        print request.POST
        s = "#"
        print request.POST.getlist('values',[])
        for p in request.POST.getlist('values',[]):
            print p
            s = s + p + '#'
        rc = record(
                kind = '#',
                name = request.POST['title'],
                detail = (u'记录人: ' + nam).encode('utf-8'),
                who = s,
                when = request.POST['date'],
                soc = int(request.POST['score'])
                )
        rc.save();

        return  HttpResponseRedirect("/score/")
    
    members = User.objects.exclude(username='hiddenadmin').order_by('email');
    
    return render(request,'score/addGroup.html',{
        'members':members,
        'name':nam,
        'un':un
        });

@login_required
def ud(request,cun):
    try:
        cu = User.objects.get(username=cun)
    except:
        return HttpResponse(cun)

    ar1 = record.objects.order_by("when")
    nam = request.user.first_name 
    
    ar = []
    for rr in ar1:
        if (rr.who==cun) or (('#'+cun+'#') in rr.who):
            ar.append(rr);


    pub_art = []
    path = '../member/'+cun+'/publicSpace/'
    if os.path.exists(path):
        for f in os.listdir(path):
            if (len(f)>5) and (f[-5:]=='.html'):
                FF = open(path+f,'r')
                text = FF.read()
                tt =  findall('<title>(.*?)</title>',text,flags=IGNORECASE)
                if tt:
                    title = tt[0]
                else:
                    title = f

                pub_art.append({
                        'f':f,
                        't':title
                    })
            


    context = {
            'ar':ar,
            'name':nam,
            'cun':cun,
            'cn':cu.first_name,
            'fac':cu.last_name,
            'gra':findall('@(\d+).com',cu.email)[0],
            'pa':pub_art
            }
    return render(request,'score/user.html',context)
 
@login_required
def us(request):
    nam = request.user.first_name 
    us = []
    for p in User.objects.all():
        ty = ''
        if p.email[0] == '0':
            ty = '考察期'
        elif p.email[0] == '1':
            ty = '正式队员'
        elif p.email[0] == '2':
            ty = '退役老兵'

        if ty:
            us.append({
                    'gra':findall('^.*?\..*?@(.*?)\.com$',p.email)[0],
                    'nam':p.first_name,
                    'fac':p.last_name,
                    'pho':findall('^.*?\.(.*?)@.*?\.com$',p.email)[0],
                    'ty':ty,
                    'un':p.username
                }
                )
    us.sort(key=itemgetter('gra'))
    return render(request,'score/users.html',{'us':us,'name':nam})

def getWho(s):
    if s[0]== '#':
        names = s[1:-1].split('#')
        print names
        ans = ''
        for name in names:
            print name
            ans = ans + ' ' + User.objects.get(username = name).first_name
        return ans[1:]
    else:
        return s

def getName(s):
    if s[0]== '#':
        names = s[1:-1].split('#')
        return "共计%d人"%(len(names))
    else:
        return User.objects.get(username = s).first_name

@login_required
def list(request):

    nam = request.user.first_name 
    if 'type' in request.GET:
        lis = record.objects.filter(kind=request.GET['type'])
    else:
        lis = record.objects.all()

    lis = lis.order_by('when')

    l = [{
            'when':x.when,
            'who':getWho(x.who),
            'rn':getName(x.who), # User.objects.get(username = x.who).first_name,
            'kind':x.kind,
            'name':x.name,
            'detail':x.detail,
            'soc':x.soc
        } for x in lis]

    return render(request,'score/list.html',{'l':l,'name':nam})
