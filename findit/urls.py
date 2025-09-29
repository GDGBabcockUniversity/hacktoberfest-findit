from django.urls import path

from . import views

# urls for the app, these urls are included in the main urls.py file in the project folder

urlpatterns = [
    path('', views.index.as_view(), name='index'),
    path('login/', views.login_view.as_view(), name='login'),
    path('register/', views.register.as_view(), name='register'),
    path('app/', views.app.as_view(), name='app'),
    path('lostitems/', views.lostitems.as_view(), name='lostitems'),
    path('view-items/', views.viewItems.as_view(), name='viewItems'),
    path('report-item/', views.reportItem.as_view(), name='reportItem'),
    path('notification/', views.notification.as_view(), name='notification'),
    path('manage-report/', views.manageReport.as_view(), name='manageReport'),
    path('edit-profile/', views.edit_profile.as_view(), name='editProfile'),
    path('logout/', views.logout_view, name='logout'),
    path('claim-item/<int:item_id>/', views.claim_item, name='claim_item'),
]