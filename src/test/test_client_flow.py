import requests
import json
from datetime import datetime, timedelta

class ClientFlowTester:
    def __init__(self, base_url="http://localhost:8000/graphql"):
        self.base_url = base_url
        self.auth_token = None
        self.user_id = None
        self.client_id = None
        self.appointment_id = None

    def run_query(self, query, variables=None):
        headers = {
            'Content-Type': 'application/json'
        }
        if self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'
        
        response = requests.post(
            self.base_url,
            headers=headers,
            json={'query': query, 'variables': variables}
        )
        return response.json()

    def sign_up_client(self):
        print("\n1. Creating new user account...")
        mutation = """
        mutation ClientSignUp {
          createUser(input: {
            username: "alice.client"
            email: "alice.client@example.com"
            password: "ClientPass123!"
            firstName: "Alice"
            lastName: "Johnson"
          }) {
            id
            username
            email
          }
        }
        """
        result = self.run_query(mutation)
        print(json.dumps(result, indent=2))
        if 'data' in result and 'createUser' in result['data']:
            self.user_id = result['data']['createUser']['id']

    def login(self):
        print("\n2. Logging in...")
        mutation = """
        mutation ClientLogin {
          login(input: {
            username: "alice.client"
            password: "ClientPass123!"
          }) {
            token
            user {
              id
              username
            }
          }
        }
        """
        result = self.run_query(mutation)
        print(json.dumps(result, indent=2))
        if 'data' in result and 'login' in result['data']:
            self.auth_token = result['data']['login']['token']

    def create_client_profile(self):
        print("\n3. Creating client profile...")
        mutation = """
        mutation CreateClientProfile($userId: UUID!) {
          createClient(input: {
            userId: $userId
            phone: "(555) 234-5678"
            service: HAIRCUT
            status: "active"
            notes: "First time client, prefers afternoon appointments"
          }) {
            id
            service
            status
          }
        }
        """
        variables = {"userId": self.user_id}
        result = self.run_query(mutation, variables)
        print(json.dumps(result, indent=2))
        if 'data' in result and 'createClient' in result['data']:
            self.client_id = result['data']['createClient']['id']

    def book_appointment(self):
        print("\n4. Booking appointment...")
        future_time = (datetime.now() + timedelta(days=1)).replace(hour=14, minute=0)
        mutation = """
        mutation BookAppointment($input: AppointmentCreateInput!) {
          createAppointment(input: $input) {
            id
            title
            startTime
            status
          }
        }
        """
        variables = {
            "input": {
                "title": "Haircut Appointment",
                "description": "First haircut appointment",
                "startTime": future_time.isoformat(),
                "durationMinutes": 30,
                "attendeeIds": [self.user_id]
            }
        }
        result = self.run_query(mutation, variables)
        print(json.dumps(result, indent=2))
        if 'data' in result and 'createAppointment' in result['data']:
            self.appointment_id = result['data']['createAppointment']['id']

    def view_appointments(self):
        print("\n5. Viewing booked appointments...")
        query = """
        query ViewMyAppointments {
          myAppointments {
            id
            title
            startTime
            status
          }
        }
        """
        result = self.run_query(query)
        print(json.dumps(result, indent=2))

    def run_full_flow(self):
        """Execute the complete client flow"""
        print("Starting client flow test...")
        self.sign_up_client()
        self.login()
        self.create_client_profile()
        self.book_appointment()
        self.view_appointments()
        print("\nClient flow test completed!")

    def test_error_cases(self):
        """Test various error scenarios"""
        print("\nTesting Error Cases...")
        
        # Test 1: Booking outside business hours
        print("\n1. Testing appointment outside business hours...")
        future_time = (datetime.now() + timedelta(days=1)).replace(hour=23, minute=0)
        mutation = """
        mutation TestAfterHours($input: AppointmentCreateInput!) {
          createAppointment(input: $input) {
            id
            title
          }
        }
        """
        variables = {
            "input": {
                "title": "After Hours Appointment",
                "description": "Should fail - outside hours",
                "startTime": future_time.isoformat(),
                "durationMinutes": 30,
                "attendeeIds": [self.user_id]
            }
        }
        result = self.run_query(mutation, variables)
        print(json.dumps(result, indent=2))

        # Test 2: Double booking
        print("\n2. Testing double booking...")
        if self.appointment_id:  # Only if we have an existing appointment
            future_time = (datetime.now() + timedelta(days=1)).replace(hour=14, minute=0)
            variables = {
                "input": {
                    "title": "Double Booked Appointment",
                    "description": "Should fail - overlapping time",
                    "startTime": future_time.isoformat(),
                    "durationMinutes": 30,
                    "attendeeIds": [self.user_id]
                }
            }
            result = self.run_query(mutation, variables)
            print(json.dumps(result, indent=2))

def print_menu():
    print("\nAppointment System Test Menu:")
    print("1. Run complete client flow")
    print("2. Create new user")
    print("3. Login")
    print("4. Create client profile")
    print("5. Book appointment")
    print("6. View appointments")
    print("7. Test error cases")
    print("8. Exit")
    return input("Select an option: ")

if __name__ == "__main__":
    tester = ClientFlowTester()
    while True:
        choice = print_menu()
        if choice == "1":
            tester.run_full_flow()
        elif choice == "2":
            tester.sign_up_client()
        elif choice == "3":
            tester.login()
        elif choice == "4":
            tester.create_client_profile()
        elif choice == "5":
            tester.book_appointment()
        elif choice == "6":
            tester.view_appointments()
        elif choice == "7":
            tester.test_error_cases()
        elif choice == "8":
            print("Exiting...")
            break
        else:
            print("Invalid option, please try again.")
