from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from .forms import *
import pandas
import json
from .models import *
from datetime import datetime
from django.contrib.auth.models import Group
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

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
    tests = User_tests.objects.filter(user=request.user, test__baseTest=None)
    return render(request,'index.html', {'tests':tests})

@login_required(redirect_field_name='login')
def addTables(request):
    group = Group.objects.get(name="employees")
    users = group.user_set.all()
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
    new_group = Group.objects.get(name='testingUsers')
    today = datetime.today()
    new_users = new_group.user_set.filter(date_joined__day=today.day,date_joined__month=today.month,date_joined__year=today.year)
    return render(request, 'list_user.html', {'users':users, 'new_users':new_users, 'today':today})

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
    if user == request.user:
        return redirect('index')
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


def createTest(name, questions, users,user,content_data=None, pks=None):
    content_data = json.dumps(content_data)
    t = Test.objects.create(name=name,content_data=content_data,create_user=user, unique_slug=TestUUID.objects.create())
    question_list = []
    for i in questions:
        answer_list = []
        for j,k in i.items():
            if k!=[]:
                for l in k:
                    if l[1] == True:
                        a = Answer.objects.create(text=l[0], right=True)
                    else:
                        a = Answer.objects.create(text=l[0])
                    answer_list.append(a)

        q = Question.objects.create(text=str(j))
        for answer in answer_list:
            q.answers.add(answer)
        question_list.append(q)
        #answer_list = []
    for question in question_list:
        t.questions.add(question)
    for pk in pks:
        pk.baseTest = t
        pk.save()
    t.save()
    for i in users:
        User_tests.objects.create(user=i, test=t)

def createModTest(data,name):
    test = Test.objects.create(name=name, unique_slug=TestUUID.objects.create())
    questionsList = []
    for i in data:
        questionTitle = i[0]
        question = Question.objects.create(text=questionTitle)
        answerList = []
        for k in i[1]:
            answerTitle = k[0]
            if k[1] == 'false':
                right = False
            else:
                right = True
            answer = Answer.objects.create(text=answerTitle, right=right)
            answerList.append(answer)
        for j in answerList:
            question.answers.add(j)
        questionsList.append(question)
    print("questionList : ",questionsList)
    for i in questionsList:
        test.questions.add(i)
    return test


def my_tests(request):
    questions_dict = {}
    qs = {}
    tests = Test.objects.filter(archive=False, create_user=request.user)
    return render(request, 'my_tests.html', {"tests": tests})

def createTestHtml(pk, number):
    test = Test.objects.get(pk=pk)
    questions = test.questions.all()
    z = ''

    #action = "\moduleTestValid\{0}"
    form = '''
    <form name="{0}" action="\moduleTestValid\{0}" data-success="success" method="post">
            <div class="tabs tabs_questions">
            <input type="text" style="display:content;" name="m_number" value={1}>
    '''.format(test.unique_slug.slug, number)

    question_number_list = ''
    zero = 0
    for i in questions:
        zero+=1
        first = ""
        if zero == 1:
            first = "checked"
        question_number = '''
        <input type="radio" class="tab_btn_pk" data-pks-id={2} name="tab-btn" id="tab-btn-{2}" value="" {1}>
                    <label for="tab-btn-{2}">{0}</label>
        '''.format(zero, first, i.pk)
        question_number_list+=question_number
        print(question_number_list)
    question_content_list = ''
    zero1 = 0
    for i in questions:
        zero1+=1
        content = '''
        <div id="content-{2}">
                         Вопрос {0}:<br>  {1}<ul class="test">
        '''.format(zero1, i.text, i.pk)
        answer_list = ''
        if i.answers.filter(right=True).count() <= 1:
            for j in i.answers.all():
                answer = '<li><input type="radio" id="{0}_{1}" name="{0}" value="{1}"><label for="{0}_{1}">{2}</label></li>'.format(i.pk, j.pk, j.text)
                answer_list += answer
        else:
            for j in i.answers.all():
                answer = '<li><input type="checkbox" id="{0}_{1}" name="{0}" value="{1}"><label for="{0}_{1}">{2}</label></li>'.format(i.pk, j.pk, j.text)
                answer_list += answer
        content+=answer_list
        content += '</ul></div>'

        question_content_list += content
    form+=question_number_list
    form+=question_content_list
    form+='''
    <button type="submit" style="
    background-color: #f56f6f;
    border-color: #ff6d6d;
    box-shadow: 0px 0px 2px #636363;
    border: 0px;
    color: #ffffff;
    float: right;
    padding: 10px;
    cursor: pointer;
    margin-top: 20px;
">Завершить</button>
            </div>
        </form>
    '''.format(test.unique_slug.slug)
    print(form)
    return form

