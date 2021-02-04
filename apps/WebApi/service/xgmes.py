import xml.sax.handler
import requests
import json


class XMLHandler(xml.sax.handler.ContentHandler):
    def __init__(self):
        super().__init__()
        self.buffer = ""
        self.mapping = {}

    def startElement(self, name, attrs):
        self.buffer = ""
        # print('starElement: ', name)
        # if name == 'movie'or name == 'collection':
            # print('starElement: ', attrs.items())

    def characters(self, data):
        if data != '\n':
            self.buffer += data
            # print('characters: ', data)

    def endElement(self, name):
        self.mapping[name] = self.buffer
        # print('endElement: ', name)

    def getDict(self):
        return self.mapping


class XGMes:

    @classmethod
    def GetMaterialState(cls, ip, SN, Site):
        try:
            params = {"barcode": SN, "site": Site}
            response = requests.get(ip + "GetMaterialState", params=params,)
            print(response.text)

            xh = XMLHandler()
            xml.sax.parseString(response.text, xh)
            resdict = xh.getDict()
            resdict = cls.str2dict(resdict['string'])

            if resdict['code'] == 0 and resdict['msg'] == 'success':
                if resdict['data']['state'] == '合格':
                    Materialinfo = {}
                    Materialinfo['SN'] = resdict['data']['barcode']
                    Materialinfo['materialName'] = resdict['data']['materialName']
                    Materialinfo['state'] = resdict['data']['state']
                    return Materialinfo
        except Exception as e:
            raise e

    @classmethod
    def GetCarState(cls, ip, VIN):
        try:
            params = {"barcode": VIN}
            response = requests.get(ip + "GetCarState", params=params)
            # print(response.text)

            xh = XMLHandler()
            xml.sax.parseString(response.text, xh)
            resdict = xh.getDict()
            resdict = cls.str2dict(resdict.get('string'))

            if resdict:
                if resdict.get('data'):
                    Carinfo = {}
                    Carinfo['VIN'] = resdict['data']['barcode']
                    Carinfo['carName'] = resdict['data']['productName']
                    Carinfo['carModel'] = resdict['data']['carModel']
                    Carinfo['state'] = resdict['data']['state']
                    return Carinfo
                else:
                    return {}
            else:
                return {}

            # if resdict['code'] == 0 and resdict['msg'] == 'success':
            #     if resdict['data']['state'] == '合格':
            #         Carinfo = {}
            #         Carinfo['VIN'] = resdict['data']['barcode']
            #         Carinfo['carModel'] = resdict['data']['carModel']
            #         Carinfo['state'] = resdict['data']['state']
            #         # print(Carinfo)
            #         return Carinfo
        except Exception as e:
            raise e

    @classmethod
    def TestResultUpdate(cls, ip, VIN, site, result, results):
        try:
            # data = json.dumps(results, ensure_ascii=False)
            data = json.dumps(results, ensure_ascii=False)
            params = {"barcode": VIN, "site": site, "type": "2", "result": result, "data": data.encode('utf-8')}
            response = requests.post(ip + "TestResultUpdate", data=params)
            print(response.text)

            xh = XMLHandler()
            xml.sax.parseString(response.text, xh)
            resdict = xh.getDict()
            resdict = cls.str2dict(resdict['string'])

            if resdict['code'] == 0 and resdict['msg'] == 'success':
                return True
            else:
                return False
        except Exception as e:
            raise e

    @classmethod
    def getPrductData(cls, ip, VIN):
        params = {"barcode": VIN, "site": "", "type": "2"}
        response = requests.post(ip + "GetTestResultNew", data=params)

        xh = XMLHandler()
        xml.sax.parseString(response.text, xh)
        resdict = xh.getDict()
        resdict = cls.str2dict(resdict['string'])

        if resdict['code'] == 0 and resdict['msg'] == 'success':
            data = resdict['data'].replace("null", "None")
            datadict = eval(data)
            return datadict

    @staticmethod
    def str2dict(instr):
        if 'null' not in instr:
            convdict = eval(instr)
            convdict['data'] = eval(convdict['data'])
            return convdict
        else:
            convdict = json.loads(instr)
            return convdict


