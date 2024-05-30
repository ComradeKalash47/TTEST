import tkinter as tk
from tkinter import ttk, filedialog, messagebox, StringVar, Toplevel, Listbox, MULTIPLE, Scrollbar
import os
import xml.etree.ElementTree as ET
import json

def validate_inputs(entries):
    for entry in entries:
        try:
            value = int(entry.get())
            if value < -1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid input", f"Please enter a valid number for {entry.get()} (>= -1)")
            return False
    return True

def validate_non_empty(entry, entry_name):
    if entry.get().strip() == "":
        messagebox.showerror("Input Error", f"{entry_name} cannot be empty.")
        return False
    return True

def generate_types_xml(type_names, nominal, lifetime, restock, min_entry, quantmin, quantmax, cost, flags, categories, usages, values, output_file, status_label, progress):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<types>\n')
        total = len(type_names)
        for idx, type_name in enumerate(type_names):
            f.write(f'    <type name="{type_name}">\n')
            f.write(f'        <nominal>{nominal.get()}</nominal>\n')
            f.write(f'        <lifetime>{lifetime.get()}</lifetime>\n')
            f.write(f'        <restock>{restock.get()}</restock>\n')
            f.write(f'        <min>{min_entry.get()}</min>\n')
            f.write(f'        <quantmin>{quantmin.get()}</quantmin>\n')
            f.write(f'        <quantmax>{quantmax.get()}</quantmax>\n')
            f.write(f'        <cost>{cost.get()}</cost>\n')
            f.write(f'        <flags count_in_cargo="{flags["count_in_cargo"].get()}" count_in_hoarder="{flags["count_in_hoarder"].get()}" count_in_map="{flags["count_in_map"].get()}" count_in_player="{flags["count_in_player"].get()}" crafted="{flags["crafted"].get()}" deloot="{flags["deloot"].get()}"/>\n')
            
            for category in categories:
                f.write(f'        <category name="{category}"/>\n')
            for usage in usages:
                f.write(f'        <usage name="{usage}"/>\n')
            for value in values:
                f.write(f'        <value name="{value}"/>\n')

            f.write('    </type>\n')
            progress['value'] = (idx + 1) / total * 100
            root.update_idletasks()
        f.write('</types>\n')
    status_label.config(text=f"Generated types.xml successfully at {output_file}")

def select_file_for_generation(nominal, lifetime, restock, min_entry, quantmin, quantmax, cost, flags, categories, usages, values, status_label, progress):
    input_file = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if input_file:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read().replace(",", " ").replace("\n", " ")
            type_names = content.split()
        output_file = filedialog.asksaveasfilename(defaultextension=".xml", filetypes=[("XML files", "*.xml")], initialfile="types.xml")
        if output_file:
            if validate_inputs([nominal, lifetime, restock, min_entry, quantmin, quantmax, cost] + list(flags.values())):
                generate_types_xml(type_names, nominal, lifetime, restock, min_entry, quantmin, quantmax, cost, flags, categories, usages, values, output_file, status_label, progress)
            else:
                status_label.config(text="Invalid input detected. Please check your entries.")
        else:
            status_label.config(text="Output file selection cancelled.")
    else:
        status_label.config(text="Input file selection cancelled.")

def show_help():
    help_text = """Instructions:
1. Enter the values for Nominal, Lifetime, Restock, Min, Quantmin, Quantmax, Cost, and Flags.
2. Enter values for Category, Usage, and Value.
3. Click the 'Select Input File' button to choose a text file containing type names. Each type name should be separated by spaces, commas, or new lines.
4. Click the 'Generate XML' button to create the types.xml file. You will be prompted to choose the save location.
5. To edit an existing types.xml file, click 'Load XML File', search for the type name, edit the values, and click 'Save Changes'.
6. To generate an Expansion Trader JSON file, click 'Generate Expansion Trader', fill in the details and click 'Generate'. The JSON file will be saved at the specified location.
7. To edit an existing JSON file, click 'Open JSON Editor', select the file, make your changes, and save."""
    help_window = tk.Toplevel()
    help_window.title("Help")
    help_label = ttk.Label(help_window, text=help_text, wraplength=400, padding=20)
    help_label.pack()

def save_settings(entries, flags):
    settings = {entry[0]: entry[1].get() for entry in entries}
    flag_settings = {flag: flags[flag].get() for flag in flags}
    settings.update(flag_settings)
    with open("settings.txt", "w") as f:
        f.write(str(settings))
    messagebox.showinfo("Settings Saved", "Settings have been saved successfully.")

