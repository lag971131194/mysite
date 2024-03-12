from django.contrib.auth.models import User
from django.db import models
from slugify import slugify
# Create your models here.

class Image(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='images')
    title=models.CharField(max_length=300)
    #存储网络图片的 URL
    url=models.URLField()
    # Image 对象的 slug 字段，与本书前面提到的一样，用在 URL 显示上。
    slug=models.SlugField(max_length=500,blank=True)
    #存储描述图片的文本内容
    description=models.TextField(blank=True)
    #db_index=True 意味着用数据库的此字段作为索引
    created=models.DateField(auto_now_add=True,db_index=True)
    #规定了图片上传到服务器的物理存储地址.upload_to 规定了所上传的图片文件的存储路径
    image=models.ImageField(upload_to='images/%Y/%m/%d')

    def __str__(self):
        return self.title
    #重写了父类的 save 方法.当通过 Image 实例调用此方法时，自动实现 slug 的生成slugify(self.title)）和存储
    def save(self,*args,**kwargs):
        self.slug=slugify(self.title)
        super(Image,self).save(*args,**kwargs)