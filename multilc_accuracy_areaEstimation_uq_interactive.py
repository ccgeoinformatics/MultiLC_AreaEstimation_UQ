"""
Script: Multi-class Land Cover Map Accuracy Assessment, Area Estimation, and Uncertainty Quantification

Description:
    This script provides a GUI for multi-class land cover map accuracy assessment, area estimation,
    and uncertainty quantification. It calculates key metrics, including user’s accuracy, 
    producer’s accuracy, overall accuracy, and error-adjusted area estimates, along with 
    confidence intervals. The calculations are based on the methods outlined in:

    - Olofsson, P., Foody, G. M., Stehman, S. V., & Woodcock, C. E. (2013). Making better use of 
      accuracy data in land change studies: Estimating accuracy and area and quantifying 
      uncertainty using stratified estimation. Remote Sensing of Environment, 129, 122-131.
    - Olofsson, P., Foody, G. M., Herold, M., Stehman, S. V., Woodcock, C. E., & Wulder, M. A. 
      (2014). Good practices for estimating area and assessing accuracy of land change. 
      Remote Sensing of Environment, 148, 42-57.

Features:
    - GUI for inputting pixel size, error matrix, and mapped pixels.
    - Interactive tooltip hints for each input field.
    - Calculation of user’s accuracy, producer’s accuracy, overall accuracy, error-adjusted area, 
      and confidence intervals for each class.
    - Option to save results to a CSV file for further analysis.

Requirements:
    - Python 3.7 or higher
    - Libraries: numpy, pandas, scipy, tkinter

Usage:
    - Run the script in a Python environment:
      python multilc_accuracy_areaEstimation_uq_interactive.py
    - Follow the instructions in the GUI to input necessary values and run the analysis.

Author:
    Jojene R. Santillan
    Institute of Photogrammetry and GeoInformation (IPI), Leibniz University Hannover, Germany 
    & Caraga Center for Geo-Informatics & Department of Geodetic Engineering, College of Engineering 
    and Geosciences, Caraga State University, Butuan City, Philippines
    Contact: santillan@ipi.uni-hannover.de, jrsantillan@carsu.edu.ph

Date:
    November 4, 2024
"""


import numpy as np
import pandas as pd
import scipy.stats as st
import tkinter as tk
from tkinter import messagebox, filedialog

def calculate_weights(mapped_pixels):
    total_pixels = np.sum(mapped_pixels, dtype=np.float64)
    weights = mapped_pixels / total_pixels
    return weights.astype(np.float64)

def convert_to_area_proportion(error_matrix, weights):
    area_proportion_matrix = np.zeros_like(error_matrix, dtype=np.float64)
    for i in range(error_matrix.shape[0]):
        row_total = error_matrix[i, :].sum()
        area_proportion_matrix[i, :] = weights[i] * (error_matrix[i, :] / row_total) if row_total != 0 else np.nan
    return area_proportion_matrix

