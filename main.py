"""
UniLife Manager Ultimate Pro
A comprehensive student life management application for tracking finances, work hours, and study time.
"""

import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from datetime import datetime
import matplotlib.pyplot as plt
from fpdf import FPDF
import csv


# ============================================================
# APPLICATION WINDOW SETUP
# ============================================================

root = tk.Tk()
root.title("UniLife Manager Ultimate Pro")
root.geometry("900x850")


# ============================================================
# DATA STORAGE
# ============================================================

jobs = []                    # Store job information
transactions = []           # Store financial transactions
study_hours = []           # Store daily study hours
WORK_HOUR_LIMIT = 48       # Maximum work hours per week


# ============================================================
# CURRENCY SYSTEM
# ============================================================

currency_rates = {
    "BDT": 1,
    "AUD": 0.012,
    "USD": 0.012,
    "GBP": 0.0097
}

currency_symbol = {
    "BDT": "৳",
    "AUD": "A$",
    "USD": "$",
    "GBP": "£"
}

selected_currency = tk.StringVar(value="BDT")


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def convert_amount(amount):
    """
    Convert amount to selected currency.
    
    Args:
        amount (float): Amount in base currency (BDT)
    
    Returns:
        float: Converted amount rounded to 2 decimal places
    """
    return round(amount * currency_rates[selected_currency.get()], 2)


def update_summary():
    """
    Update all dashboard summary tiles with current data.
    This includes income, expense, balance, and work hours.
    """
    # Calculate income and expense totals
    income_total = sum(
        convert_amount(t['amount']) 
        for t in transactions 
        if t['type'] == "Income"
    )
    expense_total = sum(
        convert_amount(t['amount']) 
        for t in transactions 
        if t['type'] == "Expense"
    )
    balance = income_total - expense_total

    # Update UI labels with currency symbol
    currency_sym = currency_symbol[selected_currency.get()]
    income_label.config(text=f"{currency_sym}{income_total}")
    expense_label.config(text=f"{currency_sym}{expense_total}")
    balance_label.config(text=f"{currency_sym}{balance}")

    # Update work hours and check if limit exceeded
    worked_hours = sum(j['hours'] for j in jobs)
    hours_label.config(text=f"{worked_hours} hrs")
    
    if worked_hours > WORK_HOUR_LIMIT:
        hours_label.config(fg="red")
    else:
        hours_label.config(fg="black")

    # Update study hours display
    total_study_hours = sum(study_hours)
    study_label.config(text=f"{total_study_hours} hrs")

    check_reminders()


def add_transaction():
    """
    Add a new income or expense transaction to the list.
    Validates all input fields before adding.
    """
    transaction_type_value = transaction_type.get()
    transaction_title_value = transaction_title.get()
    transaction_amount_value = transaction_amount.get()
    transaction_date_value = transaction_date.get()

    # Validate input fields
    if not transaction_title_value or not transaction_amount_value:
        messagebox.showwarning("Input Error", "Please fill all fields")
        return

    try:
        amount = float(transaction_amount_value)
    except ValueError:
        messagebox.showwarning("Input Error", "Amount must be a number")
        return

    # Add transaction to list
    transactions.append({
        "type": transaction_type_value,
        "title": transaction_title_value,
        "amount": amount,
        "date": transaction_date_value
    })

    # Clear input fields
    transaction_title.delete(0, 'end')
    transaction_amount.delete(0, 'end')
    transaction_date.delete(0, 'end')

    # Refresh display
    render_transactions()
    update_summary()


def render_transactions():
    """
    Display all transactions in the transaction listbox.
    Each transaction shows date, type, title, and converted amount.
    """
    transaction_list.delete(0, 'end')
    
    for transaction in transactions:
        converted_amount = convert_amount(transaction['amount'])
        currency_sym = currency_symbol[selected_currency.get()]
        
        display_text = (
            f"{transaction['date']} | "
            f"{transaction['type']} | "
            f"{transaction['title']} : "
            f"{currency_sym}{converted_amount}"
        )
        transaction_list.insert('end', display_text)


