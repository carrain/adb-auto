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
    os.popen("adb shell screencap -p /sdcard/screen.png")
    os.popen("adb pull /sdcard/screen.png")
    #改变图片分辨率
    resize_image('screen.png','screen_out.png',430,760,'png')

#    bbox = (10, 60, 525, 990)
#    img = ImageGrab.grab(bbox)
#    img.save("D:/lu-tool/script/python/test/begain/screen_out.png")

#获取手机需要被点击的点(返回为需要点击的手机坐标的高宽数组)
def get_phone_point(pos):
    #手机分辨率与图片分辨率，如更改，需修改
    phone_heigh = 1920.0
    phone_width = 1080.0
    picture_height = 760
    picture_width = 430
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
        os.popen("adb shell input tap {x} {y}".format(x=argument[1],y=argument[0]) )
    elif handle == 'insert':
        num_arry=[7,8,9,10,11,12,13,14,15,16]
        argu_leng = len(argument)
        for num in range(argu_leng):
            send_num = int(argument[num])            
            os.popen('adb shell input keyevent {date}'.format(date=num_arry[send_num]))
    elif handle == 'keyevent':
        os.popen("adb shell input keyevent {x}".format(x=argument) )
        
    
#对匹配的图片进行画圆，方便调试，看是否找对
def draw_circle(img, pos, circle_radius, color, line_width):
    cv2.circle(img, pos, circle_radius, color, line_width)
    cv2.imshow('objDetect', imsrc) 
    cv2.waitKey(1)
    cv2.destroyAllWindows()


#打开图片并关闭，目的是为了关闭图像流，这个坑爹的作者仿佛没有写关闭图像的接口，
#导致读取第一张图后后面的也全部与第一张图片匹配
def close_picture(pictur_name):
    imsrc = ac.imread(pictur_name)
    cv2.imshow('objDetect', imsrc) 
    cv2.waitKey(1)
    cv2.destroyAllWindows()

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
            return 'false'
        no_match = "try next {x}".format(x=num)
        print no_match
        num += 1

        get_now_picture()
        pos = compare('screen_out.png',goal)
    return get_phone_point(pos)



if __name__ == "__main__":
  
    for  height in range(0,5) :
        for withd in range(0,4):            
            point_height = 220+(height*294.5)
            point_width = 168+(withd*252)
            phone_point = [point_height,point_width]
            phone_handle("click",phone_point)
            print phone_point

            phone_point = if_next('no.png',20)
            if phone_point == 'false':
                phone_handle("keyevent",7)
                print "return no match111"
            else:
                phone_handle("click",phone_point)

            if if_next('return_main.png',3) != "false":
                phone_handle("keyevent",7)
                print 'home'
            else:
                phone_handle("keyevent",3)
                print 'not home'
            time.sleep(2)
            print 'over'
    print 'complet'

  