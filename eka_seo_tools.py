import tkinter as tk
from tkinter import messagebox, ttk
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options  
import threading
import time
import requests
import random

drivers = []
user_agents = []
proxies = []
sites = []
referral_urls = ["https://www.facebook.com", "https://www.twitter.com", "https://www.google.com", "https://www.bing.com",
                 "https://www.linkedin.com", "https://www.instagram.com", "https://www.pinterest.com", "https://www.youtube.com",
                 "https://www.tumblr.com", "https://www.reddit.com", "https://www.quora.com", "https://www.github.com",
                 "https://www.stackoverflow.com", "https://www.medium.com", "https://www.whatsapp.com", "https://www.telegram.org",
                 "https://www.snapchat.com", "https://www.tiktok.com", "https://www.vk.com", "https://www.weibo.com"]

def load_user_agents():
    global user_agents
    try:
        with open("user-agents.txt", "r") as f:
            user_agents = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        messagebox.showwarning("Uyarı", "user-agents.txt dosyası bulunamadı!")

def load_proxies():
    global proxies
    try:
        with open("http.txt", "r") as f:
            proxies = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        messagebox.showwarning("Uyarı", "http.txt dosyası bulunamadı!")

def load_sites():
    global sites
    try:
        with open("site.txt", "r") as f:
            sites = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        sites = []
        messagebox.showinfo("Bilgi", "site.txt dosyası bulunamadı, yeni bir tane oluşturulacak.")

def save_site_link():
    site_link = entry_link.get()
    if site_link:
        with open("site.txt", "a") as f:
            f.write(f"{site_link}\n")
        load_sites()
        site_combobox['values'] = sites
        messagebox.showinfo("Bilgi", "Site linki başarıyla kaydedildi!")
    else:
        messagebox.showwarning("Uyarı", "Lütfen geçerli bir site linki girin!")

def check_proxy(proxy):
    try:
        response = requests.get("https://www.google.com", proxies={"http": proxy.strip(), "https": proxy.strip()}, timeout=5)
        if response.status_code == 200:
            return True
    except:
        return False
    return False

def select_and_check_proxy():
    selected_proxy = proxy_combobox.get()
    if not selected_proxy:
        messagebox.showwarning("Uyarı", "Lütfen bir proxy seçin!")
        return

    progress_var.set(0)
    progress_label.config(text="Proxy kontrol ediliyor...")
    
    def run_check():
        valid = check_proxy(selected_proxy)
        if valid:
            progress_label.config(text="Proxy geçerli!")
        else:
            progress_label.config(text="Proxy geçersiz!")
        progress_var.set(100)

    threading.Thread(target=run_check).start()

def browse_site(driver, wait_time):
    start_time = time.time()
    end_time = start_time + wait_time
    while time.time() < end_time:
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)  

            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(3)

            links = driver.find_elements(By.CSS_SELECTOR, "a")
            if links:
                random.choice(links).click()
                time.sleep(3)

            remaining_time = int(end_time - time.time())
            update_timer(remaining_time, wait_time)

        except Exception as e:
            print(f"Bir hata oluştu: {e}")
            continue

def start_browsing():
    global drivers
    target_site = entry_link.get() or site_combobox.get()
    selected_user_agent = user_agent_combobox.get()
    selected_proxy = proxy_combobox.get()
    selected_referral = referral_combobox.get() if referral_combobox.get() else None
    num_browsers = int(tabs_combobox.get())
    wait_time = int(wait_time_entry.get())

    if not target_site or not selected_user_agent:
        messagebox.showwarning("Uyarı", "Lütfen geçerli bir site linki ve tarayıcı/cihaz seçimi yapın!")
        return

    chrome_options = Options()
    chrome_options.add_argument(f"user-agent={selected_user_agent}")

    if selected_referral:
        chrome_options.add_argument(f"referer={selected_referral}")

    if selected_proxy and selected_proxy != "Proxysiz Devam Et":
        chrome_options.add_argument(f"--proxy-server=http://{selected_proxy}")

    for _ in range(num_browsers):
        driver = webdriver.Chrome(service=Service("chromedriver.exe"), options=chrome_options)
        driver.get(target_site)
        drivers.append(driver)
        threading.Thread(target=browse_site, args=(driver, wait_time)).start()

    messagebox.showinfo("Bilgi", "Site gezintisi başlatıldı.")

def update_timer(remaining_time, total_time):
    progress_var.set((total_time - remaining_time) / total_time * 100)
    progress_label.config(text=f"Kalan süre: {remaining_time} saniye")
    if remaining_time <= total_time / 2:
        progress_bar.config(style="Red.Horizontal.TProgressbar")
    else:
        progress_bar.config(style="Green.Horizontal.TProgressbar")

