from selenium import webdriver
import time
import os.path
import multiprocessing as mp
from selenium.webdriver.chrome.options import Options
 
 
def readtxt():
    '''读取txt文件，返回一个列表，每个元素都是一个元组;文件的格式是图片保存的名称加英文逗号加网页地址'''
    with open('urls.txt', 'r') as f:
        lines = f.readlines()
    urls = []
    for line in lines:
        try:
            #thelist = line.strip().split(",")
            thelist = line.split(",")
            if len(thelist) == 2 and thelist[0] and thelist[1]:
                urls.append((thelist[0], thelist[1]))
        except:
            pass
    return urls


 
def get_dir(dirName):
    '''判断文件夹是否存在，如果不存在就创建一个'''
    if not os.path.isdir(dirName):
        os.makedirs(dirName)
    return dirName

def S_shoot(driver,js_height,dirName,PageNum,Section):
    try:
        k = 1
        height = driver.execute_script(js_height)
        while True:
            if k * 500 < height:
                js_move = f"window.scrollTo(0,{k * 500})"
                print(js_move)
                driver.execute_script(js_move)
                #time.sleep(0.2)
                height = driver.execute_script(js_height)
                k += 1
            else:
                break
        scroll_width = driver.execute_script('return document.body.parentNode.scrollWidth')
        scroll_height = driver.execute_script('return document.body.parentNode.scrollHeight')
        driver.set_window_size(scroll_width, scroll_height)
        driver.get_screenshot_as_file(
            rf"ALBioData\{dirName}\{Section}\{PageNum}.png")
        #print("Process {} get one pic !!!".format(os.getpid()))
        time.sleep(0.1)
    except Exception as e:
        print(dirName, e)

def Shoot_Pages(driver,js_height,dirName,Section):
    
    PageNum = 1
    Flag = False
    while True:
        S_shoot(driver,js_height,dirName,PageNum,Section)
        #点击下一页
        try:
            PageNum+=1
            print(f'{Section}Page{PageNum}')
            driver.find_element_by_xpath(f"//ul[@class='paging']/li[text()='{PageNum}']").click()
            time.sleep(1)
        except Exception:
            Flag = True
        if Flag:
            break
def Shoot_Unit():
    pass
def webshot(tup):
    # driver = webdriver.PhantomJS()
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')#无头运行
    options.add_argument('--disable-gpu')
    
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    # 返回网页的高度的js代码
    js_height = "return document.body.clientHeight"
    #picname = str(tup[0][0])

    link = tup[0][1]
    print(link)
    driver.get(link)
    time.sleep(3)
    driver.find_element_by_xpath(f"//ins[@id='nb_invite_tool']").click()
    UnitNum = 1
    while True:
        try:
            
            UnitName = driver.find_element_by_xpath(f"//div[@id='left_unit']/ul/li[{UnitNum}]/span").get_attribute('innerHTML')
            driver.find_element_by_xpath(f"//div[@id='left_unit']/ul[1]/li[{UnitNum}]").click()
            time.sleep(1)
            get_dir(rf'ALBioData\{UnitName}\MCQ')
            Shoot_Pages(driver,js_height,dirName=UnitName,Section='MCQ')
            driver.find_element_by_xpath(f"//li[text()=' Structured Question ']").click()
            time.sleep(1)
            get_dir(rf'ALBioData\{UnitName}\SQ')
            Shoot_Pages(driver,js_height,dirName=UnitName,Section='SQ')
            UnitNum+=1
        except Exception as e:
            print(e)
            break
 
if __name__ == '__main__':
    t = time.time()
    #get_dir()
    urls = readtxt()
    #pool = mp.Pool()
    #pool.map_async(func=webshot, iterable=urls)
    #pool.close()
    #pool.join()
    webshot(urls)
    print("操作结束，耗时：{:.2f}秒".format(float(time.time() - t)))
    input()
    
