from django.urls import path
from .views import *
from django.contrib.auth import views as acc

urlpatterns = [
    path('', index, name='index'),
    path('addTables/', addTables, name='addTables'),
    path('addTablesPost/', addTablesPost, name='addTablesPost'),
    path('addArchiveTables/<int:pk>', addArchiveTables, name='addArchiveTables'),
    path('detail_tables/<int:pk>', detail_tables, name='detail_tables'),
    path('my_files/', my_files, name='my_files'),
    path('archive/', archive, name='archive'),
    path('return_my_files/<int:pk>', return_my_files, name='return_my_files'),
    path('delete_archive/<int:pk>', delete_archive, name='delete_archive'),
    path('list_user/', list_user, name='list_user'),
    path('add_user/', add_user, name='add_user'),
    path('add_user_post/', add_user_post, name='add_user_post'),
    path('update_data/<int:pk>', update_data, name='update_data'),
    path('list_user/<int:pk>', detail_user, name='detail_user'),
    path('update_user/<int:pk>', update_user, name='update_user'),
    path('profile/', profile, name='profile'),
    path('delete_user/<int:pk>', delete_user, name='delete_user'),
    path('invitations', invitations, name='invitations'),
]
urlpatterns += [
    path('my_tests', my_tests, name="my_tests"),
    path('add_test', add_test, name="add_test"),
    path('test_detail/<slug:slug>', test_detail, name="test_detail"),
    path('testContent/<slug:slug>', pred_test, name="pred_test"),
    path('testIsValid/<slug:slug>', testIsValid, name="testIsValid"),
    path('addArchiveTests/<slug:slug>', addArchiveTests, name="addArchiveTests"),
    path('archive_tests', archive_tests, name="archive_tests"),
    path('delete_tests/<slug:slug>', delete_tests, name="delete_tests"),
    path('return_my_tests/<slug:slug>', return_my_tests, name="return_my_tests"),
    path('user_test_list/<slug:slug>', user_test_list, name="user_test_list"),
    path('moduleTestValid/<slug:slug>', moduleTestValid, name="moduleTestValid"),
    path('foreignTests/<slug:slug>', foreignTests, name="foreignTests"),
]
urlpatterns += [
    path('accounts/login/',acc.LoginView.as_view(),name='login'),
    path('accounts/logout/',acc.LogoutView.as_view(),name='logout'),
    path('accounts/signup/',signup,name='signup'),
    path('accounts/password-reset',acc.PasswordResetView.as_view(),name='password_reset'),
    path('accounts/password-change/done/', acc.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('accounts/password-change', acc.PasswordChangeView.as_view(),name='password_change'),
]