def stop_browsing():
    global drivers
    for driver in drivers:
        driver.quit()
    drivers = []
    messagebox.showinfo("Durum", "Gezinti durduruldu.")

app = tk.Tk()
app.title("Eka SEO Tools")

app.iconphoto(False, tk.PhotoImage(file='logo.png'))

style = ttk.Style()
style.configure('TButton', font=('Helvetica', 12, 'bold'), background='#1f6aa5', foreground='#ffffff')
style.configure('TLabel', font=('Helvetica', 12, 'bold'))
style.configure('TCheckbutton', font=('Helvetica', 12))

style.configure("Green.Horizontal.TProgressbar", background='green')
style.configure("Red.Horizontal.TProgressbar", background='red')

app.configure(bg='#dfe6e9')

app.attributes("-topmost", True)

load_user_agents()
load_proxies()
load_sites()

logo = tk.PhotoImage(file='logo.png')
logo_label = tk.Label(app, image=logo, bg='#dfe6e9')
logo_label.pack(pady=10)

label_link = ttk.Label(app, text="Site Linki (Manuel Giriş):", background='#dfe6e9', foreground='#2d3436')
label_link.pack(pady=5)

entry_link = ttk.Entry(app, width=50)
entry_link.pack(pady=5)

label_site = ttk.Label(app, text="Kayıtlı Site Seç:", background='#dfe6e9', foreground='#2d3436')
label_site.pack(pady=5)

site_combobox = ttk.Combobox(app, values=sites, state="readonly", width=80)
site_combobox.pack(pady=5)

save_site_button = tk.Button(app, text="Site Linkini Kaydet", command=save_site_link, bg='#1f6aa5', fg='#ffffff', font=('Helvetica', 12, 'bold'))
save_site_button.pack(pady=5)

label_user_agent = ttk.Label(app, text="Cihaz/Tarayıcı Seçin:", background='#dfe6e9', foreground='#2d3436')
label_user_agent.pack(pady=5)

user_agent_combobox = ttk.Combobox(app, values=user_agents, state="readonly", width=80)
user_agent_combobox.pack(pady=5)

label_proxy = ttk.Label(app, text="HTTP Proxy Seçin (Opsiyonel):", background='#dfe6e9', foreground='#2d3436')
label_proxy.pack(pady=5)

proxy_combobox = ttk.Combobox(app, values=["Proxysiz Devam Et"] + proxies, state="readonly", width=80)
proxy_combobox.pack(pady=5)

label_referral = ttk.Label(app, text="Referans URL Seçin (Opsiyonel):", background='#dfe6e9', foreground='#2d3436')
label_referral.pack(pady=5)

referral_combobox = ttk.Combobox(app, values=["Yok"] + referral_urls, state="readonly", width=80)
referral_combobox.current(0)
referral_combobox.pack(pady=5)

label_tabs = ttk.Label(app, text="Kaç Tarayıcı Açmak İstersiniz:", background='#dfe6e9', foreground='#2d3436')
label_tabs.pack(pady=5)

tabs_combobox = ttk.Combobox(app, values=[str(i) for i in range(1, 11)], state="readonly", width=10)
tabs_combobox.current(0)
tabs_combobox.pack(pady=5)

label_wait_time = ttk.Label(app, text="Bekleme Süresi (sn):", background='#dfe6e9', foreground='#2d3436')
label_wait_time.pack(pady=5)

wait_time_entry = ttk.Entry(app, width=10)
wait_time_entry.insert(0, "60")  
wait_time_entry.pack(pady=5)

start_browsing_button = tk.Button(app, text="Siteyi Gez", command=start_browsing, bg='#1f6aa5', fg='#ffffff', font=('Helvetica', 12, 'bold'))
start_browsing_button.pack(pady=5)

stop_button = tk.Button(app, text="Durdur", command=stop_browsing, bg='#1f6aa5', fg='#ffffff', font=('Helvetica', 12, 'bold'))
stop_button.pack(pady=5)

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(app, variable=progress_var, maximum=100, length=300, style="Green.Horizontal.TProgressbar")
progress_bar.pack(pady=5)

progress_label = ttk.Label(app, text="", background='#dfe6e9', foreground='#2d3436')
progress_label.pack(pady=5)

check_proxy_button = tk.Button(app, text="Proxy Check", command=select_and_check_proxy, bg='#1f6aa5', fg='#ffffff', font=('Helvetica', 12, 'bold'))
check_proxy_button.pack(pady=5)

# Uygulamayı Başlat
app.mainloop()
