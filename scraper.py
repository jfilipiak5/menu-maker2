import sys
import time
import json
import threading
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import re
import urllib.request

def validate_url(url):
    # Prosta walidacja URL (czy wygląda jak adres Pyszne)
    pattern = r"^https?://.*pyszne\.pl/.*$"
    return re.match(pattern, url.strip()) is not None

def check_internet(url_to_check="https://www.google.com", timeout=4):
    try:
        urllib.request.urlopen(url_to_check, timeout=timeout)
        return True
    except Exception:
        return False


def create_driver_for_pyszne():
    import undetected_chromedriver as uc
    options = uc.ChromeOptions()
    options.add_argument("--incognito")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
    driver = uc.Chrome(options=options, headless=False, use_subprocess=True)
    return driver

def scrape_pyszne(driver, url: str, logbox=None, parent=None):
    stop_event = threading.Event()
    menu = {}
    already = set()

    def log_inner(msg):
        if logbox:
            logbox.config(state='normal')
            logbox.insert('end', msg)
            logbox.see('end')
            logbox.config(state='disabled')

    def live_scrape():
        category_dish_names = {}
        while not stop_event.is_set():
            try:
                sections = driver.find_elements("css selector", 'section[data-qa="item-category"]')
                for sec in sections:
                    try:
                        cat = sec.find_element("css selector", 'h2[data-qa="heading"]').text.strip()
                    except Exception:
                        continue
                    if not cat:
                        continue
                    if cat not in menu:
                        menu[cat] = []
                        category_dish_names[cat] = set()
                    dishes = sec.find_elements("css selector", 'h3[data-qa="heading"]')
                    for dish in dishes:
                        try:
                            name = dish.text.strip()
                            if not name or name in category_dish_names[cat]:
                                continue
                            category_dish_names[cat].add(name)

                            price = ''
                            try:
                                price = dish.find_element(
                                    "xpath", 'ancestor::li//span[contains(text(), "zł")]'
                                ).text.strip()
                            except Exception:
                                pass

                            description = ""
                            ingredients = []
                            try:
                                desc = dish.find_element(
                                    "xpath", 'ancestor::li//div[@data-qa="text"]'
                                ).text.strip()
                                if desc:
                                    description = desc
                                    desc_clean = desc.lstrip("z ").strip() if desc.lower().startswith("z ") else desc
                                    ingredients = [s.strip() for s in desc_clean.split(",") if s.strip()]
                            except Exception:
                                pass

                            menu[cat].append({
                                'name': name,
                                'price': price,
                                'ingredients': ingredients,
                                'description': description
                            })
                            log_inner(f"  [{cat}] {name} | {price}\n")
                        except Exception:
                            continue
            except Exception:
                continue
            time.sleep(0.07)

    def stop_and_save():
        stop_event.set()
        time.sleep(0.2)
        filename = f"pyszne_{datetime.now().strftime('%Y%m%d_%H%M')}_menu.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(menu, f, ensure_ascii=False, indent=2)
        log_inner(f"\nZapisano: {filename}\n")
        if parent:
            messagebox.showinfo("Koniec", f"Menu zapisane do pliku: {filename}")

    if parent:
        stop_button = tk.Button(parent, text="STOP (Zapisz i zakończ)", command=stop_and_save, bg="#e24e54", fg="#fff", font=("Segoe UI", 11, "bold"), relief="flat", cursor="hand2")
        stop_button.grid(row=4, column=0, columnspan=3, pady=18, sticky="ew")
    else:
        stop_button = None

    driver.get(url)
    time.sleep(3)

    thread = threading.Thread(target=live_scrape, daemon=True)
    thread.start()

    if parent:
        # zamiast wait_variable, prosto: okno zamyka się po STOP
        parent.wait_window(stop_button)
    else:
        input("Naciśnij Enter żeby zakończyć i zapisać menu...")
        stop_and_save()

    if stop_button and parent:
        stop_button.destroy()

    return menu

# --- GUI ---
def start_gui():
    VERSION = "v1.0"
    root = tk.Tk()
    root.title(f"Menu Scraper {VERSION}")
    root.geometry("850x600")
    root.resizable(False, False)

    bg = "#202631"
    fg = "#e3e8f3"
    accent = "#35a2ff"
    cardbg = "#232832"
    logbg = "#1a1f29"

    root.configure(bg=bg)

    tk.Label(root, text=f"Menu Scraper", font=("Segoe UI", 21, "bold"),
             fg=accent, bg=bg, pady=8).grid(row=0, column=0, columnspan=3)

    # URL
    tk.Label(root, text="Wklej URL restauracji", bg=bg, fg=fg, font=("Segoe UI", 12)).grid(row=1, column=0, sticky='w', padx=30, pady=(12,4), columnspan=2)
    url_var = tk.StringVar()
    url_entry = tk.Entry(root, textvariable=url_var, width=60, font=("Segoe UI", 12), bg=cardbg, fg=fg, insertbackground=fg, relief="flat", highlightthickness=1, highlightbackground=accent)
    url_entry.grid(row=2, column=0, padx=30, columnspan=2, sticky="ew")
    url_entry.focus_set()

    # Logi
    card = tk.Frame(root, bg=cardbg, highlightbackground=accent, highlightthickness=1, bd=0)
    card.grid(row=3, column=0, columnspan=3, padx=24, pady=(26,6), sticky="nsew")
    tk.Label(card, text="📝 Logi scrapowania", bg=cardbg, fg=accent, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=10, pady=(4,0))
    logbox = tk.Text(card, height=18, width=104, state="disabled", font=("Consolas", 10), bg=logbg, fg="#c8ffda", insertbackground="#7fd7ff", relief="flat", borderwidth=0)
    logbox.pack(fill="both", expand=True, padx=7, pady=(2,8))
    logbox.config(state='normal')
    logbox.insert('end', f"Menu uploader created by Zimny version {VERSION}\n")
    logbox.config(state='disabled')

    # Przycisk START
    def on_start():
        url = url_var.get().strip()
        if not url:
            messagebox.showerror("Brak URL", "Podaj adres URL restauracji!")
            return
        if not validate_url(url):
            messagebox.showerror("Nieprawidłowy URL", "Adres musi prowadzić do profilu restauracji i zaczynać się od http(s)://")
            return
        if not check_internet():
            messagebox.showerror("Brak internetu", "Brak połączenia z internetem.\nSprawdź sieć i spróbuj ponownie.")
            return
        try:
            logbox.config(state='normal')
            logbox.insert('end', f"\nRozpoczynam scrapowanie {url}\n")
            logbox.config(state='disabled')
            driver = create_driver_for_pyszne()
        except Exception as e:
            messagebox.showerror("Błąd drivera", f"Nie można uruchomić przeglądarki:\n{e}")
            return

        threading.Thread(target=scrape_pyszne, args=(driver, url, logbox, root), daemon=True).start()

    start_btn = tk.Button(root, text="START", command=on_start, font=("Segoe UI", 13, "bold"),
                          bg=accent, fg=bg, activebackground="#168fe1", activeforeground="#fff", relief="flat", cursor="hand2", height=1)
    start_btn.grid(row=5, column=0, padx=30, pady=(14, 12), sticky="ew", columnspan=3)



    root.mainloop()

if __name__ == '__main__':
    start_gui()