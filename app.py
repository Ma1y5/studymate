from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

DATABASE = "study.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    # 성적 테이블
    conn.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            score INTEGER NOT NULL
        )
    """)

    # 공부 기록 테이블
    conn.execute("""
        CREATE TABLE IF NOT EXISTS study_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            subject TEXT NOT NULL,
            hours REAL NOT NULL,
            content TEXT
        )
    """)

    conn.commit()
    conn.close()


# =========================
# 메인 화면
# =========================

@app.route("/")
def home():
    conn = get_db()

    scores = conn.execute(
        "SELECT * FROM scores"
    ).fetchall()

    conn.close()

    if scores:
        average = sum(row["score"] for row in scores) / len(scores)
    else:
        average = 0

    return render_template(
        "index.html",
        scores=scores,
        average=average
    )


# =========================
# 성적 관리
# =========================

@app.route("/grades")
def grades():
    conn = get_db()

    scores = conn.execute(
        "SELECT * FROM scores"
    ).fetchall()

    conn.close()

    if scores:
        average = sum(row["score"] for row in scores) / len(scores)
    else:
        average = 0

    return render_template(
        "grades.html",
        scores=scores,
        average=average
    )


@app.route("/add_score", methods=["POST"])
def add_score():

    subject = request.form["subject"]
    score = int(request.form["score"])

    conn = get_db()

    conn.execute(
        "INSERT INTO scores (subject, score) VALUES (?, ?)",
        (subject, score)
    )

    conn.commit()
    conn.close()

    return redirect("/grades")


@app.route("/edit_score/<int:score_id>", methods=["POST"])
def edit_score(score_id):

    subject = request.form["subject"]
    score = int(request.form["score"])

    conn = get_db()

    conn.execute(
        """
        UPDATE scores
        SET subject = ?, score = ?
        WHERE id = ?
        """,
        (subject, score, score_id)
    )

    conn.commit()
    conn.close()

    return redirect("/grades")


@app.route("/delete_score/<int:score_id>", methods=["POST"])
def delete_score(score_id):

    conn = get_db()

    conn.execute(
        "DELETE FROM scores WHERE id = ?",
        (score_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/grades")


# =========================
# 공부 기록
# =========================

@app.route("/study")
def study():

    conn = get_db()

    logs = conn.execute(
        """
        SELECT *
        FROM study_logs
        ORDER BY date DESC, id DESC
        """
    ).fetchall()

    conn.close()

    return render_template(
        "study.html",
        logs=logs
    )


@app.route("/add_study", methods=["POST"])
def add_study():

    date = request.form["date"]
    subject = request.form["subject"]
    hours = float(request.form["hours"])
    content = request.form["content"]

    conn = get_db()

    conn.execute(
        """
        INSERT INTO study_logs
        (date, subject, hours, content)
        VALUES (?, ?, ?, ?)
        """,
        (date, subject, hours, content)
    )

    conn.commit()
    conn.close()

    return redirect("/study")


@app.route("/edit_study/<int:study_id>", methods=["POST"])
def edit_study(study_id):

    date = request.form["date"]
    subject = request.form["subject"]
    hours = float(request.form["hours"])
    content = request.form["content"]

    conn = get_db()

    conn.execute(
        """
        UPDATE study_logs
        SET date = ?, subject = ?, hours = ?, content = ?
        WHERE id = ?
        """,
        (date, subject, hours, content, study_id)
    )

    conn.commit()
    conn.close()

    return redirect("/study")


@app.route("/delete_study/<int:study_id>", methods=["POST"])
def delete_study(study_id):

    conn = get_db()

    conn.execute(
        "DELETE FROM study_logs WHERE id = ?",
        (study_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/study")


# =========================
# 통계
# =========================

@app.route("/statistics")
def statistics():

    conn = get_db()

    # 전체 공부 시간
    total_result = conn.execute(
        "SELECT COALESCE(SUM(hours), 0) AS total FROM study_logs"
    ).fetchone()

    total_hours = total_result["total"]


    # 과목별 공부 시간
    subject_stats = conn.execute(
        """
        SELECT
            subject,
            SUM(hours) AS hours
        FROM study_logs
        GROUP BY subject
        ORDER BY hours DESC
        """
    ).fetchall()


    # 날짜별 공부 시간
    date_stats = conn.execute(
        """
        SELECT
            date,
            SUM(hours) AS hours
        FROM study_logs
        GROUP BY date
        ORDER BY date DESC
        """
    ).fetchall()


    conn.close()


    # 그래프 최대값
    if subject_stats:
        max_subject_hours = max(
            row["hours"] for row in subject_stats
        )
    else:
        max_subject_hours = 1


    if date_stats:
        max_date_hours = max(
            row["hours"] for row in date_stats
        )
    else:
        max_date_hours = 1


    return render_template(
        "statistics.html",
        total_hours=total_hours,
        subject_stats=subject_stats,
        date_stats=date_stats,
        max_subject_hours=max_subject_hours,
        max_date_hours=max_date_hours
    )


# =========================
# 프로그램 실행
# =========================

init_db()


if __name__ == "__main__":
    app.run(debug=True)