def calculate_accuracy_metrics(area_proportion_matrix, error_matrix, weights, confidence_level=0.95):
    q = area_proportion_matrix.shape[0]
    user_accuracy, user_accuracy_se, user_accuracy_ci_lower, user_accuracy_ci_upper, user_accuracy_ci_value = ([] for _ in range(5))
    producer_accuracy, producer_accuracy_se, producer_accuracy_ci_lower, producer_accuracy_ci_upper, producer_accuracy_ci_value = ([] for _ in range(5))

    z_score = st.norm.ppf(1 - (1 - confidence_level) / 2)

    # User's accuracy calculations
    for i in range(q):
        p_ii = area_proportion_matrix[i, i]
        p_i_dot = area_proportion_matrix[i, :].sum()
        U_i = p_ii / p_i_dot if p_i_dot != 0 else np.nan
        user_accuracy.append(U_i)
        
        n_i_dot = error_matrix[i, :].sum()
        if n_i_dot > 1:
            variance_U_i = U_i * (1 - U_i) / (n_i_dot - 1)
            se_U_i = np.sqrt(variance_U_i)
            user_accuracy_se.append(se_U_i)
            ci_lower = U_i - z_score * se_U_i
            ci_upper = U_i + z_score * se_U_i
            user_accuracy_ci_lower.append(ci_lower)
            user_accuracy_ci_upper.append(ci_upper)
            user_accuracy_ci_value.append(z_score * se_U_i)
        else:
            user_accuracy_se.append(np.nan)
            user_accuracy_ci_lower.append(np.nan)
            user_accuracy_ci_upper.append(np.nan)
            user_accuracy_ci_value.append(np.nan)

    # Producer's accuracy calculations
    for j in range(q):
        p_jj = area_proportion_matrix[j, j]
        p_dot_j = area_proportion_matrix[:, j].sum()
        P_j = p_jj / p_dot_j if p_dot_j != 0 else np.nan
        producer_accuracy.append(P_j)
        
        n_dot_j = error_matrix[:, j].sum()
        if n_dot_j > 1:
            variance_P_j = (1 / n_dot_j ** 2) * (
                (n_dot_j ** 2 * (1 - P_j) ** 2 * U_i * (1 - U_i)) / (n_i_dot - 1)
                + P_j ** 2 * sum(
                    (error_matrix[i, j] / n_i_dot) * (1 - (error_matrix[i, j] / n_i_dot)) / (n_i_dot - 1)
                    for i in range(q) if i != j
                )
            )
            se_P_j = np.sqrt(variance_P_j)
            producer_accuracy_se.append(se_P_j)
            ci_lower = P_j - z_score * se_P_j
            ci_upper = P_j + z_score * se_P_j
            producer_accuracy_ci_lower.append(ci_lower)
            producer_accuracy_ci_upper.append(ci_upper)
            producer_accuracy_ci_value.append(z_score * se_P_j)
        else:
            producer_accuracy_se.append(np.nan)
            producer_accuracy_ci_lower.append(np.nan)
            producer_accuracy_ci_upper.append(np.nan)
            producer_accuracy_ci_value.append(np.nan)

    # Overall accuracy calculations
    overall_accuracy = np.trace(area_proportion_matrix)
    overall_accuracy_variance = sum(
        weights[i] ** 2 * user_accuracy[i] * (1 - user_accuracy[i]) / (error_matrix[i, :].sum() - 1)
        for i in range(q) if error_matrix[i, :].sum() > 1
    )
    overall_accuracy_se = np.sqrt(overall_accuracy_variance)
    overall_accuracy_ci_lower = overall_accuracy - z_score * overall_accuracy_se
    overall_accuracy_ci_upper = overall_accuracy + z_score * overall_accuracy_se
    overall_accuracy_ci_value = z_score * overall_accuracy_se

    return {
        "user_accuracy": user_accuracy,
        "user_accuracy_se": user_accuracy_se,
        "user_accuracy_ci_lower": user_accuracy_ci_lower,
        "user_accuracy_ci_upper": user_accuracy_ci_upper,
        "user_accuracy_ci_value": user_accuracy_ci_value,
        "producer_accuracy": producer_accuracy,
        "producer_accuracy_se": producer_accuracy_se,
        "producer_accuracy_ci_lower": producer_accuracy_ci_lower,
        "producer_accuracy_ci_upper": producer_accuracy_ci_upper,
        "producer_accuracy_ci_value": producer_accuracy_ci_value,
        "overall_accuracy": overall_accuracy,
        "overall_accuracy_se": overall_accuracy_se,
        "overall_accuracy_ci_lower": overall_accuracy_ci_lower,
        "overall_accuracy_ci_upper": overall_accuracy_ci_upper,
        "overall_accuracy_ci_value": overall_accuracy_ci_value
    }

def calculate_error_adjusted_area(area_proportion_matrix, total_area):
    adjusted_areas = total_area * area_proportion_matrix.sum(axis=0)
    return adjusted_areas

def calculate_standard_error_and_ci(error_matrix, weights, area_adjusted_estimates, total_area, confidence_level=0.95):
    q = error_matrix.shape[0]
    standard_errors = []

    for j in range(q):
        se_j_squared = 0
        for i in range(q):
            n_ij = error_matrix[i, j]
            n_i_dot = error_matrix[i, :].sum()
            if n_i_dot > 1:
                se_j_squared += weights[i] ** 2 * (n_ij / n_i_dot) * (1 - n_ij / n_i_dot) / (n_i_dot - 1)
        standard_errors.append(np.sqrt(se_j_squared))

    area_standard_errors = [total_area * se_j for se_j in standard_errors]
    z_score = st.norm.ppf(1 - (1 - confidence_level) / 2)
    confidence_intervals = [
        (
            area_adjusted_estimates[j] - z_score * area_standard_errors[j],
            area_adjusted_estimates[j] + z_score * area_standard_errors[j]
        )
        for j in range(q)
    ]

    return {
        "standard_errors": area_standard_errors,
        "confidence_intervals": confidence_intervals
    }


