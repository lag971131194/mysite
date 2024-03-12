from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from image.forms import ImageForm
from image.models import Image


@login_required(login_url='/account/login/')
@csrf_exempt
@require_POST
#处理前端表单提交的图片 URL 及其相关信息
def upload_image(request):
    #利用提交的数据建立了表单类的实例
    form=ImageForm(data=request.POST)
    if form.is_valid():
        try:
            #使用该实例的 save()方法,但这里没有保存数据（commit=False）
            new_item=form.save(commit=False)
            new_item.user=request.user
            #该图片被保存到本地指定目录中
            new_item.save()
            #返回的是 JSON 数据
            return JsonResponse({'status':"1"})
        except:
            return JsonResponse({'status':"0"})


@login_required(login_url='/account/login/')
#展示图片的函数
def list_images(request):
    images=Image.objects.filter(user=request.user)
    return render(request,'image/list_images.html',{"images":images})


@login_required(login_url='/account/login/')
@csrf_exempt
@require_POST
def del_image(request):
    image_id=request.POST['image_id']
    try:
        image=Image.objects.get(id=image_id)
        image.delete()
        return JsonResponse({'status':"1"})
    except:
        return JsonResponse({'status':"2"})

#“瀑布流”是一种网站页面布局方式，在视觉上表现为参差不齐的多栏布局，
#随着页面滚动条向下滚动，这种布局还会不断加载数据块并附加至当前尾部
def falls_images(request):
    images=Image.objects.all()
    return render(request,'image/falls_images.html',{'images':images})