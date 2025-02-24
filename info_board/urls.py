from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('api/v1/admin/', admin.site.urls),
    path('api/v1/employee/', include('info_board.employee.urls')),
    path('api/v1/schedule/', include('info_board.schedule.urls')),
]
