import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime


# ============================================================
# DATABASE
# ============================================================

DB_NAME = "parking.db"


def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_name TEXT NOT NULL,
            mobile TEXT NOT NULL,
            email TEXT,
            vehicle_number TEXT NOT NULL UNIQUE,
            vehicle_type TEXT NOT NULL,
            vehicle_model TEXT,
            vehicle_color TEXT,
            parking_slot TEXT,
            entry_time TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ============================================================
# COLORS
# ============================================================

BG = "#F4F7FB"
WHITE = "#FFFFFF"
DARK = "#172033"
PRIMARY = "#2563EB"
PRIMARY_HOVER = "#1D4ED8"
SUCCESS = "#16A34A"
DANGER = "#DC2626"
TEXT = "#1F2937"
MUTED = "#6B7280"
BORDER = "#D9E0EA"


# ============================================================
# VALIDATION
# ============================================================

def validate_mobile(mobile):
    return mobile.isdigit() and len(mobile) == 10


def validate_vehicle_number(number):
    """
    Basic Indian vehicle-number validation.

    Examples:
    UP78AB1234
    DL01CA1234
    MH12XY4567
    """

    number = number.replace(" ", "").upper()

    if len(number) < 8 or len(number) > 12:
        return False

    return number.isalnum()


# ============================================================
# REGISTER VEHICLE
# ============================================================

def register_vehicle():

    owner_name = owner_entry.get().strip()
    mobile = mobile_entry.get().strip()
    email = email_entry.get().strip()

    vehicle_number = (
        vehicle_number_entry
        .get()
        .strip()
        .upper()
        .replace(" ", "")
    )

    vehicle_type = vehicle_type_combo.get()
    vehicle_model = model_entry.get().strip()
    vehicle_color = color_entry.get().strip()

    parking_slot = slot_combo.get()

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    if not owner_name:
        messagebox.showerror(
            "Missing Information",
            "Please enter the owner's name."
        )
        owner_entry.focus()
        return

    if not mobile:
        messagebox.showerror(
            "Missing Information",
            "Please enter the mobile number."
        )
        mobile_entry.focus()
        return

    if not validate_mobile(mobile):
        messagebox.showerror(
            "Invalid Mobile Number",
            "Please enter a valid 10-digit mobile number."
        )
        mobile_entry.focus()
        return

    if not vehicle_number:
        messagebox.showerror(
            "Missing Information",
            "Please enter the vehicle registration number."
        )
        vehicle_number_entry.focus()
        return

    if not validate_vehicle_number(vehicle_number):
        messagebox.showerror(
            "Invalid Vehicle Number",
            "Please enter a valid vehicle registration number."
        )
        vehicle_number_entry.focus()
        return

    if not vehicle_type:
        messagebox.showerror(
            "Missing Information",
            "Please select the vehicle type."
        )
        vehicle_type_combo.focus()
        return

    if not vehicle_model:
        messagebox.showerror(
            "Missing Information",
            "Please enter the vehicle model."
        )
        model_entry.focus()
        return

    if not vehicle_color:
        messagebox.showerror(
            "Missing Information",
            "Please enter the vehicle color."
        )
        color_entry.focus()
        return

    if not parking_slot:
        messagebox.showerror(
            "Missing Information",
            "Please select a parking slot."
        )
        slot_combo.focus()
        return

    # --------------------------------------------------------
    # Entry Time
    # --------------------------------------------------------

    entry_time = datetime.now().strftime(
        "%d-%m-%Y %I:%M:%S %p"
    )

    # --------------------------------------------------------
    # Database
    # --------------------------------------------------------

    try:

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO vehicles (
                owner_name,
                mobile,
                email,
                vehicle_number,
                vehicle_type,
                vehicle_model,
                vehicle_color,
                parking_slot,
                entry_time
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            owner_name,
            mobile,
            email,
            vehicle_number,
            vehicle_type,
            vehicle_model,
            vehicle_color,
            parking_slot,
            entry_time
        ))

        conn.commit()
        conn.close()

        messagebox.showinfo(
            "Registration Successful",
            f"Vehicle {vehicle_number} has been registered successfully."
        )

        status_label.config(
            text=f"✓ Vehicle {vehicle_number} registered successfully",
            fg=SUCCESS
        )

        clear_form()

    except sqlite3.IntegrityError:

        messagebox.showerror(
            "Registration Failed",
            f"Vehicle {vehicle_number} is already registered."
        )

    except Exception as e:

        messagebox.showerror(
            "Database Error",
            str(e)
        )


# ============================================================
# CLEAR FORM
# ============================================================

