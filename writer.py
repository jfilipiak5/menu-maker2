VERSION = "v1.0"
import time
import json
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def upload_menu(
    driver,
    menu_json_path: str,
    skip_categories: bool = False,
    with_ingredients: bool = False,
    with_description: bool = False,
    log_func=print
):
    start_time = time.time()
    wait = WebDriverWait(driver, 20)
    with open(menu_json_path, 'r', encoding='utf-8') as f:
        menu = json.load(f)
    categories = list(menu.keys())

    if not skip_categories:
        for idx, cat in enumerate(categories, start=1):
            log_func(f"[{idx}/{len(categories)}] Dodaję kategorię: {cat}")
            btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-primary.btn-sm")))
            btn.click()
            inp = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='categoryName']")))
            inp.clear(); inp.send_keys(cat)
            save_btn = driver.find_element(
                By.XPATH,
                "//button[contains(@class, 'btn-success') and not(.//span[contains(text(), 'Opublikuj')]) and (contains(., 'ZAPISZ') or contains(., 'Zapisz'))]"
            )
            save_btn.click(); time.sleep(0.5)
    else:
        log_func("Pominięto dodawanie kategorii.")

    tab = wait.until(EC.element_to_be_clickable((By.XPATH,
        "//button[contains(@class,'filter__btn') and .//span[text()='Dania']]"
    )))
    tab.click(); time.sleep(1)

    for cat in categories:
        dishes = menu.get(cat, [])
        log_func(f"Kategoria '{cat}' - {len(dishes)} dań")
        cat_el = wait.until(EC.element_to_be_clickable(
            (By.XPATH, f"//div[contains(@class,'list-group-item') and .//span[text()='{cat}']]")
        ))
        cat_el.click(); time.sleep(0.5)

        for didx, dish in enumerate(dishes, start=1):
            name = dish.get('name', '')
            ingredients = dish.get('ingredients', [])
            opis = dish.get('description', '').strip()
            log_func(f"[{didx}/{len(dishes)}] Dodaję danie '{name}', składników: {len(ingredients)}, opis: {'TAK' if opis else 'NIE'}")
            add_btn = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button.btn.flex-shrink-0.ml-2.btn-primary.btn-sm")
            ))
            add_btn.click()
            try:
                slider = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//h4[normalize-space(text())='Domyślny']/preceding-sibling::label//span[contains(@class,'slider round')]"
                    )
                ))
                slider.click(); time.sleep(0.3)
            except:
                pass
            inp = wait.until(EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "input[name='mealName'], input[name='productName']")
            ))
            inp.clear(); inp.send_keys(name)
            try:
                price_inp = wait.until(EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "input[name='price']")
                ))
                price_inp.clear(); price_inp.send_keys(str(dish.get('price', '')).replace(' zł','').replace(',','.'))
            except Exception:
                log_func(f"Nie można wprowadzić ceny dla '{name}'")
            save_dish = driver.find_element(By.XPATH,
                "//button[contains(text(),'ZAPISZ') or contains(text(),'Zapisz')]"
            )
            save_dish.click(); time.sleep(0.5)
            errs = driver.find_elements(By.CSS_SELECTOR, "div.alert.alert-danger p.text-danger.small.m-0")
            if errs:
                log_func(f"Błąd: {errs[0].text}. Ponawiam zapis.")
                try: slider.click(); time.sleep(0.3)
                except: pass
                save_dish.click(); time.sleep(0.5)

            if with_ingredients and ingredients:
                try:
                    dish_div = wait.until(EC.element_to_be_clickable(
                        (By.XPATH,
                         f"//div[contains(@class,'list-group-item--draggable') and .//span[normalize-space(text())='{name}']]"
                        )
                    ))
                    driver.execute_script("arguments[0].scrollIntoView(true);", dish_div)
                    dish_div.click(); time.sleep(0.5)
                except Exception as e:
                    log_func(f"Nie można wybrać dania '{name}': {e}")
                for ing in ingredients:
                    try:
                        ing_btn = wait.until(EC.element_to_be_clickable(
                            (By.CSS_SELECTOR, "button.addSizeButton.btn-primary.btn-sm")
                        ))
                        driver.execute_script("arguments[0].scrollIntoView(true);", ing_btn)
                        ing_btn.click(); time.sleep(0.5)
                        inputs = driver.find_elements(By.CSS_SELECTOR, "input[name='ingredientName']")
                        if not inputs:
                            log_func(f"Brak pola input dla '{ing}'")
                            continue
                        inp_ing = inputs[-1]
                        inp_ing.clear(); inp_ing.send_keys(ing)
                        save_ing = wait.until(EC.element_to_be_clickable(
                            (By.CSS_SELECTOR, "button.btn-input.btn-success")
                        ))
                        save_ing.click(); time.sleep(0.8)
                    except Exception as e:
                        log_func(f"Błąd przy dodawaniu '{ing}': {e}")
                        continue

            if with_description and opis:
                try:
                    dish_div = wait.until(EC.element_to_be_clickable(
                        (By.XPATH,
                         f"//div[contains(@class,'list-group-item--draggable') and .//span[normalize-space(text())='{name}']]"
                        )
                    ))
                    driver.execute_script("arguments[0].scrollIntoView(true);", dish_div)
                    dish_div.click(); time.sleep(0.5)
                    desc_area = wait.until(EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, "textarea[name='mealDescription']")))
                    desc_area.clear()
                    desc_area.send_keys(opis)
                    log_func(f"Opis dodany do '{name}'")
                    back_btn = wait.until(EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, "button.btn.mr-2.btn-light.btn-sm")
                    ))
                    back_btn.click()
                    time.sleep(0.5)
                    continue
                except Exception as e:
                    log_func(f"Nie udało się dodać opisu do '{name}': {e}")
                    try:
                        back_btn = driver.find_element(By.CSS_SELECTOR, "button.btn.mr-2.btn-light.btn-sm")
                        back_btn.click(); time.sleep(0.5)
                    except Exception:
                        pass
                    continue

            # Po zapisaniu dania nie klikamy back_btn!
            # Po prostu czekamy aż wróci do listy dań (strona sama powinna to zrobić)
            # Jeśli jest operacja na opisie lub składnikach, wtedy klikamy "Wróć" po tych operacjach.

        try:
            back_btn = driver.find_element(By.CSS_SELECTOR, "button.btn.mr-2.btn-light.btn-sm")
            if back_btn.is_displayed() and back_btn.is_enabled():
                back_btn.click()
                log_func("Kliknięto 'Wróć' po wszystkich daniach w kategorii.")
                time.sleep(0.8)
        except Exception:
            pass

    elapsed = time.time() - start_time
    log_func(f"Całkowity czas działania: {elapsed:.2f} sekund")
    log_func("Zakończono! Zamknij okno Chrome.")

