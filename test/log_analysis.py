import pandas as pd
import matplotlib.pyplot as plt
import koreanize_matplotlib
from matplotlib.animation import FuncAnimation

def log_graph(num):
    
    data = pd.read_csv('{num}_increase_log.csv')
    
    x = data['시간']
    y1 = data['라이크수']
    y2 = data['라이크증가']
    y3 = data['채팅증가수']
    
    plt.figure()
    plt.plot(x, y1, label='라이크수')
    plt.plot(x, y2, label='라이크증가')
    plt.plot(x, y3, label='채팅증가수')
    
    plt.title('실시간 인기구간')
    plt.legend()
    
    plt.savefig('plot.png')
    return 'plot.png'