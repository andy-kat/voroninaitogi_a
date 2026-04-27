import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import json
import os

API_URL = "https://open.er-api.com/v6/latest/USD"
HISTORY_FILE = "history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def load_currencies():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()
        if data.get("result") != "success":
            raise Exception("API returned error")
        rates = data.get("rates", {})
        codes = sorted([code for code in rates.keys() if code != "USD"])
        codes.insert(0, "USD")
        return codes, rates
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось загрузить курсы валют: {e}")
        root.destroy()
        return [], {}

def convert():
    try:
        amount = float(amount_var.get())
    except ValueError:
        result_var.set("Введите число")
        return
    target = currency_var.get()
    if target not in rates:
        result_var.set("Выберите валюту")
        return
    rate = rates[target]
    converted = amount * rate
    result_str = f"{amount} USD = {converted:,.2f} {target}"
    result_var.set(result_str)

    
    history.insert(0, {
        "from_amount": amount,
        "from_currency": "USD",
        "to_currency": target,
        "rate": rate,
        "result": converted
    })
    history[:] = history[:100]  
    save_history(history)
    update_history_display()

def update_history_display():
    history_text.config(state="normal")
    history_text.delete(1.0, tk.END)
    for entry in history:
        
        line = f"{entry['from_amount']} USD → {entry['to_currency']} ({entry['result']:.2f}), курс: {entry['rate']}\n"
        history_text.insert(tk.END, line)
    history_text.config(state="disabled")


root = tk.Tk()
root.title("Конвертер валют (с историей)")
root.geometry("800x600")
root.resizable(False, False)

amount_var = tk.StringVar()
currency_var = tk.StringVar()
result_var = tk.StringVar()
history = load_history()
currencies, rates = load_currencies()
if not currencies:
    exit()


tk.Label(root, text="Сумма в USD:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
tk.Entry(root, textvariable=amount_var).grid(row=0, column=1, padx=10, pady=10, sticky="we", columnspan=2)

tk.Label(root, text="Валюта:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
currency_menu = ttk.Combobox(root, textvariable=currency_var, values=currencies, state="readonly", width=6)
currency_menu.current(0)
currency_menu.grid(row=1, column=1, padx=10, pady=5, sticky="w")

tk.Button(root, text="Конвертировать", command=convert).grid(row=2, column=0, columnspan=3, pady=15)

tk.Label(root, textvariable=result_var, font=("Arial", 14), fg="#006600").grid(row=3, column=0, columnspan=3, pady=5)


history_label = tk.Label(root, text="История операций:", font=("Arial", 10))
history_label.grid(row=4, column=0, columnspan=3, pady=(15, 0), sticky="w")
history_text = scrolledtext.ScrolledText(root, height=12, width=65, state="disabled", wrap="word")
history_text.grid(row=5, column=0, columnspan=3, padx=10)
update_history_display()

# Атрибуция (по требованию API)
attribution_label = tk.Label(
    root,
    text="Курсы предоставлены ExchangeRate-API",
    font=("Arial", 8),
    fg="#555",
    cursor="hand2"
)
attribution_label.grid(row=6, column=0, columnspan=3, pady=(15, 10))
attribution_label.bind("<Button-1>", lambda e: root.clipboard_clear() or root.clipboard_append("https://www.exchangerate-api.com"))

root.grid_columnconfigure(1, weight=1)
root.mainloop()
