import streamlit as st
import json
import os
import streamlit.components.v1 as components

# --- SYSTEM AUTO-ADAPTIVE CONFIGURATION ---
st.set_page_config(
    page_title="TG EAPCET Predictor Pro", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- GLOBAL PURE WHITE TEXT OVERRIDE ---
st.markdown(
    """
    <style>
    /* Force ALL text, headings, labels, captions, and widget values to pure white */
    html, body, .stApp, *, p, span, label, h1, h2, h3, h4, h5, h6, small, div, .stCaption, .stText {
        color: #FFFFFF !important;
    }
    
    /* Ensure selection item containers inside dropdowns display white text */
    div[data-baseweb="select"] *, div[data-baseweb="input"] *, input {
        color: #FFFFFF !important;
    }

    /* Keep dropdown options and inputs readable by styling their layout structure borders */
    div[data-baseweb="select"], div[data-baseweb="input"] {
        border-radius: 8px !important;
        border: 1px solid #cbd5e1 !important;
    }
    
    /* Make the separating horizontal lines distinct */
    hr {
        border-color: #ffffff !important;
        opacity: 0.4;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("TG EAPCET Seat Allotment Predictor")
st.caption("Universal Category Matching Engine — Configured for Pure White Text.")

# --- UI INPUT CONTROLS ---
st.subheader("Predictor Parameters")
col1, col2, col3, col4 = st.columns(4)

with col1:
    phase_choice = st.selectbox(
        "Counseling Phase",
        ["Phase 1 Allotments", "Phase 2 Allotments", "Final Phase Allotments"]
    )

with col2:
    user_rank = st.number_input("Your EAPCET Rank", min_value=1, value=40000, step=1)

with col3:
    caste = st.selectbox(
        "Your Category", 
        ["OC", "BC_A", "BC_B", "BC_C", "BC_D", "BC_E", "SC_I", "SC_II", "SC_III", "ST", "EWS"]
    )

with col4:
    gender = st.selectbox("Gender", ["BOYS", "GIRLS"])

col_b1, col_b2 = st.columns(2)

with col_b1:
    branch_choice = st.selectbox(
        "Target Discipline / Branch",
        ["ALL BRANCHES", "CSE", "ECE", "EEE", "INF", "CSM", "CSD", "CIV", "MEC", "AI", "DS"]
    )

with col_b2:
    college_type_filter = st.selectbox(
        "Institutional Profile",
        ["All Institutions (Co-Ed & Women)", "Women's Only Colleges"]
    )

file_map = {
    "Phase 1 Allotments": "src/data/phase1.json",
    "Phase 2 Allotments": "src/data/phase2.json",
    "Final Phase Allotments": "src/data/finalPhase.json"
}
json_path = file_map[phase_choice]

if os.path.exists(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    filtered_results = []
    
    for item in data:
        if not item:
            continue
            
        # --- ROBUST KEY NORMALIZATION ENGINE ---
        clean_item = {}
        for k, v in item.items():
            normalized_key = str(k).upper().strip().replace(" ", "_")
            while "__" in normalized_key:
                normalized_key = normalized_key.replace("__", "_")
            clean_item[normalized_key] = v
            
        inst_code = str(clean_item.get("INST_CODE", clean_item.get("CODE", "UNKNOWN"))).strip()
        inst_name_full = str(clean_item.get("INST_NAME", "Unknown Institution")).strip()
        place = str(clean_item.get("PLACE", "")).strip()
        dist_code = str(clean_item.get("DIST_CODE", "")).strip()
        branch_code = str(clean_item.get("BRANCH_CODE", "")).strip()
        co_education = str(clean_item.get("CO_EDUCATION", "COED")).strip().upper()
        
        target_key = f"{caste.upper()}_{gender.upper()}"
        raw_cutoff = clean_item.get(target_key, None)
        
        if raw_cutoff is None:
            space_key = f"{caste.upper()} {gender.upper()}"
            raw_cutoff = item.get(space_key, None)
            
        try:
            cutoff_rank = int(str(raw_cutoff).replace(',', '').strip())
        except (ValueError, TypeError):
            cutoff_rank = 0

        # --- SELECTION FILTERS ---
        if cutoff_rank > 0 and cutoff_rank != 999999:
            if branch_choice != "ALL BRANCHES" and branch_choice != branch_code.upper():
                continue
            if gender == "BOYS" and co_education in ["GIRLS", "FEMALE"]:
                continue
            if college_type_filter == "Women's Only Colleges" and co_education not in ["GIRLS", "FEMALE"]:
                continue

            # --- MATCH PREDICTABILITY CRITERIA ---
            if user_rank <= cutoff_rank:
                status_tag, status_color = "Safe Match", "#16a34a"
            elif user_rank <= (cutoff_rank * 1.15): 
                status_tag, status_color = "Risky Match", "#ea580c"
            else:
                continue

            filtered_results.append({
                "Code": inst_code, "Name": inst_name_full, "Place": place, "Dist": dist_code, "Branch": branch_code, "Type": co_education, "Cutoff": cutoff_rank, "Status": status_tag, "Color": status_color
            })
        
    filtered_results.sort(key=lambda x: (0 if x["Status"] == "Safe Match" else 1, x["Cutoff"]))
    
    st.markdown("---")
    st.subheader(f"Analysis Results ({len(filtered_results)} matches analyzed)")
    st.info(f"Active Filtering Column Target: **{caste.upper()}_{gender.upper()}**")
    
    if len(filtered_results) > 0:
        table_rows = ""
        for row in filtered_results:
            women_badge = '<span style="background:#fce7f3;color:#9d174d;padding:2px 6px;border-radius:4px;font-size:11px;font-weight:bold;margin-left:6px;">Women Only</span>' if row["Type"] in ["GIRLS", "FEMALE"] else ''
            status_badge = f'<span style="background-color:{row["Color"]}; color:white; padding:3px 8px; border-radius:12px; font-size:11px; font-weight:bold;">{row["Status"]}</span>'
            
            # The embedded iframe HTML table items are forced to white color text lines
            table_rows += f"""
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.15);">
                    <td style="padding:12px 10px; font-weight:bold; color:#FFFFFF;">{row['Code']}</td>
                    <td style="padding:12px 10px; font-weight:500; color:#FFFFFF;">{row['Name']}{women_badge}</td>
                    <td style="padding:12px 10px; color:#FFFFFF; opacity:0.85;">{row['Place']}</td>
                    <td style="padding:12px 10px; text-transform:uppercase; color:#FFFFFF; opacity:0.85;">{row['Dist']}</td>
                    <td style="padding:12px 10px; font-weight:bold; color:#3b82f6;">{row['Branch']}</td>
                    <td style="padding:12px 10px; text-align:center;">{status_badge}</td>
                    <td style="padding:12px 10px; font-weight:bold; color:#FFFFFF;">{row['Cutoff']:,}</td>
                </tr>
            """
            
        full_html = f"""
        <div style="font-family:sans-serif; width:100%; padding:10px;">
            <table style="width:100%; border-collapse:collapse; font-size:14px; text-align:left;">
                <thead>
                    <tr style="border-bottom:2px solid rgba(255,255,255,0.35);">
                        <th style="padding:12px 10px; color:#FFFFFF; font-weight:700;">Code</th>
                        <th style="padding:12px 10px; color:#FFFFFF; font-weight:700;">Institution Name</th>
                        <th style="padding:12px 10px; color:#FFFFFF; font-weight:700;">Place</th>
                        <th style="padding:12px 10px; color:#FFFFFF; font-weight:700;">Dist</th>
                        <th style="padding:12px 10px; color:#FFFFFF; font-weight:700;">Branch</th>
                        <th style="padding:12px 10px; color:#FFFFFF; font-weight:700; text-align:center;">Chances</th>
                        <th style="padding:12px 10px; color:#FFFFFF; font-weight:700;">Last Cutoff</th>
                    </tr>
                </thead>
                <tbody>{table_rows}</tbody>
            </table>
        </div>
        """
        components.html(full_html, height=650, scrolling=True)
    else:
        st.markdown("<p style='color:#ef4444; font-weight:bold;'>No matches found for your rank. Try adjusting your target rank value upward in the parameters above.</p>", unsafe_allow_html=True)
else:
    st.markdown("<p style='color:#eab308; font-weight:bold;'>Data repository file assets are missing under src/data/</p>", unsafe_allow_html=True)