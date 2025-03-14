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
    path(
        'employee-schedule/<int:employee_id>/',
        views.EmployeeScheduleView.as_view()
    ),
    path('search/', views.SearchScheduleView.as_view()),
    path('week-type/', views.WeekTypeView.as_view()),
    path(
        'room-schedule/<int:room_id>/',
        views.RoomScheduleView.as_view()
    ),
]
