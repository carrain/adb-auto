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

def delete_clone(start,stop,page):
    start_x = start%10
    start_y = start/10
    stop_x = stop%10
    stop_y = stop/10
    print start_x
    print start_y
    print stop_x
    print stop_y

    base_x = 100
    base_y = 125
    add_x  = 145
    add_y  = 167

    #判断是不是第一次删除的标志位，翻页进入新页面时使用
    begin = 1
    #判断是不是只有一页的标志位，删除最后一页时使用
    just_one_page = 1

    while page != 0 :
        #删除最后一页
        if page == 1 :
            if just_one_page == 1:
                count_x = start_x
                count_y = start_y
            else :
                count_x = 4
                count_y = 5
            while count_y != 0 :
                while count_x != 0 :
                    now_delete_x = base_x + add_x*(count_x-1)
                    now_delete_y = base_y + add_y*(count_y-1)
                    point = [now_delete_y,now_delete_x]
                    print point
                    print count_x
                    print count_y
                    phone_handle("click",point)

                    phone_point = if_next('delete.png', 50)
                    phone_handle("click",phone_point)

                    get_now_picture()
                    pos = compare('screen_out.png','delete.png')
                    while pos :
                        get_now_picture()
                        pos = compare('screen_out.png','delete.png')
                    
                    print 'stop'
                    print stop_x
                    print stop_y
                    print count_x
                    print count_y
                    if count_x == stop_x and count_y == stop_y :
                        print "delete over"
                        quit()

                    count_x = count_x-1

                count_x = 4                
                count_y = count_y-1
        #没到最后一页，删除整页
        else : 
            #如果不止一页，关闭标志位
            just_one_page = 0
            if begin == 1 :
                count_x = start_x
                count_y = start_y
                begin = 0
            else :
                count_x = 4
                count_y = 5
            while count_y != 0 :
                while count_x != 0 :
                    now_delete_x = base_x + add_x*(count_x-1)
                    now_delete_y = base_y + add_y*(count_y-1)
                    point = [now_delete_y,now_delete_x]
                    print point
                    print count_x
                    print count_y
                    phone_handle("click",point)

                    phone_point = if_next('delete.png', 50)
                    phone_handle("click",phone_point)

                    get_now_picture()
                    pos = compare('screen_out.png','delete.png')
                    while pos :
                        get_now_picture()
                        pos = compare('screen_out.png','delete.png')
                    count_x = count_x-1

                    if count_x == stop_x and count_y == stop_y :
                        print "delete over"
                        quit()

                count_x = 4                
                count_y = count_y-1

        swap_argument = [100,100,800,100,200]
        phone_handle("swap",swap_argument)
        page = page-1
    
    print "delete over"
#分身编号
start = 42
stop = 21
page = 4

if __name__ == "__main__":
    delete_clone(13,13,1)