def clear_form():

    owner_entry.delete(0, tk.END)
    mobile_entry.delete(0, tk.END)
    email_entry.delete(0, tk.END)

    vehicle_number_entry.delete(0, tk.END)
    vehicle_type_combo.set("")
    model_entry.delete(0, tk.END)
    color_entry.delete(0, tk.END)

    slot_combo.set("")

    status_label.config(
        text="Ready for new vehicle registration",
        fg=MUTED
    )

    owner_entry.focus()


# ============================================================
# VIEW REGISTERED VEHICLES
# ============================================================

def view_vehicles():

    window = tk.Toplevel(root)

    window.title(
        "Registered Vehicles"
    )

    window.geometry(
        "1250x600"
    )

    window.configure(
        bg=BG
    )

    # --------------------------------------------------------
    # Header
    # --------------------------------------------------------

    header = tk.Frame(
        window,
        bg=DARK,
        height=70
    )

    header.pack(
        fill=tk.X
    )

    tk.Label(
        header,
        text="REGISTERED VEHICLES",
        font=("Segoe UI", 20, "bold"),
        bg=DARK,
        fg=WHITE
    ).pack(
        side=tk.LEFT,
        padx=25,
        pady=18
    )

    # --------------------------------------------------------
    # Table Frame
    # --------------------------------------------------------

    table_frame = tk.Frame(
        window,
        bg=WHITE
    )

    table_frame.pack(
        fill=tk.BOTH,
        expand=True,
        padx=20,
        pady=20
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

    widths = {
        "ID": 50,
        "Owner": 130,
        "Mobile": 120,
        "Email": 180,
        "Vehicle No": 120,
        "Type": 90,
        "Model": 110,
        "Color": 90,
        "Slot": 80,
        "Entry Time": 160
    }

    for column in columns:

        tree.heading(
            column,
            text=column
        )

        tree.column(
            column,
            width=widths[column],
            anchor=tk.CENTER
        )

    # --------------------------------------------------------
    # Scrollbars
    # --------------------------------------------------------

    vertical_scroll = ttk.Scrollbar(
        table_frame,
        orient=tk.VERTICAL,
        command=tree.yview
    )

    horizontal_scroll = ttk.Scrollbar(
        table_frame,
        orient=tk.HORIZONTAL,
        command=tree.xview
    )

    tree.configure(
        yscrollcommand=vertical_scroll.set,
        xscrollcommand=horizontal_scroll.set
    )

    vertical_scroll.pack(
        side=tk.RIGHT,
        fill=tk.Y
    )

    horizontal_scroll.pack(
        side=tk.BOTTOM,
        fill=tk.X
    )

    tree.pack(
        fill=tk.BOTH,
        expand=True
    )

    # --------------------------------------------------------
    # Load Data
    # --------------------------------------------------------

    try:

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

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

        for row in rows:

            tree.insert(
                "",
                tk.END,
                values=row
            )

    except Exception as e:

        messagebox.showerror(
            "Database Error",
            str(e)
        )


# ============================================================
# BUTTON HOVER EFFECT
# ============================================================

def button_hover(button, normal_color, hover_color):

    button.bind(
        "<Enter>",
        lambda event: button.config(
            bg=hover_color
        )
    )

    button.bind(
        "<Leave>",
        lambda event: button.config(
            bg=normal_color
        )
    )


# ============================================================
# MAIN WINDOW
# ============================================================

create_database()

root = tk.Tk()

root.title(
    "Car Parking Management System | Vehicle Registration"
)

root.geometry(
    "1100x800"
)

root.minsize(
    950,
    700
)

root.configure(
    bg=BG
)


# ============================================================
# HEADER
# ============================================================

header = tk.Frame(
    root,
    bg=DARK,
    height=100
)

header.pack(
    fill=tk.X
)

# Logo

logo = tk.Label(
    header,
    text="P",
    font=("Segoe UI", 24, "bold"),
    bg=PRIMARY,
    fg=WHITE,
    width=3,
    height=1
)

logo.pack(
    side=tk.LEFT,
    padx=(30, 15),
    pady=20
)

# Title

title_frame = tk.Frame(
    header,
    bg=DARK
)

title_frame.pack(
    side=tk.LEFT
)

tk.Label(
    title_frame,
    text="CAR PARKING",
    font=("Segoe UI", 22, "bold"),
    bg=DARK,
    fg=WHITE
).pack(
    anchor="w"
)

tk.Label(
    title_frame,
    text="Management System  •  Vehicle Registration",
    font=("Segoe UI", 10),
    bg=DARK,
    fg="#CBD5E1"
).pack(
    anchor="w"
)


# ============================================================
# CONTENT
# ============================================================

content = tk.Frame(
    root,
    bg=BG
)

content.pack(
    fill=tk.BOTH,
    expand=True,
    padx=35,
    pady=25
)


# ============================================================
# PAGE TITLE
# ============================================================

tk.Label(
    content,
    text="Vehicle Registration",
    font=("Segoe UI", 24, "bold"),
    bg=BG,
    fg=TEXT
).pack(
    anchor="w"
)

tk.Label(
    content,
    text="Register customer and vehicle information for parking management.",
    font=("Segoe UI", 11),
    bg=BG,
    fg=MUTED
).pack(
    anchor="w",
    pady=(2, 20)
)


# ============================================================
# OWNER INFORMATION CARD
# ============================================================

owner_frame = tk.LabelFrame(
    content,
    text="  👤 Owner Information  ",
    font=("Segoe UI", 12, "bold"),
    bg=WHITE,
    fg=TEXT,
    bd=1,
    relief=tk.SOLID,
    padx=20,
    pady=15
)

owner_frame.pack(
    fill=tk.X,
    pady=8
)


# Owner Name

tk.Label(
    owner_frame,
    text="Owner Name *",
    font=("Segoe UI", 10, "bold"),
    bg=WHITE,
    fg=TEXT
).grid(
    row=0,
    column=0,
    sticky="w",
    padx=10,
    pady=(5, 4)
)

owner_entry = ttk.Entry(
    owner_frame,
    width=38,
    font=("Segoe UI", 10)
)

owner_entry.grid(
    row=1,
    column=0,
    padx=10,
    pady=(0, 10)
)


# Mobile

tk.Label(
    owner_frame,
    text="Mobile Number *",
    font=("Segoe UI", 10, "bold"),
    bg=WHITE,
    fg=TEXT
).grid(
    row=0,
    column=1,
    sticky="w",
    padx=10,
    pady=(5, 4)
)

mobile_entry = ttk.Entry(
    owner_frame,
    width=30,
    font=("Segoe UI", 10)
)

mobile_entry.grid(
    row=1,
    column=1,
    padx=10,
    pady=(0, 10)
)


# Email

tk.Label(
    owner_frame,
    text="Email Address",
    font=("Segoe UI", 10, "bold"),
    bg=WHITE,
    fg=TEXT
).grid(
    row=0,
    column=2,
    sticky="w",
    padx=10,
    pady=(5, 4)
)

email_entry = ttk.Entry(
    owner_frame,
    width=35,
    font=("Segoe UI", 10)
)

email_entry.grid(
    row=1,
    column=2,
    padx=10,
    pady=(0, 10)
)


# ============================================================
# VEHICLE INFORMATION CARD
# ============================================================

vehicle_frame = tk.LabelFrame(
    content,
    text="  🚗 Vehicle Information  ",
    font=("Segoe UI", 12, "bold"),
    bg=WHITE,
    fg=TEXT,
    bd=1,
    relief=tk.SOLID,
    padx=20,
    pady=15
)

vehicle_frame.pack(
    fill=tk.X,
    pady=8
)


# Vehicle Number

tk.Label(
    vehicle_frame,
    text="Registration Number *",
    font=("Segoe UI", 10, "bold"),
    bg=WHITE,
    fg=TEXT
).grid(
    row=0,
    column=0,
    sticky="w",
    padx=10,
    pady=(5, 4)
)

vehicle_number_entry = ttk.Entry(
    vehicle_frame,
    width=35,
    font=("Segoe UI", 10)
)

vehicle_number_entry.grid(
    row=1,
    column=0,
    padx=10,
    pady=(0, 10)
)


# Vehicle Type

tk.Label(
    vehicle_frame,
    text="Vehicle Type *",
    font=("Segoe UI", 10, "bold"),
    bg=WHITE,
    fg=TEXT
).grid(
    row=0,
    column=1,
    sticky="w",
    padx=10,
    pady=(5, 4)
)

vehicle_type_combo = ttk.Combobox(
    vehicle_frame,
    values=[
        "Car",
        "SUV",
        "Sedan",
        "Hatchback",
        "Motorcycle",
        "Scooter",
        "Bus",
        "Truck",
        "Other"
    ],
    width=28,
    state="readonly",
    font=("Segoe UI", 10)
)

vehicle_type_combo.grid(
    row=1,
    column=1,
    padx=10,
    pady=(0, 10)
)


# Model

tk.Label(
    vehicle_frame,
    text="Vehicle Model *",
    font=("Segoe UI", 10, "bold"),
    bg=WHITE,
    fg=TEXT
).grid(
    row=0,
    column=2,
    sticky="w",
    padx=10,
    pady=(5, 4)
)

model_entry = ttk.Entry(
    vehicle_frame,
    width=30,
    font=("Segoe UI", 10)
)

model_entry.grid(
    row=1,
    column=2,
    padx=10,
    pady=(0, 10)
)


# Color

tk.Label(
    vehicle_frame,
    text="Vehicle Color *",
    font=("Segoe UI", 10, "bold"),
    bg=WHITE,
    fg=TEXT
).grid(
    row=2,
    column=0,
    sticky="w",
    padx=10,
    pady=(10, 4)
)

color_entry = ttk.Entry(
    vehicle_frame,
    width=35,
    font=("Segoe UI", 10)
)

color_entry.grid(
    row=3,
    column=0,
    padx=10,
    pady=(0, 5)
)


# ============================================================
# PARKING INFORMATION CARD
# ============================================================

parking_frame = tk.LabelFrame(
    content,
    text="  🅿️ Parking Information  ",
    font=("Segoe UI", 12, "bold"),
    bg=WHITE,
    fg=TEXT,
    bd=1,
    relief=tk.SOLID,
    padx=20,
    pady=15
)

parking_frame.pack(
    fill=tk.X,
    pady=8
)


tk.Label(
    parking_frame,
    text="Parking Slot *",
    font=("Segoe UI", 10, "bold"),
    bg=WHITE,
    fg=TEXT
).grid(
    row=0,
    column=0,
    sticky="w",
    padx=10,
    pady=(5, 4)
)

slot_combo = ttk.Combobox(
    parking_frame,
    values=[
        f"Slot {i}"
        for i in range(1, 65)
    ],
    width=30,
    state="readonly",
    font=("Segoe UI", 10)
)

slot_combo.grid(
    row=1,
    column=0,
    padx=10,
    pady=(0, 5)
)


# Registration time

tk.Label(
    parking_frame,
    text="Registration Time",
    font=("Segoe UI", 10, "bold"),
    bg=WHITE,
    fg=TEXT
).grid(
    row=0,
    column=1,
    sticky="w",
    padx=10,
    pady=(5, 4)
)

time_text = datetime.now().strftime(
    "%d %B %Y"
)

tk.Label(
    parking_frame,
    text=time_text,
    font=("Segoe UI", 10),
    bg=WHITE,
    fg=MUTED
).grid(
    row=1,
    column=1,
    sticky="w",
    padx=10
)


# ============================================================
# BUTTONS
# ============================================================

button_frame = tk.Frame(
    content,
    bg=BG
)

button_frame.pack(
    fill=tk.X,
    pady=20
)


# Register

register_button = tk.Button(
    button_frame,
    text="  ✓  REGISTER VEHICLE  ",
    command=register_vehicle,
    font=("Segoe UI", 11, "bold"),
    bg=PRIMARY,
    fg=WHITE,
    activebackground=PRIMARY_HOVER,
    activeforeground=WHITE,
    relief=tk.FLAT,
    cursor="hand2",
    padx=15,
    pady=10
)

register_button.pack(
    side=tk.LEFT,
    padx=(0, 10)
)

button_hover(
    register_button,
    PRIMARY,
    PRIMARY_HOVER
)


# Clear

clear_button = tk.Button(
    button_frame,
    text="  ↻  CLEAR FORM  ",
    command=clear_form,
    font=("Segoe UI", 11, "bold"),
    bg=WHITE,
    fg=TEXT,
    activebackground="#E5E7EB",
    relief=tk.SOLID,
    bd=1,
    cursor="hand2",
    padx=15,
    pady=9
)

clear_button.pack(
    side=tk.LEFT,
    padx=10
)


# View Vehicles

view_button = tk.Button(
    button_frame,
    text="  ☷  REGISTERED VEHICLES  ",
    command=view_vehicles,
    font=("Segoe UI", 11, "bold"),
    bg=DARK,
    fg=WHITE,
    activebackground="#111827",
    activeforeground=WHITE,
    relief=tk.FLAT,
    cursor="hand2",
    padx=15,
    pady=10
)

view_button.pack(
    side=tk.LEFT,
    padx=10
)


# ============================================================
# STATUS BAR
# ============================================================

status_frame = tk.Frame(
    root,
    bg=WHITE,
    height=45
)

status_frame.pack(
    fill=tk.X,
    side=tk.BOTTOM
)

status_label = tk.Label(
    status_frame,
    text="Ready for new vehicle registration",
    font=("Segoe UI", 9),
    bg=WHITE,
    fg=MUTED
)

status_label.pack(
    side=tk.LEFT,
    padx=25,
    pady=12
)

tk.Label(
    status_frame,
    text="Parking Management System",
    font=("Segoe UI", 9),
    bg=WHITE,
    fg=MUTED
).pack(
    side=tk.RIGHT,
    padx=25
)


# ============================================================
# INITIAL FOCUS
# ============================================================

owner_entry.focus()


# ============================================================
# START APPLICATION
# ============================================================

root.mainloop()
