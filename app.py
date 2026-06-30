import streamlit as st
import json
import os
import pandas as pd

# --- SYSTEM AUTO-ADAPTIVE CONFIGURATION ---
st.set_page_config(
    page_title="TG EAPCET Predictor Pro", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- THEME-ADAPTIVE STYLE OVERRIDE ---
st.markdown(
    """
    <style>
    /* Clean up borders for the dropdown and input widgets without overriding global text colors */
    div[data-baseweb="select"], div[data-baseweb="input"] {
        border-radius: 8px !important;
        border: 1px solid rgba(128, 128, 128, 0.5) !important;
    }
    
    /* Make the separating horizontal lines clean and subtle in both modes */
    hr {
        opacity: 0.2;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("TG EAPCET Seat Allotment Predictor")
st.caption("Universal Category Matching Engine — Light & Dark Mode Compatible.")

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
        
    # --- STEP 1: PRE-EXTRACT UNIQUE COLLEGES FOR THE SEARCH SELECTION ---
    unique_colleges = set()
    for item in data:
        if item:
            # Check both normal and clean key patterns to find the name safely
            inst_name = item.get("INST_NAME", item.get("inst_name", ""))
            if not inst_name:
                for k, v in item.items():
                    if str(k).upper().strip() == "INST_NAME":
                        inst_name = v
                        break
            if inst_name:
                unique_colleges.add(str(inst_name).strip())
                
    sorted_colleges = sorted(list(unique_colleges))
    
    # --- NEW COLLEGE SELECTION FILTER WIDGET ---
    selected_colleges = st.multiselect(
        "Filter Specific Colleges (Leave empty to search all institutions)",
        options=sorted_colleges,
        placeholder="Type or select college names..."
    )
        
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
            # Specific College Filter Match
            if selected_colleges and inst_name_full not in selected_colleges:
                continue
            if branch_choice != "ALL BRANCHES" and branch_choice != branch_code.upper():
                continue
            if gender == "BOYS" and co_education in ["GIRLS", "FEMALE"]:
                continue
            if college_type_filter == "Women's Only Colleges" and co_education not in ["GIRLS", "FEMALE"]:
                continue

            # --- MATCH PREDICTABILITY CRITERIA ---
            if user_rank <= cutoff_rank:
                status_tag = "Safe Match"
            elif user_rank <= (cutoff_rank * 1.15): 
                status_tag = "Risky Match"
            else:
                continue

            filtered_results.append({
                "Code": inst_code, 
                "Institution Name": inst_name_full, 
                "Place": place, 
                "Dist": dist_code, 
                "Branch": branch_code, 
                "Type": co_education, 
                "Last Cutoff": cutoff_rank, 
                "Chances": status_tag
            })
        
    filtered_results.sort(key=lambda x: (0 if x["Chances"] == "Safe Match" else 1, x["Last Cutoff"]))
    
    st.markdown("---")
    st.subheader(f"Analysis Results ({len(filtered_results)} matches analyzed)")
    st.info(f"Active Filtering Column Target: **{caste.upper()}_{gender.upper()}**")
    
    if len(filtered_results) > 0:
        df = pd.DataFrame(filtered_results)
        
        st.dataframe(
            df[["Code", "Institution Name", "Place", "Dist", "Branch", "Type", "Chances", "Last Cutoff"]],
            use_container_width=True,
            height=600,
            column_config={
                "Last Cutoff": st.column_config.NumberColumn(format="%d"),
                "Chances": st.column_config.TextColumn(help="Admission safety tag prediction")
            }
        )
    else:
        st.error("No matches found for your criteria. Try adjusting your selections or target rank value upward.")
else:
    st.warning("Data repository file assets are missing under src/data/")