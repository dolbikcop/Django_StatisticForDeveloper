"""djangoProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from myapp1 import views
# from rest_framework.routers import SimpleRouter
from django.conf import settings
from django.conf.urls.static import static
# from myapp1.views import ExampleView

# router = SimpleRouter()
# router.register("api/vacancies", ExampleView)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index_page, name='home'),
    path('relevance/', views.relevance_page, name='relevance'),
    path('geography/', views.geography_page, name='geography'),
    path('skills/', views.skills_page, name='skills'),
    path('recent-vacancies/', views.recent_vacancies_page, name='recent-vacancies'),
    path('add-vacancy', views.add_vacancy, name='add-vacancy'),
    path('vue/', views.vue_page, name='vue')
]

# urlpatterns += router.urls
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
