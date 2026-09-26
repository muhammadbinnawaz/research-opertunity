from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import mysql.connector


def get_db():
    return mysql.connector.connect(
        host="localhost",
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", ""),
        database="research_portal"
    )


fields = ["title", "description", "research_area", "faculty_name",
          "department", "required_skills", "positions", "deadline", "status"]


def check_data(data):
    # returns an error message, or None if everything is fine
    for f in fields:
        if f not in data or str(data[f]).strip() == "":
            return f + " is required"

    try:
        if int(data["positions"]) < 1:
            return "positions must be at least 1"
    except ValueError:
        return "positions must be a number"

    if data["status"] not in ["Open", "Closed"]:
        return "status must be Open or Closed"

    parts = str(data["deadline"]).split("-")
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        return "deadline must look like YYYY-MM-DD"

    return None


def fix_row(row):
    row["deadline"] = str(row["deadline"])
    return row


class Handler(BaseHTTPRequestHandler):

    def send_json(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        try:
            return json.loads(self.rfile.read(length))
        except ValueError:
            return None

    def get_id(self):
        # gives back the id from /api/opportunities/5, or None for /api/opportunities
        parts = self.path.strip("/").split("/")
        if len(parts) == 3:
            return parts[2]
        return None

    def is_api(self):
        return self.path.strip("/").startswith("api/opportunities")

    def do_GET(self):
        if not self.is_api():
            with open("index.html", "rb") as f:
                page = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(page)
            return

        try:
            db = get_db()
            cur = db.cursor(dictionary=True)
            opp_id = self.get_id()

            if opp_id is None:
                cur.execute("SELECT * FROM opportunities")
                rows = [fix_row(r) for r in cur.fetchall()]
                self.send_json(200, rows)
            elif not opp_id.isdigit():
                self.send_json(400, {"error": "id must be a number"})
            else:
                cur.execute("SELECT * FROM opportunities WHERE id = %s", (opp_id,))
                row = cur.fetchone()
                if row is None:
                    self.send_json(404, {"error": "Opportunity not found"})
                else:
                    self.send_json(200, fix_row(row))
            db.close()
        except Exception as e:
            self.send_json(500, {"error": "Server error: " + str(e)})

    def do_POST(self):
        if not self.is_api() or self.get_id() is not None:
            self.send_json(404, {"error": "Route not found"})
            return

        data = self.read_body()
        if data is None:
            self.send_json(400, {"error": "Body must be valid JSON"})
            return

        message = check_data(data)
        if message:
            self.send_json(400, {"error": message})
            return

        try:
            db = get_db()
            cur = db.cursor()
            cur.execute(
                "INSERT INTO opportunities (title, description, research_area, faculty_name, "
                "department, required_skills, positions, deadline, status) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                [data[f] for f in fields])
            db.commit()
            data["id"] = cur.lastrowid
            db.close()
            self.send_json(201, data)
        except Exception as e:
            self.send_json(500, {"error": "Server error: " + str(e)})

    def do_PUT(self):
        opp_id = self.get_id()
        if not self.is_api() or opp_id is None:
            self.send_json(404, {"error": "Route not found"})
            return
        if not opp_id.isdigit():
            self.send_json(400, {"error": "id must be a number"})
            return

        new_data = self.read_body()
        if new_data is None:
            self.send_json(400, {"error": "Body must be valid JSON"})
            return

        try:
            db = get_db()
            cur = db.cursor(dictionary=True)
            cur.execute("SELECT * FROM opportunities WHERE id = %s", (opp_id,))
            row = cur.fetchone()
            if row is None:
                db.close()
                self.send_json(404, {"error": "Opportunity not found"})
                return

            # keep old values for anything the user did not send
            data = fix_row(row)
            data.update(new_data)

            message = check_data(data)
            if message:
                db.close()
                self.send_json(400, {"error": message})
                return

            cur.execute(
                "UPDATE opportunities SET title=%s, description=%s, research_area=%s, "
                "faculty_name=%s, department=%s, required_skills=%s, positions=%s, "
                "deadline=%s, status=%s WHERE id=%s",
                [data[f] for f in fields] + [opp_id])
            db.commit()
            db.close()
            data["id"] = int(opp_id)
            self.send_json(200, data)
        except Exception as e:
            self.send_json(500, {"error": "Server error: " + str(e)})

    def do_DELETE(self):
        opp_id = self.get_id()
        if not self.is_api() or opp_id is None:
            self.send_json(404, {"error": "Route not found"})
            return
        if not opp_id.isdigit():
            self.send_json(400, {"error": "id must be a number"})
            return

        try:
            db = get_db()
            cur = db.cursor()
            cur.execute("DELETE FROM opportunities WHERE id = %s", (opp_id,))
            db.commit()
            deleted = cur.rowcount
            db.close()
            if deleted == 0:
                self.send_json(404, {"error": "Opportunity not found"})
            else:
                self.send_json(200, {"message": "Opportunity deleted"})
        except Exception as e:
            self.send_json(500, {"error": "Server error: " + str(e)})


print("Server running on http://localhost:3000")
HTTPServer(("", 3000), Handler).serve_forever()
