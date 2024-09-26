import datetime

from flask import Flask, render_template, request, redirect,jsonify, flash, url_for, send_from_directory, session, send_file
import sqlite3, os, database, document_functions, json,requests
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'My_Secret_Key'

TOTAL_FEES = 2000

@app.route('/', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        admission_no = request.form['admission_no']
        password = request.form['password']

        with sqlite3.connect('student.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*)
                FROM logins
                WHERE admission_no = ? AND password = ?
            ''', (admission_no, password))

            count = cursor.fetchone()[0]
            if count > 0:  # If the student exists,
                session['admission_no'] = admission_no
                return redirect(url_for('home'))
            elif count < 1:
                with sqlite3.connect('manager.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                    SELECT COUNT(*)
                    FROM logins
                    WHERE username = ? AND password = ?
                    
                    ''', (admission_no, password))
                    count = cursor.fetchone()[0]
                    if count > 0:
                        return redirect(url_for('add_or_remove_student'))
                    else:
                        with sqlite3.connect('admin.db') as conn:
                            cursor = conn.cursor()
                            cursor.execute('''
                                SELECT COUNT(*)
                                FROM logins
                                WHERE position = ? AND password = ?
                            ''', (admission_no, password))

                            count = cursor.fetchone()[0]
                            if count > 0:
                                return redirect(url_for('admin_dashboard'))
                            else:
                                return render_template('login.html', error="Invalid admission number or password")
    return render_template('login.html')


@app.route('/home')
def home():
    admission_no = session.get('admission_no')
    return render_template('home.html', name=database.get_first_name(admission_no),
                           greeting=document_functions.greet_based_on_time(), admission_no=document_functions.replace_slash_with_dot(admission_no))


@app.route('/fee')
def fee():
    return render_template('fee.html')


@app.route('/student_scores')
def student_scores():
    admission_no = session.get('admission_no')
    conn = sqlite3.connect('student.db')
    cursor = conn.cursor()

    # Get the current year and calculate the past four years
    current_year = datetime.now().year
    years = [current_year - i for i in range(4)]

    # Query to get exam scores for the past available years
    query = '''
        SELECT year, term, average
        FROM Examinations
        WHERE admission_no = ? AND year <= ? 
        ORDER BY year, term
    '''
    cursor.execute(query, (admission_no, current_year))
    rows = cursor.fetchall()
    conn.close()

    # Organize data into a dictionary by year
    exam_scores = {str(year): [] for year in years}
    for row in rows:
        year, term, average = row
        exam_scores[str(year)].append(average)

    # Filter out years with no data
    exam_scores = {year: average for year,average in exam_scores.items() if average}

    return render_template('examtrend.html', exam_scores=exam_scores, student_id=admission_no, student_marks=view_student_marks(), length = len(view_student_marks()))


@app.route('/settings')
def settings():
    return render_template('settings.html')


@app.route('/logout')
def logout():
    return redirect(url_for('login'))


#_______________________________________________________________________________________
#=================================================================================#
#----------------ADMIN----------------------
# List of subjects (make sure the names match the ones in the HTML form)
subjects = ['mathematics', 'biology', 'chemistry', 'physics', 'geography', 'business', 'english', 'kiswahili', 'cre',
            'french']


@app.route('/admin_dash')
def admin_dashboard():
    admission_no = None
    return render_template("admin_dashboard.html", admission_no=admission_no)


@app.route('/submit_marks', methods=['POST'])
def submit_marks():
    # Extract marks from the form and put them into a list
    marks_list = [int(request.form[subject]) for subject in subjects]

    # For demonstration, let's print the marks list
    print("Marks List:", marks_list)
    admission_no = document_functions.replace_slash_with_slash(request.form['admission_no'])
    exam_type = request.form['exam_type']
    year = request.form['year']
    term = request.form['term']
    # You can now use marks_list for further processing, such as inserting into a database
    database.insert_marks(year, term, exam_type, admission_no, marks_list)
    database.set_average(admission_no,term, year, exam_type)

    return "Marks submitted successfully!"



@app.route('/submit_selection', methods=['GET', 'POST'])
def submit_selection():
    return redirect(url_for('enter_student_marks'))


@app.route('/submit_check', methods=['POST'])
def submit_check():
    marks_list = [int(request.form[subject]) for subject in subjects]
    database.insert_marks(document_functions.replace_slash_with_slash(request.form['admission_no']), marks_list)




@app.route('/type_check')
def type_check():
    return render_template('type_check.html')


@app.route('/students', methods=['GET', 'POST'])
def view_students():
    year = int(request.form['year'])
    term = int(request.form['term'])
    exam_type = request.form['type']
    grade = request.form['class']
    data = database.get_students_marks_filtered(year, term, exam_type, grade)

    return render_template('exam_list.html', students=data)


@app.route('/enter_marks/<admission_no>', methods=['GET', 'POST'])
def enter_student_marks(admission_no):
    admission_n = document_functions.replace_slash_with_slash(admission_no)
    year = request.form['year']
    term = int(request.form['term'])
    exam_type = request.form['type']
    database.insert_time(admission_n, year, term, exam_type)

    return render_template('enter_marks.html', admission_no=admission_n,year=year,exam_type=exam_type, term=term)


@app.route('/view_students_marks')
def view_students_marks():
    return render_template('view_students_marks.html', students=database.view_students())


@app.route('/<admission_no>')
def enter_marks(admission_no):
    admission_n = document_functions.replace_slash_with_slash(admission_no)
    return render_template('type_checker.html', admission_no=admission_no,
                           first_name=database.get_first_name(admission_n))


@app.route('/exam_list')
def students_results():
    return render_template('exam_list.html', students=database.get_all_students_exams())


#-------------Upload a Memo
# Set the directories for file uploads
BOOKS_FOLDER = 'static/uploads/books/'
IMAGES_FOLDER = 'static/uploads/images/'
app.config['BOOKS_FOLDER'] = BOOKS_FOLDER
app.config['IMAGES_FOLDER'] = IMAGES_FOLDER

# Ensure the upload folders exist
os.makedirs(BOOKS_FOLDER, exist_ok=True)
os.makedirs(IMAGES_FOLDER, exist_ok=True)


@app.route('/memo')
def index():
    # List all uploaded books with their front images
    books = []
    for filename in os.listdir(app.config['BOOKS_FOLDER']):
        image_name = os.path.splitext(filename)[0] + ".jpg"  # Assuming images are uploaded as .jpg
        image_path = os.path.join(app.config['IMAGES_FOLDER'], image_name)
        books.append({
            "filename": filename,
            "image": image_name if os.path.exists(image_path) else None
        })
    return render_template('index.html', books=books)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files.get('file')
        image = request.files.get('image')

        if file and file.filename.endswith('.pdf'):
            # Save the PDF book
            filepath = os.path.join(app.config['BOOKS_FOLDER'], file.filename)
            file.save(filepath)

            # Save the front image (if provided)
            if image and image.filename.endswith(('.jpg', '.jpeg', '.png')):
                image_name = os.path.splitext(file.filename)[0] + ".jpg"
                imagepath = os.path.join(app.config['IMAGES_FOLDER'], image_name)
                image.save(imagepath)

            return redirect(url_for('index'))

    return render_template('upload.html')


@app.route('/download/<filename>')
def download(filename):
    # Allow users to download the uploaded books
    return send_from_directory(app.config['BOOKS_FOLDER'], filename, as_attachment=True)


@app.route('/delete/<filename>', methods=['POST'])
def delete(filename):
    # Delete the PDF book and its front image
    book_path = os.path.join(app.config['BOOKS_FOLDER'], filename)
    image_name = os.path.splitext(filename)[0] + ".jpg"
    image_path = os.path.join(app.config['IMAGES_FOLDER'], image_name)

    if os.path.exists(book_path):
        os.remove(book_path)
    if os.path.exists(image_path):
        os.remove(image_path)

    return redirect(url_for('index'))


@app.route('/view_memo')
def view_memo():
    books = []
    for filename in os.listdir(app.config['BOOKS_FOLDER']):
        image_name = os.path.splitext(filename)[0] + ".jpg"  # Assuming images are uploaded as .jpg
        image_path = os.path.join(app.config['IMAGES_FOLDER'], image_name)
        books.append({
            "filename": filename,
            "image": image_name if os.path.exists(image_path) else None
        })
    return render_template("view_memo.html", books=books)



def load_user_data(username):
    if os.path.exists('user_data.json'):
        with open('user_data.json', 'r') as f:
            try:
                data = json.load(f)
                return data.get(username, {"username": username, "profile_picture": None})
            except json.JSONDecodeError:
                return {"username": username, "profile_picture": None}
    else:
        return {"username": username, "profile_picture": None}


# Save user data to a JSON file
def save_user_data(username, user_data):
    data = {}
    if os.path.exists('user_data.json'):
        with open('user_data.json', 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                pass
    data[username] = user_data
    with open('user_data.json', 'w') as f:
        json.dump(data, f)


# Route for user profile
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    username = request.args.get('username')
    user_data = load_user_data(username)

    if request.method == 'POST':
        if 'profile_picture' in request.files:
            profile_picture = request.files['profile_picture']
            if profile_picture.filename != '':
                profile_pic_path = f'static/uploads/{username}_profile_picture.jpg'
                profile_picture.save(profile_pic_path)
                user_data['profile_picture'] = profile_pic_path
                save_user_data(username, user_data)
                return redirect(url_for('dashb', username=username))

    return render_template('dashboard.html', username=username, profile_picture=user_data['profile_picture'])


#----------------Change Password
# @app.route('/change_password')
# def change_password():
#     return render_template('change_password.html')


@app.route('/compiler')
def compiler():
    return render_template('compiler.html')


@app.route('/manager')
def manager():
    return render_template('manager.html')


@app.route('/dash')
def dashb():
    admission_no = session.get('admission_no')
    # Get the profile picture from session or set a default one
    profile_picture = session.get('profile_picture', 'person1.png')
    username = request.args.get('username')
    user_data = load_user_data(username)
    admission=document_functions.replace_slash_with_dot(admission_no)
    if request.method == 'POST':
        if 'profile_picture' in request.files:
            profile_picture = request.files['profile_picture']
            if profile_picture.filename != '':
                profile_pic_path = f'static/uploads/{username}_profile_picture.jpg'
                profile_picture.save(profile_pic_path)
                user_data['profile_picture'] = profile_pic_path
                save_user_data(username, user_data)

    return render_template('dashboard.html', profile_picture=user_data['profile_picture'],admission_no=admission)


# @app.route('/dash')
# def dashb():
#     return render_template("dashboard.html")
#Route to display Students with Fee balances
@app.route('/students_with_balance')
def students_with_balance():
    students = database.get_students_with_balance()
    return render_template('students_with_balance.html', students=students)


#===============Add Student
@app.route('/add_or_remove')
def add_or_remove_student():
    return render_template("add_or_remove_student.html")


@app.route('/add_student')
def add():
    return render_template('add_student.html')


@app.route('/signup_success')
def signup_success():
    return render_template('signup_success.html')


@app.route('/submit_signup', methods=['POST'])
def submit_signup():
    first_name = request.form['first_name']
    middle_name = request.form['middle_name']
    last_name = request.form['last_name']
    age = request.form['age']
    gender = request.form['gender']
    grade = request.form['grade']
    sickness = request.form['sickness']
    treatment = request.form['treatment']
    admission_no = request.form['admission_no']
    phone = request.form['phone']
    existing_student = database.student_exist(admission_no)
    if existing_student:
        # Admission number already exists
        flash("Error: A student with this admission number already exists.", "error")
        return redirect(url_for('index'))

    database.add_someone(admission_no, first_name, middle_name, last_name, gender, age)
    database.add_level(admission_no, grade,phone)
    database.put_ill_students(admission_no, sickness, treatment)
    database.add_login(admission_no, last_name)
    return redirect(url_for('signup_success'))


#=================Non Compliant Student
@app.route('/non_compliant_students')
def non_compliant_students():
    students = database.non_compliant_students()
    return render_template('non_compliant_students.html', students=students)


#===============Ill Students
@app.route('/health_issue')
def health_issue():
    students = database.get_ill_students()
    return render_template('health_issue.html', students=students)
#================Add Health issue Student==========
#================Remove Health issue Student=============
#================View all registered students=============
def all_students():
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT students.admission_no, students.first_name, students.last_name, rest.phone_number, rest.Grade
        FROM students
        JOIN rest ON students.admission_no = rest.admission_no
        ORDER BY rest.Grade ASC
        ''')
        result = cursor.fetchall()
        return result


@app.route('/registered_students')
def registered():
    students = all_students()
    return render_template('registered_students.html',students=students)


#======================Fee Payment==============================================



def get_student_data(admission_number):
    conn = sqlite3.connect('fees.db')
    cursor = conn.cursor()
    cursor.execute('SELECT total_paid, remaining_balance FROM students WHERE admission_number = ?', (admission_number,))
    result = cursor.fetchone()
    conn.close()
    return result if result else (0, TOTAL_FEES)





# Function to get student data by either admission number or name
def get_student_by_admission_or_name(identifier):
    conn = sqlite3.connect('student.db')
    cursor = conn.cursor()

    # Check if identifier is a valid admission number or name
    cursor.execute('''
        SELECT admission_no FROM students
        WHERE admission_no = ? OR (first_name || ' ' || last_name) = ?
    ''', (identifier, identifier))

    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]  # Return admission number
    else:
        return None


# Updated function to handle name or admission number and fee update
def update_student_fees(identifier, amount_paid):
    # Check if the identifier is an admission number or full name
    admission_number = get_student_by_admission_or_name(identifier)

    if admission_number is None:
        return "Student not found"

    conn = sqlite3.connect('fees.db')
    cursor = conn.cursor()

    # Get the previous total paid and remaining balance
    previous_total_paid, _ = get_student_data(admission_number)
    total_paid = previous_total_paid + amount_paid
    remaining_balance = TOTAL_FEES - total_paid

    # Update the students' fee data
    cursor.execute('''
        INSERT INTO students (admission_number, total_paid, remaining_balance)
        VALUES (?, ?, ?)
        ON CONFLICT(admission_number)
        DO UPDATE SET total_paid = excluded.total_paid, remaining_balance = excluded.remaining_balance
    ''', (admission_number, total_paid, remaining_balance))

    # Record the transaction in the payment_history table
    date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        INSERT INTO payment_history (admission_number, amount_paid, remaining_balance, date_time)
        VALUES (?, ?, ?, ?)
    ''', (admission_number, amount_paid, remaining_balance, date_time))

    conn.commit()
    conn.close()

    return total_paid, remaining_balance


# def update_student_fees(admission_number, amount_paid):
#     conn = sqlite3.connect('fees.db')
#     cursor = conn.cursor()
#
#     previous_total_paid, _ = get_student_data(admission_number)
#     total_paid = previous_total_paid + amount_paid
#     remaining_balance = TOTAL_FEES - total_paid
#
#     cursor.execute('''
#         INSERT INTO students (admission_number, total_paid, remaining_balance)
#         VALUES (?, ?, ?)
#         ON CONFLICT(admission_number)
#         DO UPDATE SET total_paid = excluded.total_paid, remaining_balance = excluded.remaining_balance
#     ''', (admission_number, total_paid, remaining_balance))
#
#     # Record the transaction in payment_history with remaining balance
#     date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#     cursor.execute('''
#         INSERT INTO payment_history (admission_number, amount_paid, remaining_balance, date_time)
#         VALUES (?, ?, ?, ?)
#     ''', (admission_number, amount_paid, remaining_balance, date_time))
#
#     conn.commit()
#     conn.close()
#
#     return total_paid, remaining_balance

def get_payment_history(admission_number):
    conn = sqlite3.connect('fees.db')
    cursor = conn.cursor()
    cursor.execute('SELECT amount_paid, remaining_balance, date_time FROM payment_history WHERE admission_number = ?', (admission_number,))
    history = cursor.fetchall()
    conn.close()
    return history

@app.route('/fee_payment', methods=['GET','POST'])
def index1():
    # admission_no = get_student_by_admission_or_name(request.form['admissionNumber'])
    # admission_no = document_functions.replace_slash_with_dot(admission_no)
    return render_template('fees_payment.html' )

@app.route('/submit', methods=['POST'])
def submit():
    admission_number = request.form['admissionNumber']
    fee_paid = float(request.form['feePaid'])

    total_paid, remaining_balance = update_student_fees(admission_number, fee_paid)

    return jsonify({
        'total_paid': total_paid,
        'remaining_balance': remaining_balance
    })

@app.route('/receipt/<admission_no>', methods=['GET'])
def download_receipt(admission_no):
    admission_number = document_functions.replace_slash_with_slash(admission_no)
    total_paid, remaining_balance = get_student_data(admission_number)

    # Generate PDF receipt
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4)

    # Styles
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    normal_style = styles['Normal']

    # Receipt content
    elements = []

    # Title
    title = Paragraph(
        f"Payment Receipt for Admission Number: {document_functions.replace_slash_with_slash(admission_number)}",
        title_style)
    elements.append(title)

    # Spacer
    elements.append(Paragraph("<br/><br/>", normal_style))

    # Receipt table data
    data = [
        ["Description", "Amount (sh)"],
        ["Total Paid", f"{total_paid}"],
        ["Remaining Balance", f"{remaining_balance}"]
    ]

    # Create a table with a custom style
    table = Table(data, colWidths=[3 * inch, 2 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)

    # Spacer
    elements.append(Paragraph("<br/><br/>", normal_style))

    # Thank you message
    thank_you = Paragraph("Thank you for your payment.", normal_style)
    elements.append(thank_you)

    # Build PDF
    pdf.build(elements)

    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"receipt_{admission_number}.pdf",
                     mimetype='application/pdf')