def add_test(request):
    if request.method == "POST":
        post = dict(request.POST)
        r = post["content_data"][0]
        print(r)
        z = json.loads(r)
        pks = []
        new_content_data = {}
        p = 0
        for i in z:
            lst = []
            try:
                for j in i[1]:
                    print("J = ",j)
                    for t in post:
                        if t!="content_data" and "content_" in t and t.split('_')[1] == j[0]:
                            if t.split('_')[-1] == 'test':
                                p+=1
                                jsonLoad = json.loads(post[t][0])
                                #print(jsonLoad)
                                #print(post[t][0])
                                pk = createModTest(jsonLoad, j[1])
                                pks.append(pk)
                                j.append(createTestHtml(pk.id, j[0]))
                                lst.append(j)
                            else:
                                j.append(post[t][0])
                                lst.append(j)
                    new_content_data[i[0]] = lst
            except IndexError:
                new_content_data[i[0]] = []
                continue

        questions_list = []
        users = []
        for i in post:
            if 'user_' in i:
                user = User.objects.get(pk=i.split('_')[1])
                users.append(user)
        for i in post:
            if 'question_' in str(i):
                number1 = i.split('_')[1]
                for j in post:
                    if 'v_' in str(j):
                        number2 = j.split('_')[1]
                        if number1 == number2:
                            answers_list = []
                            zero = 0
                            for k in post[j]:
                                zero += 1
                                if k != '':
                                    try:
                                        z = post['r_{0}_{1}'.format(str(j)[2], zero)]
                                        ind_z = True
                                    except KeyError:
                                        ind_z = False
                                    lst = [k, ind_z]
                                    answers_list.append(lst)
                            question = post[i]
                            if question[0] != '':
                                question_dict = {question[0]: answers_list}
                            else:
                                question_dict = {'Не заполнено': answers_list}
                            answers_list = []
                questions_list.append(question_dict)
        createTest(name=post['testName'][0], questions=questions_list, users=users, content_data=new_content_data, user=request.user, pks=pks)
    else:
        users = User.objects.all()
        diapazon = range(1,5)
        form = AddTestForm()
        return render(request,'add_test.html', {'range': diapazon, 'form':form, 'users':users})
    return redirect('my_tests')

def content_create(request):
    return None

@login_required(redirect_field_name='login')
def test_detail(request, slug):
    test = Test.objects.get(unique_slug=slug)
    for i in request.user.tests.all():
        if i.test == test and i.success:
            return render(request, 'errorTest.html')
    questions_dict = {}
    qs = {}
    questions = test.questions.all()
    if test.archive and test.create_user != request.user:
        return render(request, '404test.html', {'test': test})
    else:
        for question in questions:
            answers = []
            for i in question.answers.all():
                answers.append({"id": i.pk, "text": i.text, "right": i.right})
            questions_dict[question.pk] = answers
            qs[question.pk] = question.text
        return render(request, 'test_detail.html', {"test":test, "questions":questions_dict, "qs":qs})