def load_settings(entries, flags):
    if os.path.exists("settings.txt"):
        with open("settings.txt", "r") as f:
            settings = eval(f.read())
            for entry in entries:
                entry[1].delete(0, tk.END)
                entry[1].insert(0, settings.get(entry[0], ""))
            for flag in flags:
                flags[flag].delete(0, tk.END)
                flags[flag].insert(0, settings.get(flag, "0"))
        messagebox.showinfo("Settings Loaded", "Settings have been loaded successfully.")
    else:
        messagebox.showwarning("No Settings Found", "No saved settings found.")

def load_xml_file(entries, flags, categories, usages, values, search_entry, status_label):
    global tree, root_element, xml_file
    xml_file = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
    if xml_file:
        try:
            tree = ET.parse(xml_file)
            root_element = tree.getroot()
            type_names = [type_elem.get('name') for type_elem in root_element.findall('type')]
            search_entry['values'] = type_names
            status_label.config(text=f"Loaded XML file: {os.path.basename(xml_file)}")
        except ET.ParseError as e:
            messagebox.showerror("Parse Error", f"Failed to parse XML file: {e}")
    else:
        status_label.config(text="XML file loading cancelled.")

def update_search_suggestions(entries, flags, categories, usages, values, search_entry, status_label):
    search_text = search_entry.get().lower()
    suggestions = [type_elem.get('name') for type_elem in root_element.findall('type') if search_text in type_elem.get('name').lower()]
    search_entry['values'] = suggestions

def search_type(entries, flags, categories, usages, values, search_entry):
    type_name = search_entry.get()
    type_elem = root_element.find(f"./type[@name='{type_name}']")
    if type_elem is not None:
        for entry in entries:
            xml_value = type_elem.find(entry[0].lower()).text if type_elem.find(entry[0].lower()) is not None else ""
            entry[1].delete(0, tk.END)
            entry[1].insert(0, xml_value)

        for flag in flags:
            flag_value = type_elem.find('flags').get(flag) if type_elem.find('flags') is not None else ""
            flags[flag].delete(0, tk.END)
            flags[flag].insert(0, flag_value)

        categories.clear()
        for category_elem in type_elem.findall('category'):
            categories.append(category_elem.get('name'))

        usages.clear()
        for usage_elem in type_elem.findall('usage'):
            usages.append(usage_elem.get('name'))

        values.clear()
        for value_elem in type_elem.findall('value'):
            values.append(value_elem.get('name'))

    else:
        messagebox.showerror("Type Not Found", f"Type '{type_name}' not found in the XML file.")

def save_changes_to_xml(entries, flags, categories, usages, values, search_entry, status_label):
    type_name = search_entry.get()
    type_elem = root_element.find(f"./type[@name='{type_name}']")
    if type_elem is not None:
        for entry in entries:
            elem = type_elem.find(entry[0].lower())
            if elem is not None:
                elem.text = entry[1].get()
        
        flags_elem = type_elem.find('flags')
        for
flag in flags:
            flags_elem.set(flag, flags[flag].get())

        # Clear existing categories, usages, and values
        for category_elem in type_elem.findall('category'):
            type_elem.remove(category_elem)
        for usage_elem in type_elem.findall('usage'):
            type_elem.remove(usage_elem)
        for value_elem in type_elem.findall('value'):
            type_elem.remove(value_elem)

        # Add new categories, usages, and values
        for category in categories:
            category_elem = ET.SubElement(type_elem, 'category')
            category_elem.set('name', category)

        for usage in usages:
            usage_elem = ET.SubElement(type_elem, 'usage')
            usage_elem.set('name', usage)

        for value in values:
            if value:
                value_elem = ET.SubElement(type_elem, 'value')
                value_elem.set('name', value)

        tree.write(xml_file, encoding='utf-8', xml_declaration=True)
        status_label.config(text=f"Changes saved to {os.path.basename(xml_file)}")
    else:
        messagebox.showerror("Type Not Found", f"Type '{type_name}' not found in the XML file.")

def generate_trader_json(display_name, icon, color, init_stock_percent, types_file):
    try:
        tree = ET.parse(types_file)
        root = tree.getroot()
        items = []
        for type_elem in root.findall('type'):
            item = {
                "ClassName": type_elem.get('name'),
                "MaxPriceThreshold": 1000,
                "MinPriceThreshold": 500,
                "SellPricePercent": -1,
                "MaxStockThreshold": 50,
                "MinStockThreshold": 10,
                "QuantityPercent": -1,
                "SpawnAttachments": [],
                "Variants": []
            }
            items.append(item)

        data = {
            "m_Version": 8,
            "DisplayName": display_name.get(),
            "Icon": icon.get(),
            "Color": color.get(),
            "InitStockPercent": int(init_stock_percent.get()),
            "Items": items
        }
        
        output_file = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")], initialfile="trader.json")
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            messagebox.showinfo("Success", f"Generated trader JSON successfully at {output_file}")
        else:
            messagebox.showwarning("Cancelled", "JSON file saving cancelled.")
    except ET.ParseError as e:
        messagebox.showerror("Parse Error", f"Failed to parse types.xml file: {e}")
    except ValueError as e:
        messagebox.showerror("Value Error", f"Invalid value: {e}")

