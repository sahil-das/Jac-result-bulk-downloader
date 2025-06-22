import requests
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from bs4 import BeautifulSoup

# Load the HTML content
with open("debug_post_result.html", "r", encoding="utf-8") as file:
    html = file.read()

soup = BeautifulSoup(html, "html.parser")

# ===== HEADER =====
print("=== HEADER ===")
board = soup.find("span", id="Label1")
address = soup.find("span", id="lblheader1")
exam = soup.find("span", id="lblheader2")

print("Board Name:", board.text.strip())
print("Address:", address.text.strip())
print("Exam:", exam.text.strip())
print()

# ===== STUDENT DETAILS =====
print("=== STUDENT DETAILS ===")
roll_code = soup.find("span", id="ContentPlaceHolder1_lblrollcode").text.strip()
roll_no = soup.find("span", id="ContentPlaceHolder1_lblrollno").text.strip()
name = soup.find("span", id="ContentPlaceHolder1_lblstudentname").text.strip()
father = soup.find("span", id="ContentPlaceHolder1_lblfather").text.strip()
mother = soup.find("span", id="ContentPlaceHolder1_lblmother").text.strip()
school = soup.find("span", id="ContentPlaceHolder1_lblschoolname").text.strip()

print(f"Roll Code: {roll_code}")
print(f"Roll Number: {roll_no}")
print(f"Student Name: {name}")
print(f"Father's Name: {father}")
print(f"Mother's Name: {mother}")
print(f"School Name: {school}")
print()

# ===== SUBJECT-WISE MARKS =====
print("=== SUBJECT-WISE MARKS ===")
marks_table = soup.find("table", style=lambda x: x and "border-collapse" in x)
subjects = []

for row in marks_table.find_all("tr")[1:-3]:  # Skip header and last 3 rows (total/result/percentage)
    cols = row.find_all("td")
    if len(cols) < 6:
        continue
    subject_code = cols[0].text.strip()
    theory = cols[1].text.strip()
    practical = cols[2].text.strip()
    total = cols[3].text.strip()
    grade = cols[4].text.strip()
    remarks = cols[5].text.strip()
    subjects.append({
        "subject": subject_code,
        "theory": theory,
        "practical": practical,
        "total": total,
        "grade": grade,
        "remarks": remarks
    })

for sub in subjects:
    print(f"{sub['subject']}: Theory={sub['theory']}, Practical/CCE={sub['practical']}, Total={sub['total']}, Grade={sub['grade']}, Remarks={sub['remarks'] or '—'}")

print()

# ===== SUMMARY =====
print("=== SUMMARY ===")
total_marks = soup.find("span", id="ContentPlaceHolder1_lbltotalobt").text.strip()
division = soup.find("span", id="ContentPlaceHolder1_lbldivision").text.strip()
percentage = soup.find("span", id="ContentPlaceHolder1_lblpercentage").text.strip()

print("Total Marks Obtained:", total_marks)
print("Result:", division)
print("Percentage:", percentage + "%")
print()

# ===== NOTE / DISCLAIMER =====
print("=== NOTE ===")
note_items = soup.select("ol li")
for i, item in enumerate(note_items, 1):
    print(f"{i}. {item.text.strip()}")

disclaimer = soup.find("b", string="Disclaimer").parent.text.strip()
print("\nDisclaimer:", disclaimer)



def fetch_result(roll_code, roll_number):
    url = "https://jacresults.com/enter-class-x-2025-student-details"
    session = requests.Session()
    
    # Step 1: GET to get hidden fields
    response_get = session.get(url)
    soup = BeautifulSoup(response_get.text, "html.parser")
    try:
        viewstate = soup.find("input", {"id": "__VIEWSTATE"})["value"]
        viewstategen = soup.find("input", {"id": "__VIEWSTATEGENERATOR"})["value"]
        eventvalidation = soup.find("input", {"id": "__EVENTVALIDATION"})["value"]
    except:
        print("Failed to get hidden fields")
        return None

    # Step 2: POST form data
    payload = {
        "__VIEWSTATE": viewstate,
        "__VIEWSTATEGENERATOR": viewstategen,
        "__EVENTVALIDATION": eventvalidation,
        "ctl00$ContentPlaceHolder1$txt_code": roll_code,
        "ctl00$ContentPlaceHolder1$txt_no": roll_number,
        "ctl00$ContentPlaceHolder1$btn_submit": "Submit"
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://jacresults.com",
        "Referer": url,
        "User-Agent": "Mozilla/5.0"
    }

    response_post = session.post(url, data=payload, headers=headers)
    soup_result = BeautifulSoup(response_post.text, "html.parser")

    # Parse student name as example (update selectors as per actual page)
    name_td = soup_result.find("td", string="Student's Name")
    if not name_td:
        return None  # no result or invalid roll no

    student_name = name_td.find_next_sibling("td").text.strip()
    roll_code_extracted = soup_result.find("td", string="Roll Code").find_next_sibling("td").text.strip()
    roll_number_extracted = soup_result.find("td", string="Roll Number").find_next_sibling("td").text.strip()

    # You can extract more fields similarly

    return {
        "Student Name": student_name,
        "Roll Code": roll_code_extracted,
        "Roll Number": roll_number_extracted,
    }

def save_results_pdf(results, filename="results.pdf"):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    y = height - 40

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "JAC 10th Class Results 2025")
    y -= 40
    c.setFont("Helvetica", 12)

    for result in results:
        if result is None:
            c.drawString(50, y, "No data found for this roll number.")
            y -= 30
            continue

        for key, val in result.items():
            c.drawString(50, y, f"{key}: {val}")
            y -= 20

        c.line(50, y, width - 50, y)
        y -= 30

        if y < 100:
            c.showPage()
            y = height - 40
            c.setFont("Helvetica", 12)

    c.save()
    print(f"Saved results to {filename}")

def main():
    roll_code = input("Enter Roll Code (e.g. 11239): ").strip()
    start_roll = int(input("Enter start Roll Number (e.g. 1): "))
    end_roll = int(input("Enter end Roll Number (e.g. 5): "))

    results = []
    for roll in range(start_roll, end_roll + 1):
        roll_str = f"{roll:04d}"  # pad to 4 digits
        print(f"Fetching result for Roll Number: {roll_str} ...")
        result = fetch_result(roll_code, roll_str)
        if result:
            print("Result found:", result["Student Name"])
        else:
            print("No result found or invalid roll number.")
        results.append(result)

    save_results_pdf(results)

if __name__ == "__main__":
    main()
