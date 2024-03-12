from django.db import models
from django.core.exceptions import ObjectDoesNotExist



#每个课程标题下会有一个或者多个课程内容，这里就涉及到对课程内容排序的问题了。虽
#然可以用自增的 id 作为排序字段，但是不能显示该内容在相应课程标题下的顺序（序号就不连
#贯了，当然在显示的时候，也能够处理成连贯的）。下面讲解一种方法，实现在数据库中保存该
#内容在相应课程标题下的序号
#这就是学习“自定义字段属性”的理由，根据此理由，创建一个自定义的字段属性。创建 fields.py 文件

#自定义的字段属性在本质上就是一个类,OrderField定义了类的名称，并且继承 models.PositiveIntegerField
#这里所定义的 OrderField 是要得到对象排序的序号，其值为整数，所以继承 models.PositiveIntegerField 是合适的。

class OrderField(models.PositiveIntegerField): #③
    def __init__(self, for_fields=None, *args, **kwargs):
        self.for_fields = for_fields
        super(OrderField, self).__init__(*args, **kwargs)

    # 在Django的字段属性中,都继承了 Field 类，pre_save()就是 Field 类中的一个方法
    # pre_save()方法的作用是在保存之前对数值进行预处理，在具体的某个字段属性中，因为特
    # 殊需要，常常将 Field 类中的这个方法重写。例如前面已经用到的 DateTimeField，曾经在数据
    # 模型类中有这样的属性（字段）created = models.DateTimeField(auto_now_add=True)或者 updated
    # = models.DateTimeField(auto_now=True)，在 DateTimeField 中就重写了 pre_save()方法，对时间
    # 进行预处理（完整代码请参阅 https://docs.djangoproject.com/en/2.1/_modules/django/db/models/
    # fields/#DateTimeField），使得我们不需要单独显式地把保存的当前时间写出来，而是在调用实例
    # 的 save()方法之后，自动完成时间的写入保存。
    #通过重写 pre_save()方法，最终将实例的序号记录下来。从前面的 Field.pre_save()
    #方法可以得知，参数 model_instance 和 add 是与祖先类保持一致的，这样的写法友好性更强
    #model_instance 引用的是实例，add 为该实例是否第一次被保存
    def pre_save(self, model_instance, add):  # ④
        # getattr()是 Python 的内建函数，它能够返回一个对象属性的值
        #getattr(model_instance,self.attname)中的 self.attname 也是在 Fields 类里面规定的一个参数
        #在 Fields 类中有如下两个方法get_attname_column(self):,set_attributes_from_name(self, name):
        #使用 self.attname 参数，判断当前对象（实例）中是否有某个属性（字段），
        #如果有，就执行 else 分支，调用父类的 pre_save()方法，但不会在数据库中增加记录；
        #否则就执行 try … except …语句，在 try 中主要计算新增一条数据后的序号
        if getattr(model_instance, self.attname) is None: #⑤
            try:
                #当前实例的所有记录。
                qs = self.model.objects.all()  # ⑥
                if self.for_fields:
                    #得到字段列表中的属性名称（字段名称）在本实例中是否存在字典
                    query = {field: getattr(model_instance, field) for field in self.for_fields}  # ⑦
                    #根据语句getattr(model_instance,self.attname)中的数据对query的结果进行筛选
                    qs = qs.filter(**query)  # ⑧
                #根据 self.attname 得到经过筛选之后的记录中的最后一条
                last_item = qs.latest(self.attname)  # ⑨
                #对当前实例进行序号的编排
                value = last_item.order + 1  # ⑩
            except ObjectDoesNotExist:
                value=0
            #经过上面的工作，最后在相应的字段上记录本实例的序号，返回该序号值并通过
            #pre_save()自动保存
            setattr(model_instance,self.attname,value)
            return value
        else:

            return super(OrderField,self).pre_save(model_instance,add)
