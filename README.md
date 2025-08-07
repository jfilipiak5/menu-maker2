
# 🍽️ Menu Scraper & Uploader

Repozytorium zawiera dwa narzędzia:

- **scraper.py** – pobiera menu i zapisuje je jako plik `.json`
- **writer.py** – automatycznie wgrywa menu (`.json`) do panelu Papu.io

---
## Możesz pobrać gotowy plik `.exe`  z folderu `dist` lub skompilować za pomocą tej instrukcji:


## Instalacja i kompilacja do `.exe`

### 1. Instalacja zależności

Upewnij się, że masz zainstalowanego **Pythona 3.8+** oraz `pip`.

Zainstaluj wymagane pakiety:

```bash
pip install pyinstaller selenium webdriver-manager undetected-chromedriver
```

> **Uwaga:**  
> `tkinter` jest wymagany przez oba narzędzia – na Windows jest domyślnie,  
> na Linux/Mac zainstaluj:  
> ```bash
> sudo apt install python3-tk
> ```

---

### 2. Kompilacja do pliku `.exe`

W folderze projektu uruchom w terminalu (osobno dla każdego skryptu):

```bash
pyinstaller --onefile --windowed scraper.py
pyinstaller --onefile --windowed writer.py
```

- `--onefile` — tworzy pojedynczy plik `.exe`
- `--windowed` — ukrywa konsolę (idealne dla aplikacji z GUI)

Po kompilacji pliki `.exe` znajdziesz w folderze `dist/`.

---

## Szybki start

### Scraper (`scraper.exe`)

1. Uruchom program
2. Wklej **URL restauracji**
3. Kliknij **START**
4. Zacznij scrollować strone w dół
4. Gotowe! Plik `pyszne_YYYYMMDD_HHMM_menu.json` zostanie zapisany w tym samym folderze

### Uploader (`writer.exe`)

1. Uruchom program
2. Wskaż plik `menu.json` (np. ten wygenerowany przez scraper)
3. Opcjonalnie zaznacz dodatkowe opcje (dodawanie składników, opisów itd.)
3. Kliknij **Otwórz Chrome** i zaloguj się do panelu Papu.io

### 4. ☠️``WAZNE: Przejdź do zakładki zarządzanie menu -> kategorie (ZAWSZE SKRYPT WŁĄCZAMY W TYM MIEJSCU)``

5. Kliknij ```Start wprowadzania menu```


---

## Najczęstsze problemy i rozwiązania

- **Brak wymaganej biblioteki:**  
  Upewnij się, że wykonałeś polecenie `pip install ...` z sekcji powyżej.

- **Nie uruchamia się Chrome:**  
  Sprawdź, czy masz zainstalowaną najnowszą wersję Google Chrome.

- **Brakuje `tkinter`:**  
  - Windows: domyślnie z Pythonem.
  - Linux/Mac:  
    ```bash
    sudo apt install python3-tk
    ```

- **Program nie działa poprawnie po kompilacji:**  
  Upewnij się, że uruchamiasz plik `.exe` z folderu `dist/`.  
  Spróbuj kompilować na tej samej wersji systemu, na której zamierzasz uruchamiać plik.


