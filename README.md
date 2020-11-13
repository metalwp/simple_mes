创建虚拟环境
使用pip安装第三方依赖
运行migrate命令，创建数据库和数据表
运行python manage.py runserver启动服务器

问题记录：
1. 前端表单校验失效，主要原因是<Input>标签的type使用了Button，需要使用submit才行，但使用submit没办法跳转到js函数，可能需要使用js自行对表单进行校验
2. order_manager的num为主键，不能有重复的情况，生成编号时会出现重复的情况----暂时解决
3. 前端bootstrap-table列排序，有些不属于这个模型的不能实现
4. admin管理页面 仍然显示is_delete为True的数据库记录，有可能是admin的管理器objects没有使用自定义的管理器
5. 排序无法按当前模型的外键模型进行排序，如BOM和MaterialModel
6. 产品的VIN规则修改页面
7. 模板中的编辑和删除物料类有些还有问题 ---暂时已解决
8. 用户信息修改，密码修改待实现