@csrf_exempt
@login_required(redirect_field_name='login')
def pred_test(request, slug):
    try:
        test = Test.objects.get(unique_slug=slug)
    except:
        return render(request, 'nonSlugExist.html', {'slug':slug})
    user = request.user
    print(user.tests)
    try:
        user_test = User_tests.objects.get(user=user, test=test)
        print(user_test)
    except User_tests.DoesNotExist:
        print(123)
        user_test = User_tests.objects.create(user=user, test=test, content_test_for_user=test.content_data)
        user_test.save()
    for i in request.user.tests.all():
        if i.test == test and user_test.success:
            return render(request, 'errorTest.html')
    if request.user.is_authenticated:
        if test.archive and test.create_user != request.user:
            return render(request, '404test.html', {'test': test})
        else:
            #print(test.content_data)
            content_data = json.loads(user_test.content_test_for_user)
            return render(request, 'pred_test_content.html', {"questions":range(60),"test":test, "content_data":content_data})
    else:
        return render(request, 'registration/signup.html', {'test_slug':'/testContent/{}'.format(test.unique_slug.slug)})

@login_required(redirect_field_name='login')
def testIsValid(request, slug):
    if request.method == "POST":
        test = Test.objects.get(unique_slug=slug)
        for i in request.user.tests.all():
            if i.test == test and i.success:
                total = test.questions.count()
                percent = round(i.right_answer / total * 100, 1)
                return render(request,'test_result.html',{"total":total,"result":i.right_answer, "percent":percent})
        total = test.questions.count()
        post = dict(request.POST)
        zero = 0
        for i in post:
            if i!="csrfmiddlewaretoken" and i!="tab-btn":
                question = Question.objects.get(pk = i)
                right_answers_count = question.answers.filter(right=True).count()
                check_answer_count = 0
                for j in post[i]:
                    answer = Answer.objects.get(pk = j)
                    right = answer.right
                    if right == True:
                        check_answer_count += 1
                if check_answer_count == right_answers_count:
                    zero+=1
        percent = round(zero/total*100, 1)
        if request.user != test.create_user:
            user_test = User_tests.objects.get(user=request.user, test=test)
            user_test.date_end = datetime.now()
            user_test.success = True
            user_test.right_answer = zero
            user_test.count_answer = total
            user_test.save()
        return render(request,'test_result.html',{"total":total,"result":zero, "percent":percent})
    return redirect('my_tests')

def addArchiveTests(request, slug):
    test = Test.objects.get(unique_slug=slug)
    test.archive = True
    test.save()
    return redirect('my_tests')

def archive_tests(request):
    tests = Test.objects.filter(archive=True, create_user=request.user)
    return render(request, "archive_test.html", {"tests":tests})

def delete_tests(request, slug):
    test = Test.objects.get(unique_slug=slug)
    test.delete()
    return redirect("archive_tests")

def return_my_tests(request, slug):
    test = Test.objects.get(unique_slug=slug)
    test.archive = False
    test.save()
    return redirect('archive_tests')

def signup(request):
    if request.user.is_authenticated and Group.objects.get(name='testingUsers') not in request.user.groups.all():
        return redirect('my_files')
    elif request.user.is_authenticated and Group.objects.get(name='testingUsers') in request.user.groups.all():
        return redirect('/')
    if request.method == 'POST':
        for i in User.objects.all():
            n = str(i.username)
            print(n, ' : ', request.POST["username"])
            if n == str(request.POST["username"]):
                return render(request, 'registration/signup.html',
                              {'word2': True, 'test_slug': request.GET['next']})
        form = SignUpForm(request.POST)
        if form.is_valid():#Если форма заполнена правильно
            form.save()#Создаем пользователя
            username = form.cleaned_data.get('username')#с именем
            raw_password = form.cleaned_data.get('password1')# и паролем

            print(username)
            print(raw_password)
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            group = Group.objects.get(name='testingUsers')
            user.groups.add(group)
            print(user)
            print(login(request, user))
            next = request.GET['next']
            return HttpResponseRedirect(next)#страница редиректа после регистрации
        else:
            print(form.errors)
            word = True
            return render(request, 'registration/signup.html', {'form': form,'word': word, 'test_slug':request.GET['next']})
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required(redirect_field_name='login')
def profile(request):
    user = request.user
    return render(request, 'profile.html', {'user':user})

