from django.contrib import admin
from .models import BlogArticles
# Register your models here.


class BlogArticlesAdmin(admin.ModelAdmin):
    #显示字段
    list_display = ('title','author','publish')
    #右边显示的过滤器
    list_filter = ('publish','author')
    #搜索框
    search_fields = ('title','body')
    #添加博客时作者由选择下拉框变为弹出页面，且显示ID
    raw_id_fields = ('author',)
    #在博客标题上方显示日期，用于检索指定日期的博客
    date_hierarchy = 'publish'
    #博客的排序
    ordering = ['-publish','author']

admin.site.register(BlogArticles,BlogArticlesAdmin)