def show_trader_generator():
    for widget in root.winfo_children():
        widget.destroy()

    main_frame = ttk.Frame(root, padding=(20, 10))
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    entry_frame = ttk.LabelFrame(main_frame, text="Trader Category", padding=(10, 5))
    entry_frame.grid(row=0, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))

    display_name_label = ttk.Label(entry_frame, text="Display Name:")
    display_name_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
    display_name_entry = ttk.Entry(entry_frame, width=40)
    display_name_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
    display_name_entry.insert(0, "My Category Title !")

    icon_label = ttk.Label(entry_frame, text="Icon:")
    icon_label.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
    icon_entry = ttk.Entry(entry_frame, width=40)
    icon_entry.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
    icon_entry.insert(0, "Deliver")

    color_label = ttk.Label(entry_frame, text="Color:")
    color_label.grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
    color_entry = ttk.Entry(entry_frame, width=40)
    color_entry.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)
    color_entry.insert(0, "FBFCFEFF")

    init_stock_percent_label = ttk.Label(entry_frame, text="Init Stock Percent:")
    init_stock_percent_label.grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
    init_stock_percent_entry = ttk.Entry(entry_frame, width=40)
    init_stock_percent_entry.grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)
    init_stock_percent_entry.insert(0, "75")

    file_frame = ttk.Frame(main_frame, padding=(10, 5))
    file_frame.grid(row=1, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))

    types_file_label = ttk.Label(file_frame, text="Select types.xml File:")
    types_file_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
    types_file_button = ttk.Button(file_frame, text="Browse", command=lambda: select_types_file(types_file_entry))
    types_file_button.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
    types_file_entry = ttk.Entry(file_frame, width=40)
    types_file_entry.grid(row=0, column=2, padx=10, pady=5, sticky=tk.W)

    button_frame = ttk.Frame(main_frame, padding=(10, 5))
    button_frame.grid(row=2, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))

    generate_button = ttk.Button(button_frame, text="Generate JSON", command=lambda: generate_trader_json(display_name_entry, icon_entry, color_entry, init_stock_percent_entry, types_file_entry.get()))
    generate_button.grid(row=0, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))

    help_button = ttk.Button(button_frame, text="Help", command=show_help)
    help_button.grid(row=1, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))

    back_button = ttk.Button(button_frame, text="Back to Menu", command=show_main_menu)
    back_button.grid(row=2, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))

def select_types_file(entry):
    types_file = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
    if types_file:
        entry.delete(0, tk.END)
        entry.insert(0, types_file)

