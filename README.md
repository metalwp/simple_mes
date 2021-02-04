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
6. 产品的VIN规则修改页面 --已完成
7. 模板中的编辑和删除物料类有些还有问题 ---暂时已解决
8. 用户信息修改，密码修改待实现 ---已完成
17. 新增BOM的时候应该检查order是否都完成了  --完成

9. 查询系统 --一.测试数据查询：1.按VIN查询 二.装配记录查询：1.按订单查询 2.按生产日期查询 3.按VIN查询 4.
10. 设备接口WebApi--1. 前期EPS和驱动电机设备依然使用XG_MES获取和保存数据，传感器标定设备使用特殊接口，接口从XGMES获取数据，保存结果到新MES
                   2. 最终EPS和驱动电机设备重新开发后，全部使用新MES接口
11. 仪表盘
12. 返工返修
13. 产品型号中不含总称ERP号，总成ERP号改为BOM中的属性--已修改
14. 产品型号配置中，名称和型号是否要改为不能重复，待确认
15. 标签打印未实现，模板/数据
16. account中的init_permission在其他模块中调用时有问题
17. 导出功能未实现
18. 服务端的LOG功能



"[{\"barcode\":\"IDPWXB202020B10013\",
\"steercontrol_eps_delay_time\":101.0,
\"steercontrol_eps_speed\":651.0,
\"drivercontrol_lag_time_speed_up\":223.0,
\"drivercontrol_lag_time_speed_down\":262.0,
\"drivercontrol_start_torque\":125.0,
\"drivercontrol_point_1_velocity\":0.93,
\"drivercontrol_point_1_torque\":700.0,
\"drivercontrol_point_2_velocity\":1.25,
\"drivercontrol_point_2_torque\":899.0,
\"ordernum\":\"2021010013\",
\"product\":null,
\"bcm_sn\":null,
\"avcu_sn\":null,
\"dmcu_sn\":null,
\"bind\":[{\"bindName\":\"Z140100058\",\"bindResult\":\"Z1401000581021114000002\"},
{\"bindName\":\"L510300052\",\"bindResult\":\"L5103000521021114000004\"},
{\"bindName\":\"L510300052\",\"bindResult\":\"L5103000521021114000003\"},
{\"bindName\":\"Z130100007\",\"bindResult\":\"Z1301000071021114000002\"},
{\"bindName\":\"Z130100006\",\"bindResult\":\"Z1301000061021114000002\"},
{\"bindName\":\"Z120100003\",\"bindResult\":\"Z1201000031021114000018\"},
{\"bindName\":\"L170200003\",\"bindResult\":\"L1702000031020B12010007\"},
{\"bindName\":\"Z120300035\",\"bindResult\":\"Z1203000351020A21010004\"},
{\"bindName\":\"Z120900001\",\"bindResult\":\"Z1209000011020B24000008\"},
{\"bindName\":\"Z120300005\",\"bindResult\":\"Z1203000051021119000004\"},
{\"bindName\":\"L172000009\",\"bindResult\":\"L1720000091020C07000005\"},
{\"bindName\":\"Z120300005\",\"bindResult\":\"Z1203000051021119000001\"},
{\"bindName\":\"Z110300002\",\"bindResult\":\"Z1103000021320C31AA0024\"},
{\"bindName\":\"Z110700003\",\"bindResult\":\"Z1107000031420C28AA0012\"},
{\"bindName\":\"Z110200005\",\"bindResult\":\"Z1102000051320330AA0010\"},
{\"bindName\":\"Z110100005\",\"bindResult\":\"Z1101000051020729AA9002\"},
{\"bindName\":\"Z120900001\",\"bindResult\":\"Z1209000011020B24000004\"},
{\"bindName\":\"Z120900001\",\"bindResult\":\"Z1209000011020B24000040\"},
{\"bindName\":\"Z170100004\",\"bindResult\":\"Z1701000041020A22010022\"},
{\"bindName\":\"Z110700005\",\"bindResult\":\"Z1107000051220417AA0016\"},
{\"bindName\":\"Z120100002\",\"bindResult\":\"Z1201000021021114000010\"},
{\"bindName\":\"Z120200026\",\"bindResult\":\"Z1202000261020923000381\"},
{\"bindName\":\"Z120200026\",\"bindResult\":\"Z1202000261020923000362\"},
{\"bindName\":\"L160100009\",\"bindResult\":\"L1601000091021109000009\"},
{\"bindName\":\"Z120200026\",\"bindResult\":\"Z1202000261020923000368\"},
{\"bindName\":\"Z120200026\",\"bindResult\":\"Z1202000261020923000363\"},
{\"bindName\":\"Z120400030V1000A\",\"bindResult\":\"Z1204000301021105070011\"},
{\"bindName\":\"Z120400029V1000A\",\"bindResult\":\"Z1204000291021106070019\"},
{\"bindName\":\"Z120400029V1000A\",\"bindResult\":\"Z1204000291021106070102\"},
{\"bindName\":\"L183000055\",\"bindResult\":\"L1830000551020B30000025\"},
{\"bindName\":\"L183000039\",\"bindResult\":\"L1830000391020B09000015\"},
{\"bindName\":\"L183000055\",\"bindResult\":\"L1830000551020B30000028\"},
{\"bindName\":\"Z120200027\",\"bindResult\":\"Z1202000271020C24050011\"},
{\"bindName\":\"Z120200027\",\"bindResult\":\"Z1202000271020C24050034\"},
{\"bindName\":\"Z120200027\",\"bindResult\":\"Z1202000271020C24050036\"},
{\"bindName\":\"Z120200027\",\"bindResult\":\"Z1202000271020C24050031\"},
{\"bindName\":\"Z120400029V1000A\",\"bindResult\":\"Z1204000291021105070058\"},
{\"bindName\":\"Z120200026\",\"bindResult\":\"Z1202000261020923000369\"},
{\"bindName\":\"Z120200026\",\"bindResult\":\"Z1202000261020923000373\"},
{\"bindName\":\"Z120200026\",\"bindResult\":\"Z1202000261020923000371\"},
{\"bindName\":\"Z120200026\",\"bindResult\":\"Z1202000261020923000370\"}]
}]"
