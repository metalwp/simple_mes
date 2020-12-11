from django.db import models


class MyManager(models.Manager):
    # 父类先声明,继承的是 models.Manager 类,需要重写 filter 方法
    #'''使用继承,重写原来类的方法,进行改进函数时,考虑类的继承'''
    # def get_queryset(self):
        # '''使 filter 自动具有保留 is_delete 为 0 的功能,is_delete 为 1 的自动过滤掉'''
        # 对父类的方法进行修改,将 is_delete 为 0 的留下
        # return super(MyManager, self).get_queryset().filter(is_delete=False)

    def filter_without_isdelete(self):
        return super().get_queryset().filter(is_delete=False)

    # def create(self,a_name = "Pandas"):
    #     # 默认创建一个熊猫
    #     '''改写创建对象语句,使用子类完成操作'''
    #     animal = self.model()
    #     # 创建一个模型
    #     animal.a_name = a_name
    #     return animal


class BaseModel(models.Model):
    """模型抽象基类,为所有继承此基类的类加入如下三个字段"""
    c_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    m_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='是否删除')

    objects = MyManager()

    class Meta:
        """说明是个抽象模型类"""
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """重写数据库删除方法实现逻辑删除"""
        self.is_delete = True
        self.save()

    def o_delete(self):
        super().delete()
