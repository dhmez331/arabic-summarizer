import re
from hijridate import Hijri

def normalize_arabic_digits(text):
    for i in range(10):
        text = text.replace(chr(0x0660 + i), str(i))
    return text

def extract_and_convert(text):
    normalized = normalize_arabic_digits(text)
    
    pattern_normal   = r'(0?[1-9]|[12][0-9]|30)[\/\-\.](0?[1-9]|1[0-2])[\/\-\.](1[0-9]{3})'
    pattern_reversed = r'(1[0-9]{3})[\/\-\.](0?[1-9]|1[0-2])[\/\-\.](0?[1-9]|[12][0-9]|30)'
    
    match = re.search(pattern_normal, normalized)
    if match:
        day, month, year = match.groups()
    else:
        match = re.search(pattern_reversed, normalized)
        if match:
            year, month, day = match.groups()
        else:
            return "❌ تاريخ غير صحيح الشكل"
    
    try:
        h = Hijri(int(year), int(month), int(day))
        g = h.to_gregorian()
        return f"✅ {g.strftime('%d.%m.%Y')}"
    except ValueError as e:
        return f"❌ تاريخ غير صحيح: {e}"

# test cases الدكتور
tests = [
    "03/04/1447",
    "٠٣/٠٤/١٤٤٧",
    "3/4/1447",
    "03-04-1447",
    "03.04.1447",
    "1447/04/03",
    "1447-04-03",
    "30/12/1447",
    "03/13/1447",
    "99/99/9999",
    "abc",
    "",
    "03/0٤/1447",
]

for t in tests:
    print(f"{t:20} → {extract_and_convert(t)}")

from hijridate import Hijri