def load_json_file(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json_file(json_file, data):
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def show_json_editor():
    json_file = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if json_file:
        data = load_json_file(json_file)
        class_names = [item["ClassName"] for item in data["Items"]]

        editor_window = tk.Toplevel()
        editor_window.title("JSON Editor")

        main_frame = ttk.Frame(editor_window, padding=(20, 10))
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        entry_frame = ttk.LabelFrame(main_frame, text="Trader Category", padding=(10, 5))
        entry_frame.grid(row=0, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))

        display_name_label = ttk.Label(entry_frame, text="Display Name:")
        display_name_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        display_name_entry = ttk.Entry(entry_frame, width=40)
        display_name_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        display_name_entry.insert(0, data["DisplayName"])

        icon_label = ttk.Label(entry_frame, text="Icon:")
        icon_label.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        icon_entry = ttk.Entry(entry_frame, width=40)
        icon_entry.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
        icon_entry.insert(0, data["Icon"])

        color_label = ttk.Label(entry_frame, text="Color:")
        color_label.grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        color_entry = ttk.Entry(entry_frame, width=40)
        color_entry.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)
        color_entry.insert(0, data["Color"])

        init_stock_percent_label = ttk.Label(entry_frame, text="Init Stock Percent:")
        init_stock_percent_label.grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        init_stock_percent_entry = ttk.Entry(entry_frame,

 width=40)
        init_stock_percent_entry.grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)
        init_stock_percent_entry.insert(0, str(data["InitStockPercent"]))

        item_frame = ttk.LabelFrame(main_frame, text="Item", padding=(10, 5))
        item_frame.grid(row=1, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))

        class_name_label = ttk.Label(item_frame, text="ClassName:")
        class_name_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        class_name_combobox = ttk.Combobox(item_frame, values=class_names, width=37)
        class_name_combobox.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        class_name_combobox.set(class_names[0])

        max_price_label = ttk.Label(item_frame, text="MaxPriceThreshold:")
        max_price_label.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        max_price_entry = ttk.Entry(item_frame, width=10)
        max_price_entry.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
        max_price_entry.insert(0, str(data["Items"][0]["MaxPriceThreshold"]))

        min_price_label = ttk.Label(item_frame, text="MinPriceThreshold:")
        min_price_label.grid(row=1, column=2, padx=10, pady=5, sticky=tk.W)
        min_price_entry = ttk.Entry(item_frame, width=10)
        min_price_entry.grid(row=1, column=3, padx=10, pady=5, sticky=tk.W)
        min_price_entry.insert(0, str(data["Items"][0]["MinPriceThreshold"]))

        sell_price_label = ttk.Label(item_frame, text="SellPricePercent:")
        sell_price_label.grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        sell_price_entry = ttk.Entry(item_frame, width=10)
        sell_price_entry.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)
        sell_price_entry.insert(0, str(data["Items"][0]["SellPricePercent"]))

        max_stock_label = ttk.Label(item_frame, text="MaxStockThreshold:")
        max_stock_label.grid(row=2, column=2, padx=10, pady=5, sticky=tk.W)
        max_stock_entry = ttk.Entry(item_frame, width=10)
        max_stock_entry.grid(row=2, column=3, padx=10, pady=5, sticky=tk.W)
        max_stock_entry.insert(0, str(data["Items"][0]["MaxStockThreshold"]))

        min_stock_label = ttk.Label(item_frame, text="MinStockThreshold:")
        min_stock_label.grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        min_stock_entry = ttk.Entry(item_frame, width=10)
        min_stock_entry.grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)
        min_stock_entry.insert(0, str(data["Items"][0]["MinStockThreshold"]))

        qty_percent_label = ttk.Label(item_frame, text="QuantityPercent:")
        qty_percent_label.grid(row=3, column=2, padx=10, pady=5, sticky=tk.W)
        qty_percent_entry = ttk.Entry(item_frame, width=10)
        qty_percent_entry.grid(row=3, column=3, padx=10, pady=5, sticky=tk.W)
        qty_percent_entry.insert(0, str(data["Items"][0]["QuantityPercent"]))

        def update_item_fields(event):
            selected_class = class_name_combobox.get()
            item = next(item for item in data["Items"] if item["ClassName"] == selected_class)
            max_price_entry.delete(0, tk.END)
            max_price_entry.insert(0, str(item["MaxPriceThreshold"]))
            min_price_entry.delete(0, tk.END)
            min_price_entry.insert(0, str(item["MinPriceThreshold"]))
            sell_price_entry.delete(0, tk.END)
            sell_price_entry.insert(0, str(item["SellPricePercent"]))
            max_stock_entry.delete(0, tk.END)
            max_stock_entry.insert(0, str(item["MaxStockThreshold"]))
            min_stock_entry.delete(0, tk.END)
            min_stock_entry.insert(0, str(item["MinStockThreshold"]))
            qty_percent_entry.delete(0, tk.END)
            qty_percent_entry.insert(0, str(item["QuantityPercent"]))

        class_name_combobox.bind("<<ComboboxSelected>>", update_item_fields)

        button_frame = ttk.Frame(main_frame, padding=(10, 5))
        button_frame.grid(row=2, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))

        def save_changes():
            data["DisplayName"] = display_name_entry.get()
            data["Icon"] = icon_entry.get()
            data["Color"] = color_entry.get()
            data["InitStockPercent"] = int(init_stock_percent_entry.get())
            
            selected_class = class_name_combobox.get()
            item = next(item for item in data["Items"] if item["ClassName"] == selected_class)
            item["MaxPriceThreshold"] = int(max_price_entry.get())
            item["MinPriceThreshold"] = int(min_price_entry.get())
            item["SellPricePercent"] = int(sell_price_entry.get())
            item["MaxStockThreshold"] = int(max_stock_entry.get())
            item["MinStockThreshold"] = int(min_stock_entry.get())
            item["QuantityPercent"] = int(qty_percent_entry.get())

            save_json_file(json_file, data)
            messagebox.showinfo("Success", "Changes saved successfully.")

        save_button = ttk.Button(button_frame, text="Save", command=save_changes)
        save_button.grid(row=0, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))

        help_button = ttk.Button(button_frame, text="Help", command=show_help)
        help_button.grid(row=1, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))

        back_button = ttk.Button(button_frame, text="Back to Menu", command=show_main_menu)
        back_button.grid(row=2, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))