# Function to run the analysis
def run_analysis():
    try:
        pixel_size = float(entry_pixel_size.get())
        error_matrix = np.zeros((num_classes, num_classes), dtype=np.float64)
        mapped_pixels = np.zeros(num_classes, dtype=np.float64)

        for i in range(num_classes):
            for j in range(num_classes):
                error_matrix[i, j] = float(error_entries[i][j].get())
            mapped_pixels[i] = float(mapped_pixel_entries[i].get())

        weights = calculate_weights(mapped_pixels)
        area_proportion_matrix = convert_to_area_proportion(error_matrix, weights)
        total_area = np.sum(mapped_pixels) * pixel_size ** 2
        accuracy_metrics = calculate_accuracy_metrics(area_proportion_matrix, error_matrix, weights)
        error_adjusted_area = calculate_error_adjusted_area(area_proportion_matrix, total_area)
        
        # Define z-score for 95% confidence level
        confidence_level = 0.95
        z_score = st.norm.ppf(1 - (1 - confidence_level) / 2)

        # Calculate SE and CI (half-width) for error-adjusted areas
        area_se_and_ci = calculate_standard_error_and_ci(
            error_matrix, weights, error_adjusted_area, total_area
        )
        area_standard_errors = area_se_and_ci["standard_errors"]
        area_ci_values = [z_score * se for se in area_standard_errors]  # CI half-widths

        # Open a new window to display results in a clearer format
        results_window = tk.Toplevel(root)
        results_window.title("Results")

        # Displaying formatted results
        results_text = tk.Text(results_window, wrap="word")
        results_text.insert("end", "User's Accuracy per Class:\n")
        for i, (ua, se, ci) in enumerate(zip(accuracy_metrics["user_accuracy"], accuracy_metrics["user_accuracy_se"], accuracy_metrics["user_accuracy_ci_value"])):
            results_text.insert("end", f"  Class {i + 1}: {ua:.4f}, SE={se:.4f}, 95% CI={ci:.4f}\n")
        
        results_text.insert("end", "\nProducer's Accuracy per Class:\n")
        for i, (pa, se, ci) in enumerate(zip(accuracy_metrics["producer_accuracy"], accuracy_metrics["producer_accuracy_se"], accuracy_metrics["producer_accuracy_ci_value"])):
            results_text.insert("end", f"  Class {i + 1}: {pa:.4f}, SE={se:.4f}, 95% CI={ci:.4f}\n")
        
        results_text.insert("end", f"\nOverall Accuracy: {accuracy_metrics['overall_accuracy']:.4f}, SE={accuracy_metrics['overall_accuracy_se']:.4f}, 95% CI={accuracy_metrics['overall_accuracy_ci_value']:.4f}\n")
        
        results_text.insert("end", "\nError-Adjusted Area per Class:\n")
        for i, (area, se, ci_value) in enumerate(zip(error_adjusted_area, area_standard_errors, area_ci_values)):
            results_text.insert("end", f"  Class {i + 1}: {area:.2f}, SE={se:.2f}, 95% CI={ci_value:.2f}\n")
        
        results_text.pack()

        # Option to save results as CSV
        def save_results():
            save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if save_path:
                # Ensure all columns have the same length
                result_data = {
                    "Class": [f"Class {i + 1}" for i in range(num_classes)],
                    "User_Accuracy": [float(ua) for ua in accuracy_metrics["user_accuracy"]],
                    "User_Accuracy_SE": [float(se) for se in accuracy_metrics["user_accuracy_se"]],
                    "User_Accuracy_95%CI": [float(ci) for ci in accuracy_metrics["user_accuracy_ci_value"]],
                    "Producer_Accuracy": [float(pa) for pa in accuracy_metrics["producer_accuracy"]],
                    "Producer_Accuracy_SE": [float(se) for se in accuracy_metrics["producer_accuracy_se"]],
                    "Producer_Accuracy_95%CI": [float(ci) for ci in accuracy_metrics["producer_accuracy_ci_value"]],
                    "Error_Adjusted_Area": [float(area) for area in error_adjusted_area],
                    "Error_Adjusted_Area_SE": [float(se) for se in area_standard_errors],
                    "Error_Adjusted_Area_95%CI_Value": [float(ci) for ci in area_ci_values]  # CI half-widths
                }
                
                # Add Overall Accuracy as a separate field, duplicated for each class row for consistency
                overall_accuracy_column = [accuracy_metrics["overall_accuracy"]] * num_classes
                overall_accuracy_se_column = [accuracy_metrics["overall_accuracy_se"]] * num_classes
                overall_accuracy_ci_column = [accuracy_metrics["overall_accuracy_ci_value"]] * num_classes
                result_data["Overall_Accuracy"] = overall_accuracy_column
                result_data["Overall_Accuracy_SE"] = overall_accuracy_se_column
                result_data["Overall_Accuracy_95%CI"] = overall_accuracy_ci_column
                
                df_result = pd.DataFrame(result_data)
                df_result.to_csv(save_path, index=False)
                messagebox.showinfo("Save Successful", f"Results saved to {save_path}")

        # Add a button in the results window to save to CSV
        tk.Button(results_window, text="Save to CSV", command=save_results).pack()

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Tooltip helper function
def create_tooltip(widget, text):
    tooltip = tk.Toplevel(widget)
    tooltip.withdraw()  # Hide initially
    tooltip.overrideredirect(True)  # Remove window decorations (e.g., title bar)
    tooltip_label = tk.Label(tooltip, text=text, background="yellow", relief="solid", borderwidth=1, font=("Arial", 8))
    tooltip_label.pack()

    def show_tooltip(event):
        tooltip.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
        tooltip.deiconify()  # Show tooltip

    def hide_tooltip(event):
        tooltip.withdraw()  # Hide tooltip

    widget.bind("<Enter>", show_tooltip)  # Show on hover
    widget.bind("<Leave>", hide_tooltip)  # Hide when not hovering