def user_test_list(request, slug):
    test = Test.objects.get(unique_slug=slug)
    users = User_tests.objects.filter(test =test, success=True)
    return render(request, 'user_test_list.html', {'users':users, 'test':test})

@csrf_exempt
def moduleTestValid(request, slug):
    if request.method == "POST":
        test = Test.objects.get(unique_slug=slug)
        baseTest = test.baseTest
        user = request.user
        print(user.tests)
        print(baseTest.users)
        user_test = User_tests.objects.get(user=user, test=baseTest)
        cont = user_test.content_test_for_user
        #cont = baseTest.content_data
        cont = json.loads(cont)
        for i in request.user.tests.all():
            if i.test == test:
                total = test.questions.count()
                percent = round(i.right_answer / total * 100, 1)
                data = {
                    "1": total,
                    "2": i.right_answer,
                    "3": percent,
                    "status": "testPassed",
                }
                print(434)
                return HttpResponse(str(total)+" : "+str(i.right_answer)+" : "+str(percent))
        total = test.questions.count()
        #Название хоз
        # поле
        # номер пробы
        # имя фамиллия пробоотборщика
        post = dict(request.POST)
        print("posy = ", post)
        zero = 0
        for i in post:
            print(i)
            if i != "m_number" and i != "csrfmiddlewaretoken" and i != "tab-btn":
                question = Question.objects.get(pk=int(i))
                right_answers_count = question.answers.filter(right=True).count()
                print('rac', right_answers_count)
                check_answer_count = 0
                for j in post[i]:
                    answer = Answer.objects.get(pk=int(j))
                    right = answer.right
                    if right == True:
                        check_answer_count += 1
                if check_answer_count == right_answers_count:
                    zero += 1
        percent = round(zero / total * 100, 1)
        if "m_number" in post:
            m_number = post["m_number"][0]
            for y in cont:
                ze = -1
                for o in cont[y]:
                    ze += 1
                    print('0 = ', o)
                    if int(o[0]) == int(m_number) and request.user != baseTest.create_user:
                        o[2] = '''
                                    <div class="svgPic" data-disable={3} data-success="success">
                                        <svg xmlns="http://www.w3.org/2000/svg" height="200" width="200" viewBox="0 0 200 200" data-value="{2}">
                                  <path class="bg" stroke="#ccc" d="M41 149.5a77 77 0 1 1 117.93 0" fill="none"></path>
                                  <path class="meter" stroke="#09c" d="M41 149.5a77 77 0 1 1 117.93 0" fill="none" stroke-dasharray="350" stroke-dashoffset="350" style="stroke-dashoffset: 209.711;"></path>
                                </svg>
                                        <span style="    margin-top: -135px;
                                    font-size: 37px;
                                    color: #0099cc;">{2}%</span>
                                    </div>
                                <p style="
                                    margin-top: 65px;
                                    text-align: center;
                                    color: #0099cc;
                                ">Результаты теста: {0} из {1}</p>
                        '''.format(zero, total, percent, o[0])
                        cont[y][ze] = o
                        user_test.content_test_for_user = json.dumps(cont)
                        user_test.save()
                        print("UesrTets",user_test)
        if request.user != test.create_user :
            User_tests.objects.create(user=request.user, test=test, success=True,date_end=datetime.now(), right_answer=zero, count_answer=total)
        data = {
            "total": total,
            "zero": zero,
            "percent": percent,
            "status": "testSuccess",
        }
    return HttpResponseRedirect(reverse('pred_test', args=[baseTest.unique_slug.slug]))


def foreignTests(request, slug):
    test = Test.objects.get(unique_slug=slug)
    children = test.childrenTest.all()
    tests = []
    for i in children:
        new_test = User_tests.objects.get(user=request.user, test=i)
        if new_test.success:
            tests.append(new_test)
    return render(request, 'foreignTests.html', {'children': tests})