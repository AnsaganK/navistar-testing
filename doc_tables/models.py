from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
import uuid

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    photo = models.FileField(upload_to='photoUsers',null=True, blank=True)
    phone = models.CharField(max_length=300, null=True, blank=True)
    work = models.CharField(max_length=100, null=True, blank=True)
    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Tables(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='tables')
    file = models.FileField(upload_to='Excel', verbose_name='Файл эксель')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Время загрузки файла')
    archive_date = models.DateTimeField(auto_now=True, verbose_name='Время отправки в архив')
    archive = models.BooleanField(default=False)
    users = models.ManyToManyField(User, null=True, blank=True, related_name='work_tables')

    def __str__(self):
        return str(self.file)

    class Meta:
        verbose_name='Файл Excel'
        verbose_name_plural='Файлы Excel'

class Data(models.Model):
    name = models.CharField(max_length=500,null=True, blank=True, verbose_name='Имя файла')
    file = models.OneToOneField(Tables, on_delete=models.CASCADE, related_name='data')
    json_data = models.TextField(null=True, blank=True)
    def get_absolute_url(self):
        return reverse('detail_tables', args=[str(self.id)])




#--------------------------------------------------------------------------------------
#---------------------------Тут начинается платформа для тестов------------------------
#--------------------------------------------------------------------------------------


class TestUUID(models.Model):
    slug = models.UUIDField(primary_key=True, default=uuid.uuid4)

class Test(models.Model):
    content_1 = models.TextField(null=True, blank=True,verbose_name="Контент для теста")
    name = models.CharField(max_length=300, null=True, blank=True, default="Без названия", verbose_name='Названия теста')
    questions = models.ManyToManyField('Question')
    date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    create_user = models.ForeignKey(User,null=True, blank=True , on_delete=models.CASCADE, related_name="my_tests")
    unique_slug = models.OneToOneField(TestUUID, on_delete=models.CASCADE, related_name="test")
    archive = models.BooleanField(default=False)
    content_data = models.TextField(null=True, blank=True)
    baseTest = models.ForeignKey('self', blank=True,null=True, on_delete=models.CASCADE, related_name="childrenTest")
    #password = models.CharField()
    def get_absolute_url(self):
        return reverse('test_detail', args=[str(self.unique_slug.slug)])
    def __str__(self):
        return str(self.name)


class Question(models.Model):
    text = models.TextField()
    high = models.BooleanField(default=False)
    answers = models.ManyToManyField('Answer', related_name='question')
    def __str__(self):
        return self.text

class Answer(models.Model):
    text = models.TextField(null=True, blank=True, verbose_name='Вариант ответа')
    right = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class FakeUser(models.Model):
    first_name = models.CharField(max_length=500,null=True,blank=True)
    last_name = models.CharField(max_length=500,null=True,blank=True)
    def __str__(self):
        return self.first_name + '  ' + self.last_name


class User_tests(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True, related_name="tests")
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="users")
    success = models.BooleanField(default=False)
    count_answer = models.IntegerField(null=True, blank=True, default=1)
    right_answer = models.IntegerField(null=True, blank=True, default=0)
    date = models.DateTimeField(auto_now_add=True)
    date_end = models.DateTimeField(null=True, blank=True)

    #start_time = models.DateTimeField()
    #end_time = models.DateTimeField()

    content = models.TextField(null=True, blank=True)
    all_result = models.TextField(null=True, blank=True)
    content_test_for_user = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.user.username) + ' | ' + self.test.name +' | '+ str(self.date)

    def percentTest(self):
        return str(round((self.right_answer/self.count_answer)*100,1))+'%'

    class Meta:
        verbose_name = "Тест пользвателя"
        verbose_name_plural = "Тесты пользователей"

