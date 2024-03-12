import json
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView,DeleteView
from braces.views import LoginRequiredMixin
from django.views.generic.base import TemplateResponseMixin

from course.forms import CreateCourseForm, CreateLessonForm
from course.models import Course, Lesson


class AboutView(TemplateView):
    template_name = 'course/about.html'

#使用 ListView 来读取数据库表中课程数据记录
#声明了类，并且继承 ListView
class CourseListView(ListView):
    #声明本类所用到的数据模型,得到相应数据库表（此处是 course_course 表）中的所有记录
    #但是没有使用 Course.objects.all()
    model = Course
    #声明了传入模板中的变量名称。如果不写则模板默认变量名称是 object
    context_object_name = "courses"
    #声明模板文件
    template_name = 'course/course_list.html'

#创建了类 UserMixin，表示这个类将被用于后面的类中，而不是作为视图使用
class UserMixin:
    def get_queryset(self):
        qs=super(UserMixin,self).get_queryset()
        return qs.filter(user=self.request.user)

#还是一个 Mixin，但它继承了 UserMixin，意味着UserMixin中所定义的方法也被带入到UserCourseMixin
class UserCourseMixin(UserMixin,LoginRequiredMixin):
    model=Course
    #声明了用户登录的 URL,需要继承braces的LoginRequiredMixin
    login_url = "/account/login/"

#继承顺序，这种顺序是有讲究的，一般将 Mixin 类放在左边，其他类放在右边。这里显然是多重继承，
#类 UserCourseMixin 所代入的就是UserMixin和UserCourseMixin两个类中所定义的方法和属性。
# 类似地，还能够创建其他的类，继承serMixin和UserCourseMixin的类，从而不必在类中重复相同的代码

class ManageCourseListView(UserCourseMixin,ListView):
    context_object_name = "courses"
    template_name = 'course/manage/manage_course_list.html'

#以上代码用于用户登录后，进入“后台管理”，对课程进行“增删改查”等操作

#继承对象列表中包括 CreateView（一个通用视图类），当用户以 GET 方式请求时，即在页面中显示表单
#CreateView 就是完成这个作用的类，只要继承它，就不需要写 get()方法了
class CreateCourseView(UserCourseMixin,CreateView):
    #声明在表单中显示的字段
    fields = ['title','overview']
    template_name = 'course/manage/create_course.html'

    #专门处理以 POST 方式提交的表单内容，处理方法与以往的方法一样
    def post(self, request, *args, **kwargs):
        form=CreateCourseForm(data=request.POST)
        if form.is_valid():
            new_course=form.save(commit=False)
            new_course.user=self.request.user
            new_course.save()
            #当表单内容被保存后，将页面转向指定位置
            return redirect("course:manage_course")
        #在表单数据检测不通过时，让用户重新填写，注意这里没有使用 render()，而是使
        #用了实例的render_to_response()方法
        return self.render_to_response({"form":form})


#类继承 DeleteView 类后，后续代码就不需要重复删除动作了，只需要声明确认
#删除的模板 template_name 和删除完成之后的界面 success_url 即可
# class DeleteCourseView(UserCourseMixin,DeleteView):
#     template_name = 'course/manage/delete_course_confirm.html'
#     success_url = reverse_lazy("course:manage_course")

#改写删除类，为了不跳转页面
class DeleteCourseView(UserCourseMixin,DeleteView):
    # template_name = 'course/manage/delete_course_confirm.html'
    success_url = reverse_lazy("course:manage_course")

    #重写了 DeleteView 类中的 dispatch()方法，在这个方法中首先执行语句resp=super(DeleteCourseView,self).dispatch(*args,**kwargs)
    #原本在DeleteView 类中执行 dispatch()方法后，会实现 URL 的转向，但是在此指令发送给前端之前，
    #通过if self.request.is_ajax():进行判断，如果是 Ajax 方法提交过来的数据，就直接反馈 HttpResponse 对象给前端，
    #前端的 JavaScript 函数得到反馈结果，这样就完成了删除和页面的刷新。为此，在前端模板中
    #就要嵌入 JavaScript 代码
    def dispatch(self, *args, **kwargs):
        resp=super(DeleteCourseView,self).dispatch(*args,**kwargs)
        if self.request.is_ajax():
            response_data={"result":"ok"}
            return HttpResponse(json.dumps(response_data),content_type="application/json")
        else:
            return resp


#这个类依然可以继承 CreateView，但为了学习技能，改用其他方法
#语句①所引入的类在有的程序中也写成 from django.views.generic.base import View，所引入
#的 View 类是所有基于类的视图的基类，前面已经学习过的 CreateView 等都继承了它。
#在 View 类中没有默认的 get()和 post()方法，因此需要动手写这两个方法，以响应前端发出
#的两种方式的请求
class CreateLessonView(LoginRequiredMixin, View):
    model = Lesson
    login_url = "/account/login/"

    #因为 get()是当前所在类中的一个方法，所以第一个参数必须是self。
    #另外，get()还要接收网站前端所提交的数据，即 HttpRequest 对象，所以第二个参数使用request
    #，这与写视图函数一样。后面的参数是什么意思呢?
    def get(self, request, *args, **kwargs):
        #创建了表单类的实例，注意在表单类 CreateLessonForm 中，已经重写了初始化函数__init__()，
        #并且增加了一个参数 user，所以在实例化时需要传入 user 值。
        form = CreateLessonForm(user=self.request.user)
        return render(request, "course/manage/create_lesson.html", {"form": form})

    #响应用户提交的表单
    def post(self, request, *args, **kwargs):
        #提交的表单中有上传的文件，所以必须传入 request.FILES。
        form = CreateLessonForm(self.request.user, request.POST, request.FILES)
        if form.is_valid():
            new_lesson = form.save(commit=False)
            new_lesson.user = self.request.user
            new_lesson.save()
            return redirect("course:manage_course")

#引入了 TemplateResponseMixin 类，它提供了一种模板渲染的机制，在子类中，可以
#指定模板文件和渲染数据
class ListLessonView(LoginRequiredMixin,TemplateResponseMixin,View):

    login_url = "/account/login/"
    template_name = 'course/manage/list_lesson.html'

    #相应前端 GET 请求的方法，因为要识别课程标题，所以传入了参数 course_id。
    #根据 course_id 得到当前的“课程标题”对象
    def get(self, request, course_id):  # ④
        course = get_object_or_404(Course, id=course_id)  # ⑤
        #将该数据渲染到模板中,render_to_response()就是 TemplateResponseMixin 类的方法。
        return self.render_to_response({'course': course})


class DetailLessonView(LoginRequiredMixin,TemplateResponseMixin,View):
    login_url = '/account/login/'
    template_name = 'course/manage/detail_lesson.html'

    def get(self,request,lesson_id):
        lesson=get_object_or_404(Lesson,id=lesson_id)
        return self.render_to_response({'lesson':lesson})


#类继承上面已经创建的 ListLessonView 类，因为显示的模板文件有所不同
#重写模板
class StudentListLessonView(ListLessonView):
    template_name = 'course/slist_lessons.html'

    #因为以 Ajax 方式向视图端提交了注册本课程的信息类中要写一个 POST 方法
    def post(self, request, *args, **kwargs):
        course = Course.objects.get(id=kwargs['course_id'])
        course.student.add(self.request.user)
        return HttpResponse("ok")

class StudentDetailLessonView(DetailLessonView):
    template_name = 'course/sdetail_lesson.html'

