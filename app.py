from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import TEXT, String

TEXT = {"Content-Type": "text/plain; charset=utf-8"}
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-chi-dung-khi-phat-trien"
app.config["SQLALCHEMY_DATABASE_URI"] = \
    "sqlite:///qlsv.db"
db.init_app(app)



class Student(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    mssv: Mapped[str] = mapped_column(String(10),
                                      unique=True)
    name: Mapped[str] = mapped_column(String(100))
    gpa: Mapped[float] = mapped_column(default=0.0)

    def __repr__(self):
        return f"<Student {self.mssv} - {self.name}>"
with app.app_context():
    db.create_all()

@app.get("/them-mau")
def add_sample():
    total = db.session.scalar(
        db.select(db.func.count(Student.id))
    )
    if total > 0:
        return f"Đã có {total} sinh viên, không thêm nữa."
    an = Student(mssv="23T1020312",
                 name="Nguyễn Văn An", gpa=8.5)
    before = an.id
    db.session.add(an)
    db.session.add_all([
        Student(mssv="23T1020077", name="Lê Trung Danh", gpa=2),
        Student(mssv="23T1020213", name="Lê Thế Huy", gpa=3.8),
        Student(mssv="23T1020570", name="Trần Đình Hữu Thọ", gpa=10.0),
        Student(mssv="23T1020250", name="Nguyễn Trọng Hy", gpa=0.5),
    ])
    db.session.commit()
    return (f"Đã thêm 5 sinh viên. id của An: "
            f"trước commit = {before}, " 
            f"sau commit = {an.id}")

@app.get("/thu-truy-van")
def try_query():
    if db.session.scalar(
        db.select(db.func.count(Student.id))) == 0:
        return "Chưa có dữ liệu, hãy mở /them-mau trước."
    lines = []
    lines.append(f"1. get(3): {db.session.get(Student, 3)}")
    lines.append(f"2. get(99): {db.session.get(Student, 99)}")
    everyone = db.session.execute(
        db.select(Student)).scalars().all()
    lines.append(f"3. Tất cả: {len(everyone)} sinh viên")
    stmt = (db.select(Student)
            .where(Student.gpa >= 8.0)
            .order_by(Student.gpa.desc()))
    good = db.session.execute(stmt).scalars().all()
    lines.append(f"4. Điểm >= 8.0: {good}")
    binh = db.session.scalar(db.select(Student)
                             .filter_by(mssv="23T1020213"))
    lines.append(f"5. filter_by(mssv='23T1020213'): {binh}")
    count = db.session.scalar(db.select(db.func.count(Student.id)))
    avg = db.session.scalar(db.select(db.func.avg(Student.gpa)))
    lines.append(f"6. Số SV: {count}, Điểm trung bình: {avg:.2f}")
    return "\n".join(lines), TEXT

@app.get("/students")
def student_list():
    students = db.session.execute(db.select(Student)).scalars().all()
    return render_template("students.html", students=students)

if __name__ == "__main__":
    app.run(debug=True, port=8000)