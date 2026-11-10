
import socket # tcp socket library
import json # Client data read in JSON format 
import psycopg # PostgreSQL database adapter for Python
import getpass # password input securely

# Server configuration
HOST = "127.0.0.1"
PORT = 5000

# PostgreSQL configuration
DB_NAME = "online_library"
DB_USER = "postgres"
DB_PASSWORD = getpass.getpass("Enter PostgreSQL password: ")

# Connect to PostgreSQL
try:
    connection = psycopg.connect(
        host="localhost",
        port=5432,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    print("Database Connected Successfully!")

except psycopg.Error as error:
    print("Database Connection Failed:", error)
    raise SystemExit(1)


# Function to register a library member
def register_member(data):
    try:
        required = [
            "full_name",
            "residential_address",
            "contact_number",
            "email_address"
        ]

        if any(not isinstance(data.get(field), str)
               or not data[field].strip() for field in required):
            return {"status": "error",
                    "message": "All personal details are required."}

        duration = data.get("membership_duration")

        if type(duration) is not int or duration not in (6, 12):
            return {"status": "error",
                    "message": "Membership must be 6 or 12 months."}

        with connection.transaction():
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO library_members
                    (full_name, residential_address,
                     contact_number, email_address,
                     membership_duration)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING registration_number
                    """,
                    (
                        data["full_name"],
                        data["residential_address"],
                        data["contact_number"],
                        data["email_address"],
                        duration
                    )
                )

                registration_number = cursor.fetchone()[0]

        print("Member registered:", registration_number)

        return {
            "status": "success",
            "registration_number": registration_number
        }

    except (psycopg.Error, KeyError, TypeError) as error:
        print("Registration error:", error)
        return {
            "status": "error",
            "message": "Registration failed."
        }


# Start TCP server
try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(5)

        print("Server is running...")
        print(f"Listening on {HOST}:{PORT}")

        while True:
            client_socket, address = server.accept()

            with client_socket:
                print("Client connected:", address)

                try:
                    # Receive one JSON message ending with newline
                    with client_socket.makefile("r", encoding="utf-8") as reader:
                        message = reader.readline(65537)

                    if not message or len(message) > 65536 or not message.endswith("\n"):
                        raise ValueError("Invalid or oversized message.")

                    data = json.loads(message)

                    if not isinstance(data, dict):
                        raise ValueError("Expected a JSON object.")

                    print("Registration data received.")
                    response = register_member(data)

                except (ValueError, json.JSONDecodeError) as error:
                    response = {
                        "status": "error",
                        "message": "Invalid registration data."
                    }
                    print("Invalid request:", error)

                client_socket.sendall(
                    (json.dumps(response) + "\n").encode("utf-8")
                )

                print("Response sent to client.")

except KeyboardInterrupt:
    print("\nServer stopped.")

except OSError as error:
    print("Server error:", error)

finally:
    connection.close()
    print("Database connection closed.")
