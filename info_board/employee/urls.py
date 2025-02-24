from django.urls import path
from info_board.employee import views

urlpatterns = [
    path('list/', views.EmployeeListView.as_view()),
]