@app.route('/history', methods=['GET'])
def view_history():
    admission_number = session.get('admission_no')
    admission_number = document_functions.replace_slash_with_slash(admission_number)
    history = get_payment_history(admission_number)
    return render_template('payment_history.html', history=history, admission_number=document_functions.replace_slash_with_dot(admission_number))

@app.route('/download_history', methods=['GET'])
def download_history():
    admission_number = session.get('admission_no')

    # Fetch payment history
    history = get_payment_history(document_functions.replace_slash_with_slash(admission_number))

    # Create buffer
    buffer = io.BytesIO()

    # Create a PDF document using SimpleDocTemplate
    pdf = SimpleDocTemplate(buffer, pagesize=A4)

    # Container for the elements in the PDF
    elements = []

    # Add a title
    styles = getSampleStyleSheet()
    title = Paragraph(f"Payment History for : {database.get_first_name( admission_number)} {database.get_middle_name(admission_number)} {database.get_last_name(admission_number)}", styles['Title'])
    elements.append(title)

    # Table data (headers)
    data = [['Amount Paid', 'Remaining Balance', 'Date & Time']]

    # Table data (rows)
    for amount_paid, remaining_balance, date_time in history:
        data.append([f"sh.{amount_paid}", f"sh.{remaining_balance}", date_time])

    # Create a table
    table = Table(data)

    # Apply table style
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Header background color
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Header text color
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    # Add table to elements
    elements.append(table)

    # Build the PDF
    pdf.build(elements)

    # Return PDF file
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"payment_history_{admission_number}.pdf",
                     mimetype='application/pdf')


