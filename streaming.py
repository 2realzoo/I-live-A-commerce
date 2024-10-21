import os
import time
import pychrome
import requests
import subprocess
import shutil
import asyncio
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta


class Streaming:
    def __init__(self, num, category):
        self.num = num
        self.category = category
        self.ts_files = []
        self.output_file = f'streaming_{self.num}.mp4'
        self.idx = 0
        os.makedirs(f'{self.num}_data', exist_ok=True)

    # Selenium 설정
    def setting_selenium(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless") 
        chrome_options.add_argument("--no-sandbox") 
        chrome_options.add_argument("--window-size=1920x1080")
        service = Service(ChromeDriverManager().install())
        return service, chrome_options

    # 새로운 라이브 방송 들어가기
    def new_live(self):
        service, options = self.setting_selenium()
        driver = webdriver.Chrome(service=service, options=options)
        wait = WebDriverWait(driver, 10)
        driver.get(f'https://shoppinglive.naver.com/categories/dc:{self.category}')

    
        status = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="content"]/section[2]/div[4]/div[1]/a[1]/div/div[2]/div[1]/span/span[1]')))
        if status.text == '라이브':
            element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="content"]/section[2]/div[4]/div[1]/a[2]')))
            live_url = element.get_attribute('href')
        else:
            live_url = None

        driver.quit()
        return live_url

    # 스트리밍 영상 만들기
    def download_ts_file(self, video_url, idx):
        ts_filename = f'{self.num}_data/{idx}.ts'
     
        response = requests.get(video_url, timeout=10)
        response.raise_for_status()
        with open(ts_filename, 'wb') as f:
            f.write(response.content)
        self.ts_files.append(ts_filename)
        return ts_filename
    
    def merge_ts_to_mp4(self):
        if len(self.ts_files) > 1:
            filelist_path = f'{self.num}_data/filelist.txt'
            with open(filelist_path, 'w') as f:
                for ts in self.ts_files:
                    absolute_ts_path = os.path.abspath(ts) 
                    f.write(f"file '{absolute_ts_path}'\n")
            
            subprocess.run([
                'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', filelist_path,
                '-c', 'copy', '-bsf:a', 'aac_adtstoasc', self.output_file
            ], check=True)
        


    # 스트리밍 주소 가져오기
    def log_request(self, request, idx):
        video_url = request.get('url')
        if video_url and video_url.endswith('.ts'):
            ts_filename = self.download_ts_file(video_url, idx)
            if ts_filename:
                self.merge_ts_to_mp4()

    def handle_network_event(self, **kwargs):
        request = kwargs.get('request')
        if request:
            self.log_request(request, self.idx)
            self.idx += 1

    async def streaming_file(self, driver):
        browser = pychrome.Browser(url='http://localhost:7000') 
        tab = browser.list_tab()[0]
        tab.start()
        tab.Network.requestWillBeSent = self.handle_network_event
        tab.Network.enable()
        
        try:
            while True:
                await asyncio.sleep(5)
                if len(self.ts_files) == 600:
                    return True
        except:
            tab.stop()
            shutil.rmtree(f'{self.num}_data')
            os.remove(f'streaming_{self.num}.mp4')

    # 좋아요, 채팅 증가 수 가져오기
    def get_like_count(self,driver):
        wait = WebDriverWait(driver, 10)
        try:
            like_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".LikeButton_number_IXgmK.__disable_double_tab")))
            like_count_text = like_element.text.replace(',','')
            return int(like_count_text)
        except ValueError:
            print('라이크 수 집계 중')
            return None
        except Exception as e:
            print(f'Error: {e}')
            return None
    
    def get_chat_count(self,driver):
        try:
            chat_element = driver.find_elements(By.CSS_SELECTOR, 'div.Comment_wrap_wRrdF')
            return len(chat_element)
        except Exception as e:
            print(f'Error : {e}')
            return 0
    
    def log_results(self, log_file, elapsed_time, like_count, like_increase, chat_count_interval):
        try:
            with open(log_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([elapsed_time, like_count, like_increase, chat_count_interval])
    
        except Exception as e:
            print(f"Error writing to log file: {e}")   
            
    async def increase_count(self,driver):
        log_file = os.path.abspath(f'{self.num}_increase_log.csv')
        with open(log_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['시간', '라이크수', '라이크증가', '채팅증가수'])
            
        start_time = time.time()
        
        pre_like_count = None
        
        while True:
            like_count = self.get_like_count(driver)
            if like_count is None:
                continue
                
            elapsed_time = timedelta(seconds=int(time.time() - start_time))
            initial_chat_count = self.get_chat_count(driver)
                
            await asyncio.sleep(5)
                
            final_chat_count = self.get_chat_count(driver)
            chat_count_interval = final_chat_count - initial_chat_count
                
            if pre_like_count != None:
                like_increase = like_count - pre_like_count
                self.log_results(log_file, elapsed_time, like_count, like_increase, chat_count_interval)
                
            pre_like_count = like_count
        
    
    def run(self):
        service, options = self.setting_selenium()
        options.add_argument('--remote-debugging-port=7000')
        driver = webdriver.Chrome(service=service, options=options)

        try:
            live_url = self.new_live()
            if live_url == None:
                return
        
            driver.get(live_url)

            async def gather_tasks():
                await asyncio.gather(self.streaming_file(driver), self.increase_count(driver))
                
            limit = asyncio.run(gather_tasks())
            
            return limit
        
        finally:
            driver.quit()
