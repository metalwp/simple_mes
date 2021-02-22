创建虚拟环境
使用pip安装第三方依赖
运行migrate命令，创建数据库和数据表
运行python manage.py runserver启动服务器

问题记录：
1. 前端表单校验失效，主要原因是<Input>标签的type使用了Button，需要使用submit才行，但使用submit没办法跳转到js函数，可能需要使用js自行对表单进行校验
2. （OK）order_manager的num为主键，不能有重复的情况，生成编号时会出现重复的情况----暂时解决
3. 前端bootstrap-table列排序，有些不属于这个模型的不能实现
4. admin管理页面 仍然显示is_delete为True的数据库记录，有可能是admin的管理器objects没有使用自定义的管理器
5. 排序无法按当前模型的外键模型进行排序，如BOM和MaterialModel
6. （OK）产品的VIN规则修改页面 --已完成
7. （OK）模板中的编辑和删除物料类有些还有问题 ---暂时已解决
8. （OK）用户信息修改，密码修改待实现 ---已完成
17.（OK）新增BOM的时候应该检查order是否都完成了  --完成

9. 查询系统 --一.测试数据查询：1.按VIN查询 二.装配记录查询：1.按订单查询 2.按生产日期查询 3.按VIN查询 4.
10.（OK）设备接口WebApi--1. 前期EPS和驱动电机设备依然使用XG_MES获取和保存数据，传感器标定设备使用特殊接口，接口从XGMES获取数据，保存结果到新MES
                       2. 最终EPS和驱动电机设备重新开发后，全部使用新MES接口
11. 仪表盘
12. （OK）返工返修
13. （OK）产品型号中不含总称ERP号，总成ERP号改为BOM中的属性--已修改
14. （OK）产品型号配置中，名称和型号改为不能重复
15. （OK）标签打印未实现，模板/数据
16. （OK）account中的init_permission在其他模块中调用时有问题--不能放在django返回render前面，只能放在返回JsonResponse前面
17.  (OK)导出功能未实现--菜单和权限导入导出功能已实现
18. （OK）服务端的LOG功能
19. bootstrap-table-resizable 表格可以拖拽宽度



uwsgi --http :8001 --chdir /home/metalwp/Work/test2/simple_mes/ --home=/home/metalwp/Work/test2/simple_mes/venv/ --module simple_mes.wsgi
