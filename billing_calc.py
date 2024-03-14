import tkinter as tk
from tkinter import ttk
import datetime
from tkinter import messagebox
import sys
import requests
import base64

selected_month2 = 0
selected_year2 = 0

# check if the current mpnth is selected and calculates passed time based on hours
def part_month():
    now = datetime.datetime.now()
    current_day = now.day
    current_hour = now.hour
    current_month = now.month
    if str(current_month) == selected_month2 and str(current_year) == selected_year2:
        total_days_in_month = (now.replace(day=1, month=current_month % 12 + 1, year=now.year if current_month % 12 != 12 else now.year + 1) - datetime.timedelta(days=1)).day
        total_hours_in_month = total_days_in_month * 24
        total_hours_passed = (current_day - 1) * 24 + current_hour
        percentage_passed = (total_hours_passed / total_hours_in_month) * 100
        return percentage_passed
    else:
        return 100

#multiplies current usage with rest of the month
def forecaster(value):
    perc = part_month()
    partm = 100/perc
    fullmonth = partm*value
    return fullmonth

#main function
def submit_values():
    username = entry_username.get()
    password = entry_password.get()
    selected_month = month_combobox.get()
    selected_year = year_combobox.get()
    
    #for global use, withour leading 0
    global selected_month2
    selected_month2 = month_combobox.get()
    global selected_year2
    selected_year2 = year_combobox.get()
    contractnumber = entry_contract.get()
    
    # Check if any input field is empty
    if not all([username, password, selected_month, selected_year]):
        tk.messagebox.showerror("Error", "Please fill out all fields before submitting.")
        return
    
    input_window_closed = True
    
    authstr=str(username+":"+password)
    authstr=authstr.encode()
    base64str=base64.b64encode(authstr)
    base64str=base64str.decode()
    basicauth={"Authorization": "Basic "+base64str+""}
    
    #add leading 0 for period in url
    if selected_month == "10" or selected_month == "11" or selected_month == "12":
        selected_month = selected_month
    else:
        selected_month = "0"+selected_month
    
    #creates url for billing API usage and products
    url_usage = "https://api.ionos.com/billing/"+contractnumber+"/usage/?period="+selected_year+"-"+selected_month
    url_products = "https://api.ionos.com/billing/"+contractnumber+"/products"
    
    
    response_data = requests.get(url_usage, headers=basicauth)
    data=response_data.json()
    response_prices = requests.get(url_products, headers=basicauth)
    prices=response_prices.json()
    
    # Create a dictionary to store aggregated quantities and units for each "meterId"
    aggregated_data_usage = {}
    for datacenter in data.get('datacenters', []):
        for meter in datacenter.get('meters', []):
            meter_id = meter.get('meterId')
            quantity = float(meter.get('quantity', {}).get('quantity', 0))
            unit = meter.get('quantity', {}).get('unit', '')

            if meter_id in aggregated_data_usage:
                aggregated_data_usage[meter_id]['quantity'] += quantity
            else:
                aggregated_data_usage[meter_id] = {'quantity': quantity, 'unit': unit}

    # Create a dictionary to store prices for each "meterId"
    aggregated_data_price = {}
    for product in prices.get('products', []):
        meter_id = product.get('meterId')
        meter_desc = product.get('meterDesc')
        price = float(product.get('unitCost', {}).get('quantity', 0))
        currency = product.get('unitCost', {}).get('unit', '')
        aggregated_data_price[meter_id] = {'desc': meter_desc, 'price': price, 'currency': currency}

    table_window.deiconify()
    input_window.withdraw()
    
    title = f"Billing data for {selected_month}/{selected_year}"
    table_window.title(title)  # Set the title of the table window
      
    # Display the aggregated quantities and units for each "meterId"
    total_cost_now = 0
    total_cost_month = 0
    for meter_id, data in aggregated_data_usage.items():
        total_quantity = round(data['quantity'], 2)
        unit = data['unit']
        for meter_id2, data_p in aggregated_data_price.items():
            if meter_id == meter_id2:
                price = data_p['price']
                if price != 0:
                    desc = data_p['desc']
                    currency = data_p['currency']
                    total = round(total_quantity*price, 2)
                    forecast = round(forecaster(total), 2)
                    table.insert('', 'end', values=(meter_id, desc, unit, total_quantity, price, currency, str(total) +" " + currency, str(forecast) +" " + currency))
                    total_cost_now = total_cost_now + total
                    total_cost_month = total_cost_month + forecast

    table.insert('', 'end', values=("", "", "", "", "", "Total", round(total_cost_now,2), round(total_cost_month,2)))
    
def show_input_window():
    input_window.deiconify()
    table_window.withdraw()
    table_window_closed = True
    clear_table()
    
def clear_table():
    for row in table.get_children():
        table.delete(row)

