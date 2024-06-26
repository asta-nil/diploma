import os

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import dotenv
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from marshmallow import Schema, fields

dotenv.load_dotenv()

db_user = os.environ.get('MYSQL_USER')
db_pass = os.environ.get('MYSQL_PASSWORD')
db_hostname = os.environ.get('MYSQL_HOST')
db_name = os.environ.get('MYSQL_DATABASE')

DB_URI = 'mysql+pymysql://{db_username}:{db_password}@{db_host}/{database}'.format(db_username=db_user, db_password=db_pass, db_host=db_hostname, database=db_name)  # noqa: E501

engine = create_engine(DB_URI, echo=True)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Student(db.Model):
    __tablename__ = "student"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    cellphone = db.Column(db.String(13), unique=True, nullable=False)

    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def change(self):
        db.session.change(self)
        db.session.commit()


class StudentSchema(Schema):
    id = fields.Integer()
    name = fields.Str()
    email = fields.Str()
    age = fields.Integer()
    cellphone = fields.Str()


@app.route('/api', methods=['GET'])
def api_main():
    return jsonify('This API hepls ou to fill mysql database using some methods like: POST, PUT, PATCH, GET. With method POST, PUT, PATCH you receive answer code 201 which show you the data you want to add. With GET you receive code 200 which shows you data by request; /api/students uses GET request to get all data; /api/students/get/id uses GET request to get data by id; /api/students/add uses POST request to add new data; /api/students/modify/id uses PATCH request to modify part of data by id; /api/students/change/id uses PUT request to change all data by id; /api/students/delete/id uses POST request to delete data; /api/health-check/ok and api/health-check/bad use GET request to check health of script'), 200  # noqa: E501


@app.route('/api/students', methods=['GET'])
def get_all_students():
    students = Student.get_all()
    student_list = StudentSchema(many=True)
    response = student_list.dump(students)
    return jsonify(response), 200


@app.route('/api/students/get/<int:id>', methods=['GET'])
def get_student(id):
    student_info = Student.get_by_id(id)
    serializer = StudentSchema()
    response = serializer.dump(student_info)
    return jsonify(response), 200


@app.route('/api/students/add', methods=['POST'])
def add_student():
    json_data = request.get_json()
    new_student = Student(
        name=json_data.get('name'),
        email=json_data.get('email'),
        age=json_data.get('age'),
        cellphone=json_data.get('cellphone')
    )
    new_student.save()
    serializer = StudentSchema()
    data = serializer.dump(new_student)
    return jsonify(data), 201


# added modify feature
@app.route('/api/students/modify/<int:id>', methods=['PATCH'])
def edit_student(id):
    json_data = request.get_json()
    cur_student = Student.get_by_id(id)
    if json_data.get('name'):
        cur_student.name = json_data.get('name')
    if json_data.get('email'):
        cur_student.email = json_data.get('email')
    if json_data.get('age'):
        cur_student.age = json_data.get('age')
    if json_data.get('cellphone'):
        cur_student.age = json_data.get('cellphone')

    cur_student.save()
    serializer = StudentSchema()
    response = serializer.dump(cur_student)
    return jsonify(response), 201


# added change feature
@app.route('/api/students/change/<int:id>', methods=['PUT'])
def change_student(id):
    json_data = request.get_json()
    cur_student = Student.get_by_id(id)
    new_data = Student(
        name=json_data.get('name'),
        email=json_data.get('email'),
        age=json_data.get('age'),
        cellphone=json_data.get('cellphone')
    )
    cur_student.name = new_data.name
    cur_student.email = new_data.email
    cur_student.age = new_data.age
    cur_student.cellphone = new_data.cellphone

    cur_student.save()
    serializer = StudentSchema()
    response = serializer.dump(cur_student)
    return jsonify(response), 201


# added delete feature
@app.route('/api/students/delete/<int:id>', methods=['POST'])
def del_student(id):
    student_info = Student.get_by_id(id)
    student_info.delete()
    serializer = StudentSchema()
    response = serializer.dump(student_info)
    return jsonify(response), 201


# added synthetic heath check "OK"
@app.route('/api/heath-check/ok', methods=['GET'])
def healthcheck_ok():
    return jsonify('Everything is fine'), 200


# added synthetic heath check "BAD"
@app.route('/api/heath-check/bad', methods=['GET'])
def healthcheck_bad():
    return jsonify('Error, could not get healthy state'), 500


if __name__ == '__main__':
    with app.app_context():
        if not database_exists(engine.url):
            create_database(engine.url)
        db.create_all()
        app.run(host="0.0.0.0", debug=True, port=5000)