# Function to set up matrix inputs and open matrix window
def setup_matrix_inputs():
    global num_classes, entry_pixel_size, error_entries, mapped_pixel_entries
    try:
        num_classes = int(entry_classes.get())
        root.withdraw()  # Hide the initial window instead of destroying it
        
        # Open secondary window for matrix inputs
        matrix_window = tk.Toplevel()
        matrix_window.title("Enter Matrix Values and Pixel Size")

        # Instructions panel
        instructions = (
            "Instructions:\n"
            "1. Click 'Set Number of Classes' to reconfigure the matrix, or to start a new analysis.\n"
            "2. Enter pixel size in the provided field.\n"
            "3. Fill in the error matrix with counts for each class.\n"
            "4. Enter the total mapped pixels for each class in the last column.\n"
            "5. Click 'Run Analysis' to calculate metrics."
        )
        tk.Label(matrix_window, text=instructions, justify="left", wraplength=300).grid(row=0, column=0, columnspan=num_classes + 2, padx=10, pady=10)

        # Pixel size entry with tooltip
        tk.Label(matrix_window, text="Enter pixel size:").grid(row=1, column=0)
        entry_pixel_size = tk.Entry(matrix_window)
        entry_pixel_size.grid(row=1, column=1)
        create_tooltip(entry_pixel_size, "Enter the pixel size in meters (e.g., 10 for 10x10 m pixels).")

        error_entries = []
        mapped_pixel_entries = []

        # Add column headers
        for j in range(num_classes):
            label = tk.Label(matrix_window, text=f"Class {j + 1}")
            label.grid(row=2, column=j + 1)
            create_tooltip(label, f"Error matrix column for Class {j + 1}")

        # Create input fields for the error matrix and mapped pixels, with row labels
        for i in range(num_classes):
            # Row header for each class
            row_label = tk.Label(matrix_window, text=f"Class {i + 1}")
            row_label.grid(row=i + 3, column=0)
            create_tooltip(row_label, f"Error matrix row for Class {i + 1}")

            row_entries = []
            for j in range(num_classes):
                entry = tk.Entry(matrix_window, width=5)
                entry.grid(row=i + 3, column=j + 1)
                create_tooltip(entry, f"Enter count for Class {i + 1} vs. Class {j + 1}")
                row_entries.append(entry)
            error_entries.append(row_entries)
            
            # Mapped pixel entries (additional column)
            mapped_entry = tk.Entry(matrix_window, width=10)
            mapped_entry.grid(row=i + 3, column=num_classes + 1)
            create_tooltip(mapped_entry, f"Enter total mapped pixels for Class {i + 1}")
            mapped_pixel_entries.append(mapped_entry)

        # Label the column for mapped pixels
        tk.Label(matrix_window, text="Mapped Pixels").grid(row=2, column=num_classes + 1)

        # Add a button to run the analysis
        tk.Button(matrix_window, text="Run Analysis", command=run_analysis).grid(row=num_classes + 4, column=0, columnspan=num_classes + 2)
        
        # Add a button to set a new number of classes
        def set_new_classes():
            matrix_window.destroy()
            root.deiconify()  # Show the initial window again to reset classes

        tk.Button(matrix_window, text="Set New Number of Classes", command=set_new_classes).grid(row=num_classes + 5, column=0, columnspan=num_classes + 2)
        
        # Add a button to exit the application
        tk.Button(matrix_window, text="Exit", command=lambda: (matrix_window.destroy(), root.destroy())).grid(row=num_classes + 6, column=0, columnspan=num_classes + 2)

    except ValueError:
        messagebox.showerror("Input Error", "Please enter a valid number of classes.")
		
# Initial window to set the number of classes
root = tk.Tk()
root.title("Land Cover Map Accuracy Assessment, Area Estimation, and Uncertainty Quantification")

tk.Label(root, text="Enter number of classes:").pack()
entry_classes = tk.Entry(root)
entry_classes.pack()
tk.Button(root, text="Set Number of Classes", command=setup_matrix_inputs).pack()

root.mainloop()
