import tkinter as tk
from tkinter import ttk

def update_from_hex(event=None):
    try:
        dec = int(hex_var.get(), 16)
        dec_var.set(str(dec))
    except:
        dec_var.set("")

def update_from_dec(event=None):
    try:
        hex_val = hex(int(dec_var.get()))
        hex_var.set(hex_val)
    except:
        hex_var.set("")

def toggle_shift_count_visibility(*args):
    op = op_var.get()
    if op in ["A << B", "A >> B"]:
        shift_frame.grid()
    else:
        shift_frame.grid_remove()

def calculate_bitwise():
    try:
        a = int(bit_a.get(), 0)
        op = op_var.get()

        if op in ["A << B", "A >> B"]:
            count = int(shift_count.get(), 0)
        else:
            b = int(bit_b.get(), 0)

        if op == "AND":
            result = a & b
        elif op == "OR":
            result = a | b
        elif op == "XOR":
            result = a ^ b
        elif op == "NOT A":
            result = ~a
        elif op == "A << B":
            result = a << count
        elif op == "A >> B":
            result = a >> count
        else:
            result = 0

        dec_result_label.result_text = str(result)
        hex_result_label.result_text = hex(result)

        dec_result_label.config(text=f"Decimal: {dec_result_label.result_text}")
        hex_result_label.config(text=f"Hex: {hex_result_label.result_text}")
    except Exception:
        dec_result_label.config(text="Decimal: Error")
        hex_result_label.config(text="Hex: Error")
        dec_result_label.result_text = ""
        hex_result_label.result_text = ""

def copy_label_result(label):
    text = getattr(label, "result_text", "")
    if text:
        root.clipboard_clear()
        root.clipboard_append(text)
        original = label.cget("text")
        label.config(text="Copied!")
        root.after(1000, lambda: label.config(text=f"{'Decimal' if 'Decimal' in original else 'Hex'}: {text}"))

root = tk.Tk()
root.title("Hex/Bitwise Tool")
root.attributes("-topmost", True)
root.resizable(False, False)

frame = ttk.Frame(root, padding=10)
frame.grid()

ttk.Label(frame, text="Hex:").grid(column=0, row=0, sticky="e")
hex_var = tk.StringVar()
hex_entry = ttk.Entry(frame, textvariable=hex_var, width=20)
hex_entry.grid(column=1, row=0)
hex_entry.bind("<KeyRelease>", update_from_hex)

ttk.Label(frame, text="Dec:").grid(column=0, row=1, sticky="e")
dec_var = tk.StringVar()
dec_entry = ttk.Entry(frame, textvariable=dec_var, width=20)
dec_entry.grid(column=1, row=1)
dec_entry.bind("<KeyRelease>", update_from_dec)

ttk.Separator(frame, orient="horizontal").grid(columnspan=2, pady=10, sticky="ew")

ttk.Label(frame, text="A:").grid(column=0, row=2, sticky="e")
bit_a = tk.StringVar()
ttk.Entry(frame, textvariable=bit_a, width=20).grid(column=1, row=2)

ttk.Label(frame, text="B:").grid(column=0, row=3, sticky="e")
bit_b = tk.StringVar()
ttk.Entry(frame, textvariable=bit_b, width=20).grid(column=1, row=3)

op_var = tk.StringVar(value="AND")
ops = ["AND", "OR", "XOR", "NOT A", "A << B", "A >> B"]
op_menu = ttk.OptionMenu(frame, op_var, ops[0], *ops)
op_menu.grid(column=0, row=4, columnspan=2, pady=5)
op_var.trace_add("write", toggle_shift_count_visibility)

shift_frame = ttk.Frame(frame)
ttk.Label(shift_frame, text="Shift count:").grid(column=0, row=0, sticky="e")
shift_count = tk.StringVar(value="1")
ttk.Entry(shift_frame, textvariable=shift_count, width=10).grid(column=1, row=0)
shift_frame.grid(column=0, row=5, columnspan=2)
shift_frame.grid_remove()

ttk.Button(frame, text="Calculate", command=calculate_bitwise).grid(column=0, row=6, columnspan=2)

dec_result_label = ttk.Label(frame, text="Decimal: ", foreground="blue", cursor="hand2")
dec_result_label.grid(column=0, row=7, columnspan=2, pady=2)
dec_result_label.result_text = ""
dec_result_label.bind("<Button-1>", lambda e: copy_label_result(dec_result_label))

hex_result_label = ttk.Label(frame, text="Hex: ", foreground="purple", cursor="hand2")
hex_result_label.grid(column=0, row=8, columnspan=2, pady=2)
hex_result_label.result_text = ""
hex_result_label.bind("<Button-1>", lambda e: copy_label_result(hex_result_label))

hex_var.set("0xFF")
update_from_hex()
bit_a.set("0xF0")
bit_b.set("0x0F")
calculate_bitwise()

root.mainloop()
