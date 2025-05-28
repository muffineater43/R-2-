import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

# --- Page config ---
st.set_page_config(page_title="R² PDF Dashboard", layout="wide")
st.title("R² PDF Dashboard")

# --- Sidebar ---
st.sidebar.header("Inputs")
uploaded_files = st.sidebar.file_uploader(
    "Upload Excel files (.xlsx)", 
    type=["xlsx"], 
    accept_multiple_files=True
)
val_input = st.sidebar.text_input(
    "Enter date_value (e.g. 300 or 2024-12-15)"
)
analyze = st.sidebar.button("Analyze")

if analyze:
    if not uploaded_files:
        st.error("Please upload at least one Excel file.")
    elif not val_input:
        st.error("Please enter a date_value to analyze.")
    else:
        # Interpret input
        try:
            key = int(val_input)
        except ValueError:
            key = val_input
        
        # Gather all matching r2_rolling
        vals = []
        for file in uploaded_files:
            try:
                df = pd.read_excel(file, engine="openpyxl")
            except Exception as e:
                st.warning(f"Could not read {file.name}: {e}")
                continue
            
            if "date_value" not in df.columns or "r2_rolling" not in df.columns:
                st.warning(f"{file.name} missing required columns.")
                continue
            
            df = df.set_index("date_value")
            if key in df.index:
                series = df.loc[key, "r2_rolling"]
                if isinstance(series, pd.Series):
                    vals.extend(series.dropna().tolist())
                elif pd.notna(series):
                    vals.append(series)
        
        if not vals:
            st.warning(f"No r2_rolling values found for date_value = {key!r}")
        else:
            arr = np.array(vals, dtype=float)
            mu = arr.mean()
            sigma = arr.std(ddof=1)
            
            # Plot PDF
            x = np.linspace(mu - 4*sigma, mu + 4*sigma, 200)
            y = norm.pdf(x, mu, sigma)
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(x, y, lw=2)
            ax.set_title(f"PDF of r2_rolling for date_value = {key}")
            ax.set_xlabel("r2_rolling")
            ax.set_ylabel("Density")
            ax.grid(True)
            st.pyplot(fig)
            
            # Display stats
            st.markdown(f"**Samples:** {len(arr)}")
            st.markdown(f"**Mean (μ):** {mu:.4f}")
            st.markdown(f"**Std Dev (σ):** {sigma:.4f}")



