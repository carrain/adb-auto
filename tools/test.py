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
import random

#改变图片分辨率（因为手机图片发送到电脑截图与原分辨率不同）
def resize_image(input_image,out_image,width,height,type):
    img = Image.open(input_image)
    out_rule = img.resize((width,height),Image.ANTIALIAS)
    out_rule.save(out_image,type)


#从手机截屏，并发送到电脑
def get_now_picture():
    os.popen("adb -s bd5c889 shell screencap -p /sdcard/screen.png")
    os.popen("adb -s bd5c889 pull /sdcard/screen.png")
    #改变图片分辨率
    resize_image('screen.png','screen_out.png',516,919,'png')

#    bbox = (10, 60, 525, 990)
#    img = ImageGrab.grab(bbox)
#    img.save("D:/lu-tool/script/python/test/begain/screen_out.png")

#获取手机需要被点击的点(返回为需要点击的手机坐标的高宽数组)
def get_phone_point(pos):
    #手机分辨率与图片分辨率，如更改，需修改
    phone_heigh = 1280.0
    phone_width = 720.0
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
        os.popen("adb -s bd5c889 shell input tap {x} {y}".format(x=argument[1],y=argument[0]) )
    elif handle == 'insert':
#        num_arry=[7,8,9,10,11,9,13,14,15,16]
#        argu_leng = len(argument)
#        for num in range(argu_leng):
#            send_num = int(argument[num])            
#            os.popen('adb shell input keyevent {date}'.format(date=num_arry[send_num]))
        os.popen('adb -s bd5c889 shell input text {x}'.format(x=argument))
    elif handle == 'keyevent':
        os.popen("adb -s bd5c889 shell input keyevent {x}".format(x=argument) )
    elif handle == 'swap':
        os.popen('adb -s bd5c889 shell input swipe {x} {y} {x1} {y1} {z}'.format(x=argument[0],y=argument[1],x1=argument[2],y1=argument[3],z=argument[4]))
        

#随机机型选择
def phone_choice():
    brand = random.randint(0,16)
    brand_point = brand*90+200
    model = random.randint(0,13)
    model_point = model*90+270
    choice_point = [347,brand_point,347,model_point]
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
def get_phone_number(project_id):
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
def get_message(phone_number,project_id):
    url ='http://api.ixinsms.com/api/do.php?action=getMessage&sid={x}&phone={y}&token={z}'.format(x=project_id,y=phone_number,z=token)
    while 2<3:
        req = urllib2.Request(url)
        res_data = urllib2.urlopen(req)
        res = res_data.read()
        ree = re.compile('(\d+)')
        match = ree.findall(res)
        if match[0] == '1':
            break
        time.sleep(2)
        print "waiting message"
    print "get message success"
    message = match[1]
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


#登录判断标志
logged = 0
#获取的token，重复使用
token = "im first"
#项目id
project_id = 24239
#邀请码
invite_number = 2278898

if __name__ == "__main__":

    print "get number begain"
    if logged == 0:
        token = log_in()
        logged = 1
    phone_number = get_phone_number(project_id)

    phone_point = if_next('phone_number.png', 50)
    phone_handle("click",phone_point)
    print "insert number"
    phone_handle("insert",phone_number)

    print "send message"    
    get_now_picture() 
    phone_point = if_next('send.png', 50)
    phone_handle("click",phone_point)
    phone_point = if_next('if_swap.png', 50)
    time.sleep(1)
    
    pos = compare('screen_out.png','if_swap.png')   
    while pos != None :
        swap_road = [215,830,510,830,2000]
        phone_handle("swap",swap_road)
        get_now_picture()
        pos = compare('screen_out.png','if_swap.png')

    print "insert invite"
    phone_point = if_next('invite.png', 50)
    phone_handle("click",phone_point)
    phone_point = if_next('down.png', 50)
    phone_handle("click",phone_point)
    phone_handle("insert",invite_number)

    print "waite message"
    message = get_message(phone_number,project_id)
    phone_point = if_next('security.png', 50)
    phone_handle("click",phone_point)
    phone_point = if_next('down.png', 50)
    phone_handle("click",phone_point)
    phone_handle("insert",message)
    
    phone_point = if_next('login.png', 50)
    phone_handle("click",phone_point)
    time.sleep(1)
    
    
    
    
    
    print num
    print "                                            over"
    
    print "return"
    phone_handle('keyevent','82')
    phone_point = if_next('return.png', 50)
    phone_handle("click",phone_point)
