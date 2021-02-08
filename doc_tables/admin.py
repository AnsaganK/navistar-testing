from django.contrib import admin
from .models import *
from django import forms

from ckeditor_uploader.widgets import CKEditorUploadingWidget


class TestAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget())
    class Meta:
        model = Test
        fields = '__all__'


admin.site.register(Tables)
admin.site.register(Data)
admin.site.register(Profile)
admin.site.register(User_tests)
admin.site.register(TestUUID)

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('name', 'date')
    list_display_links = ('name', 'date')
    form = TestAdminForm