#coding=utf-8
import cv2
import aircv as ac
import os
from PIL import Image
from PIL import ImageGrab
import time
import datetime
import re
import urllib
import urllib2
import sys

#改变图片分辨率（因为手机图片发送到电脑截图与原分辨率不同）
def resize_image(input_image,out_image,width,height,type):
    img = Image.open(input_image)
    out_rule = img.resize((width,height),Image.ANTIALIAS)
    out_rule.save(out_image,type)


#从手机截屏，并发送到电脑
#新方案，电脑安装投影软件，更快
def get_now_picture():
    os.popen("adb -s 86e2ca1a shell screencap -p /sdcard/screen.png")
    os.popen("adb -s 86e2ca1a pull /sdcard/screen.png")
    #改变图片分辨率
    resize_image('screen.png','screen_out.png',516,919,'png')

#    bbox = (10, 60, 525, 990)
#    img = ImageGrab.grab(bbox)
#    img.save("D:/lu-tool/script/python/test/begain/screen_out.png")

#获取手机需要被点击的点(返回为需要点击的手机坐标的高宽数组)
def get_phone_point(pos):
    #手机分辨率与图片分辨率，如更改，需修改
    phone_heigh = 1920.0
    phone_width = 1080.0
    picture_height = 919
    picture_width = 516
    resolution_list = []
    
    #获取匹配出的中心点
    point = pos['result']
    get_height = point[1]
    get_width = point[0]
    #将图片点坐标转换为手机对应坐标
    phone_point_height = phone_heigh/picture_height*get_height
    phone_point_width = phone_width/picture_width*get_width
    resolution_list.append(phone_point_height)
    resolution_list.append(phone_point_width)
    return resolution_list


#打开两个图片进行匹配（返回为匹配出点的信息）
def compare(source_picture,goal):
    imsrc = ac.imread(source_picture)
    imobj = ac.imread(goal)    
#    imsrc = cv2.imread(source_picture)
#    imobj = cv2.imread(goal)
    pos = ac.find_template(imsrc, imobj)
    return pos


#对手机进行操作
def phone_handle(handle,argument):
    if handle == "click":
        os.popen("adb -s 86e2ca1a shell input tap {x} {y}".format(x=argument[1],y=argument[0]) )
    elif handle == 'insert':
#        num_arry=[7,8,9,10,11,9,13,14,15,16]
#        argu_leng = len(argument)
#        for num in range(argu_leng):
#            send_num = int(argument[num])            
#            os.popen('adb shell input keyevent {date}'.format(date=num_arry[send_num]))
        os.popen('adb -s 86e2ca1a shell input text {x}'.format(x=argument))
    elif handle == 'keyevent':
        os.popen("adb -s 86e2ca1a shell input keyevent {x}".format(x=argument) )
    elif handle == 'swap':
        os.popen('adb -s 86e2ca1a shell input swipe {x} {y} {x1} {y1} {z}'.format(x=argument[0],y=argument[1],x1=argument[2],y1=argument[3],z=argument[4]))
        
    
#对匹配的图片进行画圆，方便调试，看是否找对
def draw_circle(img, pos, circle_radius, color, line_width):
    cv2.circle(img, pos, circle_radius, color, line_width)
    cv2.imshow('objDetect', imsrc) 
    cv2.waitKey(1)
    cv2.destroyAllWindows()


#打开图片并关闭，目的是为了关闭图像流，这个坑爹的作者仿佛没有写关闭图像的接口，
#导致读取第一张图后后面的也全部与第一张图片匹配
def close_picture(pictur_name):
#    imsrc = ac.imread(pictur_name)
#    cv2.imshow('objDetect', imsrc) 
#    cv2.waitKey(1)
#    cv2.destroyAllWindows()
    xxxxxl = 1

#随机机型选择
def phone_choice():
    brand = random.randint(0,16)
    brand_point = brand*90+380
    model = random.randint(0,13)
    model_point = model*90+410
    choice_point = [534,brand_point,534,model_point]
    return choice_point


