import database
import sqlite3
# database.add_someone("EB3/57373/21","KEITH","RICHARD","MUMO","MALE",22)
# database.delete_student('EB3/56373/21')
# # # database.add_logins()
# #
# # database.add_someone("EB3/57222/21","KASYOKI","MULE","KYULE","MALE",23)
# #
# # database.add_someone("EB3/55555/21","NATALIE","REBECA","MUIRO","FEMALE",21)
#
# data = database.get_students_and_subjects()
# print(data)
# import sqlite3
# def add_average_column():
#     with sqlite3.connect('student.db') as conn:
#         cursor = conn.cursor()
#
#         # Adding the 'average' column to the 'subjects' table
#         cursor.execute('''
#             ALTER TABLE subjects
#             ADD COLUMN average REAL
#         ''')
#         conn.commit()
#
# add_average_column()
#
#
# def calculate_and_store_averages():
#     with sqlite3.connect('student.db') as conn:
#         cursor = conn.cursor()
#
#         # Fetch all students and their marks
#         cursor.execute('''
#             SELECT admission_no, Mathematics, Biology, Chemistry, Physics, Geography,
#                    Business, English, Kiswahili, CRE, French
#             FROM subjects
#         ''')
#         students = cursor.fetchall()
#
#         # Calculate the average for each student and update the 'average' column
#         for student in students:
#             admission_no = student[0]
#             marks = student[1:]  # Exclude admission_no
#             valid_marks = [mark for mark in marks if mark is not None]  # Remove None values
#             if valid_marks:
#                 average = sum(valid_marks) / len(valid_marks)
#             else:
#                 average = None
#
#             # Update the 'average' column in the database
#             cursor.execute('''
#                 UPDATE subjects
#                 SET average = ?
#                 WHERE admission_no = ?
#             ''', (average, admission_no))
#
#         conn.commit()
#
# # Call the function to calculate and store the averages
# calculate_and_store_averages()
#database.add_login("EB3/57373/21","Keith99!!")
#database.add_all_tables()
#database.add_admin_data1("Lecturer","Mutina","WuWu","Magigi","Male",45)
#database.add_admin_login1("Lecturer","Keith99!!")
#database.add_all_tables()
# database.set_fee('EB3/57373/21',20000,'2024-04-01',6000)
# check=database.student_exist('EB3/5373/21')
# if check:
#     print('found')
# database.insert_non_compliant_students('EB3/57373/21','2023-09-03','2023-09-20','2 weeks','Eating alot','reported')
# database.insert_non_compliant_students('EB3/59843/21','2024-06-02','','3 weeks','walking Here and There','absent')
#data = database.get_all_students_exams()
# print(data)
# #database.set_average('EB3/57373/21')
# data = database.get_students_marks_filtered(2024,2,'mid-term','form4')
# print(data)
#database.add_level('EB3/21702688/21',grade='form4')
# database.insert_marks('EB3/57373/21',[23,45,66,78,89,90,99,87,96,10])
#database.set_average('EB3/55555/21')
# from intasend import APIService
#
# publishable_key = "INTASEND_PUBLISHABLE_KEY"
#
# service = APIService(token=token,publishable_key=publishable_key)
#
# response = service.collect.mpesa_stk_push(phone_number=254759843995,
#                                   email="joe@doe.com", amount=10, narrative="Purchase")
# print(response)
# import requests
# from requests.auth import HTTPBasicAuth
#
# # Replace these with your actual credentials
# consumer_key = ' sTFmEBfTSz6jg0AOFuB2GoSvy3sFMSIPXBRIcDYdZGu3KfzH'
# consumer_secret = ' iiT9sSspIQHp8Po4Gvv7zIl5k1yfeGqSNZrF50IiZ7GGeDHt5R0JWlBG1mA59V4Z'
#
# api_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
#
#
# response = requests.get(api_url, auth=HTTPBasicAuth(consumer_key, consumer_secret))
#
# if response.status_code == 200:
#     access_token = response.json()['access_token']
#     print(f"Access Token: {access_token}")
# else:
#     print(f"Failed to get access token: {response.status_code}")
#     print(f"Response Text: {response.text}")
# def truncate_table(db_path, table_name):
#     try:
#         # Connect to the SQLite database
#         conn = sqlite3.connect(db_path)
#         cursor = conn.cursor()
#
#         # Execute the DELETE statement to remove all rows
#         cursor.execute(f"DELETE FROM {table_name};")
#
#         # Optionally, reset the auto-increment counter (if applicable)
#         cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table_name}';")
#
#         # Commit the transaction
#         conn.commit()
#
#         print(f"Table {table_name} has been truncated.")
#
#     except sqlite3.Error as e:
#         print(f"An error occurred: {e}")
#
#     finally:
#         # Close the connection
#         if conn:
#             conn.close()
#
# # Example usage
# truncate_table('student.db', 'Examinations')
# database.add_manager('kay','1234')
# database.setup_database()
# Function to insert student data and set the initial fee balance

# Add a student


# with sqlite3.connect('fees.db') as conn:
#     cursor = conn.cursor()
#     def insert_student(admission_no, first_name, last_name, total_fee):
#         cursor.execute('''
#             INSERT INTO fees (admission_no, total_fee, balance_amount)
#             VALUES (?, ?, ?)
#         ''', (admission_no, total_fee, total_fee))
#
#         conn.commit()
#         print(f"Student {first_name} {last_name} added with a fee balance of {total_fee}.")
#
# insert_student('EB3/55555/21', 'John',  'Doe', 50000)
# data = database.get_students_with_balance()
# print(data)
# database.insert_marks('EB3/57373/21',[30,50,77,99,22,66,72,99,23,50])
# database.insert_time('EB3/57373/21',2024,2,'mid-term')
# database.insert_marks('EB3/55555/21',[60,34,67,90,45,67,98,66,5,59])
# database.insert_time('EB3/55555/21',2024,2,'mid-term')
#
# database.insert_marks('EB3/57222/21',[30,50,77,99,22,66,72,99,23,50])
# database.insert_time('EB3/57222/21',2024,2,'mid-term')

# database.add_level('EB3/59843/21','form2')
# import sqlite3
#
# def add_phone_number_column(db_path, table_name):
#     # Connect to the SQLite database
#     conn = sqlite3.connect(db_path)
#     cursor = conn.cursor()
#
#     # SQL command to add a new column "phone_number"
#     alter_table_query = f'''
#     ALTER TABLE {table_name}
#     ADD COLUMN phone_number TEXT;
#     '''
#
#     try:
#         # Execute the query to add the column
#         cursor.execute(alter_table_query)
#         conn.commit()
#         print(f"'phone_number' column added successfully to the {table_name} table.")
#     except sqlite3.OperationalError as e:
#         # If the column already exists or another error occurs, catch the exception
#         print(f"An error occurred: {e}")
#     finally:
#         # Close the connection
#         conn.close()
#
# # Example usage:
# db_path = 'student.db'  # Path to your SQLite database file
# table_name = 'rest'       # Name of the table to add the column to
# add_phone_number_column(db_path, table_name)
import app2
# import sqlite3
data=app2.view_student_marks('EB3/57373/21')
print(data)
# def delete_exam_records(admission_no, year, term):
#     with sqlite3.connect('student.db') as conn:
#         cursor = conn.cursor()
#
#         # SQL query to delete records based on admission_no, year, and term
#         query = '''
#             DELETE FROM Examinations
#             WHERE admission_no = ? AND year = ? AND term = ?
#         '''
#
#         # Execute the query
#         cursor.execute(query, (admission_no, year, term))
#         conn.commit()
#
#         if cursor.rowcount > 0:
#             print(f"Records for admission_no {admission_no}, year {year}, term {term} deleted successfully.")
#         else:
#             print(f"No records found for admission_no {admission_no}, year {year}, term {term}.")
# delete_exam_records('EB3/57373/21',2024,2)