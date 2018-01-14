from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import argparse
import time

try_count = 10
def find_element(browser, by, objective, timeout):
    global try_count
    start_time = time.time()
    try:
        locator = (by, objective)
        WebDriverWait(browser, timeout).until(EC.presence_of_element_located(locator))
        return browser.find_element(*locator)
    except TimeoutException:
        end_time = int(time.time() - start_time)
        print("{} get element timeout, cost:{} except:{}".format(objective, end_time, timeout))
        #exit()
        try_count -= 1
        if try_count <= 0: exit()
        # time.sleep(10)
        return find_element(browser, by, objective, timeout)

def find_element_by_id(browser, objective, timeout): return find_element(browser, By.ID, objective, timeout)
def find_element_by_xpath(browser, objective, timeout): return find_element(browser, By.XPATH, objective, timeout)

def get_tackets(args):
    #get 12306 html
    driver = webdriver.Chrome()
    driver.get('https://kyfw.12306.cn/otn/index/initMy12306')
    #enter your 12306 account
    time.sleep(3)
    find_element_by_id(driver, "username", 10).send_keys(args.username)
    time.sleep(3)
    find_element_by_id(driver, "password", 10).send_keys(args.password)
    #select verification info
    time.sleep(3)
    print("Please select verification information !!!")
    find_element_by_id(driver, "loginSub", 10).click()

    time.sleep(2)
    find_element_by_id(driver, "selectYuding", 5).click()
    time.sleep(2)
    find_element_by_id(driver, "dc", 5).click()
    find_element_by_id(driver, "fromStationText", 5).clear()
    find_element_by_id(driver, "fromStationText", 5).click()
    find_element_by_id(driver, "fromStationText", 5).send_keys(u'深圳')
    find_element_by_id(driver, "fromStationText", 5).send_keys(Keys.ENTER)
    time.sleep(2)
    find_element_by_id(driver, "toStationText", 5).clear()
    find_element_by_id(driver, "toStationText", 5).click()
    find_element_by_id(driver, "toStationText", 5).send_keys(u'西安北')
    find_element_by_id(driver, "toStationText", 5).send_keys(Keys.ENTER)
    print('chose your journey date')
    time.sleep(5)

    js = "$('input[class=\"inp_selected\"').removeAttr('readonly')"
    driver.execute_script(js)
    find_element_by_id(driver, "train_date", 5).clear()
    find_element_by_id(driver, 'train_date', 5).send_keys(args.departure_date)
    time.sleep(5)

    #type of your journey
    # if args.dc:
    #     driver.find_element_by_id("dc").click()
    #     driver.find_element_by_id("train_date").send_keys(u'2017-01-06')
    #     time.sleep(5)
    # else:
    #     driver.find_element_by_id("wf").click()
    #     driver.find_element_by_id("train_date").send_keys(u'2017-01-09')
    #     driver.find_element_by_id("train_date").send_keys(Keys.ENTER)
    #     time.sleep(5)
    #     driver.find_element_by_id("back_train_date").send_keys(args.return_date)
    #     driver.find_element_by_id("back_train_date").send_keys(Keys.ENTER)
    #     time.sleep(5)
    # driver.implicitly_wait(20)
    # time.sleep(10)

    train_type_dict = {'T': '//input[@name="cc_type" and @value="T"]',  # 特快
                       'G': '//input[@name="cc_type" and @value="G"]',  # 高铁
                       'D': '//input[@name="cc_type" and @value="D"]',  # 动车
                       'Z': '//input[@name="cc_type" and @value="Z"]'}  # 直达
    if args.train_type == 'T' or args.train_type == 'G' or args.train_type == 'D' or args.train_type == 'Z':
        find_element_by_xpath(driver, train_type_dict[args.train_type], 5).click()
    else:
        print("no {} type of train available ".format(args.train_type))



    query_times = 0
    while True:
        time.sleep(1)
        search_btn = find_element_by_id(driver, "query_ticket", 3)
        search_btn.click()
        try:   # search for your exception ticket
            acquire_ticket = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="ZE_6i0000G8180A"]')))

            tick_info = acquire_ticket.text
        except:  # no reaction when clicking query button
            search_btn.click()
            acquire_ticket = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="ZE_6i0000G8180A"]')))
            tick_info = acquire_ticket.text

        if tick_info == u'无' or tick_info == u'*':  # no ticket or has not on sale yet
            query_times += 1
            print("query_times:", query_times)
            continue
        else:
            find_element_by_xpath(driver, '//*[@id="ticket_6i0000G8180A"]/td[13]', 5).click()
            break

    cust_sel_url = 'https://kyfw.12306.cn/otn/leftTicket/init'

    # wait for jumping into pay page
    while True:
        if (driver.current_url == cust_sel_url):
            print("Well done, you are getting one ticket")
            break
        else:
            continue

    # choose passenger
    while True:
        try:
            find_element_by_xpath(driver, '//*[@id="normalPassenger_1"]', 5).click()
            time.sleep(1)
            find_element_by_xpath(driver, '//*[@id="normalPassenger_3"]', 5).click()
            break
        except:
            print("no passenger info available")

    # Submit the information after confirming it
    find_element_by_xpath(driver, '//*[@id="submitOrder_id"]', 5).click()
    time.sleep(2)

    # confirm ticket info
    while True:
        try:
            # find_element_by_xpath(driver, '//*[@id="1F"]', 5).click()
            # time.sleep(2)
            # find_element_by_xpath(driver, '//*[@id="1D"]', 5).click()
            # time.sleep(2)
            find_element_by_xpath(driver, '//*[@id="qr_submit_id"]', 10).click()
            print("get ticket successfully")
            break
        except:
            print("Please select verification information !!!")
            time.sleep(5)
            break
    return


if __name__ == "__main__":

    def str2bool(v): return v.lower() in ("yes", "true", "t", "1", True)
    parser = argparse.ArgumentParser(prog="python", description="auto get tickets")
    parser.add_argument('--username', type=str, help='Enter your 12306 usename')
    parser.add_argument('--password', type=str, help='Enter your 12306 password')
    parser.add_argument('--dc', type=str2bool, default=False, help='your journey type: DanChengPiao')
    parser.add_argument('--wf', type=str2bool, default=False, help='your journey type: WangFanPiao')
    parser.add_argument('--departure_date', type=str, help='your journey departure date, example: 2017-06-07')
    parser.add_argument('--return_date', type=str, help='your journey return date, example: 2017-06-07')
    parser.add_argument('--train_type', default='G', type=str, help='Type of train,example: T、G、D or Z')
    args = parser.parse_args()
    get_tackets(args)

