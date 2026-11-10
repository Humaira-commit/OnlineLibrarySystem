# TCP Connection and Database Setup
import socket 
import json # Client data read in JSON format
 
HOST = "127.0.0.1"
PORT = 5000

print("====================================")
print("    ONLINE LIBRARY REGISTRATION")
print("====================================")

# Collect customer information
full_name = input("Enter Full Name: ").strip()
residential_address = input("Enter Residential Address: ").strip()
contact_number = input("Enter Contact Number: ").strip()
email_address = input("Enter Email Address: ").strip()

# Validate required fields
if not all([full_name, residential_address,
            contact_number, email_address]):
    print("Error: All fields are required.")
    raise SystemExit(1)

# Membership duration
while True:
    duration_input = input(
        "Enter Membership Duration (6 or 12 months): "
    )

    if duration_input in ("6", "12"):
        membership_duration = int(duration_input)
        break

    print("Invalid choice! Enter 6 or 12.")

# Prepare registration data
customer_data = {
    "full_name": full_name,
    "residential_address": residential_address,
    "contact_number": contact_number,
    "email_address": email_address,
    "membership_duration": membership_duration
}

try:
    # Connect to TCP server
    with socket.create_connection((HOST, PORT), timeout=10) as client:
        print("\nConnected to Server!")

        # Send customer data as JSON
        message = json.dumps(customer_data) + "\n"
        client.sendall(message.encode("utf-8"))

        print("Registration details sent successfully!")

        # Receive server response
        with client.makefile("r", encoding="utf-8") as reader:
            response_line = reader.readline(65537)

        if not response_line or len(response_line) > 65536:
            raise ValueError("Invalid server response.")

        response = json.loads(response_line)

        if response.get("status") == "success":
            print("\n====================================")
            print("      REGISTRATION SUCCESSFUL!")
            print("====================================")
            print("Name:", full_name)
            print("Registration Number:",
                  response["registration_number"])
            print("Membership Duration:",
                  membership_duration, "months")
        else:
            print("\nRegistration Failed!")
            print(response.get("message", "Unknown error."))

except (OSError, ValueError, json.JSONDecodeError) as error:
    print("\nConnection or response error:", error)
