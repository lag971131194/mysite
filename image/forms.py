from urllib import request

from django import forms
from django.core.files.base import ContentFile
from slugify import slugify


from image.models import Image


class ImageForm(forms.ModelForm):
    class Meta:
        model=Image
        fields=('title','url','description')

    #处理某个字段值.
    def clean_url(self):
        #通过 self.cleaned_data 获取相应字段的值
        url=self.cleaned_data['url']
        #规定了图片的扩展名
        valid_extensions=['jpg','jpeg','png']
        #rsplit()表示从右侧开始将字符串拆分为列表，切片类表从左到右下标从0开始
        #从得到的图片的网址中分解出其扩展名
        extension=url.rsplit('.',1)[1].lower()
        if extension not in valid_extensions:
            raise forms.ValidationError("The given Url does not match valid image extension.")
        #将经过验证后的字段值返回
        return url

    #重写了save()这个方法，当通过 ImageForm 类实例调用 save()方法时，调用
    def save(self,force_insert=False,force_update=False,commit=True):
        #执行父类 ModelForm 的 save()方法，commit=False 意味着实例虽然被建立了,但并没有保存数据
        image=super(ImageForm,self).save(commit=False)
        image_url=self.cleaned_data['url']
        image_name='{0}.{1}'.format(slugify(image.title),image_url.rsplit('.',1)[1].lower())
        # Python 标准库 Urllib 中的一部分,是一个很好的爬虫工具.以 GET 方式访问该图片地址,
        #览器中返回相应的内容，这里同样返回一个 Request 对象
        response=request.urlopen(image_url)
        #通过该对象得到所访问 URL 的数据, response.read()就是要得到此数据
        #结果保存到本地,并按照约定的名称给该图片文件命名
        image.image.save(image_name,ContentFile(response.read()),save=False)
        if commit:
            image.save()
        return image
