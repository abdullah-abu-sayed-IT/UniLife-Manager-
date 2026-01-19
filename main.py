import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from datetime import datetime
import matplotlib.pyplot as plt
from fpdf import FPDF
import csv

# ----------------- App Window -----------------
root = tk.Tk()
root.title("UniLife Manager Ultimate Pro")
root.geometry("900x850")

# ----------------- Data Storage -----------------
jobs = []
transactions = []
study_hours = []
WORK_HOUR_LIMIT = 48  # per week

# ----------------- Currency System -----------------
currency_rates = {"BDT":1,"AUD":0.012,"USD":0.012,"GBP":0.0097}
currency_symbol = {"BDT":"৳","AUD":"A$","USD":"$","GBP":"£"}
selected_currency = tk.StringVar(value="BDT")

# ----------------- Helper Functions -----------------
def convert_amount(amount):
    return round(amount * currency_rates[selected_currency.get()],2)

def update_summary():
    income_total = sum(convert_amount(t['amount']) for t in transactions if t['type']=="Income")
    expense_total = sum(convert_amount(t['amount']) for t in transactions if t['type']=="Expense")
    balance = income_total - expense_total

    income_label.config(text=f"{currency_symbol[selected_currency.get()]}{income_total}")
    expense_label.config(text=f"{currency_symbol[selected_currency.get()]}{expense_total}")
    balance_label.config(text=f"{currency_symbol[selected_currency.get()]}{balance}")

    worked_hours = sum(j['hours'] for j in jobs)
    hours_label.config(text=f"{worked_hours} hrs")
    if worked_hours > WORK_HOUR_LIMIT:
        hours_label.config(fg="red")
    else:
        hours_label.config(fg="black")

    check_reminders()

def add_transaction():
    t_type = transaction_type.get()
    t_title = transaction_title.get()
    t_amount = transaction_amount.get()
    t_date = transaction_date.get()
    if not t_title or not t_amount:
        messagebox.showwarning("Input Error","Fill all fields")
        return
    try:
        amount = float(t_amount)
    except:
        messagebox.showwarning("Input Error","Amount must be number")
        return
    transactions.append({"type":t_type,"title":t_title,"amount":amount,"date":t_date})
    transaction_title.delete(0,'end')
    transaction_amount.delete(0,'end')
    transaction_date.delete(0,'end')
    render_transactions()
    update_summary()

def render_transactions():
    transaction_list.delete(0,'end')
    for t in transactions:
        converted = convert_amount(t['amount'])
        transaction_list.insert('end', f"{t['date']} | {t['type']} | {t['title']} : {currency_symbol[selected_currency.get()]}{converted}")

def add_job():
    job_title_val = job_title.get()
    shift_val = shift_type.get()
    hours_val = job_hours.get()
    if not job_title_val or not hours_val:
        messagebox.showwarning("Input Error","Fill all fields")
        return
    try:
        hours_num = float(hours_val)
    except:
        messagebox.showwarning("Input Error","Hours must be number")
        return
    jobs.append({"title":job_title_val,"shift":shift_val,"hours":hours_num})
    job_title.delete(0,'end')
    job_hours.delete(0,'end')
    render_jobs()
    update_summary()

def render_jobs():
    job_list.delete(0,'end')
    for j in jobs:
        job_list.insert('end', f"{j['title']} | {j['shift']} | {j['hours']} hrs")

def add_study():
    study_val = study_hours_entry.get()
    if not study_val:
        messagebox.showwarning("Input Error","Fill study hours")
        return
    try:
        hours_num = float(study_val)
    except:
        messagebox.showwarning("Input Error","Hours must be number")
        return
    study_hours.append(hours_num)
    study_hours_entry.delete(0,'end')
    render_study()
    update_summary()

def render_study():
    study_list.delete(0,'end')
    for i,h in enumerate(study_hours):
        study_list.insert('end', f"Day {i+1} : {h} hrs")

def check_reminders():
    worked_hours = sum(j['hours'] for j in jobs)
    if worked_hours > WORK_HOUR_LIMIT:
        messagebox.showwarning("Alert","Weekly work hours exceeded!")
    balance = sum(convert_amount(t['amount']) for t in transactions if t['type']=='Income') - sum(convert_amount(t['amount']) for t in transactions if t['type']=='Expense')
    if balance < 100:
        messagebox.showwarning("Alert","Low balance warning!")

