from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('problems/', include('problems.urls')),
    path('ai_chat/', include('ai_chat.urls')),
    path('code_execution/', include('code_execution.urls')),
]
