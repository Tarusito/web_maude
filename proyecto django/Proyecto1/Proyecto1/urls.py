"""
URL configuration for Proyecto1 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from Proyecto1 import views  # Importa la vista 'home' desde 'Proyecto1.views'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', views.home, name='home'),  # Usa 'home' directamente como vista
    path('run_maude_command/', views.run_maude_command, name='run_maude_command'),
]

