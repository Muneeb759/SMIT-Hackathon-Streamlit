import re

class Student():
    def __init__(self, student_id, name, age, grade, email, phone, attendance=100.0):
        # Validate and set student_id
        if not student_id or not isinstance(student_id, str) or not student_id.strip():
            raise ValueError("Student ID is required and must be a non-empty string")
        self.student_id = student_id.strip()
        
        # Validate and set name
        if not name or not isinstance(name, str) or not name.strip():
            raise ValueError("Name is required and must be a non-empty string")
        if not re.match(r'^[a-zA-Z\s]+$', name.strip()):
            raise ValueError("Name must contain only letters and spaces")
        self.name = name.strip()
        
        # Validate and set age
        if not isinstance(age, (int, float)):
            raise ValueError("Age must be a number")
        age = int(age)
        if age < 1 or age > 100:
            raise ValueError("Age must be between 1 and 100")
        self.age = age
        
        # Validate and set grade
        valid_grades = ['A', 'B', 'C', 'D', 'E', 'F']
        if grade not in valid_grades:
            raise ValueError(f"Grade must be one of {valid_grades}")
        self.grade = grade
        
        # Validate and set email
        if not email or not isinstance(email, str):
            raise ValueError("Email is required and must be a string")
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email.strip()):
            raise ValueError("Invalid email format. Please use format: user@example.com")
        self.email = email.strip().lower()
        
        # Validate and set phone
        if not phone or not isinstance(phone, str):
            raise ValueError("Phone is required and must be a string")
        # Remove common separators for validation
        phone_digits = re.sub(r'[\s\-\(\)]+', '', phone.strip())
        if not re.match(r'^[\+]?[0-9]{11}$', phone_digits):
            raise ValueError("Phone must contain only digits (11 digits), optionally with + prefix. No alphabets allowed")
        self.phone = phone.strip()
        
        # Validate and set attendance
        if not isinstance(attendance, (int, float)):
            raise ValueError("Attendance must be a number")
        if attendance < 0 or attendance > 100:
            raise ValueError("Attendance must be between 0 and 100")
        self.attendance = float(attendance)
        
        self.courses = []
    
    def add_course(self, course):
        if course not in self.courses:
            self.courses.append(course)
    
    def remove_course(self, course):
        if course in self.courses:
            self.courses.remove(course)
    
    def to_dict(self):
        return {
            'student_id': self.student_id,
            'name': self.name,
            'age': self.age,
            'grade': self.grade,
            'email': self.email,
            'phone': self.phone,
            'courses': self.courses,
            'attendance': self.attendance
        }
    
    def __str__(self):
        return f"ID: {self.student_id}, Name: {self.name}, Age: {self.age}, Grade: {self.grade}"