if __name__ == '__main__':
    # try:
    #     a = NetWork.GetCarState('http://192.168.10.2:8989/', 'IDPWXB201001920001')
    #     print(a)
    # except Exception as e:
    #     print(e)
    try:

        data = [{"detectionType": 1, "errorInfo": "成功", "testItems": "灯光测试", "testName": "前大灯"},
                {"detectionType": 1, "errorInfo": "成功", "testItems": "灯光测试", "testName": "刹车灯"}]

        # data2 = [{
        #             "perception_lidar_x_offset_top_center": 0,
        #             "perception_lidar_y_offset_top_center": 0,
        #             "perception_lidar_z_offset_top_center": 0,
        #             "perception_lidar_roll_top_center": 0,
        #             "perception_lidar_pitch_top_center": 0,
        #             "perception_lidar_yaw_top_center": 0,
        #             "perception_lidar_x_offset_bottom_front": 0,
        #             "perception_lidar_y_offset_bottom_front": 0,
        #             "perception_lidar_z_offset_bottom_front": 0,
        #             "perception_lidar_roll_bottom_front": 0,
        #             "perception_lidar_pitch_bottom_front": 0,
        #             "perception_lidar_yaw_bottom_front": 0,
        #             "perception_camera_x_offset": 0,
        #             "perception_camera_y_offset": 0,
        #             "perception_camera_z_offset": 0,
        #             "perception_camera_roll": 0,
        #             "perception_camera_pitch": 0,
        #             "perception_camera_yaw": 0}]
        data3 = [{'detectionType': 0, 'testItems': '网络故障检测', 'testName': '无', 'errorInfo': '无故障'}]

        data4 = [{'detectionType': 0, 'testItems': '网络故障检测', 'testName': '无', 'errorInfo': '无故障'},
                 {'detectionType': 0, 'testItems': 'CMCU', 'testName': '挡板推杆电机过流状态', 'errorInfo': '确认故障'},
                 {'detectionType': 1, 'errorInfo': '成功', 'testItems': '灯光测试', 'testName': '前大灯'},
                 {'detectionType': 1, 'errorInfo': '成功', 'testItems': '灯光测试', 'testName': '刹车灯'},
                 {'detectionType': 1, 'errorInfo': '成功', 'testItems': '灯光测试', 'testName': '左后转向灯'},
                 {'detectionType': 1, 'errorInfo': '成功', 'testItems': '灯光测试', 'testName': '左前转向灯'},
                 {'detectionType': 1, 'errorInfo': '成功', 'testItems': '灯光测试', 'testName': '右前转向灯'},
                 {'detectionType': 1, 'errorInfo': '成功', 'testItems': '灯光测试', 'testName': '右后转向灯'},
                 {'detectionType': 1, 'errorInfo': '成功', 'testItems': '灯光测试', 'testName': '左示廓灯'},
                 {'detectionType': 1, 'errorInfo': '成功', 'testItems': '灯光测试', 'testName': '右示廓灯'},
                 {'detectionType': 1, 'errorInfo': '成功', 'testItems': '灯光测试', 'testName': '左前双闪灯'},
                 {'detectionType': 1, 'errorInfo': '成功', 'testItems': '灯光测试', 'testName': '左后双闪灯'},
                 {'detectionType': 1, 'errorInfo': '成功', 'testItems': '灯光测试', 'testName': '右前双闪灯'},
                 {'detectionType': 1, 'errorInfo': '成功', 'testItems': '灯光测试', 'testName': '右后双闪灯'},
                 {'detectionType': 1, 'errorInfo': '成功', 'testItems': '蜂鸣器&语音模块', 'testName': '蜂鸣器'},
                 {'detectionType': 1, 'errorInfo': '故障', 'testItems': '蜂鸣器&语音模块', 'testName': '左语音模块'},
                 {'detectionType': 1, 'errorInfo': '故障', 'testItems': '蜂鸣器&语音模块', 'testName': '右语音模块'},
                 {'detectionType': 1, 'errorInfo': '成功', 'testItems': '高清摄像头测试', 'testName': '高清摄像头'},
                 {'detectionType': 1, 'errorInfo': '成功', 'testItems': '超声波测试', 'testName': '超声波探头0'},
                 {'detectionType': 1, 'errorInfo': '成功', 'testItems': '超声波测试', 'testName': '超声波探头1'},
                 {'detectionType': 1, 'errorInfo': '成功', 'testItems': '超声波测试', 'testName': '超声波探头2'},
                 {'detectionType': 1, 'errorInfo': '成功', 'testItems': '超声波测试', 'testName': '超声波探头3'},
                 {'detectionType': 1, 'errorInfo': '成功', 'testItems': '超声波测试', 'testName': '超声波探头4'},
                 {'detectionType': 1, 'errorInfo': '成功', 'testItems': '超声波测试', 'testName': '超声波探头5'},
                 {'detectionType': 1, 'errorInfo': '成功', 'testItems': '超声波测试', 'testName': '超声波探头6'},
                 {'detectionType': 1, 'errorInfo': '成功', 'testItems': '超声波测试', 'testName': '超声波探头7'},
                 {'detectionType': 1, 'errorInfo': '成功', 'testItems': '超声波测试', 'testName': '超声波探头8'},
                 {'detectionType': 1, 'errorInfo': '成功', 'testItems': '超声波测试', 'testName': '超声波探头9'},
                 {'detectionType': 1, 'errorInfo': '成功', 'testItems': '超声波测试', 'testName': '超声波探头10'},
                 {'detectionType': 1, 'errorInfo': '成功', 'testItems': '超声波测试', 'testName': '超声波探头11'},
                 {'detectionType': 1, 'errorInfo': '成功', 'testItems': '急停测试', 'testName': '急停'},
                 {'detectionType': 1, 'errorInfo': '成功', 'testItems': '碰撞测试', 'testName': '碰撞开关'},
                 {'detectionType': 1, 'errorInfo': 'Min: 0.20, Max: 0.37', 'testItems': '清扫电机测试', 'testName': 'sbrusher_push_down_current'},
                 {'detectionType': 1, 'errorInfo': 'Min: 0.54, Max: 0.78', 'testItems': '清扫电机测试', 'testName': 'l2_edgebrush_current'},
                 {'detectionType': 1, 'errorInfo': 'Min: 0.50, Max: 0.85', 'testItems': '清扫电机测试', 'testName': 'r2_edgebrush_current'},
                 {'detectionType': 1, 'errorInfo': 'Min: 0.00, Max: 0.18', 'testItems': '清扫电机测试', 'testName': 'mainpush_down_current'},
                 {'detectionType': 1, 'errorInfo': 'Min: 0.71, Max: 0.92', 'testItems': '清扫电机测试', 'testName': 'l2_edgebrush_down_current'},
                 {'detectionType': 1, 'errorInfo': 'Min: 0.65, Max: 1.00', 'testItems': '清扫电机测试', 'testName': 'r2_edgebrush_down_current'},
                 {'detectionType': 1, 'errorInfo': 'Min: 0.19, Max: 0.28', 'testItems': '清扫电机测试', 'testName': 'pump_current'},
                 {'detectionType': 1, 'errorInfo': 'Min: 1.08, Max: 2.32', 'testItems': '清扫电机测试', 'testName': 'dust_current'},
                 {'detectionType': 1, 'errorInfo': 'Min: 15.70, Max: 16.54', 'testItems': '清扫电机测试', 'testName': 'fan1_current'},
                 {'detectionType': 1, 'errorInfo': 'Min: 22.70, Max: 27.96', 'testItems': '清扫电机测试', 'testName': 'main_brush_current'},
                 {'detectionType': 1, 'errorInfo': 'Min: 22.27, Max: 26.65', 'testItems': '清扫电机测试', 'testName': 'main_brush_down_current'},
                 {'detectionType': 1, 'errorInfo': 'Min: 10.24, Max: 14.41', 'testItems': '清扫电机测试', 'testName': 'main_brush_current'},
                 {'detectionType': 1, 'errorInfo': 'Min: 22.91, Max: 27.87', 'testItems': '清扫电机测试', 'testName': 'main_brush_down_current'},
                 {'detectionType': 1, 'errorInfo': 'Min: 10.21, Max: 13.33', 'testItems': '清扫电机测试', 'testName': 'main_brush_current'},
                 {'detectionType': 1, 'errorInfo': 'Min: 22.60, Max: 26.93', 'testItems': '清扫电机测试', 'testName': 'main_brush_down_current'},
                 {'detectionType': 1, 'errorInfo': 'Min: 22.11, Max: 26.19', 'testItems': '清扫电机测试', 'testName': 'main_brush_down_current'},
                 {'detectionType': 1, 'errorInfo': 'Min: 21.89, Max: 26.65', 'testItems': '清扫电机测试', 'testName': 'main_brush_down_current'},
                 {'detectionType': 1, 'errorInfo': '成功', 'testItems': '清扫电机测试', 'testName': '边刷推杆电机'},
                 {'detectionType': 1, 'errorInfo': '成功', 'testItems': '清扫电机测试', 'testName': '左边刷电机'},
                 {'detectionType': 1, 'errorInfo': '成功', 'testItems': '清扫电机测试', 'testName': '右边刷电机'},
                 {'detectionType': 1, 'errorInfo': '成功', 'testItems': '清扫电机测试', 'testName': '主刷推杆电机'},
                 {'detectionType': 1, 'errorInfo': '成功', 'testItems': '清扫电机测试', 'testName': '水泵电机'},
                 {'detectionType': 1, 'errorInfo': '成功', 'testItems': '清扫电机测试', 'testName': '振尘电机'},
                 {'detectionType': 1, 'errorInfo': '成功', 'testItems': '清扫电机测试', 'testName': '引风电机'},
                 {'detectionType': 1, 'errorInfo': '成功', 'testItems': '清扫电机测试', 'testName': '主刷电机'},
                 {'detectionType': 1, 'errorInfo': '故障', 'testItems': '清扫电机测试', 'testName': '挡板电机'},
                 {'detectionType': 1, 'errorInfo': '故障', 'testItems': '广角摄像头测试', 'testName': '前广角摄像头'},
                 {'detectionType': 1, 'errorInfo': '故障', 'testItems': '广角摄像头测试', 'testName': '左广角摄像头'},
                 {'detectionType': 1, 'errorInfo': '故障', 'testItems': '广角摄像头测试', 'testName': '后广角摄像头'},
                 {'detectionType': 1, 'errorInfo': '故障', 'testItems': '广角摄像头测试', 'testName': '右广角摄像头'}]


        # print(type(data4))
        res = NetWork.TestResultUpdate('http://192.168.10.2:8989/', 'IDPWXBX1000002', 'P07', '0', data4)
        # data_json = json.dumps(data3, ensure_ascii=False)
        # url = "http://192.168.10.2:8989/TestResultUpdate?barcode=IDPWXBX1000002&site=P07&type=2&result=0&data=" + data_json
        # res = requests.get(url)

        # print(str(res.text, encoding='gb2312'))

    except Exception as e:
        print(e)

    # payload = {"key1": "value1", "key2": "value2"}
    # r = requests.post("http://httpbin.org/post", data=payload)
    # print(r.text)

    # NetWork.TestResultUpdate('IDPWXBX1000002', 'P07', '1', '''{"detectionType": 0, "testItems": "","testName": "","errorInfo": "故障"}''')
    # data = {'barcode': 'IDPWXBX1000002', 'site': 'P07', 'type': '2', 'result': '1', 'data': '''[{"detectionType": 0, "testItems": "","testName": "","errorInfo": "故障"}]'''}
    # data = {'barcode': 'IDPWXBX1000002', 'site': 'P07', 'type': 2, 'result': 1, 'data': [{"detectionType": 0, "testItems": "","testName": "","errorInfo": "故障"}]}
    # data1 = json.dumps(data)
    # print(data1, type(data1))
    # response = requests.post("http://192.168.10.2:8989/TestResultUpdate", data=data)
    #
    #
    # print(response.text)
    # data = {'name': 'tom', 'age': '22'}
    #
    # response = requests.post('http://httpbin.org/post', data=data)
    # print(response.text)

    # print(response.text)










