from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Count

from article.models import ArticlePost,Comment
from article.forms import CommentForm
import redis
from django.conf import settings

r=redis.StrictRedis(host=settings.REDIS_HOST,port=settings.REDIS_PORT,db=settings.REDIS_DB)


def article_titles(request,username=None):
    if username:
        user=User.objects.get(username=username)
        article_title=ArticlePost.objects.filter(author=user)
        try:
            userinfo=user.userinfo
        except:
            userinfo=None
    else:
        article_title=ArticlePost.objects.all()

    paginator=Paginator(article_title,2)
    page=request.GET.get('page')
    try:
        current_page=paginator.page(page)
        articles=current_page.object_list
    except PageNotAnInteger:
        current_page = paginator.page(1)
        articles = current_page.object_list
    except EmptyPage:
        current_page = paginator.page(paginator.num_pages)
        articles = current_page.object_list
    if username:
        return render(request,'article/list/author_articles.html',{"articles":articles,"page":current_page,
                                                                   "userinfo":userinfo,"user":user})
    else:
        return render(request,'article/list/article_titles.html',{'articles':articles,

                                                              'page':current_page})
def article_detail(request,id,slug):
    article=get_object_or_404(ArticlePost,id=id,slug=slug)
    total_views=r.incr("article:{}:views".format(article.id))
    #即文章被访问一次，article_ranking 就将该文章 id的值增加 1
    r.zincrby('article_ranking',1,article.id)
    #得到 article_ranking 中排序前 10 名的对象
    article_ranking=r.zrange('article_ranking',0,-1,desc=True)[:10]
    article_ranking_ids=[int(id) for id in article_ranking]
    #其功能是查询出 id 在 article_ranking_ids中的所有文章对象，并以文章对象为元素生成列表。
    most_viewed=list(ArticlePost.objects.filter(id__in=article_ranking_ids))
    most_viewed.sort(key=lambda x:article_ranking_ids.index(x.id))

    if request.method=='POST':
        comment_form=CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment=comment_form.save(commit=False)
            new_comment.article=article
            new_comment.save()
    else:
        comment_form=CommentForm()
    #得到 article 对象的属性 article_tag 的 id 列表
    article_tags_ids=article.article_tag.values_list("id",flat=True)
    #找出文章标签的 id 在 article_tags_ids（列表）里面的所有 ArticlePost;第一部分筛选出来的结果中，将当前文章清除
    similar_articles=ArticlePost.objects.filter(article_tag__in=article_tags_ids).exclude(id=article.id)
    #根据与当前文章相同的标签数量进行标注
    similar_articles=similar_articles.annotate(same_tags=Count("article_tag")).order_by('-same_tags','-created')[0:4]
    return render(request,"article/list/article_content.html",{"article":article,
                                                               "total_views":total_views,
                                                               "most_viewed":most_viewed,
                                                               "comment_form":comment_form,
                                                               'similar_articles':similar_articles})


@csrf_exempt
@require_POST
@login_required(login_url='account/login/')
def like_article(request):
    article_id=request.POST.get("id")
    action=request.POST.get("action")
    if article_id and action:
        try:
            article=ArticlePost.objects.get(id=article_id)
            if action=="like":
                article.users_like.add(request.user)
                return HttpResponse("1")
            else:
                article.users_like.remove(request.user)
                return HttpResponse("2")
        except:
            return HttpResponse("no")
