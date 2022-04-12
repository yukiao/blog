def get_formatted_date(date):
    month_dict = {
        1: "Januari",
        2: "Februari",
        3: "Maret",
        4: "April",
        5: "Mei",
        6: "Juni",
        7: "Juli",
        8: "Agustus",
        9: "September",
        10: "Oktober",
        11: "November",
        12: "Desember"
    }
    
    day = date.day
    month = month_dict[date.month]
    year = date.year
    
    return f'{day} {month} {year}'