def add_job():
    """
    Add a new job shift to the jobs list.
    Validates that all required fields are filled and hours is numeric.
    """
    job_title_value = job_title.get()
    shift_type_value = shift_type.get()
    job_hours_value = job_hours.get()

    # Validate input fields
    if not job_title_value or not job_hours_value:
        messagebox.showwarning("Input Error", "Please fill all fields")
        return

    try:
        hours_numeric = float(job_hours_value)
    except ValueError:
        messagebox.showwarning("Input Error", "Hours must be a number")
        return

    # Add job to list
    jobs.append({
        "title": job_title_value,
        "shift": shift_type_value,
        "hours": hours_numeric
    })

    # Clear input fields
    job_title.delete(0, 'end')
    job_hours.delete(0, 'end')

    # Refresh display
    render_jobs()
    update_summary()


def render_jobs():
    """
    Display all jobs in the jobs listbox.
    Each job shows title, shift type, and hours.
    """
    job_list.delete(0, 'end')
    
    for job in jobs:
        display_text = f"{job['title']} | {job['shift']} | {job['hours']} hrs"
        job_list.insert('end', display_text)


def add_study():
    """
    Add daily study hours to the study log.
    Validates that hours is provided and is numeric.
    """
    study_hours_value = study_hours_entry.get()

    # Validate input
    if not study_hours_value:
        messagebox.showwarning("Input Error", "Please fill study hours")
        return

    try:
        hours_numeric = float(study_hours_value)
    except ValueError:
        messagebox.showwarning("Input Error", "Hours must be a number")
        return

    # Add study hours to list
    study_hours.append(hours_numeric)

    # Clear input field
    study_hours_entry.delete(0, 'end')

    # Refresh display
    render_study()
    update_summary()


def render_study():
    """
    Display all study hours in the study listbox.
    Each entry shows the day number and hours studied.
    """
    study_list.delete(0, 'end')
    
    for day_index, hours in enumerate(study_hours):
        display_text = f"Day {day_index + 1} : {hours} hrs"
        study_list.insert('end', display_text)


def check_reminders():
    """
    Check and alert user about important thresholds:
    - Work hours exceeding weekly limit
    - Balance falling below threshold
    """
    worked_hours = sum(j['hours'] for j in jobs)
    
    if worked_hours > WORK_HOUR_LIMIT:
        messagebox.showwarning("Alert", "Weekly work hours exceeded!")

    income_total = sum(
        convert_amount(t['amount']) 
        for t in transactions 
        if t['type'] == 'Income'
    )
    expense_total = sum(
        convert_amount(t['amount']) 
        for t in transactions 
        if t['type'] == 'Expense'
    )
    balance = income_total - expense_total

    if balance < 100:
        messagebox.showwarning("Alert", "Low balance warning!")


def show_time_pie_chart():
    """
    Display a pie chart showing weekly time distribution
    between work, study, and other activities (out of 168 hours).
    """
    worked_hours = sum(j['hours'] for j in jobs)
    studied_hours = sum(study_hours)
    other_hours = 168 - (worked_hours + studied_hours)

    labels = ['Worked Hours', 'Study Hours', 'Others']
    sizes = [worked_hours, studied_hours, other_hours]
    colors = ['#ff9999', '#66b3ff', '#99ff99']

    plt.figure(figsize=(6, 6))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors)
    plt.title("Weekly Time Distribution")
    plt.show()