def show_main_menu():
    for widget in root.winfo_children():
        widget.destroy()
    main_menu()

def main_menu():
    menu_frame = ttk.Frame(root, padding=(20, 10))
    menu_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    generator_button = ttk.Button(menu_frame, text="Open XML Generator", command=open_generator)
    generator_button.grid(row=0, column=0, padx=20, pady=20, sticky=(tk.W, tk.E))

    editor_button = ttk.Button(menu_frame, text="Open XML Editor", command=open_editor)
    editor_button.grid(row=1, column=0, padx=20, pady=20, sticky=(tk.W, tk.E))

    trader_button = ttk.Button(menu_frame, text="Generate Expansion Trader", command=show_trader_generator)
    trader_button.grid(row=2, column=0, padx=20, pady=20, sticky=(tk.W, tk.E))

    json_editor_button = ttk.Button(menu_frame, text="Open JSON Editor", command=show_json_editor)
    json_editor_button.grid(row=3, column=0, padx=20, pady=20, sticky=(tk.W, tk.E))

    bulk_edit_button = ttk.Button(menu_frame, text="Bulk Edit Types", command=show_bulk_editor)
    bulk_edit_button.grid(row=4, column=0, padx=20, pady=20, sticky=(tk.W, tk.E))

def open_generator():
    for widget in root.winfo_children():
        widget.destroy()
    generator_gui()

def open_editor():
    for widget in root.winfo_children():
        widget.destroy()
    editor_gui()

def generator_gui():
    main_frame = ttk.Frame(root, padding=(20, 10))
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    entry_frame = ttk.LabelFrame(main_frame, text="Entry Fields", padding=(10, 5))
    entry_frame.grid(row=0, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))

    entries = [
        ("Nominal", ttk.Entry(entry_frame, width=40)),
        ("Lifetime", ttk.Entry(entry_frame, width=40)),
        ("Restock", ttk.Entry(entry_frame, width=40)),
        ("Min", ttk.Entry(entry_frame, width=40)),
        ("Quantmin", ttk.Entry(entry_frame, width=40)),
        ("Quantmax", ttk.Entry(entry_frame, width=40)),
        ("Cost", ttk.Entry(entry_frame, width=40)),
    ]

    labels = ["Nominal", "Lifetime", "Restock", "Min", "Quantmin", "Quantmax", "Cost"]
    for i, (label_text, entry) in enumerate(zip(labels, entries)):
        label = ttk.Label(entry_frame, text=f"{label_text}:")
        label.grid(row=i, column=0, padx=10, pady=5, sticky=tk.W)
        entry[1].grid(row=i, column=1, padx=10, pady=5, sticky=tk.W)
        if label_text == "Quantmin":
            entry[1].insert(0, "-1")
        if label_text == "Quantmax":
            entry[1].insert(0, "-1")
        if label_text == "Cost":
            entry[1].insert(0, "100")

    flags_frame = ttk.LabelFrame(main_frame, text="Flags", padding=(10, 5))
    flags_frame.grid(row=1, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))

    flags = {
        "count_in_cargo": ttk.Entry(flags_frame, width=40),
        "count_in_hoarder": ttk.Entry(flags_frame, width=40),
        "count_in_map": ttk.Entry(flags_frame, width=40),
        "count_in_player": ttk.Entry(flags_frame, width=40),
        "crafted": ttk.Entry(flags_frame, width=40),
        "deloot": ttk.Entry(flags_frame, width=40),
    }

    flag_defaults = {
        "count_in_cargo": "0",
        "count_in_hoarder": "0",
        "count_in_map": "1",
        "count_in_player": "0",
        "crafted": "0",
        "deloot": "0",
    }

    for i, (flag, entry) in enumerate(flags.items()):
        label = ttk.Label(flags_frame, text=f"{flag.replace('_', ' ').capitalize()}:")
        label.grid(row=i, column=0, padx=10, pady=5, sticky=tk.W)
        entry.grid(row=i, column=1, padx=10, pady=5, sticky=tk.W)
        entry.insert(0, flag_defaults[flag])

    category_label = ttk.Label(main_frame, text="Categories:")
    category_label.grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
    category_entry = tk.Listbox(main_frame, selectmode=MULTIPLE, height=5)
    for category in ["Clothes", "Containers", "Explosives", "Food", "Tools", "Vehicle Parts", "Weapons"]:
        category_entry.insert(tk.END, category)
    category_entry.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)

    usage_label = ttk.Label(main_frame, text="Usages:")
    usage_label.grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
    usage_entry = tk.Listbox(main_frame, selectmode=MULTIPLE, height=5)
    for usage in ["Coast", "Farm", "Firefighter", "Hunting", "Industrial", "Medic", "Military", "Office", "Police", "Prison", "School", "Town", "Village"]:
        usage_entry.insert(tk.END, usage)
    usage_entry.grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)

    value_label = ttk.Label(main_frame, text="Values:")
    value_label.grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
    value_entry = tk.Listbox(main_frame, selectmode=MULTIPLE, height=4)
    for value in ["Tier1", "Tier2", "Tier3", "Tier4"]:
        value_entry.insert(tk.END, value)
    value_entry.grid(row=4, column=1, padx=10, pady=5, sticky=tk.W)

    button_frame = ttk.Frame(main_frame, padding=(10, 5))
    button_frame.grid(row=0, column=2, rowspan=5, padx=10, pady=10, sticky=(tk.N, tk.S))

    select_button = ttk.Button(button_frame, text="Select Input File", command=lambda: select_file_for_generation(*[entry[1] for entry in entries], flags, list(category_entry.get(0, tk.END)), list(usage_entry.get(0, tk.END)), list(value_entry.get(0, tk.END)), status_label, progress))
    select_button.grid(row=0, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))

    help_button = ttk.Button(button_frame, text="Help", command=show_help)
    help_button.grid(row=1, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))

    save_button = ttk.Button(button_frame, text="Save Settings", command=lambda: save_settings(entries, flags))
    save_button.grid(row=2, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))

    load_button = ttk.Button(button_frame, text="Load Settings", command=lambda: load_settings(entries, flags))
    load_button.grid(row=3, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))

    back_button = ttk.Button(button_frame, text="Back to Menu", command=show_main_menu)
    back_button.grid(row=4, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))

    progress = ttk.Progressbar(root, mode='determinate')
    progress.grid(row=5, column=0, padx=20, pady=10, sticky=(tk.W, tk.E))

    status_label = ttk.Label(root, text="", font=('Arial', 12))
    status_label.grid(row=6, column=0, padx=20, pady=10, sticky=(tk.W, tk.E))

