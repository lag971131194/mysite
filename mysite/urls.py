"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path,include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',TemplateView.as_view(template_name="home.html")),
    path('admin/', admin.site.urls),
    path('blog/',include('blog.urls',namespace='blog')),
    path('account/',include('account.urls',namespace='account')),
    path('article/',include('article.urls',namespace='article')),
    path('home/',TemplateView.as_view(template_name="home.html"),name='home'),
    path('image/',include('image.urls',namespace='image')),
    path('course/',include('course.urls',namespace='course')),
]

#这样就为每个上传的静态图片配置了 URL 路径。做好上面的配置之后再将上面提到
#的./templates/image/list_images.html 文件中将要替代的部分用下面的代码替代。
#<td><img src="{{ image.image.url }}" width="100px" height="100px"></td>
urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)