def show_income_expense_chart():
    """
    Display a stacked bar chart comparing income and expense over time.
    """
    if not transactions:
        messagebox.showinfo("No Data", "Please add transactions first")
        return

    dates = [t['date'] for t in transactions]
    income_values = [
        convert_amount(t['amount']) if t['type'] == "Income" else 0
        for t in transactions
    ]
    expense_values = [
        convert_amount(t['amount']) if t['type'] == "Expense" else 0
        for t in transactions
    ]

    plt.figure(figsize=(8, 5))
    plt.bar(dates, income_values, label="Income", color="#4CAF50")
    plt.bar(dates, expense_values, bottom=income_values, label="Expense", color="#F44336")
    
    plt.xlabel("Date")
    plt.ylabel("Amount")
    plt.title("Income & Expense Overview")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def export_csv():
    """
    Export all data (transactions, jobs, study hours) to a CSV file.
    User selects save location via file dialog.
    """
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")]
    )
    
    if not file_path:
        return

    try:
        with open(file_path, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Type/Job/Study", "Title", "Amount/Hours", "Date/Day"])

            # Write transactions
            for transaction in transactions:
                writer.writerow([
                    transaction['type'],
                    transaction['title'],
                    transaction['amount'],
                    transaction['date']
                ])

            # Write jobs
            for job in jobs:
                writer.writerow([
                    "Job",
                    job['title'],
                    job['hours'],
                    job['shift']
                ])

            # Write study hours
            for day_index, hours in enumerate(study_hours):
                writer.writerow([
                    "Study",
                    f"Day {day_index + 1}",
                    hours,
                    "N/A"
                ])

        messagebox.showinfo("Exported", "Data exported to CSV successfully!")
    
    except Exception as error:
        messagebox.showerror("Export Error", f"Failed to export: {str(error)}")


def export_pdf():
    """
    Export a comprehensive PDF report containing all summary statistics.
    User selects save location via file dialog.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Monthly Student Life Report", ln=True, align="C")

    pdf.set_font("Arial", "", 12)
    pdf.ln(10)

    # Calculate totals
    income_total = sum(
        convert_amount(t['amount']) 
        for t in transactions 
        if t['type'] == 'Income'
    )
    expense_total = sum(
        convert_amount(t['amount']) 
        for t in transactions 
        if t['type'] == 'Expense'
    )
    balance = income_total - expense_total
    worked_hours = sum(j['hours'] for j in jobs)
    studied_hours = sum(study_hours)

    # Add report content
    currency_sym = currency_symbol[selected_currency.get()]
    
    pdf.cell(0, 10, f"Total Income: {currency_sym}{income_total}", ln=True)
    pdf.cell(0, 10, f"Total Expense: {currency_sym}{expense_total}", ln=True)
    pdf.cell(0, 10, f"Balance: {currency_sym}{balance}", ln=True)
    pdf.cell(0, 10, f"Total Worked Hours: {worked_hours}", ln=True)
    pdf.cell(0, 10, f"Total Study Hours: {studied_hours}", ln=True)

    # Save file
    file_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")]
    )

    if file_path:
        try:
            pdf.output(file_path)
            messagebox.showinfo("PDF Exported", "Report exported to PDF successfully!")
        except Exception as error:
            messagebox.showerror("Export Error", f"Failed to export: {str(error)}")


def currency_changed(*args):
    """Handle currency selection changes."""
    update_summary()
    render_transactions()


# Register currency change handler
selected_currency.trace("w", currency_changed)


# ============================================================
# DARK / LIGHT MODE
# ============================================================

dark_mode = tk.BooleanVar(value=False)


def toggle_theme():
    """
    Toggle between dark and light themes.
    Updates background and foreground colors for all widgets.
    """
    if dark_mode.get():
        bg_color = "#222"
        fg_color = "white"
    else:
        bg_color = "white"
        fg_color = "black"

    root.configure(bg=bg_color)

    # Update all child widgets
    for widget in root.winfo_children():
        try:
            widget.configure(bg=bg_color, fg=fg_color)
        except tk.TclError:
            # Some widgets don't support these configurations
            pass


# Dark mode toggle button
tk.Checkbutton(
    root,
    text="Dark Mode",
    variable=dark_mode,
    command=toggle_theme
).pack(pady=5)


# ============================================================
# TABBED INTERFACE
# ============================================================

notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill='both')

# Create tabs
dash_tab = tk.Frame(notebook)
notebook.add(dash_tab, text="Dashboard")

finance_tab = tk.Frame(notebook)
notebook.add(finance_tab, text="Finance")

jobs_tab = tk.Frame(notebook)
notebook.add(jobs_tab, text="Jobs")

study_tab = tk.Frame(notebook)
notebook.add(study_tab, text="Study")

charts_tab = tk.Frame(notebook)
notebook.add(charts_tab, text="Charts & Export")


# ============================================================
# DASHBOARD TAB - SUMMARY TILES
# ============================================================

income_tile = tk.LabelFrame(
    dash_tab,
    text="Income",
    bg="#4CAF50",
    fg="white",
    font=("Arial", 12, "bold")
)
income_tile.pack(padx=10, pady=5, fill="x")
income_label = tk.Label(
    income_tile,
    text="৳0",
    font=("Arial", 12),
    bg="#4CAF50",
    fg="white"
)
income_label.pack()

expense_tile = tk.LabelFrame(
    dash_tab,
    text="Expense",
    bg="#F44336",
    fg="white",
    font=("Arial", 12, "bold")
)
expense_tile.pack(padx=10, pady=5, fill="x")
expense_label = tk.Label(
    expense_tile,
    text="৳0",
    font=("Arial", 12),
    bg="#F44336",
    fg="white"
)
expense_label.pack()

balance_tile = tk.LabelFrame(
    dash_tab,
    text="Balance",
    bg="#2196F3",
    fg="white",
    font=("Arial", 12, "bold")
)
balance_tile.pack(padx=10, pady=5, fill="x")
balance_label = tk.Label(
    balance_tile,
    text="৳0",
    font=("Arial", 12),
    bg="#2196F3",
    fg="white"
)
balance_label.pack()

worked_tile = tk.LabelFrame(
    dash_tab,
    text="Worked Hours",
    bg="#FF9800",
    fg="white",
    font=("Arial", 12, "bold")
)
worked_tile.pack(padx=10, pady=5, fill="x")
hours_label = tk.Label(
    worked_tile,
    text="0 hrs",
    font=("Arial", 12),
    bg="#FF9800",
    fg="white"
)
hours_label.pack()

study_tile = tk.LabelFrame(
    dash_tab,
    text="Study Hours",
    bg="#9C27B0",
    fg="white",
    font=("Arial", 12, "bold")
)
study_tile.pack(padx=10, pady=5, fill="x")
study_label = tk.Label(
    study_tile,
    text="0 hrs",
    font=("Arial", 12),
    bg="#9C27B0",
    fg="white"
)
study_label.pack()


# ============================================================
# FINANCE TAB - TRANSACTIONS
# ============================================================

tk.Label(
    finance_tab,
    text="Add Income/Expense",
    font=("Arial", 14, "bold")
).pack(pady=5)

transaction_type = tk.StringVar(value="Income")
tk.OptionMenu(finance_tab, transaction_type, "Income", "Expense").pack()

transaction_title = tk.Entry(finance_tab)
transaction_title.pack()
transaction_title.insert(0, "Title")

transaction_amount = tk.Entry(finance_tab)
transaction_amount.pack()
transaction_amount.insert(0, "Amount")

transaction_date = tk.Entry(finance_tab)
transaction_date.pack()
transaction_date.insert(0, datetime.today().strftime("%Y-%m-%d"))

tk.Button(
    finance_tab,
    text="Add Transaction",
    command=add_transaction
).pack(pady=5)

transaction_list = tk.Listbox(finance_tab, width=80)
transaction_list.pack(pady=5)


# ============================================================
# JOBS TAB - WORK SHIFTS
# ============================================================

tk.Label(
    jobs_tab,
    text="Add Job Shift",
    font=("Arial", 14, "bold")
).pack(pady=10)

job_title = tk.Entry(jobs_tab)
job_title.pack()
job_title.insert(0, "Job Name")

shift_type = tk.StringVar(value="Day")
tk.OptionMenu(jobs_tab, shift_type, "Day", "Night").pack()

job_hours = tk.Entry(jobs_tab)
job_hours.pack()
job_hours.insert(0, "Hours")

tk.Button(
    jobs_tab,
    text="Add Job",
    command=add_job
).pack(pady=5)

job_list = tk.Listbox(jobs_tab, width=80)
job_list.pack(pady=5)


# ============================================================
# STUDY TAB - STUDY HOURS
# ============================================================

tk.Label(
    study_tab,
    text="Add Study Hours (Daily)",
    font=("Arial", 14, "bold")
).pack(pady=10)

study_hours_entry = tk.Entry(study_tab)
study_hours_entry.pack()
study_hours_entry.insert(0, "Hours")

tk.Button(
    study_tab,
    text="Add Study Hours",
    command=add_study
).pack(pady=5)

study_list = tk.Listbox(study_tab, width=50)
study_list.pack(pady=5)


# ============================================================
# CHARTS & EXPORT TAB
# ============================================================

tk.Button(
    charts_tab,
    text="Show Weekly Time Pie Chart",
    command=show_time_pie_chart,
    bg="#4CAF50",
    fg="white"
).pack(pady=5)

tk.Button(
    charts_tab,
    text="Show Income & Expense Chart",
    command=show_income_expense_chart,
    bg="#2196F3",
    fg="white"
).pack(pady=5)

tk.Button(
    charts_tab,
    text="Export All Data to CSV",
    command=export_csv,
    bg="#FF9800",
    fg="white"
).pack(pady=5)

tk.Button(
    charts_tab,
    text="Export PDF Report",
    command=export_pdf,
    bg="#9C27B0",
    fg="white"
).pack(pady=5)


# ============================================================
# APPLICATION STARTUP
# ============================================================

update_summary()
root.mainloop()