def editor_gui():
    main_frame = ttk.Frame(root, padding=(20, 10))
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    entry_frame = ttk.LabelFrame(main_frame, text="Entry Fields", padding=(10, 5))
    entry_frame.grid(row=0, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))

    entries = [
        ("Nominal", ttk.Entry(entry_frame, width=40)),
        ("Lifetime", ttk.Entry(entry_frame, width=40)),
        ("Restock", ttk.Entry(entry_frame, width=40)),
        ("Min", ttk.Entry(entry_frame, width=40)),
        ("Quantmin", ttk.Entry(entry_frame, width=40)),
        ("Quantmax", ttk.Entry(entry_frame, width=40)),
        ("Cost", ttk.Entry(entry_frame, width=40)),
    ]

    labels = ["Nominal", "Lifetime", "Restock", "Min", "Quantmin", "Quantmax", "Cost"]
    for i, (label_text, entry) in enumerate(zip(labels, entries)):
        label = ttk.Label(entry_frame, text=f"{label_text}:")
        label.grid(row=i, column=0, padx=10, pady=5, sticky=tk.W)
        entry[1].grid(row=i, column=1, padx=10, pady=5, sticky=tk.W)
        if label_text == "Quantmin":
            entry[1].insert(0, "-1")
        if label_text == "Quantmax":
            entry[1].insert(0, "-1")
        if label_text == "Cost":
            entry[1].insert(0, "100")

    category_label = ttk.Label(entry_frame, text="Categories:")
    category_label.grid(row=6, column=0, padx=10, pady=5, sticky=tk.W)
    category_entry = tk.Listbox(entry_frame, selectmode=MULTIPLE, height=5)
    for category in ["Clothes", "Containers", "Explosives", "Food", "Tools", "Vehicle Parts", "Weapons"]:
        category_entry.insert(tk.END, category)
    category_entry.grid(row=6, column=1, padx=10, pady=5, sticky=tk.W)

    usage_label = ttk.Label(entry_frame, text="Usages:")
    usage_label.grid(row=7, column=0, padx=10, pady=5, sticky=tk.W)
    usage_entry = tk.Listbox(entry_frame, selectmode=MULTIPLE, height=5)
    for usage in ["Coast", "Farm", "Firefighter", "Hunting", "Industrial", "Medic", "Military", "Office", "Police", "Prison", "School", "Town", "Village"]:
        usage_entry.insert(tk.END, usage)
    usage_entry.grid(row=7, column=1, padx=10, pady=5, sticky=tk.W)

    value_label = ttk.Label(entry_frame, text="Values:")
    value_label.grid(row=8, column=0, padx=10, pady=5, sticky=tk.W)
    value_entry = tk.Listbox(entry_frame, selectmode=MULTIPLE, height=4)
    for value in ["Tier1", "Tier2", "Tier3", "Tier4"]:
        value_entry.insert(tk.END, value)
    value_entry.grid(row=8, column=1, padx=10, pady=5, sticky=tk.W)

    button_frame = ttk.Frame(main_frame, padding=(10, 5))
    button_frame.grid(row=0, column=2, rowspan=9, padx=10, pady=10, sticky=(tk.N, tk.S))

    load_xml_button = ttk.Button(button_frame, text="Load XML File", command=lambda: load_xml_file(entries, flags, list(category_entry.get(0, tk.END)), list(usage_entry.get(0, tk.END)), list(value_entry.get(0, tk.END)), search_entry, status_label))
    load_xml_button.grid(row=0, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))

    help_button = ttk.Button(button_frame, text="Help", command=show_help)
    help_button.grid(row=1, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))

    search_label = ttk.Label(main_frame, text="Search Type Name:")
    search_label.grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
    search_entry = ttk.Combobox(main_frame, width=37)
    search_entry.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)
    search_entry.bind("<KeyRelease>", lambda event: update_search_suggestions(entries, flags, list(category_entry.get(0, tk.END)), list(usage_entry.get(0, tk.END)), list(value_entry.get(0, tk.END)), search_entry, status_label))

    search_button = ttk.Button(main_frame, text="Search", command=lambda: search_type(entries, flags, list(category_entry.get(0, tk.END)), list(usage_entry.get(0, tk.END)), list(value_entry.get(0, tk.END)), search_entry))
    search_button.grid(row=2, column=2, padx=10, pady=5, sticky=tk.W)

    save_changes_button = ttk.Button(main_frame, text="Save Changes", command=lambda: save_changes_to_xml(entries, flags, list(category_entry.get(0, tk.END)), list(usage_entry.get(0, tk.END)), list(value_entry.get(0, tk.END)), search_entry, status_label))
    save_changes_button.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky=(tk.W, tk.E))

    back_button = ttk.Button(button_frame, text="Back to Menu", command=show_main_menu)
    back_button.grid(row=2, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))

    status_label = ttk.Label(root, text="", font=('Arial', 12))
    status_label.grid(row=4, column=0, padx=20, pady=10, sticky=(tk.W, tk.E))

