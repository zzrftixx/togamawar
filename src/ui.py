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
    tab1, tab2 = st.tabs(["Ringkasan Denda", "Detail Data"])
    
    with tab1:
        # Group by Name and Sum Fine
        summary = df.groupby("name")[["fine"]].sum().sort_values("fine", ascending=False)
        st.subheader("Total Denda per Orang")
        st.dataframe(summary, use_container_width=True)
        
        total_fine = df["fine"].sum()
        st.metric("Total Uang Denda Bulan Ini", f"Rp {total_fine:,.0f}")

    with tab2:
        st.subheader("Data Masuk")
        # Display readable table
        display_df = df[["week_number", "day_name", "name", "is_present", "notes", "fine"]]
        display_df.columns = ["Minggu", "Hari", "Nama", "Hadir", "Keterangan", "Denda"]
        st.dataframe(display_df, use_container_width=True)
        
        # Export logic
        if st.download_button(
            label="📥 Download Excel",
            data=to_excel(display_df),
            file_name=f"Laporan_TogaMawar_{selected_month_view}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ):
            st.success("File siap didownload!")

def to_excel(df):
    from io import BytesIO
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()
