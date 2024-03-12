from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from slugify import slugify
from course.fields import OrderField


class Course(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='courses_user')
    title=models.CharField(max_length=200)
    slug=models.SlugField(max_length=200,unique=True)
    overview=models.TextField()
    created=models.DateTimeField(auto_now_add=True)
    student=models.ManyToManyField(User,related_name="courses_joined",blank=True)

    class Meta:
        ordering=('-created',)

    def save(self,*args,**kwargs):
        self.slug=slugify(self.title)
        super(Course,self).save(*args,**kwargs)

    def __str__(self):
        return self.title


#这个函数接收两个参数，instance 引用的是 Lesson 类实例，filename 则为得到的文件名
#Lesson 类中upload_to 就可以通过这个函数确定新的文件存储路径
def user_directory_path(instance,filename):
    return "courses/user_{0}/{1}".format(instance.user.id,filename)


class Lesson(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='lesson_user')
    course = models.ForeignKey(Course, on_delete=models.CASCADE,related_name='lesson')
    title = models.CharField(max_length=200)
    #接收上传的视频, upload_to规定所上传文件的存储路径
    #最好是把用户上传的文件存放到用户自己的目录中，于是可以在这个类前面
    #增加一个函数user_directory_path
    video = models.FileField(upload_to=user_directory_path)
    description = models.TextField(blank=True)
    #接收上传的附件
    attach = models.FileField(blank=True, upload_to=user_directory_path)
    created = models.DateTimeField(auto_now_add=True)
    #order 用来存储某内容在相应的课程标题 Course 中的序号（序号从 0 开始）
    order = OrderField(blank=True, for_fields=['course'])

    class Meta:
        ordering = ['order']

    def __str__(self):
        return '{}.{}'.format(self.order, self.title)