def show_time_pie_chart():
    worked = sum(j['hours'] for j in jobs)
    studied = sum(study_hours)
    others = 168 - (worked + studied)
    labels = ['Worked Hours','Study Hours','Others']
    sizes = [worked,studied,others]
    colors = ['#ff9999','#66b3ff','#99ff99']
    plt.figure(figsize=(6,6))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors)
    plt.title("Weekly Time Distribution")
    plt.show()

def show_income_expense_chart():
    if not transactions: return
    dates = [t['date'] for t in transactions]
    income = [convert_amount(t['amount']) if t['type']=="Income" else 0 for t in transactions]
    expense = [convert_amount(t['amount']) if t['type']=="Expense" else 0 for t in transactions]
    plt.figure(figsize=(8,5))
    plt.bar(dates, income, label="Income", color="#4CAF50")
    plt.bar(dates, expense, bottom=income, label="Expense", color="#F44336")
    plt.xlabel("Date"); plt.ylabel("Amount"); plt.title("Income & Expense Overview")
    plt.legend(); plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def export_csv():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
    if not file_path: return
    with open(file_path, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Type/Job/Study","Title","Amount/Hours","Date/Day"])
        for t in transactions:
            writer.writerow([t['type'], t['title'], t['amount'], t['date']])
        for j in jobs:
            writer.writerow(["Job", j['title'], j['hours'], j['shift']])
        for i,h in enumerate(study_hours):
            writer.writerow(["Study", f"Day {i+1}", h, "N/A"])
    messagebox.showinfo("Exported","Data exported successfully!")

def export_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Monthly Student Life Report", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.ln(10)
    pdf.cell(0,10,f"Total Income: {currency_symbol[selected_currency.get()]}{sum(convert_amount(t['amount']) for t in transactions if t['type']=='Income')}", ln=True)
    pdf.cell(0,10,f"Total Expense: {currency_symbol[selected_currency.get()]}{sum(convert_amount(t['amount']) for t in transactions if t['type']=='Expense')}", ln=True)
    pdf.cell(0,10,f"Balance: {currency_symbol[selected_currency.get()]}{sum(convert_amount(t['amount']) for t in transactions if t['type']=='Income') - sum(convert_amount(t['amount']) for t in transactions if t['type']=='Expense')}", ln=True)
    pdf.cell(0,10,f"Total Worked Hours: {sum(j['hours'] for j in jobs)}", ln=True)
    pdf.cell(0,10,f"Total Study Hours: {sum(study_hours)}", ln=True)
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files","*.pdf")])
    if file_path:
        pdf.output(file_path)
        messagebox.showinfo("PDF Exported","Report exported successfully!")

def currency_changed(*args):
    update_summary()
    render_transactions()

selected_currency.trace("w", currency_changed)

# ----------------- Dark / Light Mode -----------------
dark_mode = tk.BooleanVar()
def toggle_theme():
    bg_color = "#222" if dark_mode.get() else "white"
    fg_color = "white" if dark_mode.get() else "black"
    root.configure(bg=bg_color)
    for widget in root.winfo_children():
        try:
            widget.configure(bg=bg_color, fg=fg_color)
        except:
            pass

tk.Checkbutton(root, text="Dark Mode", variable=dark_mode, command=toggle_theme).pack(pady=5)

# ----------------- Tabs -----------------
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill='both')

# Dashboard Tab
dash_tab = tk.Frame(notebook)
notebook.add(dash_tab, text="Dashboard")

# Finance Tab
finance_tab = tk.Frame(notebook)
notebook.add(finance_tab, text="Finance")

# Jobs Tab
jobs_tab = tk.Frame(notebook)
notebook.add(jobs_tab, text="Jobs")

# Study Tab
study_tab = tk.Frame(notebook)
notebook.add(study_tab, text="Study")

# Charts Tab
charts_tab = tk.Frame(notebook)
notebook.add(charts_tab, text="Charts & Export")

# ----------------- Dashboard Tiles -----------------
income_tile = tk.LabelFrame(dash_tab, text="Income", bg="#4CAF50", fg="white", font=("Arial",12,"bold"))
income_tile.pack(padx=10, pady=5, fill="x")
income_label = tk.Label(income_tile,text="৳0", font=("Arial",12), bg="#4CAF50", fg="white")
income_label.pack()