#=====================Delete Student
def get_db_connection():
    conn = sqlite3.connect('student.db')
    conn.row_factory = sqlite3.Row
    return conn

# Route to render the HTML page
@app.route('/delete_students')
def delete_students():
    return render_template('students.html')

# API to fetch all students from the database
@app.route('/all_students', methods=['GET'])
def get_students():
    conn = get_db_connection()
    students = conn.execute('''
    SELECT students.admission_no, students.first_name, students.last_name, rest.Grade
    FROM students
    JOIN rest ON students.admission_no = rest.admission_no
    ''').fetchall()
    conn.close()

    student_list = [{'admission_no': document_functions.replace_slash_with_dot(student['admission_no']), 'name': student['first_name'], 'last_name':student['last_name'],'grade':student['Grade']} for student in students]
    return jsonify(student_list)

# API to delete a student by ID
@app.route('/delete_student/<admission_no>', methods=['DELETE'])
def delete_student(admission_no):
    admission = document_functions.replace_slash_with_slash(admission_no)
    database.delete_student(admission)
    return jsonify({'success': True})
#===============Change Password
@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        # Get form data
        admission_no = session.get('admission_no')  # Example admission number, ideally you'd get this from session or another source
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # Connect to the database
        conn = sqlite3.connect('student.db')
        cursor = conn.cursor()

        # Check if current password is correct
        cursor.execute("SELECT password FROM logins WHERE admission_no = ?", (admission_no,))
        result = cursor.fetchone()

        if result and result[0] == current_password:
            # Check if the new password and confirmation match
            if new_password == confirm_password:
                # Update the password in the logins table
                cursor.execute("UPDATE logins SET password = ? WHERE admission_no = ?", (new_password, admission_no))
                conn.commit()
                flash('Password changed successfully!', 'success')
                return redirect(url_for('home'))
            else:
                flash('New password and confirmation do not match.', 'error')
        else:
            flash('Current password is incorrect.', 'error')

        conn.close()
    return render_template('change_password.html')

#==================Developer portal
UPLOAD_FOLDER = 'static/images'
FIXED_FILENAME = 'your_uploaded_image.jpg'

# Configure upload folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/developer')
def developer():
    return render_template('developer.html')

@app.route('/upload_image', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return "No file part"

    file = request.files['image']

    if file.filename == '':
        return "No selected file"

    if file:
        # Use the fixed filename for the uploaded image
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], FIXED_FILENAME)
        file.save(file_path)
        return f'Image successfully uploaded and saved as {FIXED_FILENAME}'
#===============================Exam Results
def view_student_marks():
    admission_no = session.get('admission_no')
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT * FROM Examinations
        WHERE admission_no = ?
        ''',(admission_no,))
    result = cursor.fetchall()
    return result

if __name__ == '__main__':
    if not os.path.exists('static/uploads'):
        os.makedirs('static/uploads')
    database.add_all_tables()
    app.run(debug=True)
