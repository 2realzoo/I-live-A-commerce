import os
import re
import time
import pychrome
import requests
import subprocess
import shutil
import asyncio
import csv
import random
import socket
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from live_graph import run_cusum
import json

channels = []
CHANNELS_FILE = 'DB/channels.json'
# 카테고리 매핑
def save_channels():
    with open(CHANNELS_FILE, 'w', encoding='utf-8') as f:
        json.dump(channels, f, ensure_ascii=False, indent=4)

def load_channels():
    if os.path.exists(CHANNELS_FILE):
        with open(CHANNELS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

channels = load_channels()

category_map = {
    1 : '뷰티',
    2 : '푸드',
    3 : '패션',
    4 : '라이프',
    5 : '여행/체험',
    6 : '키즈',
    7 : '테크',
    8 : '취미레저',
    9 : '문화생활' 
}

class Streaming:
    def __init__(self, category):
        self.channel_num = None
        self.category = category
        self.ts_files = []
        self.output_file = None
        self.idx = 0
        self.port = self.get_free_port() 

    # Selenium 설정
    def get_free_port(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return s.getsockname()[1]
    
    def setting_selenium(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless=new') 
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument(f'--remote-debugging-port={self.port}')
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
            match = re.search(r'lives/(\d+)\?', live_url)
            self.channel_num = match.group(1)
            category_str = category_map[self.category]
            channels.append({'Category':category_str, 'Channel':self.channel_num})
            save_channels()
            os.makedirs(f'DB/{self.category}_{self.channel_num}', exist_ok=True)
            os.makedirs(f'DB/{self.category}_{self.channel_num}/{self.category}_{self.channel_num}_data', exist_ok=True)
            self.output_file = f'DB/{self.category}_{self.channel_num}/streaming_{self.category}_{self.channel_num}.mp4'

        else:
            live_url = None

        driver.quit()
        return live_url

    # 스트리밍 영상 만들기
    def download_ts_file(self, video_url, idx):
        ts_filename = f'DB/{self.category}_{self.channel_num}/{self.category}_{self.channel_num}_data/{idx}.ts'
     
        response = requests.get(video_url, timeout=10)
        response.raise_for_status()
        with open(ts_filename, 'wb') as f:
            f.write(response.content)
        self.ts_files.append(ts_filename)
        return ts_filename
    
    def merge_ts_to_mp4(self):
        dir_path = f'DB/{self.category}_{self.channel_num}/{self.category}_{self.channel_num}_data'
        if not os.path.exists(dir_path):
            print(f"Directory not found, creating: {dir_path}")
            os.makedirs(dir_path, exist_ok=True)

        if len(self.ts_files) > 1:
            filelist_path = os.path.join(dir_path, 'filelist.txt')
            with open(filelist_path, 'w') as f:
                for ts in self.ts_files:
                    absolute_ts_path = os.path.abspath(ts)
                    f.write(f"file '{absolute_ts_path}'\n")
            
            subprocess.run([
                'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', filelist_path,
                '-c', 'copy', '-bsf:a', 'aac_adtstoasc', self.output_file
            ], check=True)

    def remove_channel_from_list(self, channel_num):
        """채널 번호를 기반으로 채널 리스트에서 해당 채널을 제거합니다."""
        global channels
        updated_channels = [channel for channel in channels if channel.get('Channel') != channel_num]
        
        if len(updated_channels) != len(channels):
            print(f"Channel {channel_num} removed successfully.")
        else:
            print(f"Channel {channel_num} not found in the list.")
        
        channels = updated_channels
        save_channels()

    def make_m3u8(self):
        m3u8_path = f'DB/{self.category}_{self.channel_num}/{self.category}_{self.channel_num}_data/output.m3u8' 
        with open(m3u8_path, 'w') as f:
            current_time = datetime.utcnow()
    
            # m3u8 헤더 작성
            f.write("#EXTM3U\n")
            f.write("#EXT-X-VERSION:3\n")
            f.write("#EXT-X-ALLOW-CACHE:NO\n")
            f.write("#EXT-X-TARGETDURATION:2\n")
            f.write("#EXT-X-MEDIA-SEQUENCE:0\n")
            f.write("#EXT-X-DISCONTINUITY-SEQUENCE:0\n")
            f.write(f"#EXT-X-DATERANGE:ID=\"nmss-daterange\",START-DATE=\"{current_time.isoformat()}Z\"\n")
            f.write(f"#EXT-X-PROGRAM-DATE-TIME:{current_time.isoformat()}Z\n")
            f.write("\n")

            for ts_file in self.ts_files:
                ts = ts_file.split('/')[-1]
                f.write("#EXTINF:2.000000,\n")
                f.write(f"{ts}\n")
          
                current_time += timedelta(seconds=2)
                f.write(f"#EXT-X-PROGRAM-DATE-TIME:{current_time.isoformat()}Z\n")

            
    # 스트리밍 주소 가져오기
    def log_request(self, request, idx):
        video_url = request.get('url')
        if video_url and video_url.endswith('.ts'):
            ts_filename = self.download_ts_file(video_url, idx)
            if ts_filename:
                self.make_m3u8()
                timer = threading.Timer(60, self.merge_ts_to_mp4)
                timer.start()

    def handle_network_event(self, **kwargs):
        request = kwargs.get('request')
        if request:
            self.log_request(request, self.idx)
            self.idx += 1

    async def streaming_file(self, driver):
        browser = pychrome.Browser(url=f'http://localhost:{self.port}') 
        tab = browser.list_tab()[0]
        tab.start()
        tab.Network.requestWillBeSent = self.handle_network_event
        tab.Network.enable()

        try:
            while True:
                await asyncio.sleep(5)
                try:
                    mark = driver.find_element(By.XPATH, '//*[@id="product-root"]/div/div/div[1]/div/div/div[3]/div[2]/div[1]/div/div[1]/span[1]')
                    text = mark.get_attribute('aria-label')

                    if text == '종료':
                        print(f"[INFO] 라이브 종료 감지 - {self.category}_{self.channel_num}")
                        self.remove_channel_from_list(self.channel_num)
                        
                        # 🔹 종료 감지 시 파일 삭제
                        if len(self.ts_files) > 0:
                            self.merge_ts_to_mp4()
                        
                        dir_path = f'DB/{self.category}_{self.channel_num}'
                        if os.path.exists(dir_path):
                            shutil.rmtree(dir_path)

                        if os.path.exists(self.output_file):
                            os.remove(self.output_file)

                        break  # 🔹 루프 종료
                except Exception as e:
                    print(f'Error : {e}')
        except Exception as e:
            print(f'Error : {e}')
        finally:
            tab.stop()
            driver.quit()


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
    
    def get_chat_comment(self, count, driver):
        try:
            chat_comment_element = driver.find_element(By.XPATH, f'//*[@id="product-root"]/div/div/div[1]/div/div/div[3]/div[2]/div[3]/div/div[1]/div[1]/div[3]/div/div/div/div/div[{count}]/span/span')
            chat_comment = chat_comment_element.text
            return chat_comment
        except Exception as e:
            print(f'Error : {e}')
            return 'empty'
    
    def log_results(self, log_file, elapsed_time, like_count, like_increase, chat_count_interval):
        try:
            with open(log_file, 'a', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow([elapsed_time, like_count, like_increase, chat_count_interval])
    
        except Exception as e:
            print(f"Error writing to log file: {e}")   

    def comment_log_results(self, comment_file, elapsed_time, comments):
        try:
            with open(comment_file, 'a', newline='', encoding='utf-8-sig') as f:
                comment_writer = csv.writer(f)
                for comment in comments:
                    comment_writer.writerow([elapsed_time, comment])            
        except Exception as e:
            print(f'Error writing to comment file: {e}')
            
    async def increase_count(self, driver):
        log_file = os.path.abspath(f'DB/{self.category}_{self.channel_num}/{self.category}_{self.channel_num}_increase_log.csv')
        comment_file = os.path.abspath(f'DB/{self.category}_{self.channel_num}/{self.category}_{self.channel_num}_comment_log.csv')
        
        with open(log_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['시간', '라이크수', '라이크증가', '채팅증가수'])
        
        with open(comment_file, 'w', newline='', encoding='utf-8-sig') as f:
            comment_writer = csv.writer(f)
            comment_writer.writerow(['시간', '댓글'])
    
        start_time = time.time()
        
        pre_like_count = None
        
        while True:
            comments = []
            like_count = self.get_like_count(driver)
            if like_count is None:
                continue
            
            elapsed_time = timedelta(seconds=int(time.time() - start_time))
            initial_chat_count = self.get_chat_count(driver)
                
            await asyncio.sleep(5)
                
            final_chat_count = self.get_chat_count(driver)
            chat_count_interval = abs(final_chat_count - initial_chat_count)
            
            for count in range(initial_chat_count, final_chat_count+1):
                comments.append(self.get_chat_comment(count, driver))
            
            self.comment_log_results(comment_file, elapsed_time, comments)
            
            if pre_like_count != None:
                like_increase = like_count - pre_like_count
                self.log_results(log_file, elapsed_time, like_count, like_increase, chat_count_interval)
                
            pre_like_count = like_count
            run_cusum(self.category, self.channel_num)
            
    
    def run(self):
        service, options = self.setting_selenium()
        options.add_argument(f'--remote-debugging-port={self.port}')
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
            

async def main():
    tasks = []
    for category in range(2,5):
        sr = Streaming(category)
        task = asyncio.create_task(asyncio.to_thread(sr.run))
        tasks.append(task)
        
    await asyncio.gather(*tasks)