expense_tile = tk.LabelFrame(dash_tab, text="Expense", bg="#F44336", fg="white", font=("Arial",12,"bold"))
expense_tile.pack(padx=10, pady=5, fill="x")
expense_label = tk.Label(expense_tile,text="৳0", font=("Arial",12), bg="#F44336", fg="white")
expense_label.pack()

balance_tile = tk.LabelFrame(dash_tab, text="Balance", bg="#2196F3", fg="white", font=("Arial",12,"bold"))
balance_tile.pack(padx=10, pady=5, fill="x")
balance_label = tk.Label(balance_tile,text="৳0", font=("Arial",12), bg="#2196F3", fg="white")
balance_label.pack()

worked_tile = tk.LabelFrame(dash_tab, text="Worked Hours", bg="#FF9800", fg="white", font=("Arial",12,"bold"))
worked_tile.pack(padx=10, pady=5, fill="x")
hours_label = tk.Label(worked_tile,text="0 hrs", font=("Arial",12), bg="#FF9800", fg="white")
hours_label.pack()

study_tile = tk.LabelFrame(dash_tab, text="Study Hours", bg="#9C27B0", fg="white", font=("Arial",12,"bold"))
study_tile.pack(padx=10, pady=5, fill="x")
study_label = tk.Label(study_tile,text="0 hrs", font=("Arial",12), bg="#9C27B0", fg="white")
study_label.pack()

# ----------------- Finance Tab -----------------
tk.Label(finance_tab,text="Add Income/Expense", font=("Arial",14,"bold")).pack(pady=5)
transaction_type = tk.StringVar(value="Income")
tk.OptionMenu(finance_tab, transaction_type,"Income","Expense").pack()
transaction_title = tk.Entry(finance_tab); transaction_title.pack(); transaction_title.insert(0,"Title")
transaction_amount = tk.Entry(finance_tab); transaction_amount.pack(); transaction_amount.insert(0,"Amount")
transaction_date = tk.Entry(finance_tab); transaction_date.pack(); transaction_date.insert(0,datetime.today().strftime("%Y-%m-%d"))
tk.Button(finance_tab,text="Add Transaction",command=add_transaction).pack(pady=5)
transaction_list = tk.Listbox(finance_tab,width=80); transaction_list.pack(pady=5)

# ----------------- Jobs Tab -----------------
tk.Label(jobs_tab,text="Add Job Shift", font=("Arial",14,"bold")).pack(pady=10)
job_title = tk.Entry(jobs_tab); job_title.pack(); job_title.insert(0,"Job Name")
shift_type = tk.StringVar(value="Day"); tk.OptionMenu(jobs_tab,shift_type,"Day","Night").pack()
job_hours = tk.Entry(jobs_tab); job_hours.pack(); job_hours.insert(0,"Hours")
tk.Button(jobs_tab,text="Add Job",command=add_job).pack(pady=5)
job_list = tk.Listbox(jobs_tab,width=80); job_list.pack(pady=5)

# ----------------- Study Tab -----------------
tk.Label(study_tab,text="Add Study Hours (Daily)", font=("Arial",14,"bold")).pack(pady=10)
study_hours_entry = tk.Entry(study_tab); study_hours_entry.pack(); study_hours_entry.insert(0,"Hours")
tk.Button(study_tab,text="Add Study Hours",command=add_study).pack(pady=5)
study_list = tk.Listbox(study_tab,width=50); study_list.pack(pady=5)

# ----------------- Charts & Export Tab -----------------
tk.Button(charts_tab,text="Show Weekly Time Pie Chart",command=show_time_pie_chart,bg="#4CAF50",fg="white").pack(pady=5)
tk.Button(charts_tab,text="Show Income & Expense Chart",command=show_income_expense_chart,bg="#2196F3",fg="white").pack(pady=5)
tk.Button(charts_tab,text="Export All Data to CSV",command=export_csv,bg="#FF9800",fg="white").pack(pady=5)
tk.Button(charts_tab,text="Export PDF Report",command=export_pdf,bg="#9C27B0",fg="white").pack(pady=5)

# ----------------- Start -----------------
update_summary()
root.mainloop()
