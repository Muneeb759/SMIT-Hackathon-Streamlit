import json
import os
from models import Student


class Manager():
    def __init__(self):
        self.students = {}
    
    def add_student(self, student):
        """Add a new student"""
        if student.student_id in self.students:
            return False, "Student ID already exists"
        self.students[student.student_id] = student
        return True, "Student added successfully"
    
    def update_student(self, student_id, **kwargs):
        """Update student information"""
        if student_id not in self.students:
            return False, "Student not found"
        
        student = self.students[student_id]
        
        # Validate before updating
        try:
            # Create a temporary student object with updated values to validate
            temp_data = {
                'student_id': student_id,
                'name': kwargs.get('name', student.name),
                'age': kwargs.get('age', student.age),
                'grade': kwargs.get('grade', student.grade),
                'email': kwargs.get('email', student.email),
                'phone': kwargs.get('phone', student.phone),
                'attendance': kwargs.get('attendance', student.attendance)
            }
            # This will raise ValueError if validation fails
            temp_student = Student(**temp_data)
            
            # If validation passes, update the actual student
            for key, value in kwargs.items():
                if hasattr(student, key):
                    setattr(student, key, value)
            return True, "Student updated successfully"
        except ValueError as e:
            return False, f"Validation error: {str(e)}"
    
    def delete_student(self, student_id):
        """Delete a student"""
        if student_id not in self.students:
            return False, "Student not found"
        del self.students[student_id]
        return True, "Student deleted successfully"
    
    def get_student(self, student_id):
        """Get a specific student"""
        return self.students.get(student_id)
    
    def list_students(self):
        """List all students"""
        return list(self.students.values())
    
    def search_students(self, **filters):
        """Search students by various criteria"""
        results = []
        for student in self.students.values():
            match = True
            for key, value in filters.items():
                if key == 'name' and value.lower() not in student.name.lower():
                    match = False
                    break
                elif key == 'grade' and student.grade != value:
                    match = False
                    break
                elif key == 'age' and student.age != value:
                    match = False
                    break
            if match:
                results.append(student)
        return results


class DataStorage:
    def __init__(self, json_file='students.json'):
        self.json_file = json_file
    
    def save_to_json(self, manager):
        """Save students data to JSON file"""
        data = {sid: student.to_dict() for sid, student in manager.students.items()}
        with open(self.json_file, 'w') as f:
            json.dump(data, f, indent=4)
    
    def load_from_json(self, manager):
        """Load students data from JSON file"""
        if not os.path.exists(self.json_file):
            return
        
        try:
            with open(self.json_file, 'r') as f:
                data = json.load(f)
            
            for student_id, student_data in data.items():
                try:
                    student = Student(
                        student_data['student_id'],
                        student_data['name'],
                        student_data['age'],
                        student_data['grade'],
                        student_data['email'],
                        student_data['phone'],
                        student_data.get('attendance', 100.0)
                    )
                    student.courses = student_data.get('courses', [])
                    manager.students[student.student_id] = student
                except (ValueError, KeyError) as e:
                    # Skip invalid student records and log the error
                    print(f"Warning: Skipping invalid student record {student_id}: {str(e)}")
                    continue
        except json.JSONDecodeError as e:
            print(f"Error: Failed to load JSON file: {str(e)}")
            return
