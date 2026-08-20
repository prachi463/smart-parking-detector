import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3


DB_NAME = "parking.db"


# ============================================================
# DATABASE
# ============================================================

def get_vehicles(search_text=""):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if search_text:
        query = """
            SELECT
                id,
                owner_name,
                mobile,
                email,
                vehicle_number,
                vehicle_type,
                vehicle_model,
                vehicle_color,
                parking_slot,
                entry_time
            FROM vehicles
            WHERE
                owner_name LIKE ?
                OR mobile LIKE ?
                OR vehicle_number LIKE ?
                OR vehicle_model LIKE ?
                OR parking_slot LIKE ?
            ORDER BY id DESC
        """

        value = f"%{search_text}%"

        cursor.execute(
            query,
            (value, value, value, value, value)
        )

    else:
        cursor.execute("""
            SELECT
                id,
                owner_name,
                mobile,
                email,
                vehicle_number,
                vehicle_type,
                vehicle_model,
                vehicle_color,
                parking_slot,
                entry_time
            FROM vehicles
            ORDER BY id DESC
        """)

    rows = cursor.fetchall()

    conn.close()

    return rows


# ============================================================
# LOAD DATA INTO TABLE
# ============================================================

def load_vehicles():

    for item in tree.get_children():
        tree.delete(item)

    search_text = search_entry.get().strip()

    rows = get_vehicles(search_text)

    for row in rows:
        tree.insert(
            "",
            tk.END,
            values=row
        )

    count_label.config(
        text=f"Registered Vehicles: {len(rows)}"
    )


# ============================================================
# CLEAR SEARCH
# ============================================================

def clear_search():

    search_entry.delete(0, tk.END)

    load_vehicles()


# ============================================================
# DELETE VEHICLE
# ============================================================

def delete_vehicle():

    selected = tree.selection()

    if not selected:
        messagebox.showwarning(
            "Select Vehicle",
            "Please select a vehicle from the table."
        )
        return

    item = tree.item(selected[0])

    vehicle_id = item["values"][0]

    vehicle_number = item["values"][4]

    confirm = messagebox.askyesno(
        "Confirm Delete",
        f"Delete vehicle {vehicle_number}?"
    )

    if not confirm:
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM vehicles WHERE id = ?",
        (vehicle_id,)
    )

    conn.commit()
    conn.close()

    messagebox.showinfo(
        "Deleted",
        "Vehicle deleted successfully."
    )

    load_vehicles()


# ============================================================
# SHOW DETAILS
# ============================================================

def show_details(event=None):

    selected = tree.selection()

    if not selected:
        return

    item = tree.item(selected[0])

    values = item["values"]

    details = f"""
Owner Name:       {values[1]}
Mobile Number:    {values[2]}
Email:            {values[3]}

Vehicle Number:   {values[4]}
Vehicle Type:     {values[5]}
Vehicle Model:    {values[6]}
Vehicle Color:    {values[7]}

Parking Slot:     {values[8]}
Entry Time:       {values[9]}
"""

    messagebox.showinfo(
        "Vehicle Details",
        details
    )


# ============================================================
# MAIN WINDOW
# ============================================================

root = tk.Tk()

root.title(
    "Car Parking Management System - Registered Vehicles"
)

root.geometry("1350x650")

root.minsize(1100, 550)


# ============================================================
# HEADER
# ============================================================

header = tk.Frame(
    root,
    bg="#1f2937",
    height=80
)

header.pack(
    fill=tk.X
)

title = tk.Label(
    header,
    text="REGISTERED VEHICLES",
    font=("Arial", 24, "bold"),
    bg="#1f2937",
    fg="white"
)

title.pack(
    pady=20
)


# ============================================================
# SEARCH AREA
# ============================================================

search_frame = tk.Frame(root)

search_frame.pack(
    fill=tk.X,
    padx=25,
    pady=15
)


search_label = tk.Label(
    search_frame,
    text="Search:",
    font=("Arial", 12, "bold")
)

search_label.pack(
    side=tk.LEFT,
    padx=5
)


search_entry = ttk.Entry(
    search_frame,
    width=45
)

search_entry.pack(
    side=tk.LEFT,
    padx=10
)


search_entry.bind(
    "<KeyRelease>",
    lambda event: load_vehicles()
)


search_button = ttk.Button(
    search_frame,
    text="SEARCH",
    command=load_vehicles
)

search_button.pack(
    side=tk.LEFT,
    padx=5
)


clear_button = ttk.Button(
    search_frame,
    text="CLEAR",
    command=clear_search
)

clear_button.pack(
    side=tk.LEFT,
    padx=5
)


refresh_button = ttk.Button(
    search_frame,
    text="REFRESH",
    command=load_vehicles
)

refresh_button.pack(
    side=tk.LEFT,
    padx=5
)


delete_button = ttk.Button(
    search_frame,
    text="DELETE SELECTED",
    command=delete_vehicle
)

delete_button.pack(
    side=tk.RIGHT,
    padx=5
)


# ============================================================
# COUNT
# ============================================================

count_label = tk.Label(
    root,
    text="Registered Vehicles: 0",
    font=("Arial", 12, "bold")
)

count_label.pack(
    anchor="w",
    padx=30
)


# ============================================================
# TABLE
# ============================================================

table_frame = tk.Frame(root)

table_frame.pack(
    fill=tk.BOTH,
    expand=True,
    padx=25,
    pady=10
)


columns = (
    "ID",
    "Owner",
    "Mobile",
    "Email",
    "Vehicle No",
    "Type",
    "Model",
    "Color",
    "Slot",
    "Entry Time"
)


tree = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings"
)


# Column headings

for column in columns:

    tree.heading(
        column,
        text=column
    )


# Column widths

widths = {
    "ID": 50,
    "Owner": 130,
    "Mobile": 120,
    "Email": 180,
    "Vehicle No": 120,
    "Type": 90,
    "Model": 100,
    "Color": 90,
    "Slot": 80,
    "Entry Time": 150
}


for column, width in widths.items():

    tree.column(
        column,
        width=width,
        anchor=tk.CENTER
    )


# ============================================================
# SCROLLBARS
# ============================================================

vertical_scrollbar = ttk.Scrollbar(
    table_frame,
    orient=tk.VERTICAL,
    command=tree.yview
)

horizontal_scrollbar = ttk.Scrollbar(
    table_frame,
    orient=tk.HORIZONTAL,
    command=tree.xview
)


tree.configure(
    yscrollcommand=vertical_scrollbar.set,
    xscrollcommand=horizontal_scrollbar.set
)


vertical_scrollbar.pack(
    side=tk.RIGHT,
    fill=tk.Y
)

horizontal_scrollbar.pack(
    side=tk.BOTTOM,
    fill=tk.X
)

tree.pack(
    fill=tk.BOTH,
    expand=True
)


# Double-click for details

tree.bind(
    "<Double-1>",
    show_details
)


# ============================================================
# START
# ============================================================

load_vehicles()

root.mainloop()