#登录模块，如果返回的第一位不是1，则一直循环登录，直到返回结果正常
def log_in():
    url = "http://api.ixinsms.com/api/do.php?action=loginIn&name=carrain&password=d1035688497"
    while 2<3:
        req = urllib2.Request(url)
        res_data = urllib2.urlopen(req)
        res = res_data.read()
        ree = re.compile('(\d)\|(\w+)')
        match = ree.findall(res)
        if match[0][0] == '1':
            break
    print "log_in success"
    token = match[0][1]
    return token

#获取手机号码
def get_phone_number(token,project_id):
    url ='http://api.ixinsms.com/api/do.php?action=getPhone&sid={x}&token={y}'.format(x=project_id,y=token)
    while 2<3:
        req = urllib2.Request(url)
        res_data = urllib2.urlopen(req)
        res = res_data.read()
        ree = re.compile('(\d)\|(\w+)')
        match = ree.findall(res)
        if match[0][0] == '1':
            break
    print "get number success"
    phon_number = match[0][1]
    return phon_number

#获取短信
def get_message(token,project_id):
    url ='http://api.ixinsms.com/api/do.php?action=getMessage&sid={x}id&phone={y}'.format(x=project_id,y=token)
    while 2<3:
        req = urllib2.Request(url)
        res_data = urllib2.urlopen(req)
        res = res_data.read()
        ree = re.compile('(\d)\|(\w+)')
        match = ree.findall(res)
        if match[0][0] == '1':
            break
        time.sleep(2)
        print "waiting message"
    print "get message success"
    message = match[0][1]
    return message



#检查下一步的图片是否出现
def if_next(goal,wait_time):
    get_now_picture()
    pos = compare('screen_out.png',goal)
    num = 0
    while not pos:
        if num == wait_time :
            print 'no next picture'
            print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
            print id
            os.exit()
            return 'false'
        no_match = "try next {x}".format(x=num)
        print no_match
        num += 1

        get_now_picture()
        pos = compare('screen_out.png',goal)
    return get_phone_point(pos)



#分身编号
id = 350

if __name__ == "__main__":
#定义所有全局变量，初始化标志位
    #需要添加的钱包地址
    address = '0x0E69D0A2bbB30aBcB7e5CfEA0E4FDe19C00A8d47'
    address_len = len(address)
    #钱包密码
    password = 'd1035688497'
    #左滑一次的坐标点
    up_down = [821,914,250,914,100]

    #是否第一次进入
    first = 1
    #组标志位
    flag_group = 0
    #滑动位置
    flag_swipe = 0
    #分身内钱包编号
    flag_name = 0

    print '1'


    while id <1000:
#进入到指定组的指定页面
        #oppo每次会自动返回主界面
        if first == 1:
            #点击指定组
            print 'first click group'
            group = id/72
            withd = group%4
            height = group/4
            point_height = 200+(height*290)
            point_width = 150+(withd*260)
            phone_point = [point_height,point_width]
            phone_handle("click",phone_point)
            #更新组标志位
            flag_group = group
            time.sleep(1)
            
            #滑动到指定界面
            print 'first swipe '
            swipe = id%72/9
            num = 0 
            while num <swipe:
                phone_handle('swap',up_down)
                num += 1
            #更新滑动标志位
            flag_swipe = swipe
            time.sleep(1)
        

#进入指定分身
        print '1                                                    creat clone {x}'.format(x=id)
        print 'enter id fenshen'
        location = id%72%9
        height = location/3
        withd  = location%3
        point_height = 550+(height*283)
        point_width = 250+(withd*300)
        phone_point = [point_height,point_width]
        phone_handle("click",phone_point)

#开始初始化钱包
        print 'begain no'
        get_now_picture()
        phone_point = if_next('no.png',50)
        phone_handle("click",phone_point)
        close_picture('screen_out.png')
        close_picture('no.png')
        time.sleep(1)

        print 'begain read'
        get_now_picture()
        phone_point = if_next('read.png',50)
        phone_handle("click",phone_point)
        close_picture('screen_out.png')
        close_picture('read.png')
        time.sleep(2)

        print 'begain continue'
        get_now_picture()
        phone_point = if_next('continue.png',50)
        phone_handle("click",phone_point)
        close_picture('screen_out.png')
        close_picture('continue.png')
        time.sleep(1)

        phone_handle('keyevent',3)
        id += 1
#226

#250 550
#850 550
#250 1400   

#300 283

#150 200
#930 200
#150 780 



#520 920

#181
