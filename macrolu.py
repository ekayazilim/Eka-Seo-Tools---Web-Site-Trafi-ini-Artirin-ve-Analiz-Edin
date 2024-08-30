import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import threading
import time
import pickle
import requests

drivers = []  
macro_steps = []
user_agents = []
proxies = []

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

def start_recording():
    global drivers, macro_steps
    macro_steps = []
    target_site = entry_link.get()
    selected_user_agent = user_agent_combobox.get()
    selected_proxy = proxy_combobox.get()
    num_browsers = int(tabs_combobox.get())

    if not target_site or not selected_user_agent:
        messagebox.showwarning("Uyarı", "Lütfen geçerli bir site linki ve tarayıcı/cihaz seçimi yapın!")
        return

    chrome_options = Options()
    chrome_options.add_argument(f"user-agent={selected_user_agent}")
    
    if selected_proxy and selected_proxy != "Proxysiz Devam Et":
        chrome_options.add_argument(f"--proxy-server=http://{selected_proxy}")

    for _ in range(num_browsers):
        driver = webdriver.Chrome(service=Service("chromedriver.exe"), options=chrome_options)
        driver.get(target_site)
        drivers.append(driver)

    messagebox.showinfo("Bilgi", "Makro kaydedilmeye başlandı. Tarayıcıda yaptığınız işlemler kaydedilecek.")

def record_step(step_type, element):
    global macro_steps
    macro_steps.append((step_type, element))

def play_macro():
    global drivers, macro_steps
    if not macro_steps:
        messagebox.showwarning("Uyarı", "Kayıtlı bir makro bulunamadı!")
        return

    for driver in drivers:
        for step in macro_steps:
            step_type, element_selector = step
            if step_type == "click":
                try:
                    element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, element_selector)))
                    element.click()
                    time.sleep(2)
                except TimeoutException:
                    print("Zaman aşımı, bir sonraki adıma geçiliyor.")
                except Exception as e:
                    print(f"Bir hata oluştu: {e}")
                    continue

    messagebox.showinfo("Bilgi", "Makro tamamlandı!")

def save_macro():
    global macro_steps
    file_path = filedialog.asksaveasfilename(defaultextension=".pkl", filetypes=[("Pickle files", "*.pkl")])
    if file_path:
        try:
            with open(file_path, "wb") as f:
                pickle.dump(macro_steps, f)
            messagebox.showinfo("Bilgi", "Makro başarıyla kaydedildi!")
        except Exception as e:
            messagebox.showwarning("Uyarı", f"Makro kaydedilirken bir hata oluştu: {e}")

def load_macro():
    global macro_steps
    file_path = filedialog.askopenfilename(filetypes=[("Pickle files", "*.pkl")])
    if file_path:
        try:
            with open(file_path, "rb") as f:
                macro_steps = pickle.load(f)
            if not macro_steps:
                messagebox.showwarning("Uyarı", "Yüklenen makroda herhangi bir adım bulunamadı!")
            else:
                messagebox.showinfo("Bilgi", "Makro başarıyla yüklendi!")
        except (FileNotFoundError, pickle.UnpicklingError, Exception) as e:
            messagebox.showwarning("Uyarı", f"Geçersiz bir makro dosyası yüklendi veya hata oluştu: {e}")

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

app.configure(bg='#dfe6e9')

app.attributes("-topmost", True)

load_user_agents()
load_proxies()

logo = tk.PhotoImage(file='logo.png')  # Logonuzu buraya ekleyin.
logo_label = tk.Label(app, image=logo, bg='#dfe6e9')
logo_label.pack(pady=10)

label_link = ttk.Label(app, text="Site Linki:", background='#dfe6e9', foreground='#2d3436')
label_link.pack(pady=5)

entry_link = ttk.Entry(app, width=50)
entry_link.pack(pady=5)

label_user_agent = ttk.Label(app, text="Cihaz/Tarayıcı Seçin:", background='#dfe6e9', foreground='#2d3436')
label_user_agent.pack(pady=5)

user_agent_combobox = ttk.Combobox(app, values=user_agents, state="readonly", width=80)
user_agent_combobox.pack(pady=5)

label_proxy = ttk.Label(app, text="HTTP Proxy Seçin (Opsiyonel):", background='#dfe6e9', foreground='#2d3436')
label_proxy.pack(pady=5)

proxy_combobox = ttk.Combobox(app, values=["Proxysiz Devam Et"] + proxies, state="readonly", width=80)
proxy_combobox.pack(pady=5)

label_tabs = ttk.Label(app, text="Kaç Tarayıcı Açmak İstersiniz:", background='#dfe6e9', foreground='#2d3436')
label_tabs.pack(pady=5)

tabs_combobox = ttk.Combobox(app, values=[str(i) for i in range(1, 11)], state="readonly", width=10)
tabs_combobox.current(0)
tabs_combobox.pack(pady=5)

start_record_button = tk.Button(app, text="Makro Kaydet", command=start_recording, bg='#1f6aa5', fg='#ffffff', font=('Helvetica', 12, 'bold'))
start_record_button.pack(pady=5)

save_macro_button = tk.Button(app, text="Makro Kaydet ve Kaydet", command=save_macro, bg='#1f6aa5', fg='#ffffff', font=('Helvetica', 12, 'bold'))
save_macro_button.pack(pady=5)

load_macro_button = tk.Button(app, text="Makro Yükle", command=load_macro, bg='#1f6aa5', fg='#ffffff', font=('Helvetica', 12, 'bold'))
load_macro_button.pack(pady=5)

play_macro_button = tk.Button(app, text="Makroyu Oynat", command=lambda: threading.Thread(target=play_macro).start(), bg='#1f6aa5', fg='#ffffff', font=('Helvetica', 12, 'bold'))
play_macro_button.pack(pady=5)

stop_button = tk.Button(app, text="Durdur", command=stop_browsing, bg='#1f6aa5', fg='#ffffff', font=('Helvetica', 12, 'bold'))
stop_button.pack(pady=5)

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(app, variable=progress_var, maximum=100, length=300)
progress_bar.pack(pady=5)

progress_label = ttk.Label(app, text="", background='#dfe6e9', foreground='#2d3436')
progress_label.pack(pady=5)

check_proxy_button = tk.Button(app, text="Proxy Check", command=select_and_check_proxy, bg='#1f6aa5', fg='#ffffff', font=('Helvetica', 12, 'bold'))
check_proxy_button.pack(pady=5)

# Uygulamayı Başlat
app.mainloop()
