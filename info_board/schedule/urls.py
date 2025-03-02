from django.urls import path

from info_board.schedule import views

urlpatterns = [
    path('group-schedule/<int:group_id>/', views.GroupScheduleView.as_view()),
    path('faculties/', views.FacultyListView.as_view()),
    path('faculties-groups/', views.FacultyGroupListView.as_view()),
    path(
        'faculties-groups/<int:faculty_id>/',
        views.FacultyGroupView.as_view()
    ),
]
