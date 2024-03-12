from django import forms

from course.models import Course,Lesson


class CreateCourseForm(forms.ModelForm):
    class Meta:
        model=Course
        fields=("title","overview")


class CreateLessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['course', 'title', 'video', 'description', 'attach']


    #如果按照上面表单类中的 fields 声明，必然会列出所有用户创建的 course，而这不是功能所需要的。
    #功能的要求是每个用户只能看到自己所设置的课程标题。对于这个需求，可以在视图中解决，
    #而这里要讲解一种在表单类中解决的方法，就是重写__init__()初始化函数
    #参数多了一个 user，通过这个参数传入当前用户,筛选出当前用户的 course 值
    def __init__(self, user, *args, **kwargs):
        super(CreateLessonForm, self).__init__(*args, **kwargs)
        self.fields['course'].queryset = Course.objects.filter(user=user)

