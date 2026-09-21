from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import get_db_connection
import os
import uuid


app = Flask(__name__)

app.secret_key = "visitorpro_secret_key"


# =========================
# Upload Folder
# =========================

UPLOAD_FOLDER = "static/uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():
    return render_template("index.html")


# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        db = None
        cursor = None

        try:

            db = get_db_connection()

            cursor = db.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT *
                FROM admins
                WHERE username = %s
                AND password = %s
                """,
                (username, password)
            )

            admin = cursor.fetchone()

            if admin:

                return redirect(
                    url_for("admin_dashboard")
                )

            flash(
                "Invalid username or password.",
                "error"
            )

        except Exception as e:

            print("ADMIN LOGIN ERROR:", e)

            flash(
                "Database error. Please try again.",
                "error"
            )

        finally:

            if cursor:
                cursor.close()

            if db:
                db.close()

    return render_template("admin_login.html")


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin/dashboard")
def admin_dashboard():

    db = None
    cursor = None

    try:

        db = get_db_connection()

        cursor = db.cursor()

        # Total Visitors
        cursor.execute(
            "SELECT COUNT(*) FROM visitors"
        )

        total_visitors = cursor.fetchone()[0]


        # Currently Inside
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM visits
            WHERE status = 'Inside'
            """
        )

        inside_visitors = cursor.fetchone()[0]


        # Total Employees
        cursor.execute(
            "SELECT COUNT(*) FROM employees"
        )

        total_employees = cursor.fetchone()[0]


        return render_template(
            "admin_dashboard.html",
            total_visitors=total_visitors,
            inside_visitors=inside_visitors,
            total_employees=total_employees
        )


    except Exception as e:

        print("DASHBOARD ERROR:", e)

        return render_template(
            "admin_dashboard.html",
            total_visitors=0,
            inside_visitors=0,
            total_employees=0
        )


    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# VISITOR RECORDS
# =========================================================

@app.route("/admin/visitors")
def visitor_records():

    db = None
    cursor = None

    try:

        db = get_db_connection()

        cursor = db.cursor(dictionary=True)


        query = """
            SELECT
                v.visitor_id,
                v.name,
                v.mobile,
                e.name AS employee_name,
                vi.id AS visit_id,
                vi.purpose,
                vi.check_in,
                vi.check_out,
                vi.status

            FROM visits vi

            JOIN visitors v
                ON vi.visitor_id = v.id

            LEFT JOIN employees e
                ON vi.employee_id = e.id

            ORDER BY vi.check_in DESC
        """


        cursor.execute(query)

        visitors = cursor.fetchall()


        return render_template(
            "visitor_records.html",
            visitors=visitors
        )


    except Exception as e:

        print(
            "VISITOR RECORDS ERROR:",
            e
        )

        return render_template(
            "visitor_records.html",
            visitors=[]
        )


    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# CHECK OUT VISITOR
# =========================================================

@app.route(
    "/admin/checkout/<int:visit_id>",
    methods=["POST"]
)
def checkout_visitor(visit_id):

    db = None
    cursor = None

    try:

        db = get_db_connection()

        cursor = db.cursor()


        cursor.execute(
            """
            UPDATE visits

            SET
                check_out = NOW(),
                status = 'Checked Out'

            WHERE id = %s
            """,
            (visit_id,)
        )


        db.commit()


        flash(
            "Visitor checked out successfully.",
            "success"
        )


    except Exception as e:

        print(
            "CHECKOUT ERROR:",
            e
        )


        if db:
            db.rollback()


        flash(
            "Unable to checkout visitor.",
            "error"
        )


    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


    return redirect(
        url_for("visitor_records")
    )


# =========================================================
# VISITOR LOGIN
# =========================================================

@app.route(
    "/visitor/login",
    methods=["GET", "POST"]
)
def visitor_login():

    if request.method == "POST":

        visitor_id = request.form.get(
            "visitor_id",
            ""
        ).strip()

        mobile = request.form.get(
            "mobile",
            ""
        ).strip()


        db = None
        cursor = None


        try:

            db = get_db_connection()

            cursor = db.cursor(
                dictionary=True
            )


            cursor.execute(
                """
                SELECT *
                FROM visitors

                WHERE visitor_id = %s
                AND mobile = %s
                """,
                (
                    visitor_id,
                    mobile
                )
            )


            visitor = cursor.fetchone()


            if visitor:

                session["visitor_id"] = (
                    visitor["visitor_id"]
                )


                return redirect(
                    url_for(
                        "visitor_dashboard"
                    )
                )


            flash(
                "Invalid Visitor ID or Mobile Number.",
                "error"
            )


        except Exception as e:

            print(
                "VISITOR LOGIN ERROR:",
                e
            )


            flash(
                "Database error. Please try again.",
                "error"
            )


        finally:

            if cursor:
                cursor.close()

            if db:
                db.close()


    return render_template(
        "visitor_login.html"
    )