def on_closing(window, flag):
    if window.winfo_exists():
        window.destroy()
    sys.exit()

# Input window
input_window_closed = False
input_window = tk.Tk()
input_window.title("IONOS billing")

# Set the width of the main window
window_width = 330  # Set the desired width in pixels
window_height = 260  # Set the desired height in pixels

# Get the screen width and height
screen_width = input_window.winfo_screenwidth()
screen_height = input_window.winfo_screenheight()

# Calculate the x and y coordinates for the top-left corner of the window to center it on the screen
x_pos = (screen_width // 2) - (window_width // 2)
y_pos = (screen_height // 2) - (window_height // 2)

# Set the geometry of the main window
input_window.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")
input_window.resizable(width=False, height=False)

label_description = tk.Label(input_window, text="Enter your login data and the billing month:")
label_description.config(fg='navy')  # Custom font and text color
label_description.grid(row=0, column=0, columnspan=2, pady=(10, 5))

label_username = tk.Label(input_window, text="Username:")
label_username.grid(row=1, column=0, pady=5, padx=25)
entry_username = tk.Entry(input_window, highlightthickness=1, highlightbackground='lightgrey')
entry_username.grid(row=1, column=1, pady=5)

label_password = tk.Label(input_window, text="Password:")
label_password.grid(row=2, column=0, pady=5, padx=5)
entry_password = tk.Entry(input_window, show="*", highlightthickness=1, highlightbackground='lightgrey')
entry_password.grid(row=2, column=1, pady=5)

label_contract = tk.Label(input_window, text="Contractnumber:")
label_contract.grid(row=3, column=0, pady=5, padx=25)
entry_contract = tk.Entry(input_window, highlightthickness=1, highlightbackground='lightgrey')
entry_contract.grid(row=3, column=1, pady=5)

label_month = tk.Label(input_window, text="Month:")
label_month.grid(row=4, column=0, pady=5)
months = [f"{month}" for month in range(1, 13)]
month_combobox = ttk.Combobox(input_window, values=months, state="readonly")
month_combobox.grid(row=4, column=1, pady=5)

label_year = tk.Label(input_window, text="Year:")
label_year.grid(row=5, column=0, pady=5)
current_year = datetime.datetime.now().year
years = [str(year) for year in range(current_year, current_year - 3, -1)]
year_combobox = ttk.Combobox(input_window, values=years, state="readonly")
year_combobox.grid(row=5, column=1, pady=5)

submit_button = tk.Button(input_window, text="Submit", command=submit_values)
submit_button.grid(row=6, column=1, pady=(20, 10), padx=(5, 100))

input_window.protocol("WM_DELETE_WINDOW", lambda: on_closing(input_window, input_window_closed))

# Table window
table_window_closed = False
table_window = tk.Tk()
table_window.title("Billing data")

# Set the width of the main window
window_width = 1000  # Set the desired width in pixels
window_height = 400  # Set the desired height in pixels

# Get the screen width and height
screen_width = table_window.winfo_screenwidth()
screen_height = table_window.winfo_screenheight()

# Calculate the x and y coordinates for the top-left corner of the window to center it on the screen
x_pos = (screen_width // 2) - (window_width // 2)
y_pos = (screen_height // 2) - (window_height // 2)

# Set the geometry of the main window
table_window.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")

frame = ttk.Frame(table_window)
frame.pack(fill='both', expand=True)

table = ttk.Treeview(frame, columns=('MeterID', 'Description', 'Unit', 'Quantity', 'Price', 'Currency', 'Total', 'Forecast')) #, 'Growth'))
table.heading('#0', text='')
table.heading('MeterID', text='MeterID')
table.heading('Description', text='Description')
table.heading('Unit', text='Unit')
table.heading('Quantity', text='Quantity')
table.heading('Price', text='Price')
table.heading('Currency', text='Currency')
table.heading('Total', text='Total')
table.heading('Forecast', text='Forecast')
#table.heading('Growth', text='Growth')

scrollbar = ttk.Scrollbar(frame, orient='vertical', command=table.yview)
table.configure(yscrollcommand=scrollbar.set)

table.column('#0', width=0, stretch=tk.NO)
table.column('MeterID', width=60)
table.column('Description', width=250)
table.column('Unit', width=80)
table.column('Quantity', width=80)
table.column('Price', width=80)
table.column('Currency', width=80)
table.column('Total', width=100)
table.column('Forecast', width=100)
#table.column('Growth', width=80)
table.pack(side='left', expand=True, fill='both')
scrollbar.pack(side='right', fill='y')

back_button = tk.Button(table_window, text="Back", command=show_input_window)
back_button.pack()

table_window.protocol("WM_DELETE_WINDOW", lambda: on_closing(table_window, table_window_closed))

table_window.withdraw()

tk.mainloop()