def show_bulk_editor():
    for widget in root.winfo_children():
        widget.destroy()

    bulk_editor_window = ttk.Frame(root, padding=(20, 10))
    bulk_editor_window.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    load_xml_button = ttk.Button(bulk_editor_window, text="Load XML File", command=lambda: load_xml_file_for_bulk_edit(status_label, type_listbox))
    load_xml_button.grid(row=0, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))

    listbox_label = ttk.Label(bulk_editor_window, text="Select Types to Edit:")
    listbox_label.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)

    global type_listbox
    type_listbox = Listbox(bulk_editor_window, selectmode=MULTIPLE, width=50, height=20)
    type_listbox.grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)

    scrollbar = Scrollbar(bulk_editor_window, orient="vertical")
    scrollbar.config(command=type_listbox.yview)
    type_listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.grid(row=2, column=1, sticky='ns')

    entry_frame = ttk.LabelFrame(bulk_editor_window, text="Entry Fields", padding=(10, 5))
    entry_frame.grid(row=3, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))

    entries = [
        ("Nominal", ttk.Entry(entry_frame, width=40)),
        ("Lifetime", ttk.Entry(entry_frame, width=40)),
        ("Restock", ttk.Entry(entry_frame, width=40)),
        ("Min", ttk.Entry(entry_frame, width=40)),
        ("Quantmin", ttk.Entry(entry_frame, width=40)),
        ("Quantmax", ttk.Entry(entry_frame, width=40)),
        ("Cost", ttk.Entry(entry_frame, width=40)),
    ]

    labels = ["Nominal", "Lifetime", "Restock", "Min", "Quantmin", "Quantmax", "Cost"]
    for i, (label_text, entry) in enumerate(zip(labels, entries)):
        label = ttk.Label(entry_frame, text=f"{label_text}:")
        label.grid(row=i, column=0, padx=10, pady=5, sticky=tk.W)
        entry[1].grid(row=i, column=1, padx=10, pady=5, sticky=tk.W)
        if label_text == "Quantmin":
            entry[1].insert(0, "-1")
        if label_text == "Quantmax":
            entry[1].insert(0, "-1")
        if label_text == "Cost":
            entry[1].insert(0, "100")

    category_label = ttk.Label(entry_frame, text="Categories:")
    category_label.grid(row=8, column=0, padx=10, pady=5, sticky=tk.W)
    category_entry = tk.Listbox(entry_frame, selectmode=MULTIPLE, height=5)
    for category in ["Clothes", "Containers", "Explosives", "Food", "Tools", "Vehicle Parts", "Weapons"]:
        category_entry.insert(tk.END, category)
    category_entry.grid(row=8, column=1, padx=10, pady=5, sticky=tk.W)

    usage_label = ttk.Label(entry_frame, text="Usages:")
    usage_label.grid(row=9, column=0, padx=10, pady=5, sticky=tk.W)
    usage_entry = tk.Listbox(entry_frame, selectmode=MULTIPLE, height=5)
    for usage in ["Coast", "Farm", "Firefighter", "Hunting", "Industrial", "Medic", "Military", "Office", "Police", "Prison", "School", "Town", "Village"]:
        usage_entry.insert(tk.END, usage)
    usage_entry.grid(row=9, column=1, padx=10, pady=5, sticky=tk.W)

    value_label = ttk.Label(entry_frame, text="Values:")
    value_label.grid(row=10, column=0, padx=10, pady=5, sticky=tk.W)
    value_entry = tk.Listbox(entry_frame, selectmode=MULTIPLE, height=4)
    for value in ["Tier1", "Tier2", "Tier3", "Tier4"]:
        value_entry.insert(tk.END, value)
    value_entry.grid(row=10, column=1, padx=10, pady=5, sticky=tk.W)

    button_frame = ttk.Frame(bulk_editor_window, padding=(10, 5))
    button_frame.grid(row=4, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))

    bulk_edit_button = ttk.Button(button_frame, text="Apply Changes", command=lambda: apply_bulk_edits(entries, flags, list(category_entry.get(0, tk.END)), list(usage_entry.get(0, tk.END)),
    list(value_entry.get(0, tk.END)), type_listbox))
    bulk_edit_button.grid(row=0, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))

    back_button = ttk.Button(button_frame, text="Back to Menu", command=show_main_menu)
    back_button.grid(row=1, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))

    status_label = ttk.Label(root, text="", font=('Arial', 12))
    status_label.grid(row=5, column=0, padx=20, pady=10, sticky=(tk.W, tk.E))

