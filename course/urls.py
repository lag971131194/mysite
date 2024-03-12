from django.urls import path
# from django.views.generic import TemplateView
from . import views

app_name="course"

urlpatterns=[
    path('about/',views.AboutView.as_view(),name='about'),
    path('course-list/',views.CourseListView.as_view(),name='course_list'),
    path('manage-course/',views.ManageCourseListView.as_view(),name='manage_course'),
    path('create-course/',views.CreateCourseView.as_view(),name='create_course'),
    #在默认状态下，DeleteView 类接收以 pk 或者 slug 作为参数传入的值，并且通过 GET 方式
    #访问一个删除的确认页面，然后以 POST 方式提交删除表单，才能完成删除。
    #按照上述流程，以 GET 方式访问的地址就是配置的 URL其模板页面即为 template_name 所规定的页面
    path('delete-course/<int:pk>/',views.DeleteCourseView.as_view(),name='delete_course'),
    path('create-lesson/',views.CreateLessonView.as_view(),name='create_lesson'),
    path('list-lesson/<int:course_id>/',views.ListLessonView.as_view(),name='list_lesson'),
    path('detail-lesson/<int:lesson_id>/',views.DetailLessonView.as_view(),name='detail_lesson'),
    path('lessons-list/<int:course_id>/',views.StudentListLessonView.as_view(),name='lessons_list'),
    path('lessons-detail/<int:lesson_id>/',views.StudentDetailLessonView.as_view(),name='lessons_detail'),
]