'''
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .forms import *
import pandas
import json
from .models import *
from datetime import datetime
from django.contrib.auth.models import Group
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required

#def login(request):

def toTable(data):
    a = data[0]
    headers = []
    for i in a:
        headers.append(i)
    thead = ''
    for i in headers:
        thead += "<td contenteditable='true'>{0}</td>".format(i)
    thead = "<thead id='thead'><tr>"+thead+'</tr></thead>'
    tbody = ''
    for j in data:
        tr = ''
        for k in j:
            el =j[k]
            el = str(el)
            if el == 'nan' or el == 'None':
                el = ''
            td = "<td contenteditable='true'>"+el+'</td>'
            tr+=td
        tr = '<tr>' + tr + '</tr>'
        tbody += tr
    tbody = '<tbody>' + tbody + '</tbody>'

    table = "<table class='table' id='table_tag'>"+thead+tbody+'</table>'
    return table



def excelToTable(name,data):
    date = str(datetime.now())
    date = date.replace('-', '').replace(' ', '').replace(':', '').replace('.','')
    name = str(name)
    name = name.replace('.xlsx', '('+date+').xlsx')
    with open('data/{0}'.format(name), 'wb') as f:
        f.write(data)
    excel_data_df = pandas.read_excel('data/'+str(name))
    data = excel_data_df.to_dict(orient='records')
    for i in range(len(data)):
        for j in list(data[i]):
            if type(data[i][j]) == pandas._libs.tslibs.timestamps.Timestamp:
                data[i][j] = str(data[i][j])
            if 'Unnamed' in str(j):
                del data[i][j]
    data = json.dumps(data)
    return data

@login_required(redirect_field_name='login')
def index(request):
    return render(request,'index.html')

@login_required(redirect_field_name='login')
def addTables(request):
    #group = Group.objects.get(name="employees")
    #users = group.user_set.all()
    users = User.objects.all()
    context = {
        'users':users,
    }
    return render(request,'addTables.html', context)

@login_required(redirect_field_name='login')
def addTablesPost(request):
    if request.method == 'POST':
        form = TablesForm(request.POST, request.FILES)
        zero = []
        for i in request.POST:
            if i != 'csrfmiddlewaretoken':
                zero.append(User.objects.get(pk=int(i)))
        if form.is_valid():
            info = request.FILES['file'].read()
            name = form.cleaned_data['file']

            file = form.save(commit=False)
            file.user = request.user
            file.save()

            last = Tables.objects.last()
            json_data = excelToTable(name, info)
            Data.objects.create(name=name, file=last, json_data=json_data)
            data = Data.objects.last()

            last.users.add(*zero)
            last.save()
            return redirect(data.get_absolute_url())
        else:
            print(form.errors)
    return redirect('addTablesPost')

@login_required(redirect_field_name='login')
def detail_tables(request, pk):
    data = Data.objects.get(pk=pk)
    file = data.file
    zero = []
    for i in file.users.all():
        zero.append(i.pk)
    table = toTable(json.loads(data.json_data))
    users = User.objects.exclude(pk=request.user.pk)
    return render(request, 'detail_tables.html', {'data': data, 'table':table, 'users':users, 'zero':zero})

@login_required(redirect_field_name='login')
def my_files(request):
    user = request.user
    files = Tables.objects.filter(user=user, archive=False)
    context = {
        'files':files
    }
    return render(request, 'my_files.html', context)

@login_required(redirect_field_name='login')
def addArchiveTables(request, pk):
    table = Tables.objects.get(pk=pk)
    table.archive = True
    table.save()
    return redirect('my_files')

@login_required(redirect_field_name='login')
def archive(request):
    user = request.user
    files = Tables.objects.filter(user=user, archive=True)
    context = {
        'files': files
    }
    return render(request, 'archive.html', context)

@login_required(redirect_field_name='login')
def return_my_files(request, pk):
    table = Tables.objects.get(pk=pk)
    table.archive = False
    table.save()
    return redirect('archive')

@login_required(redirect_field_name='login')
def delete_archive(request, pk):
    table = Tables.objects.get(pk=pk)
    table.delete()
    return redirect('archive')

@login_required(redirect_field_name='login')
def list_user(request):
    group = Group.objects.get(name="employees")
    users = group.user_set.all()
    return render(request, 'list_user.html', {'users':users})

@login_required(redirect_field_name='login')
def update_data(request,pk):
    data = Data.objects.get(pk=pk)
    if request.method == "POST":

        form = DataForm(request.POST, instance=data)
        l = str(form['json_data']).replace("'", "\'").replace('"', "\'").replace('&#x27;', "\"").replace('\n', '').replace("<textarea name='json_data' cols='40' rows='10' id='id_json_data'>", '').replace('</textarea>', '')
        post = form.save(commit=False)
        post.json_data = l
        zero = []
        for i in request.POST:
            if i != 'csrfmiddlewaretoken' and i != 'json_data':
                zero.append(User.objects.get(pk=int(i)))
        post.file.users.clear()
        post.file.users.add(*zero)
        if form.is_valid():
            post.save()
            return HttpResponse('success')
        else:
            return HttpResponse('error')
     #redirect(data.get_absolute_url())

@login_required(redirect_field_name='login')
def add_user_post(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        error1 = False
        error2 = False
        alls = User.objects.all()
        for i in alls:
            if i.username == request.POST['username']:
                error1 = True
                return render(request,'add_user.html',{'error1':error1})
        if request.POST['password1'] != request.POST['password2']:
            error2 = True
            return render(request,'add_user.html',{'error2':error2})
        if form.is_valid():#Если форма заполнена правильно
            form.save()#Создаем пользователя
            username = form.cleaned_data.get('username')#с именем
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            post = request.POST
            group = Group.objects.get(name='employees')
            user.groups.add(group)
            user.save()
        form2 = UpdateFormProfile(request.POST, request.FILES, instance=user.profile)
        if form2.is_valid():
            form2.save()

        return redirect('list_user')

@login_required(redirect_field_name='login')
def delete_user(request, pk):
    user = User.objects.get(pk = pk)
    user.delete()
    return redirect('list_user')

@login_required(redirect_field_name='login')
def add_user(request):
    return render(request, 'add_user.html')

@login_required(redirect_field_name='login')
def login(request):
    return render(request, 'login.html')

@login_required(redirect_field_name='login')
def detail_user(request, pk):
    user = User.objects.get(pk = pk)
    return render(request, 'detail_user.html', {'user': user})

@login_required(redirect_field_name='login')
def update_user(request, pk):
    user = User.objects.get(pk = pk)
    if request.method == "POST":
        form = UpdateUser(request.POST, instance=user)
        if form.is_valid():
            form.save()
        form2 = UpdateFormProfile(request.POST, request.FILES, instance=user.profile)
        if form2.is_valid():
            form2.save()
    return redirect('list_user')

def invitations(request):
    user = request.user
    tables = user.objects.files
    unready_tables = tables.filter(unread=True)
    active_tables = tables.filter(archive=False)
    archive_tables = tables.filter(archive=True)
    return render(request, 'invitations.html', {'tables': tables})

def delete_user(request, pk):
    user = User.objects.get(pk=pk)
    user.delete()
    return redirect('list_user')



#--------------------------------------------------------------------------------------
#---------------------------Тут начинается платформа для тестов------------------------
#--------------------------------------------------------------------------------------


def createTest(name,questions,c):
    t = Test.objects.create(name=name)
    t.content = c
    question_list = []
    for i in questions:
        answer_list = []
        for j,k in i.items():
            print(j)
            if k!=[]:
                for l in k:
                    print(l)
                    if l[1] == True:
                        a = Answer.objects.create(text=l[0], right=True)
                    else:
                        a = Answer.objects.create(text=l[0])
                    answer_list.append(a)
        q = Question.objects.create(text=str(j))
        for answer in answer_list:
            q.answers.add(answer)
        question_list.append(q)
        answer_list = []
    for question in question_list:
        t.questions.add(question)
    t.save()



def my_tests(request):
    questions_dict = {}
    qs = {}
    tests = Test.objects.all()
    return render(request, 'my_tests.html', {"tests": tests})

def add_test(request):
    if request.method == "POST":
        post = dict(request.POST)
        content = request.POST['content']
        print(content)
        questions_list = []
        for i in post:
            if 'question_' in str(i):
                number1 = i.split('_')[1]
                for j in post:
                    if 'v_' in str(j):
                        number2 = j.split('_')[1]
                        if number1 == number2:
                            answers_list = []
                            for k in post[j]:
                                if k != '':
                                    print(k)
                                    try:
                                        z = post['r_{}'.format(str(j)[2:])]
                                        ind_z = True
                                    except KeyError:
                                        ind_z = False
                                    lst = [k, ind_z]
                                    print(lst)
                                    answers_list.append(k)
                                    print('123',answers_list)
                            question = post[i]
                            if question[0] != '':
                                question_dict = {question[0]: answers_list}
                            else:
                                question_dict = {'Не заполнено': answers_list}
                            answers_list = []
                questions_list.append(question_dict)
        print(questions_list)
        createTest(post['testName'][0], questions_list, content)
    else:
        diapazon = range(1,5)
        form = AddTestForm()
        return render(request,'add_test.html', {'range': diapazon, 'form':form})
    return redirect('my_tests')

def test_detail(request, pk):
    test = Test.objects.get(pk=pk)
    questions_dict = {}
    qs = {}
    questions = test.questions.all()
    for question in questions:
        answers = []
        for i in question.answers.all():
            answers.append({"id": i.pk, "text": i.text})
        questions_dict[question.pk] = answers
        qs[question.pk] = question.text
    return render(request, 'test_detail.html', {"test":test,"questions":questions_dict, "qs":qs})


def pred_test(request, pk):
    test = Test.objects.get(pk=pk)
    return render(request, 'pred_test_content.html', {"test":test})
'''