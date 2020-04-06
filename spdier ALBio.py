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
def readaccount():
    '''从txt文件中读取用户登录信息，文件格式为：用户名,密码'''
    with open('account.txt', 'r') as f:
        lines = f.readlines()
    account = lines[0].split(',')
    return account
def get_dir(dirName):
    #判断文件夹是否存在，如果不存在就创建一个
    if not os.path.isdir(dirName):
        os.makedirs(dirName)
    return dirName
def  get_cookie():
    pass
def scroll_down(driver):
    # 返回网页的高度的js代码
    js_height = "return document.body.clientHeight"
    k = 0
    height = driver.execute_script(js_height)
    while True:
        if k * 500 < height:
            js_move = f"window.scrollTo(0,{k * 500})"
            print(f'Shooting {js_move}')
            driver.execute_script(js_move)
            #time.sleep(0.2)
            height = driver.execute_script(js_height)
            k += 1
        else:
            break
def Search_and_click(driver,xpath):
    '''
    依据xpath找到并点击按钮
    点击成功返回True
    未找到按钮返回False
    '''
    Flag = True
    js_height = "return document.body.clientHeight"
    k = 0
    height = driver.execute_script(js_height)
    while True:
        if k * 500 < height:
            try:
                driver.find_element_by_xpath(xpath).click()
                break
            except Exception:
                pass
            js_move = f"window.scrollTo(0,{k * 500})"
            print(f'Searching btn {js_move}')
            driver.execute_script(js_move)
            #time.sleep(0.2)
            height = driver.execute_script(js_height)
            k += 1
        else:
            Flag = False
            break
    return Flag
def S_shoot(driver,dirName,PageNum,QuestionNum,Section):
    try:
        scroll_down(driver)
        scroll_width = driver.execute_script('return document.body.parentNode.scrollWidth')
        scroll_height = driver.execute_script('return document.body.parentNode.scrollHeight')
        LowerB = driver.find_element_by_xpath(f"//div[@class='next-prev-question']").location['y']
        driver.set_window_size(scroll_width, LowerB)
        js_move = f"window.scrollTo(0,0)"
        driver.execute_script(js_move)
        driver.get_screenshot_as_file(
            rf"ALBioData\{dirName}\{Section}\P{PageNum} Q{QuestionNum}.png")
        print(rf'get one pic, saved as ALBioData\{dirName}\{Section}\P{PageNum} Q{QuestionNum}.png')
        #print("Process {} get one pic !!!".format(os.getpid()))
        driver.set_window_size(scroll_width, scroll_height)
        time.sleep(0.1)
    except Exception as e:
        print(dirName, e)

def Shoot_Pages(driver,dirName,Section):
    '''遍历当前页面下的每一道题'''
    PageNum = 1
    while True:
        print(f'{Section}Page{PageNum}')
        Shoot_Questions(driver,dirName,PageNum,Section)
        time.sleep(0.1)
        #点击下一页
        try:
            PageNum+=1
            driver.find_element_by_xpath(f"//ul[@class='paging']/li[text()='{PageNum}']").click()
            time.sleep(0.1)
        except Exception:
            break
def Shoot_Questions(driver,dirName,PageNum,Section):
    QuestionNum = 1
    while True:
        try:
            print(f'try {Section} P{PageNum} Q{QuestionNum}')
            driver.find_element_by_xpath(f"//div[@class='result-list']/div[@class='question-item'][{QuestionNum}]/div[2]/div[2]").click()
            time.sleep(0.5)
            driver.find_element_by_xpath(f"//div[@class='show-answer']").click()
            #driver.find_element_by_xpath(f"//ins[@id='nb_invite_tool']").click()
            time.sleep(0.1)
            S_shoot(driver,dirName,PageNum,QuestionNum,Section)
            driver.find_element_by_xpath(f"//span[text()='{dirName}']").click()
            QuestionNum+=1
        except Exception:
            break
def webshot(tup):
    # driver = webdriver.PhantomJS()

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    #picname = str(tup[0][0])

    link = tup[0][1]
    print(link)
    driver.get(link)
    #关广告
    time.sleep(3)
    driver.find_element_by_xpath(f"//ins[@id='nb_invite_tool']").click()
    #登录
    '''
    account = readaccount()
    username , password = account[0] , account[1]
    driver.find_element_by_xpath("//div[@class='login_btn']").click()
    driver.find_element_by_xpath("//div[@prop='username']/input").send_keys(username)
    driver.find_element_by_xpath("//div[@prop='password']/input").send_keys(password)
    driver.find_element_by_xpath("//div[@class='submit_btn']").click()
    time.sleep(1)
    cookies = driver.get_cookies()
    open('cookies.txt','w').write(str(cookies))
    '''
    #cookie 操作
    driver.delete_all_cookies()
    savedCookies = eval(open('cookies.txt','r').read())
    #遍历savedCookies中的两个元素
    for cookie in savedCookies:
        #k代表着add_cookie的参数cookie_dict中的键名，这次我们要传入这5个键
        for k in {'name', 'value', 'domain', 'path', 'expiry'}:
            #cookie.keys()属于'dict_keys'类，通过list将它转化为列表
            if k not in list(cookie.keys()):
                #saveCookies中的第一个元素，由于记录的是登录前的状态，所以它没有'expiry'的键名，我们给它增加
                if k == 'expiry':
                    t = time.time()
                    cookie[k] = int(t)    #时间戳s
        #将每一次遍历的cookie中的这五个键名和键值添加到cookie
        driver.add_cookie({k: cookie[k] for k in {'name', 'value', 'domain', 'path', 'expiry'}})

    UnitNum = 1
    while True:
        try:
            UnitName = driver.find_element_by_xpath(f"//div[@id='left_unit']/ul/li[{UnitNum}]/span").get_attribute('innerHTML')
            driver.find_element_by_xpath(f"//div[@id='left_unit']/ul[1]/li[{UnitNum}]").click()
            time.sleep(1)
            get_dir(rf'ALBioData\{UnitName}\MCQ+ms')
            Shoot_Pages(driver,dirName=UnitName,Section='MCQ+ms')
            driver.find_element_by_xpath(f"//li[text()=' Structured Question ']").click()
            time.sleep(1)
            get_dir(rf'ALBioData\{UnitName}\SQ+ms')
            Shoot_Pages(driver,dirName=UnitName,Section='SQ+ms')
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
    