def load_xml_file_for_bulk_edit(status_label, type_listbox):
    global tree, root_element, xml_file
    xml_file = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
    if xml_file:
        try:
            tree = ET.parse(xml_file)
            root_element = tree.getroot()
            type_names = [type_elem.get('name') for type_elem in root_element.findall('type')]
            type_listbox.delete(0, tk.END)
            for type_name in type_names:
                type_listbox.insert(tk.END, type_name)
            status_label.config(text=f"Loaded XML file: {os.path.basename(xml_file)}")
        except ET.ParseError as e:
            messagebox.showerror("Parse Error", f"Failed to parse XML file: {e}")
    else:
        status_label.config(text="XML file loading cancelled.")

def apply_bulk_edits(entries, flags, categories, usages, values, type_listbox):
    selected_types = [type_listbox.get(i) for i in type_listbox.curselection()]
    for type_name in selected_types:
        type_elem = root_element.find(f"./type[@name='{type_name}']")
        if type_elem is not None:
            for entry in entries:
                elem = type_elem.find(entry[0].lower())
                if elem is not None:
                    elem.text = entry[1].get()
            
            flags_elem = type_elem.find('flags')
            for flag in flags:
                flags_elem.set(flag, flags[flag].get())

            # Clear existing categories, usages, and values
            for category_elem in type_elem.findall('category'):
                type_elem.remove(category_elem)
            for usage_elem in type_elem.findall('usage'):
                type_elem.remove(usage_elem)
            for value_elem in type_elem.findall('value'):
                type_elem.remove(value_elem)

            # Add new categories, usages, and values
            for category in categories:
                category_elem = ET.SubElement(type_elem, 'category')
                category_elem.set('name', category)

            for usage in usages:
                usage_elem = ET.SubElement(type_elem, 'usage')
                usage_elem.set('name', usage)

            for value in values:
                if value:
                    value_elem = ET.SubElement(type_elem, 'value')
                    value_elem.set('name', value)

    tree.write(xml_file, encoding='utf-8', xml_declaration=True)
    messagebox.showinfo("Success", "Bulk edits applied successfully.")
    status_label.config(text=f"Changes saved to {os.path.basename(xml_file)}")

root = tk.Tk()
root.title("Types XML Tool")

main_menu()

root.mainloop()