# =========================================================
# VISITOR INFORMATION
# =========================================================

@app.route("/visitor/dashboard")
def visitor_dashboard():

    # Check Visitor Login
    if "visitor_id" not in session:

        return redirect(
            url_for("visitor_login")
        )


    db = None
    cursor = None


    try:

        db = get_db_connection()

        cursor = db.cursor(
            dictionary=True
        )


        cursor.execute(
            """
            SELECT *
            FROM visitors

            WHERE visitor_id = %s
            """,
            (
                session["visitor_id"],
            )
        )


        visitor = cursor.fetchone()


        if not visitor:

            session.pop(
                "visitor_id",
                None
            )


            return redirect(
                url_for("visitor_login")
            )


        return render_template(
            "visitor_dashboard.html",
            visitor=visitor
        )


    except Exception as e:

        print(
            "VISITOR DASHBOARD ERROR:",
            e
        )


        flash(
            "Unable to load your information.",
            "error"
        )


        return redirect(
            url_for("visitor_login")
        )


    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# VISITOR LOGOUT
# =========================================================

@app.route("/visitor/logout")
def visitor_logout():

    session.pop(
        "visitor_id",
        None
    )


    return redirect(
        url_for("visitor_login")
    )


# =========================================================
# VISITOR REGISTRATION
# =========================================================

@app.route(
    "/visitor/register",
    methods=["GET", "POST"]
)
def visitor_register():

    # Get Employees

    db = get_db_connection()

    cursor = db.cursor(
        dictionary=True
    )


    cursor.execute(
        """
        SELECT
            id,
            name,
            department,
            designation

        FROM employees

        ORDER BY name
        """
    )


    employees = cursor.fetchall()


    cursor.close()

    db.close()


    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()


        mobile = request.form.get(
            "mobile",
            ""
        ).strip()


        email = request.form.get(
            "email",
            ""
        ).strip()


        address = request.form.get(
            "address",
            ""
        ).strip()


        id_proof = request.form.get(
            "id_proof",
            ""
        ).strip()


        employee_id = request.form.get(
            "employee_id",
            ""
        ).strip()


        purpose = request.form.get(
            "purpose",
            ""
        ).strip()


        # Required Fields

        if (
            not name
            or not mobile
            or not employee_id
            or not purpose
        ):

            flash(
                "Please fill all required fields.",
                "error"
            )


            return render_template(
                "visitor_register.html",
                employees=employees
            )


        # =================================================
        # Generate Visitor ID
        # =================================================

        visitor_id = (
            "VIS-"
            + uuid.uuid4().hex[:6].upper()
        )


        # =================================================
        # Photo Upload
        # =================================================

        photo = request.files.get(
            "photo"
        )


        photo_filename = None


        if photo and photo.filename:

            original_name = os.path.basename(
                photo.filename
            )


            photo_filename = (
                visitor_id
                + "_"
                + original_name
            )


            photo_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                photo_filename
            )


            photo.save(photo_path)


        db = None
        cursor = None


        try:

            db = get_db_connection()

            cursor = db.cursor()


            # =================================================
            # Insert Visitor
            # =================================================

            visitor_query = """
                INSERT INTO visitors
                (
                    visitor_id,
                    name,
                    mobile,
                    email,
                    address,
                    id_proof,
                    photo
                )

                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
            """


            visitor_values = (
                visitor_id,
                name,
                mobile,
                email,
                address,
                id_proof,
                photo_filename
            )


            cursor.execute(
                visitor_query,
                visitor_values
            )


            # New Visitor Database ID

            visitor_database_id = (
                cursor.lastrowid
            )


            # =================================================
            # Insert Visit
            # =================================================

            visit_query = """
                INSERT INTO visits
                (
                    visitor_id,
                    employee_id,
                    purpose,
                    status
                )

                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s
                )
            """


            visit_values = (
                visitor_database_id,
                int(employee_id),
                purpose,
                "Inside"
            )


            cursor.execute(
                visit_query,
                visit_values
            )


            # =================================================
            # Save
            # =================================================

            db.commit()


            flash(
                f"Registration successful! Your Visitor ID is {visitor_id}",
                "success"
            )


            return redirect(
                url_for("visitor_register")
            )


        except Exception as e:

            print(
                "DATABASE ERROR:",
                e
            )


            if db:
                db.rollback()


            flash(
                "Registration failed. Please check the database.",
                "error"
            )


        finally:

            if cursor:
                cursor.close()

            if db:
                db.close()


    # =====================================================
    # Registration Page
    # =====================================================

    return render_template(
        "visitor_register.html",
        employees=employees
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )