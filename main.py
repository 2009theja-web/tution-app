import sqlite3
import hashlib
from datetime import date
from pathlib import Path

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup


DB_NAME = "student_app.db"


def hash_password(password):
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


def create_database():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            phone TEXT NOT NULL,
            course TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            attendance_date TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            total_fee REAL NOT NULL,
            paid_fee REAL NOT NULL,
            pending_fee REAL NOT NULL,
            payment_date TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


class StyledLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(0.07, 0.09, 0.14, 1)
            self.bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[18]
            )

        self.bind(
            pos=self._update_bg,
            size=self._update_bg
        )

    def _update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size


class StyledButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0.10, 0.45, 0.75, 1)
        self.color = (1, 1, 1, 1)
        self.bold = True

        with self.canvas.before:
            Color(0.10, 0.45, 0.75, 1)
            self.bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[12]
            )

        self.bind(
            pos=self._update_bg,
            size=self._update_bg
        )

    def _update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size


class StyledTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.background_color = (0.12, 0.14, 0.20, 1)
        self.foreground_color = (1, 1, 1, 1)
        self.hint_text_color = (0.65, 0.68, 0.75, 1)
        self.cursor_color = (1, 1, 1, 1)
        self.padding = [14, 14, 14, 14]



class TuitionApp(App):

    def build(self):
        Window.clearcolor = (0.04, 0.05, 0.08, 1)

        create_database()

        connection = sqlite3.connect(DB_NAME)
        cursor = connection.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM admins"
        )

        admin_count = cursor.fetchone()[0]

        connection.close()

        if admin_count == 0:
            self.create_account_screen()
        else:
            self.login_screen()

        return self.main_layout

    # ==========================================
    # CREATE ACCOUNT
    # ==========================================

    def create_account_screen(self):

        self.main_layout = StyledLayout(
            orientation="vertical",
            padding=30,
            spacing=15
        )

        title = Label(
            text="TUITION MANAGEMENT",
            font_size=30,
            color=(0.90, 0.95, 1, 1),
            size_hint_y=None,
            height=70
        )

        subtitle = Label(
            text="CREATE ADMIN ACCOUNT",
            font_size=22,
            color=(0.70, 0.85, 1, 1),
            size_hint_y=None,
            height=50
        )

        self.create_username = StyledTextInput(
            hint_text="Create Username",
            multiline=False,
            size_hint_y=None,
            height=55
        )

        self.create_password = StyledTextInput(
            hint_text="Create Password",
            password=True,
            multiline=False,
            size_hint_y=None,
            height=55
        )

        self.confirm_password = StyledTextInput(
            hint_text="Confirm Password",
            password=True,
            multiline=False,
            size_hint_y=None,
            height=55
        )

        create_button = StyledButton(
            text="CREATE ACCOUNT",
            font_size=19,
            size_hint_y=None,
            height=60
        )

        create_button.bind(
            on_press=self.save_admin
        )

        self.main_layout.add_widget(title)
        self.main_layout.add_widget(subtitle)
        self.main_layout.add_widget(
            self.create_username
        )
        self.main_layout.add_widget(
            self.create_password
        )
        self.main_layout.add_widget(
            self.confirm_password
        )
        self.main_layout.add_widget(
            create_button
        )

    def save_admin(self, instance):

        username = self.create_username.text.strip()
        password = self.create_password.text
        confirm = self.confirm_password.text

        if username == "":
            self.show_message(
                "Please enter username."
            )
            return

        if password == "":
            self.show_message(
                "Please enter password."
            )
            return

        if len(password) < 4:
            self.show_message(
                "Password must contain at least 4 characters."
            )
            return

        if password != confirm:
            self.show_message(
                "Passwords do not match."
            )
            return

        connection = sqlite3.connect(DB_NAME)
        cursor = connection.cursor()

        try:

            cursor.execute("""
                INSERT INTO admins
                (username, password)
                VALUES (?, ?)
            """, (
                username,
                hash_password(password)
            ))

            connection.commit()
            connection.close()

            self.show_message(
                "Account created successfully."
            )

            self.login_screen()

        except sqlite3.IntegrityError:

            connection.close()

            self.show_message(
                "Username already exists."
            )

    # ==========================================
    # LOGIN
    # ==========================================

    def login_screen(self):

        self.main_layout = StyledLayout(
            orientation="vertical",
            padding=30,
            spacing=15
        )

        title = Label(
            text="TUITION MANAGEMENT",
            font_size=30,
            color=(0.90, 0.95, 1, 1),
            size_hint_y=None,
            height=70
        )

        subtitle = Label(
            text="ADMIN LOGIN",
            font_size=23,
            size_hint_y=None,
            height=50
        )

        self.login_username = StyledTextInput(
            hint_text="Username",
            multiline=False,
            size_hint_y=None,
            height=55
        )

        self.login_password = StyledTextInput(
            hint_text="Password",
            password=True,
            multiline=False,
            size_hint_y=None,
            height=55
        )

        login_button = StyledButton(
            text="LOGIN",
            font_size=20,
            size_hint_y=None,
            height=60
        )

        login_button.bind(
            on_press=self.check_login
        )

        self.main_layout.add_widget(title)
        self.main_layout.add_widget(subtitle)
        self.main_layout.add_widget(
            self.login_username
        )
        self.main_layout.add_widget(
            self.login_password
        )
        self.main_layout.add_widget(
            login_button
        )

    def check_login(self, instance):

        username = self.login_username.text.strip()
        password = self.login_password.text

        if username == "":
            self.show_message(
                "Enter username."
            )
            return

        if password == "":
            self.show_message(
                "Enter password."
            )
            return

        connection = sqlite3.connect(DB_NAME)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id
            FROM admins
            WHERE username = ?
            AND password = ?
        """, (
            username,
            hash_password(password)
        ))

        result = cursor.fetchone()

        connection.close()

        if result:

            self.home_screen()

        else:

            self.show_message(
                "Wrong username or password."
            )

    # ==========================================
    # HOME / DASHBOARD
    # ==========================================

    def home_screen(self):

        self.main_layout.clear_widgets()

        title = Label(
            text="STUDENT MANAGEMENT",
            font_size=38,
            size_hint_y=None,
            height=60
        )

        self.main_layout.add_widget(title)

        dashboard = Label(
            text="DASHBOARD",
            font_size=23,
            size_hint_y=None,
            height=45
        )

        self.main_layout.add_widget(dashboard)

        self.total_label = Label(
            text="Total Students: 0",
            font_size=21,
            size_hint_y=None,
            height=40
        )

        self.present_label = Label(
            text="Present Today: 0",
            font_size=21,
            size_hint_y=None,
            height=40
        )

        self.absent_label = Label(
            text="Absent Today: 0",
            font_size=21,
            size_hint_y=None,
            height=40
        )

        self.percent_label = Label(
            text="Today's Attendance: 0%",
            font_size=21,
            size_hint_y=None,
            height=40
        )

        self.main_layout.add_widget(
            self.total_label
        )
        self.main_layout.add_widget(
            self.present_label
        )
        self.main_layout.add_widget(
            self.absent_label
        )
        self.main_layout.add_widget(
            self.percent_label
        )

        self.update_dashboard()

        buttons = [
            ("Add Student", self.add_student),
            ("View Students", self.view_students),
            ("Search Student", self.search_student),
            ("Student Profile", self.student_profile),
            ("Edit Student", self.edit_student),
            ("Delete Student", self.delete_student),
            ("Mark Attendance", self.mark_attendance),
            ("View Attendance", self.view_attendance),
            ("Attendance Summary", self.attendance_summary),
            ("FEES", self.fees),
            ("MONTHLY REPORT", self.monthly_report),
            ("BACKUP DATA", self.backup_data),
            ("PARENT CONTACT", self.parent_contact),
            ("Refresh Dashboard", self.update_dashboard),
            ("Logout", self.logout)
        ]

        for text, function in buttons:

            button = StyledButton(
                text=text,
                font_size=18,
                size_hint_y=None,
                height=52
            )

            button.bind(
                on_press=function
            )

            self.main_layout.add_widget(button)

    # ==========================================
    # DASHBOARD UPDATE
    # ==========================================

    def update_dashboard(self, instance=None):

        connection = sqlite3.connect(DB_NAME)
        cursor = connection.cursor()

        today = str(date.today())

        cursor.execute(
            "SELECT COUNT(*) FROM students"
        )

        total = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM attendance
            WHERE attendance_date = ?
            AND status = 'Present'
        """, (today,))

        present = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM attendance
            WHERE attendance_date = ?
            AND status = 'Absent'
        """, (today,))

        absent = cursor.fetchone()[0]

        connection.close()

        marked = present + absent

        if marked > 0:
            percentage = (
                present / marked
            ) * 100
        else:
            percentage = 0

        self.total_label.text = (
            f"Total Students: {total}"
        )

        self.present_label.text = (
            f"Present Today: {present}"
        )

        self.absent_label.text = (
            f"Absent Today: {absent}"
        )

        self.percent_label.text = (
            f"Today's Attendance: {percentage:.1f}%"
        )

    # ==========================================
    # ADD STUDENT
    # ==========================================

    def add_student(self, instance):

        layout = StyledLayout(
            orientation="vertical",
            padding=15,
            spacing=10
        )

        name = StyledTextInput(
            hint_text="Student Name"
        )

        age = StyledTextInput(
            hint_text="Age",
            input_filter="int"
        )

        phone = StyledTextInput(
            hint_text="Phone"
        )

        course = StyledTextInput(
            hint_text="Course"
        )

        save = StyledButton(
            text="SAVE STUDENT",
            size_hint_y=None,
            height=55
        )

        layout.add_widget(name)
        layout.add_widget(age)
        layout.add_widget(phone)
        layout.add_widget(course)
        layout.add_widget(save)

        popup = Popup(
            title="Add Student",
            content=layout,
            size_hint=(0.9, 0.8)
        )

        def save_student(instance):

            if not name.text.strip():
                self.show_message(
                    "Enter student name."
                )
                return

            if not age.text.strip():
                self.show_message(
                    "Enter age."
                )
                return

            if not phone.text.strip():
                self.show_message(
                    "Enter phone."
                )
                return

            if not course.text.strip():
                self.show_message(
                    "Enter course."
                )
                return

            connection = sqlite3.connect(DB_NAME)
            cursor = connection.cursor()

            cursor.execute("""
                INSERT INTO students
                (name, age, phone, course)
                VALUES (?, ?, ?, ?)
            """, (
                name.text.strip(),
                int(age.text),
                phone.text.strip(),
                course.text.strip()
            ))

            connection.commit()
            connection.close()

            popup.dismiss()

            self.update_dashboard()

            self.show_message(
                "Student added successfully."
            )

        save.bind(
            on_press=save_student
        )

        popup.open()

    # ==========================================
    # VIEW STUDENTS
    # ==========================================

    def view_students(self, instance):

        connection = sqlite3.connect(DB_NAME)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, name, age, phone, course
            FROM students
            ORDER BY id DESC
        """)

        students = cursor.fetchall()

        connection.close()

        text = ""

        for student in students:

            text += (
                f"ID: {student[0]}\n"
                f"Name: {student[1]}\n"
                f"Age: {student[2]}\n"
                f"Phone: {student[3]}\n"
                f"Course: {student[4]}\n"
                "--------------------\n"
            )

        if text == "":
            text = "No students found."

        Popup(
            title="Student List",
            content=Label(text=text),
            size_hint=(0.9, 0.8)
        ).open()

    # ==========================================
    # SEARCH STUDENT
    # ==========================================

    def search_student(self, instance):

        layout = StyledLayout(
            orientation="vertical",
            padding=15,
            spacing=10
        )

        search_box = StyledTextInput(
            hint_text="Student Name"
        )

        search_button = StyledButton(
            text="SEARCH",
            size_hint_y=None,
            height=55
        )

        layout.add_widget(search_box)
        layout.add_widget(search_button)

        popup = Popup(
            title="Search Student",
            content=layout,
            size_hint=(0.9, 0.5)
        )

        def search(instance):

            connection = sqlite3.connect(DB_NAME)
            cursor = connection.cursor()

            cursor.execute("""
                SELECT id, name, age, phone, course
                FROM students
                WHERE name LIKE ?
            """, (
                "%" + search_box.text.strip() + "%",
            ))

            students = cursor.fetchall()

            connection.close()

            text = ""

            for student in students:

                text += (
                    f"ID: {student[0]}\n"
                    f"Name: {student[1]}\n"
                    f"Age: {student[2]}\n"
                    f"Phone: {student[3]}\n"
                    f"Course: {student[4]}\n"
                    "--------------------\n"
                )

            if text == "":
                text = "Student not found."

            Popup(
                title="Search Result",
                content=Label(text=text),
                size_hint=(0.9, 0.7)
            ).open()

        search_button.bind(
            on_press=search
        )

        popup.open()

    # ==========================================
    # STUDENT PROFILE
    # ==========================================

    def student_profile(self, instance):

        self.ask_student_id(
            "Student Profile",
            self.show_profile
        )

    def show_profile(self, student_id):

        connection = sqlite3.connect(DB_NAME)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, name, age, phone, course
            FROM students
            WHERE id = ?
        """, (student_id,))

        student = cursor.fetchone()

        if not student:

            connection.close()

            self.show_message(
                "Student ID not found."
            )

            return

        cursor.execute("""
            SELECT
                COUNT(*),
                SUM(
                    CASE
                        WHEN status = 'Present'
                        THEN 1
                        ELSE 0
                    END
                ),
                SUM(
                    CASE
                        WHEN status = 'Absent'
                        THEN 1
                        ELSE 0
                    END
                )
            FROM attendance
            WHERE student_id = ?
        """, (student_id,))

        result = cursor.fetchone()

        connection.close()

        total = result[0] or 0
        present = result[1] or 0
        absent = result[2] or 0

        percentage = (
            present / total * 100
            if total > 0 else 0
        )

        text = (
            "STUDENT PROFILE\n\n"
            f"ID: {student[0]}\n"
            f"Name: {student[1]}\n"
            f"Age: {student[2]}\n"
            f"Phone: {student[3]}\n"
            f"Course: {student[4]}\n\n"
            "ATTENDANCE\n\n"
            f"Total Days: {total}\n"
            f"Present: {present}\n"
            f"Absent: {absent}\n"
            f"Attendance: {percentage:.1f}%"
        )

        Popup(
            title="Student Profile",
            content=Label(text=text),
            size_hint=(0.9, 0.8)
        ).open()

    # ==========================================
    # STUDENT ID POPUP
    # ==========================================

    def ask_student_id(self, title, callback):

        layout = StyledLayout(
            orientation="vertical",
            padding=15,
            spacing=10
        )

        student_id = StyledTextInput(
            hint_text="Student ID",
            input_filter="int"
        )

        open_button = StyledButton(
            text="OPEN",
            size_hint_y=None,
            height=55
        )

        layout.add_widget(student_id)
        layout.add_widget(open_button)

        popup = Popup(
            title=title,
            content=layout,
            size_hint=(0.9, 0.5)
        )

        def open_result(instance):

            if not student_id.text:
                self.show_message(
                    "Enter Student ID."
                )
                return

            popup.dismiss()

            callback(
                int(student_id.text)
            )

        open_button.bind(
            on_press=open_result
        )

        popup.open()

    # ==========================================
    # EDIT STUDENT
    # ==========================================

    def edit_student(self, instance):

        layout = StyledLayout(
            orientation="vertical",
            padding=15,
            spacing=10
        )

        student_id = StyledTextInput(
            hint_text="Student ID",
            input_filter="int"
        )

        name = StyledTextInput(
            hint_text="New Name"
        )

        age = StyledTextInput(
            hint_text="New Age",
            input_filter="int"
        )

        phone = StyledTextInput(
            hint_text="New Phone"
        )

        course = StyledTextInput(
            hint_text="New Course"
        )

        update = StyledButton(
            text="UPDATE",
            size_hint_y=None,
            height=55
        )

        layout.add_widget(student_id)
        layout.add_widget(name)
        layout.add_widget(age)
        layout.add_widget(phone)
        layout.add_widget(course)
        layout.add_widget(update)

        popup = Popup(
            title="Edit Student",
            content=layout,
            size_hint=(0.9, 0.85)
        )

        def update_student(instance):

            if not all([
                student_id.text,
                name.text.strip(),
                age.text.strip(),
                phone.text.strip(),
                course.text.strip()
            ]):
                self.show_message(
                    "Fill all details."
                )
                return

            connection = sqlite3.connect(DB_NAME)
            cursor = connection.cursor()

            cursor.execute("""
                UPDATE students
                SET name=?, age=?, phone=?, course=?
                WHERE id=?
            """, (
                name.text.strip(),
                int(age.text),
                phone.text.strip(),
                course.text.strip(),
                int(student_id.text)
            ))

            changed = cursor.rowcount

            connection.commit()
            connection.close()

            popup.dismiss()

            if changed:
                self.show_message(
                    "Student updated successfully."
                )
            else:
                self.show_message(
                    "Student ID not found."
                )

        update.bind(
            on_press=update_student
        )

        popup.open()

    # ==========================================
    # DELETE STUDENT
    # ==========================================

    def delete_student(self, instance):

        layout = StyledLayout(
            orientation="vertical",
            padding=15,
            spacing=10
        )

        student_id = StyledTextInput(
            hint_text="Student ID",
            input_filter="int"
        )

        delete = StyledButton(
            text="DELETE STUDENT",
            size_hint_y=None,
            height=55
        )

        layout.add_widget(student_id)
        layout.add_widget(delete)

        popup = Popup(
            title="Delete Student",
            content=layout,
            size_hint=(0.9, 0.5)
        )

        def delete_student_data(instance):

            if not student_id.text:
                self.show_message(
                    "Enter Student ID."
                )
                return

            connection = sqlite3.connect(DB_NAME)
            cursor = connection.cursor()

            cursor.execute(
                "DELETE FROM students WHERE id=?",
                (int(student_id.text),)
            )

            deleted = cursor.rowcount

            connection.commit()
            connection.close()

            popup.dismiss()

            if deleted:

                self.update_dashboard()

                self.show_message(
                    "Student deleted."
                )

            else:

                self.show_message(
                    "Student ID not found."
                )

        delete.bind(
            on_press=delete_student_data
        )

        popup.open()

    # ==========================================
    # MARK ATTENDANCE
    # ==========================================

    def mark_attendance(self, instance):

        layout = StyledLayout(
            orientation="vertical",
            padding=15,
            spacing=10
        )

        student_id = StyledTextInput(
            hint_text="Student ID",
            input_filter="int"
        )

        attendance_date = StyledTextInput(
            text=str(date.today()),
            hint_text="YYYY-MM-DD"
        )

        present = StyledButton(
            text="PRESENT",
            size_hint_y=None,
            height=55
        )

        absent = StyledButton(
            text="ABSENT",
            size_hint_y=None,
            height=55
        )

        layout.add_widget(student_id)
        layout.add_widget(attendance_date)
        layout.add_widget(present)
        layout.add_widget(absent)

        popup = Popup(
            title="Mark Attendance",
            content=layout,
            size_hint=(0.9, 0.7)
        )

        def save_attendance(status):

            if not student_id.text:
                self.show_message(
                    "Enter Student ID."
                )
                return

            connection = sqlite3.connect(DB_NAME)
            cursor = connection.cursor()

            cursor.execute(
                "SELECT name FROM students WHERE id=?",
                (int(student_id.text),)
            )

            student = cursor.fetchone()

            if not student:

                connection.close()

                self.show_message(
                    "Student ID not found."
                )

                return

            cursor.execute("""
                SELECT id
                FROM attendance
                WHERE student_id=?
                AND attendance_date=?
            """, (
                int(student_id.text),
                attendance_date.text.strip()
            ))

            existing = cursor.fetchone()

            if existing:

                cursor.execute("""
                    UPDATE attendance
                    SET status=?
                    WHERE id=?
                """, (
                    status,
                    existing[0]
                ))

            else:

                cursor.execute("""
                    INSERT INTO attendance
                    (student_id, attendance_date, status)
                    VALUES (?, ?, ?)
                """, (
                    int(student_id.text),
                    attendance_date.text.strip(),
                    status
                ))

            connection.commit()
            connection.close()

            popup.dismiss()

            self.update_dashboard()

            self.show_message(
                f"{student[0]} marked {status}."
            )

        present.bind(
            on_press=lambda x:
            save_attendance("Present")
        )

        absent.bind(
            on_press=lambda x:
            save_attendance("Absent")
        )

        popup.open()

    # ==========================================
    # VIEW ATTENDANCE
    # ==========================================

    def view_attendance(self, instance):

        connection = sqlite3.connect(DB_NAME)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                attendance.student_id,
                students.name,
                attendance.attendance_date,
                attendance.status
            FROM attendance
            INNER JOIN students
            ON attendance.student_id = students.id
            ORDER BY attendance.attendance_date DESC
        """)

        records = cursor.fetchall()

        connection.close()

        text = ""

        for record in records:

            text += (
                f"ID: {record[0]}\n"
                f"Name: {record[1]}\n"
                f"Date: {record[2]}\n"
                f"Status: {record[3]}\n"
                "--------------------\n"
            )

        if text == "":
            text = "No attendance records."

        Popup(
            title="Attendance Records",
            content=Label(text=text),
            size_hint=(0.9, 0.85)
        ).open()

    # ==========================================
    # ATTENDANCE SUMMARY
    # ==========================================

    def attendance_summary(self, instance):

        self.ask_student_id(
            "Attendance Summary",
            self.show_summary
        )

    def show_summary(self, student_id):

        connection = sqlite3.connect(DB_NAME)
        cursor = connection.cursor()

        cursor.execute(
            "SELECT name FROM students WHERE id=?",
            (student_id,)
        )

        student = cursor.fetchone()

        if not student:

            connection.close()

            self.show_message(
                "Student ID not found."
            )

            return

        cursor.execute("""
            SELECT
                COUNT(*),
                SUM(
                    CASE
                        WHEN status='Present'
                        THEN 1
                        ELSE 0
                    END
                ),
                SUM(
                    CASE
                        WHEN status='Absent'
                        THEN 1
                        ELSE 0
                    END
                )
            FROM attendance
            WHERE student_id=?
        """, (student_id,))

        result = cursor.fetchone()

        connection.close()

        total = result[0] or 0
        present = result[1] or 0
        absent = result[2] or 0

        percentage = (
            present / total * 100
            if total > 0 else 0
        )

        text = (
            f"Student ID: {student_id}\n"
            f"Name: {student[0]}\n\n"
            f"Total Days: {total}\n"
            f"Present: {present}\n"
            f"Absent: {absent}\n"
            f"Attendance: {percentage:.1f}%"
        )

        Popup(
            title="Attendance Summary",
            content=Label(text=text),
            size_hint=(0.9, 0.6)
        ).open()


    # ==========================================
    # PARENT CONTACT
    # ==========================================

    def parent_contact(self, instance):

        layout = StyledLayout(
            orientation="vertical",
            padding=15,
            spacing=10
        )

        student_id = StyledTextInput(
            hint_text="Student ID",
            input_filter="int",
            multiline=False
        )

        button = StyledButton(
            text="VIEW CONTACT",
            size_hint_y=None,
            height=55
        )

        layout.add_widget(student_id)
        layout.add_widget(button)

        popup = Popup(
            title="PARENT / STUDENT CONTACT",
            content=layout,
            size_hint=(0.9, 0.5)
        )

        def view_contact(instance):

            if not student_id.text:
                self.show_message("Enter Student ID.")
                return

            connection = sqlite3.connect(DB_NAME)
            cursor = connection.cursor()

            cursor.execute("""
                SELECT name, phone, course
                FROM students
                WHERE id=?
            """, (int(student_id.text),))

            student = cursor.fetchone()
            connection.close()

            if not student:
                self.show_message("Student ID not found.")
                return

            popup.dismiss()

            Popup(
                title="CONTACT DETAILS",
                content=Label(
                    text=(
                        f"Student: {student[0]}\n"
                        f"Phone: {student[1]}\n"
                        f"Course: {student[2]}"
                    )
                ),
                size_hint=(0.9, 0.5)
            ).open()

        button.bind(on_press=view_contact)

        popup.open()

    # ==========================================
    # BACKUP DATA
    # ==========================================

    def backup_data(self, instance):

        try:
            source = Path(DB_NAME)

            if not source.exists():
                self.show_message("Database file not found.")
                return

            backup_name = (
                "student_app_backup_"
                + date.today().strftime("%Y%m%d")
                + ".db"
            )

            backup_path = source.parent / backup_name

            connection = sqlite3.connect(DB_NAME)
            backup_connection = sqlite3.connect(str(backup_path))

            connection.backup(backup_connection)

            backup_connection.close()
            connection.close()

            self.show_message(
                "Backup created:\n" + str(backup_path)
            )

        except Exception as error:
            self.show_message(
                "Backup failed:\n" + str(error)
            )

    # ==========================================
    # MONTHLY REPORT
    # ==========================================

    def monthly_report(self, instance):

        layout = StyledLayout(
            orientation="vertical",
            padding=15,
            spacing=10
        )

        month = StyledTextInput(
            hint_text="Month (01-12)",
            input_filter="int",
            multiline=False
        )

        year = StyledTextInput(
            hint_text="Year (e.g. 2026)",
            input_filter="int",
            multiline=False
        )

        button = StyledButton(
            text="GENERATE REPORT",
            size_hint_y=None,
            height=55
        )

        layout.add_widget(month)
        layout.add_widget(year)
        layout.add_widget(button)

        popup = Popup(
            title="MONTHLY REPORT",
            content=layout,
            size_hint=(0.9, 0.6)
        )

        def generate(instance):

            if not month.text or not year.text:
                self.show_message("Enter month and year.")
                return

            m = int(month.text)
            y = int(year.text)

            if m < 1 or m > 12:
                self.show_message("Month must be between 1 and 12.")
                return

            connection = sqlite3.connect(DB_NAME)
            cursor = connection.cursor()

            month_text = f"{y:04d}-{m:02d}%"

            cursor.execute("""
                SELECT COUNT(*)
                FROM attendance
                WHERE attendance_date LIKE ?
            """, (month_text,))

            total_attendance = cursor.fetchone()[0] or 0

            cursor.execute("""
                SELECT COUNT(*)
                FROM attendance
                WHERE attendance_date LIKE ?
                AND status='Present'
            """, (month_text,))

            present = cursor.fetchone()[0] or 0

            cursor.execute("""
                SELECT COUNT(*)
                FROM attendance
                WHERE attendance_date LIKE ?
                AND status='Absent'
            """, (month_text,))

            absent = cursor.fetchone()[0] or 0

            cursor.execute("""
                SELECT COUNT(*)
                FROM students
            """)

            students = cursor.fetchone()[0] or 0

            cursor.execute("""
                SELECT
                    COALESCE(SUM(paid_fee), 0),
                    COALESCE(SUM(pending_fee), 0)
                FROM fees
            """)

            fees = cursor.fetchone()

            paid = fees[0] or 0
            pending = fees[1] or 0

            connection.close()

            percentage = (
                present / total_attendance * 100
                if total_attendance else 0
            )

            report = (
                f"MONTH: {m:02d}/{y}\n\n"
                f"Total Students: {students}\n\n"
                f"Attendance Records: {total_attendance}\n"
                f"Present: {present}\n"
                f"Absent: {absent}\n"
                f"Attendance Rate: {percentage:.1f}%\n\n"
                f"Fees Paid: ₹{paid:.2f}\n"
                f"Fees Pending: ₹{pending:.2f}"
            )

            popup.dismiss()

            Popup(
                title="MONTHLY REPORT",
                content=Label(text=report),
                size_hint=(0.9, 0.8)
            ).open()

        button.bind(on_press=generate)

        popup.open()

    # ==========================================
    # FEES
    # ==========================================

    def fees(self, instance):

        layout = StyledLayout(
            orientation="vertical",
            padding=15,
            spacing=10
        )

        student_id = StyledTextInput(
            hint_text="Student ID",
            input_filter="int"
        )

        total_fee = StyledTextInput(
            hint_text="Total Fee ₹",
            input_filter="float"
        )

        paid_fee = StyledTextInput(
            hint_text="Paid Amount ₹",
            input_filter="float"
        )

        save_button = StyledButton(
            text="SAVE FEE",
            size_hint_y=None,
            height=55
        )

        view_button = StyledButton(
            text="VIEW FEE",
            size_hint_y=None,
            height=55
        )

        layout.add_widget(student_id)
        layout.add_widget(total_fee)
        layout.add_widget(paid_fee)
        layout.add_widget(save_button)
        layout.add_widget(view_button)

        popup = Popup(
            title="FEES",
            content=layout,
            size_hint=(0.9, 0.75)
        )

        def save_fee(instance):

            if not student_id.text:
                self.show_message("Enter Student ID.")
                return

            if not total_fee.text or not paid_fee.text:
                self.show_message("Enter total fee and paid amount.")
                return

            total = float(total_fee.text)
            paid = float(paid_fee.text)

            if total < 0 or paid < 0:
                self.show_message("Fee cannot be negative.")
                return

            if paid > total:
                self.show_message(
                    "Paid amount cannot be greater than total fee."
                )
                return

            connection = sqlite3.connect(DB_NAME)
            cursor = connection.cursor()

            cursor.execute(
                "SELECT name FROM students WHERE id=?",
                (int(student_id.text),)
            )

            student = cursor.fetchone()

            if not student:
                connection.close()
                self.show_message("Student ID not found.")
                return

            pending = total - paid

            cursor.execute("""
                SELECT id FROM fees
                WHERE student_id=?
            """, (int(student_id.text),))

            old = cursor.fetchone()

            if old:
                cursor.execute("""
                    UPDATE fees
                    SET total_fee=?,
                        paid_fee=?,
                        pending_fee=?,
                        payment_date=?
                    WHERE id=?
                """, (
                    total,
                    paid,
                    pending,
                    str(date.today()),
                    old[0]
                ))
            else:
                cursor.execute("""
                    INSERT INTO fees
                    (student_id, total_fee, paid_fee,
                     pending_fee, payment_date)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    int(student_id.text),
                    total,
                    paid,
                    pending,
                    str(date.today())
                ))

            connection.commit()
            connection.close()

            self.show_message(
                f"Fee saved for {student[0]}."
            )

        def view_fee(instance):

            if not student_id.text:
                self.show_message("Enter Student ID.")
                return

            connection = sqlite3.connect(DB_NAME)
            cursor = connection.cursor()

            cursor.execute("""
                SELECT
                    students.name,
                    fees.total_fee,
                    fees.paid_fee,
                    fees.pending_fee,
                    fees.payment_date
                FROM fees
                INNER JOIN students
                ON fees.student_id = students.id
                WHERE fees.student_id=?
            """, (int(student_id.text),))

            result = cursor.fetchone()
            connection.close()

            if not result:
                self.show_message("Fee record not found.")
                return

            status = "PAID" if result[3] == 0 else "PENDING"

            text = (
                f"Name: {result[0]}\n\n"
                f"Total Fee: ₹{result[1]:.2f}\n"
                f"Paid: ₹{result[2]:.2f}\n"
                f"Pending: ₹{result[3]:.2f}\n"
                f"Date: {result[4]}\n"
                f"Status: {status}"
            )

            Popup(
                title="FEE DETAILS",
                content=Label(text=text),
                size_hint=(0.9, 0.65)
            ).open()

        save_button.bind(on_press=save_fee)
        view_button.bind(on_press=view_fee)

        popup.open()

    # ==========================================
    # LOGOUT
    # ==========================================

    def logout(self, instance):

        self.login_screen()

    # ==========================================
    # MESSAGE
    # ==========================================

    def show_message(self, message):

        Popup(
            title="Tuition App",
            content=Label(text=message),
            size_hint=(0.8, 0.3)
        ).open()


if __name__ == "__main__":
    TuitionApp().run()
