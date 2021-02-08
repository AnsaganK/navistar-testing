from django import template
import json
from doc_tables.models import *

register = template.Library()

@register.filter(name='returnDicEl')
def returnDicEl(data, id):
    return data[id]


@register.filter(name='checkCount')
def checkCount(data):
    count = 0
    for i in data:
        print(i)
        if i['right']:
            count+=1

    return count == 1

@register.filter(name='countModAndTems')
def countModAndTems(model):
    data = model.content_data
    data = json.loads(data)
    mod = 0
    tems = 0
    tests = model.childrenTest.count()
    for i in data:
        mod+=1
        for j in data[i]:
            tems+=1
    return "{0} модулей, {1} тем, {2} тестов".format(mod, tems-tests, tests)

@register.filter(name='hasNotGroup')
def hasNotGroup(user, group):
    for i in user.groups.all():
        if i.name == group:
            return False
    return True

@register.filter(name='userTests')
def userTests(test):
    test = User_tests.objects.filter(test=test, success=True)
    test_count = test.count()
    return test_count

@register.filter(name='returnPercent')
def returnPercent(total,right):
    try:
        return round(right/total*100, 1)
    except:
        return "Не пройдено"


@register.filter(name='returnChildrenTest')
def returnChildrenTest(test, user):
    data = test.childrenTest.all()
    print(data)
    zets = []
    for i in data:
        t = Test.objects.get(pk=i.pk)
        zet = User_tests.objects.get(test=t, user=user)
        zets.append(zet)
    return zets