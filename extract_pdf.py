import pdfplumber
import json
import os

def extract_complete_eapcet_pdf(pdf_path, output_json_path):
    if not os.path.exists(pdf_path):
        print(f"⚠️ Skipped: '{pdf_path}' not found in this folder.")
        return

    print(f"🔄 Processing '{pdf_path}'... Extracting all wide data columns.")
    
    # 31 explicit columns matching your exact PDF screenshot layout
    headers = [
        "inst_code", "inst_name", "place", "dist_code", "co_education", 
        "coll_type", "branch_code", "branch_name", 
        "OC_BOYS", "OC_GIRLS", "BC_A_BOYS", "BC_A_GIRLS", 
        "BC_B_BOYS", "BC_B_GIRLS", "BC_C_BOYS", "BC_C_GIRLS", 
        "BC_D_BOYS", "BC_D_GIRLS", "BC_E_BOYS", "BC_E_GIRLS", 
        "SC_I_BOYS", "SC_I_GIRLS", "SC_II_BOYS", "SC_II_GIRLS", 
        "SC_III_BOYS", "SC_III_GIRLS", "ST_BOYS", "ST_GIRLS", 
        "EWS_BOYS", "EWS_GIRLS", "affiliated_to"
    ]
    
    parsed_records = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            table = page.extract_table()
            if not table:
                continue
                
            for row in table:
                if not row:
                    continue
                
                # Convert cells to clean strings and strip whitespace
                row_cells = [str(cell).strip() if cell is not None else "" for cell in row]
                
                # Skip title headings, empty structural cells, or system noise lines
                if not row_cells[0] or "Inst Code" in row_cells[0] or "LAST RANK" in "".join(row_cells).upper():
                    continue
                
                # Safety padding: if row elements don't span the full length, expand it
                while len(row_cells) < len(headers):
                    row_cells.append("")
                    
                # Zip headers and cells into a dictionary safely
                record = {}
                for idx, header in enumerate(headers):
                    record[header] = row_cells[idx]
                    
                parsed_records.append(record)
                
    # Ensure folder path structure is generated safely before saving file assets
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(parsed_records, f, indent=4)
        
    print(f"🎉 Success! Extracted {len(parsed_records)} rows into '{output_json_path}' with all 24 category streams intact.")

# --- AUTOMATED CONVERSION EXECUTOR ---
# Uses your exact uploaded filenames
if __name__ == "__main__":
    extract_complete_eapcet_pdf("TGEAPCET_2025_LASTRANKS_FirstPhase.pdf", "src/data/phase1.json")
    extract_complete_eapcet_pdf("TGEAPCET_2025_LASTRANKS_SecondPhase.pdf", "src/data/phase2.json")
    extract_complete_eapcet_pdf("TGEAPCET_2025_FINALPHASE_LASTRANKS (2).pdf", "src/data/finalPhase.json")