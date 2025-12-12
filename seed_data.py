import pandas as pd
from datetime import datetime

data = [
    {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "month_name": "Desember",
        "week_number": 1,
        "day_name": "Senin",
        "name": "Bu Nur Hayati",
        "is_present": True,
        "notes": "",
        "fine": 0,
        "timestamp": datetime.now().isoformat()
    },
    {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "month_name": "Desember",
        "week_number": 1,
        "day_name": "Senin",
        "name": "Bu Sari",
        "is_present": False,
        "notes": "Sakit",
        "fine": 5000,
        "timestamp": datetime.now().isoformat()
    }
]

df = pd.DataFrame(data)
df.to_csv("d:/SERVERCOMPLITE/WEBSITEAPPS/ProjectJadwalTogaMawar/attendance_data.csv", index=False)
print("Dummy data created.")