# -----------------------------------------------
#             NOWOCZESNE GUI
# -----------------------------------------------

class ModernCheckbutton(tk.Frame):
    def __init__(self, master, text, variable, accent="#35a2ff", fg="#e3e8f3", bg="#232832", font=("Segoe UI", 11), **kwargs):
        super().__init__(master, bg=bg)
        self.var = variable
        self.accent = accent
        self.bg = bg
        self.fg = fg
        self.font = font
        self.box = tk.Canvas(self, width=22, height=22, bg=bg, highlightthickness=0)
        self.box.pack(side="left")
        self.label = tk.Label(self, text=text, font=font, fg=fg, bg=bg)
        self.label.pack(side="left", padx=(6,0))
        self.box.bind("<Button-1>", self.toggle)
        self.label.bind("<Button-1>", self.toggle)
        self.redraw()
        self.var.trace_add("write", lambda *a: self.redraw())

    def toggle(self, event=None):
        self.var.set(not self.var.get())
        self.redraw()

    def redraw(self):
        self.box.delete("all")
        if self.var.get():
            self.box.create_rectangle(3, 3, 19, 19, outline=self.accent, width=2, fill=self.accent)
            self.box.create_line(7,12, 11,16, 17,7, fill="white", width=2, capstyle="round")
        else:
            self.box.create_rectangle(3, 3, 19, 19, outline=self.accent, width=2, fill=self.bg)

class PapuGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Menu Uploader")
        self.root.geometry("850x640")
        self.root.resizable(False, False)
        self.url = "https://system.papu.io/settings/menu-edit"
        self.driver = None
        self.upload_thread = None
        self.uploading = False

        # --- STYLE ---
        bg = "#202631"
        fg = "#e3e8f3"
        accent = "#35a2ff"
        ok = "#18e094"
        stopc = "#e24e54"
        cardbg = "#232832"
        logbg = "#1a1f29"

        self.root.configure(bg=bg)

        # HEADER
        tk.Label(root, text="Papu Menu Uploader", font=("Segoe UI", 21, "bold"),
                 fg=accent, bg=bg, pady=8).grid(row=0, column=0, columnspan=6)

        # Plik menu.json + buttons
        tk.Label(root, text="Plik menu.json:", bg=bg, fg=fg, font=("Segoe UI", 11)).grid(row=1, column=0, sticky="w", padx=18, pady=6)
        self.menu_entry = tk.Entry(root, width=44, font=("Segoe UI", 11), bg=cardbg, fg=fg, insertbackground=fg, relief="flat", highlightthickness=1, highlightbackground=accent)
        self.menu_entry.grid(row=1, column=1, padx=6, columnspan=3)

        self.menu_button = tk.Button(root, text="Wybierz...", command=self.choose_menu, font=("Segoe UI", 11, "bold"), bg=accent, fg=bg, activebackground=ok, activeforeground=bg, relief="flat", cursor="hand2", height=1)
        self.menu_button.grid(row=1, column=4, padx=(0,4), sticky="ew")

        self.preview_button = tk.Button(root, text="Podgląd menu.json", command=self.preview_json, font=("Segoe UI", 10, "bold"),
                               bg="#384c66", fg="#bfe3fa", activebackground="#1b334b", activeforeground="#71cfff", relief="flat", cursor="hand2")
        self.preview_button.grid(row=1, column=5, padx=2)

        # Status walidacji pod spodem
        self.json_status_label = tk.Label(root, text="", fg="#ff5a5a", bg=bg, font=("Segoe UI", 10, "bold"))
        self.json_status_label.grid(row=2, column=0, columnspan=6, sticky="w", padx=30, pady=(0, 10))



        # Modern checkboxes
        self.skip_categories_var = tk.BooleanVar()
        self.with_ingredients_var = tk.BooleanVar()
        self.with_description_var = tk.BooleanVar()
        ModernCheckbutton(root, "Pomiń dodawanie kategorii", self.skip_categories_var, accent=accent, fg=fg, bg=bg, font=("Segoe UI", 11, "bold")).grid(row=4, column=0, sticky="w", padx=24, pady=(10,2), columnspan=2)
        ModernCheckbutton(root, "Dodaj składniki", self.with_ingredients_var, accent=accent, fg=fg, bg=bg, font=("Segoe UI", 11, "bold")).grid(row=5, column=0, sticky="w", padx=24, pady=2, columnspan=2)
        ModernCheckbutton(root, "Dodaj opisy dań", self.with_description_var, accent=accent, fg=fg, bg=bg, font=("Segoe UI", 11, "bold")).grid(row=6, column=0, sticky="w", padx=24, pady=2, columnspan=2)

        # Adres menu
        tk.Label(root, text="Docelowy adres panelu:", fg="#65d5ff", bg=bg, font=("Segoe UI", 11, "bold")).grid(row=7, column=0, sticky="w", padx=24, pady=(10,0), columnspan=2)
        tk.Label(root, text=self.url, fg=accent, bg=bg, font=("Segoe UI", 11, "bold")).grid(row=8, column=0, sticky="w", padx=24, columnspan=6)

        # Otwórz chrome
        self.open_chrome_button = tk.Button(root, text="Otwórz Chrome", font=("Segoe UI", 12, "bold"), bg=accent, fg=bg, activebackground=ok, activeforeground=bg, relief="flat", cursor="hand2", height=1, state="disabled")
        self.open_chrome_button.grid(row=9, column=0, padx=24, pady=18, columnspan=6, sticky="ew")
        self.open_chrome_button.config(command=self.open_chrome)

        # Start/STOP
        self.start_button = tk.Button(root, text="Start wprowadzania menu", font=("Segoe UI", 12, "bold"), bg=ok, fg=bg, activebackground=accent, activeforeground=bg, relief="flat", cursor="hand2", height=1)
        self.start_button.grid(row=10, column=0, padx=24, pady=0, columnspan=6, sticky="ew")
        self.start_button.config(command=self.start_upload)
        self.start_button.grid_remove()
        self.is_stop_button = False

        # LOGI jako card
        card = tk.Frame(root, bg=cardbg, highlightbackground=accent, highlightthickness=1, bd=0)
        card.grid(row=11, column=0, columnspan=6, padx=12, pady=(14,6), sticky="nsew")
        tk.Label(card, text="📝 Logi operacji", bg=cardbg, fg=accent, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=10, pady=(4,0))
        self.log = tk.Text(card, height=11, width=104, state="disabled", font=("Consolas", 10), bg=logbg, fg="#c8ffda", insertbackground="#7fd7ff", relief="flat", borderwidth=0)
        self.log.pack(fill="both", expand=True, padx=7, pady=(2,8))
        self.log.pack(fill="both", expand=True, padx=7, pady=(2, 8))
        self.log_print(f"Menu uploader created by Zimny {VERSION}\n")

    def validate_json(self):
        path = self.menu_entry.get()
        if not os.path.isfile(path):
            self.open_chrome_button.config(state="disabled")
            return False, ["Brak pliku menu.json!"]
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            self.open_chrome_button.config(state="disabled")
            return False, [f"Nie udało się wczytać pliku: {e}"]

        errors = []
        if not isinstance(data, dict):
            errors.append("Plik nie jest słownikiem ({}).")
        else:
            for cat, dishes in data.items():
                if not isinstance(cat, str):
                    errors.append(f"Kategoria {cat} nie jest tekstem.")
                if not isinstance(dishes, list):
                    errors.append(f"Wartość kategorii '{cat}' nie jest listą.")
                else:
                    for idx, dish in enumerate(dishes):
                        if not isinstance(dish, dict):
                            errors.append(f"W kategorii '{cat}' pozycja {idx+1} nie jest obiektem.")
                            continue
                        if "name" not in dish:
                            errors.append(f"W kategorii '{cat}' pozycja {idx+1} brak pola 'name'.")
                        if "price" not in dish:
                            errors.append(f"W kategorii '{cat}' pozycja {idx+1} brak pola 'price'.")
                        if "ingredients" in dish and not isinstance(dish["ingredients"], list):
                            errors.append(f"W kategorii '{cat}' danie '{dish.get('name','')}' pole 'ingredients' nie jest listą.")
                        if "description" in dish and not isinstance(dish["description"], str):
                            errors.append(f"W kategorii '{cat}' danie '{dish.get('name','')}' pole 'description' nie jest tekstem.")
        if errors:
            self.open_chrome_button.config(state="disabled")
        else:
            self.open_chrome_button.config(state="normal")
        return not errors, errors

    def show_json_status(self, is_ok, errs):
        if is_ok:
            self.json_status_label.config(text="✔ Poprawny plik JSON", fg="#18e094")
        else:
            self.json_status_label.config(text="❌ Błędna struktura: " + "; ".join(errs[:1]), fg="#ff5a5a")

    def choose_menu(self):
        filename = filedialog.askopenfilename(title="Wybierz menu.json", filetypes=[("JSON files", "*.json")])
        if filename:
            self.menu_entry.delete(0, tk.END)
            self.menu_entry.insert(0, filename)
            is_ok, errs = self.validate_json()
            self.show_json_status(is_ok, errs)

    def choose_profile(self):
        initialdir = None
        if sys.platform == "win32":
            localappdata = os.environ.get("LOCALAPPDATA", "")
            chrome_user_data = os.path.join(localappdata, "Google", "Chrome", "User Data")
            if os.path.isdir(chrome_user_data):
                initialdir = chrome_user_data
        dirname = filedialog.askdirectory(title="Wybierz katalog profilu Chrome", initialdir=initialdir)
        if dirname:
            self.profile_entry.delete(0, tk.END)
            self.profile_entry.insert(0, dirname)

    def preview_json(self):
        path = self.menu_entry.get()
        if not os.path.isfile(path):
            messagebox.showerror("Błąd", "Najpierw wskaż prawidłowy plik menu.json!")
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wczytać pliku:\n{e}")
            return

        is_ok, errors = self.validate_json()

        # 25 pierwszych linii JSONa
        pretty_json = json.dumps(data, indent=2, ensure_ascii=False)
        lines = pretty_json.splitlines()
        first_lines = "\n".join(lines[:25])
        # Mini-wzór struktury
        example = (
            '{\n'
            '  "Kategoria": [\n'
            '    {\n'
            '      "name": "Nazwa dania",\n'
            '      "price": "23.50",\n'
            '      "ingredients": ["składnik1", "składnik2"],  // opcjonalne\n'
            '      "description": "opis dania"                 // opcjonalne\n'
            '    }\n'
            '  ]\n'
            '}'
        )

        win = tk.Toplevel(self.root)
        win.title("Podgląd menu.json")
        win.configure(bg="#232832")

        if is_ok:
            tk.Label(win, text="✔ Plik poprawny!", font=("Segoe UI", 11, "bold"), bg="#232832", fg="#3af279").pack(anchor="w", padx=12, pady=(10,2))
        else:
            tk.Label(win, text="❌ BŁĘDNY PLIK", font=("Segoe UI", 11, "bold"), bg="#232832", fg="#ff6565").pack(anchor="w", padx=12, pady=(10,2))
            text0 = tk.Text(win, width=70, height=5, bg="#332727", fg="#ffcccc", font=("Consolas", 10), borderwidth=0)
            text0.pack(padx=12, pady=(0,8))
            text0.insert("1.0", "\n".join(errors))
            text0.config(state="disabled")

        tk.Label(win, text="Pierwsze linijki pliku JSON:", font=("Segoe UI", 11, "bold"), bg="#232832", fg="#39aaff").pack(anchor="w", padx=12, pady=(6,0))
        text1 = tk.Text(win, width=70, height=12, bg="#202631", fg="#d8ffdd", font=("Consolas", 10), borderwidth=0)
        text1.pack(padx=12, pady=(0,8))
        text1.insert("1.0", first_lines)
        text1.config(state="disabled")

        tk.Label(win, text="Wzór poprawnej struktury:", font=("Segoe UI", 11, "bold"), bg="#232832", fg="#39aaff").pack(anchor="w", padx=12, pady=(4,0))
        text2 = tk.Text(win, width=70, height=8, bg="#181c22", fg="#f2f2f2", font=("Consolas", 10), borderwidth=0)
        text2.pack(padx=12, pady=(0,12))
        text2.insert("1.0", example)
        text2.config(state="disabled")
        win.transient(self.root)
        win.grab_set()

    def log_print(self, txt):
        self.log.config(state="normal")
        self.log.insert(tk.END, str(txt)+"\n")
        self.log.yview_moveto(1)
        self.log.config(state="disabled")
        self.root.update()

    def open_chrome(self):
        menu_path = self.menu_entry.get()
        is_ok, errs = self.validate_json()
        if not is_ok:
            messagebox.showerror("Błąd", "Nie można uruchomić — błędny plik menu.json!\n" + "\n".join(errs))
            return
        self.open_chrome_button.config(state="disabled")
        self.log_print("Otwieram Chrome z panelem edycji menu...")

        def run_chrome():
            options = webdriver.ChromeOptions()
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            self.driver.get(self.url)
            self.log_print("Zaloguj się do systemu Papu i przejdź do ekranu edycji menu,")
            self.log_print("następnie kliknij przycisk 'Start wprowadzania menu' poniżej 👇")
            self.start_button.grid()

        threading.Thread(target=run_chrome, daemon=True).start()

    def start_upload(self):
        if self.driver is None:
            self.log_print("Najpierw kliknij 'Otwórz Chrome'!")
            return
        if self.is_stop_button:
            self.log_print("Kończę program na żądanie użytkownika!")
            try:
                if self.driver:
                    self.driver.quit()
            except Exception:
                pass
            self.root.quit()
            self.root.destroy()
            sys.exit(0)
        menu_path = self.menu_entry.get()
        skip_cat = self.skip_categories_var.get()
        with_ing = self.with_ingredients_var.get()
        with_desc = self.with_description_var.get()
        self.start_button.config(text="STOP", bg="#e24e54", fg="white", activebackground="#e24e54", activeforeground="white", command=self.start_upload)
        self.is_stop_button = True
        self.log_print("Startuję automatyczne wprowadzanie menu...")

        def do_upload():
            try:
                upload_menu(
                    self.driver,
                    menu_path,
                    skip_categories=skip_cat,
                    with_ingredients=with_ing,
                    with_description=with_desc,
                    log_func=self.log_print
                )
                self.log_print("Gotowe! Możesz zamknąć okno.")
            except Exception as e:
                self.log_print(f"❌ Błąd: {e}")

        self.upload_thread = threading.Thread(target=do_upload, daemon=True)
        self.upload_thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = PapuGUI(root)
    root.mainloop()