from flask import Flask, jsonify, render_template, request

from db import close_db, get_db, init_db


app = Flask(__name__)
app.teardown_appcontext(close_db)


def ok(data=None, message="success"):
    return jsonify({"code": 0, "message": message, "data": data})


def error(message, status=400):
    return jsonify({"code": status, "message": message, "data": None}), status


def get_json_body():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return None
    return body


def parse_age(value):
    if value in (None, ""):
        return None
    try:
        age = int(value)
    except (TypeError, ValueError):
        raise ValueError("年龄必须是整数")
    if age < 1 or age > 120:
        raise ValueError("年龄必须在 1 到 120 之间")
    return age


def parse_class_id(value):
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValueError("班级编号无效")


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/classes")
def list_classes():
    db = get_db()
    rows = db.execute(
        "SELECT class_id, class_name FROM classes ORDER BY class_id"
    ).fetchall()
    return ok([dict(row) for row in rows])


@app.post("/api/classes")
def create_class():
    body = get_json_body()
    name = (body or {}).get("class_name", "").strip()
    if not name:
        return error("班级名称不能为空")
    db = get_db()
    try:
        cursor = db.execute("INSERT INTO classes (class_name) VALUES (?)", (name,))
        db.commit()
    except Exception as exc:
        db.rollback()
        if "UNIQUE" in str(exc).upper():
            return error("班级名称已存在")
        return error("新增班级失败", 500)
    return ok({"class_id": cursor.lastrowid, "class_name": name}, "新增班级成功")


@app.put("/api/classes/<int:class_id>")
def update_class(class_id):
    body = get_json_body()
    name = (body or {}).get("class_name", "").strip()
    if not name:
        return error("班级名称不能为空")
    db = get_db()
    try:
        cursor = db.execute(
            "UPDATE classes SET class_name = ? WHERE class_id = ?",
            (name, class_id),
        )
        db.commit()
    except Exception as exc:
        db.rollback()
        if "UNIQUE" in str(exc).upper():
            return error("班级名称已存在")
        return error("修改班级失败", 500)
    if cursor.rowcount == 0:
        return error("班级不存在", 404)
    return ok({"class_id": class_id, "class_name": name}, "修改班级成功")


@app.delete("/api/classes/<int:class_id>")
def delete_class(class_id):
    db = get_db()
    cursor = db.execute("DELETE FROM classes WHERE class_id = ?", (class_id,))
    db.commit()
    if cursor.rowcount == 0:
        return error("班级不存在", 404)
    return ok(message="删除班级成功")


@app.get("/api/students")
def list_students():
    class_id = request.args.get("class_id")
    try:
        class_id = parse_class_id(class_id)
    except ValueError as exc:
        return error(str(exc))

    db = get_db()
    sql = """
        SELECT s.student_id, s.student_name, s.gender, s.age,
               GROUP_CONCAT(c.class_name, ', ') AS class_name,
               MIN(c.class_id) AS class_id
        FROM students s
        LEFT JOIN student_class sc ON sc.student_id = s.student_id
        LEFT JOIN classes c ON c.class_id = sc.class_id
    """
    params = []
    if class_id is not None:
        sql += " WHERE EXISTS (SELECT 1 FROM student_class x WHERE x.student_id = s.student_id AND x.class_id = ?)"
        params.append(class_id)
    sql += " GROUP BY s.student_id ORDER BY s.student_id"
    rows = db.execute(sql, params).fetchall()
    return ok([dict(row) for row in rows])


@app.post("/api/students")
def create_student():
    body = get_json_body() or {}
    name = str(body.get("student_name", "")).strip()
    if not name:
        return error("学生姓名不能为空")
    try:
        age = parse_age(body.get("age"))
        class_id = parse_class_id(body.get("class_id"))
    except ValueError as exc:
        return error(str(exc))

    db = get_db()
    try:
        if class_id is not None and not db.execute(
            "SELECT 1 FROM classes WHERE class_id = ?", (class_id,)
        ).fetchone():
            return error("班级不存在", 404)
        cursor = db.execute(
            "INSERT INTO students (student_name, gender, age) VALUES (?, ?, ?)",
            (name, body.get("gender", "").strip(), age),
        )
        student_id = cursor.lastrowid
        if class_id is not None:
            db.execute(
                "INSERT INTO student_class (student_id, class_id) VALUES (?, ?)",
                (student_id, class_id),
            )
        db.commit()
    except Exception:
        db.rollback()
        return error("新增学生失败", 500)
    return ok({"student_id": student_id}, "新增学生成功")


@app.put("/api/students/<int:student_id>")
def update_student(student_id):
    body = get_json_body() or {}
    name = str(body.get("student_name", "")).strip()
    if not name:
        return error("学生姓名不能为空")
    try:
        age = parse_age(body.get("age"))
        class_id = parse_class_id(body.get("class_id"))
    except ValueError as exc:
        return error(str(exc))

    db = get_db()
    try:
        if not db.execute(
            "SELECT 1 FROM students WHERE student_id = ?", (student_id,)
        ).fetchone():
            return error("学生不存在", 404)
        if class_id is not None and not db.execute(
            "SELECT 1 FROM classes WHERE class_id = ?", (class_id,)
        ).fetchone():
            return error("班级不存在", 404)
        db.execute(
            "UPDATE students SET student_name = ?, gender = ?, age = ? WHERE student_id = ?",
            (name, body.get("gender", "").strip(), age, student_id),
        )
        db.execute("DELETE FROM student_class WHERE student_id = ?", (student_id,))
        if class_id is not None:
            db.execute(
                "INSERT INTO student_class (student_id, class_id) VALUES (?, ?)",
                (student_id, class_id),
            )
        db.commit()
    except Exception:
        db.rollback()
        return error("修改学生失败", 500)
    return ok(message="修改学生成功")


@app.delete("/api/students/<int:student_id>")
def delete_student(student_id):
    db = get_db()
    cursor = db.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
    db.commit()
    if cursor.rowcount == 0:
        return error("学生不存在", 404)
    return ok(message="删除学生成功")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
