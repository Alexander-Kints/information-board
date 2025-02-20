from django.urls import path
from info_board.employee import views

urlpatterns = [
    path('list/', views.EmployeeListAPIView.as_view()),
]
