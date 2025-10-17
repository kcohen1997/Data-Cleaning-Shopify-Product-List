# Import packages
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd

# Set variant fields
VARIANT_FIELDS = [
    "Handle",
    "Option1 Value",
    "Option2 Value",
    "Option3 Value",
    "Variant SKU",
    "Variant Grams",
    "Variant Inventory Tracker",
    "Variant Inventory Qty",
    "Variant Inventory Policy",
    "Variant Fulfillment Service",
    "Variant Price",
    "Variant Compare At Price",
    "Variant Requires Shipping",
    "Variant Taxable",
    "Variant Barcode",
    "Image Src",
    "Image Position",
    "Image Alt Text",
    "Variant Image",
    "Variant Weight Unit",
    "Variant Tax Code"
]

# Clean up CSV file
def process_csv(file_path):
    df = pd.read_csv(file_path)

    # Add missing required fields
    for field in VARIANT_FIELDS:
        if field not in df.columns:
            df[field] = pd.NA

    # Forward fill non-variant fields
    non_variant_fields = [col for col in df.columns if col not in VARIANT_FIELDS and col != "Full Title"]
    if "Handle" in df.columns:
        df[non_variant_fields] = df.groupby("Handle")[non_variant_fields].ffill()
    else:
        df[non_variant_fields] = df[non_variant_fields].ffill()

    # Generate Full Title
    def build_full_title(row):
        parts = [row.get("Title", ""), row.get("Option1 Value", ""), row.get("Option2 Value", ""), row.get("Option3 Value", "")]
        return " - ".join([str(p).strip() for p in parts if pd.notna(p) and str(p).strip() != ""])

    df["Full Title"] = df.apply(build_full_title, axis=1)

    # Move Full Title to second column
    cols = df.columns.tolist()
    if "Full Title" in cols:
        cols.insert(1, cols.pop(cols.index("Full Title")))
        df = df[cols]

    # Drop completely empty columns
    df = df.dropna(axis=1, how='all')
    df = df.loc[:, ~(df == "").all()]

    # Replace blanks and NaNs with 'N/A'
    df = df.fillna("N/A")
    df.replace("", "N/A", inplace=True)

    return df

# Store processed DataFrame
processed_df = None

# Upload/Process File
def upload_file():
    global processed_df

    # Upload file (must be CSV)
    file_path = filedialog.askopenfilename(
        title="Select a CSV File",
        filetypes=(("CSV Files", "*.csv"),)
    )

    if not file_path:
        return

    # If successful, display message saying that CSV has been processed successfully
    try:
        processed_df = process_csv(file_path)
        save_button.config(state=tk.NORMAL)
        messagebox.showinfo("Success", "CSV processed successfully. Click 'Save CSV' to export it.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred:\n{e}")

# Save File Button
def save_file():
    if processed_df is None:
        messagebox.showwarning("No Data", "Please upload and process a CSV first.")
        return

    # Save File
    save_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
        title="Save Processed CSV"
    )

    # If successful, display message box saying that CSV file has been saved successfully
    if save_path:
        try:
            processed_df.to_csv(save_path, index=False)
            messagebox.showinfo("Saved", "CSV file saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save CSV:\n{e}")

# GUI Setup
root = tk.Tk()
root.title("CSV Shopify Product File Conversion")
root.geometry("450x200")

label = tk.Label(root, text="Upload a CSV file in order to clean it up", wraplength=400)
label.pack(pady=20)

upload_button = tk.Button(root, text="Upload CSV", command=upload_file)
upload_button.pack(pady=10)

save_button = tk.Button(root, text="Save CSV", command=save_file, state=tk.DISABLED)
save_button.pack(pady=5)

root.mainloop()
