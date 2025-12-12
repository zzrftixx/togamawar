import streamlit as st
import pandas as pd
from datetime import datetime
from src.const import SCHEDULE_DATA, DAYS_ORDER, FINE_AMOUNT
from src.data import save_entry, get_monthly_summary

MONTHS = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni", 
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]

def render_header():
    st.title("🌺 Jadwal Piket Toga Mawar")
    st.markdown("---")

def render_input_form():
    st.header("📝 Catatan Piket Mingguan")
    
    # Context Selection
    col1, col2 = st.columns(2)
    with col1:
        selected_month = st.selectbox("Bulan", MONTHS, index=datetime.now().month - 1)
    with col2:
        week_num = st.selectbox("Minggu Ke-", [1, 2, 3, 4, 5])
    
    day_name = st.selectbox("Hari", DAYS_ORDER)
    
    # Get people for that day
    people = SCHEDULE_DATA.get(day_name, [])
    
    st.subheader(f"Jadwal: {day_name}")
    st.info(f"Petugas: {', '.join(people)}")
    
    # Input Form
    with st.form("attendance_form"):
        entries = []
        st.write("Silahkan centang yang **HADIR**. Jika tidak hadir, isi keterangan (denda otomatis diisi).")
        
        for person in people:
            st.markdown(f"#### 👤 {person}")
            col_a, col_b, col_c = st.columns([1, 2, 2])
            
            with col_a:
                is_present = st.checkbox("Hadir", value=True, key=f"check_{person}")
            
            with col_b:
                notes = st.text_input("Keterangan", key=f"note_{person}", placeholder="Isi jika tidak hadir...")
            
            with col_c:
                # Logic: If not present, default fine. If present, default 0.
                default_fine = 0 if is_present else FINE_AMOUNT
                fine = st.number_input("Denda (Rp)", min_value=0, step=500, value=default_fine, key=f"fine_{person}")
            
            entries.append({
                "date": datetime.now().strftime("%Y-%m-%d"), # Timestamp of entry
                "month_name": selected_month,
                "week_number": week_num,
                "day_name": day_name,
                "name": person,
                "is_present": is_present,
                "notes": notes,
                "fine": fine,
                "timestamp": datetime.now().isoformat()
            })
            st.markdown("---")
        
        submitted = st.form_submit_button("💾 Simpan Data", use_container_width=True)
        
        if submitted:
            if save_entry(entries):
                st.success(f"Data piket hari {day_name} berhasil disimpan!")
            else:
                st.error("Gagal menyimpan data.")

def render_dashboard():
    st.header("📊 Dashboard & Laporan")
    
    selected_month_view = st.selectbox("Lihat Laporan Bulan", MONTHS, key="view_month", index=datetime.now().month - 1)
    
    df = get_monthly_summary(selected_month_view)
    
    if df.empty:
        st.warning("Belum ada data untuk bulan ini.")
        return

    # Tabs
    tab1, tab2 = st.tabs(["💰 Ringkasan Denda", "📅 Laporan Harian"])
    
    with tab1:
        # Group by Name and Sum Fine
        summary = df.groupby("name")[["fine"]].sum().sort_values("fine", ascending=False)
        st.subheader("Total Denda per Orang")
        
        # Display as a clean table with index (Name) as a column
        summary = summary.reset_index()
        summary.columns = ["Nama", "Total Denda"]
        
        # Format currency for display
        st.dataframe(
            summary.style.format({"Total Denda": "Rp {:,.0f}"}), 
            use_container_width=True,
            hide_index=True
        )
        
        total_fine = df["fine"].sum()
        st.metric("Total Uang Denda Bulan Ini", f"Rp {total_fine:,.0f}")

    with tab2:
        st.subheader("Rekap Harian")
        
        # Aggregate by Date/Day
        if not df.empty:
            daily_rows = []
            # Group by date/day context
            # We use date as primary key for day groups
            groups = df.groupby(['date', 'week_number', 'day_name'])
            
            for (date, week, day), group in groups:
                # Get absent people
                absent_mask = ~group['is_present']
                absent_df = group[absent_mask]
                
                absent_names = ", ".join(absent_df['name'].tolist()) if not absent_df.empty else "-"
                
                # Format notes: "Name (Note)"
                notes_list = []
                for _, row in absent_df.iterrows():
                    if row['notes']:
                        notes_list.append(f"{row['name']} ({row['notes']})")
                
                notes_str = "; ".join(notes_list) if notes_list else "-"
                total_daily_fine = group['fine'].sum()
                
                daily_rows.append({
                    "Tanggal": date,
                    "Minggu Ke": week,
                    "Hari": day,
                    "Yang Tidak Hadir": absent_names,
                    "Keterangan": notes_str,
                    "Total Denda": total_daily_fine
                })
            
            daily_df = pd.DataFrame(daily_rows)
            
            # Display nicely
            st.dataframe(
                daily_df.style.format({"Total Denda": "Rp {:,.0f}"}),
                use_container_width=True,
                hide_index=True
            )
            
            # Export logic
            if st.download_button(
                label="📥 Download Laporan Excel (Lengkap)",
                data=to_excel_improved(summary, daily_df),
                file_name=f"Laporan_TogaMawar_{selected_month_view}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ):
                st.success("File siap didownload!")
        else:
            st.info("Belum ada data harian.")

def to_excel_improved(summary_df, daily_df):
    from io import BytesIO
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Sheet 1: Ringkasan Denda
        summary_df.to_excel(writer, index=False, sheet_name='Ringkasan Denda')
        
        # Sheet 2: Laporan Harian
        daily_df.to_excel(writer, index=False, sheet_name='Laporan Harian')
        
        # Adjust column widths (Basic attempt)
        for worksheet in writer.sheets.values():
            for column in worksheet.columns:
                max_length = 0
                column = [cell for cell in column]
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)
                worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
                
    return output.getvalue()
