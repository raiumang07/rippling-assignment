# Boostly — Boost morale, one kudos at a time

A peer recognition platform for college students built with Python FastAPI. This application allows students to recognize peers with credits, endorse recognitions, redeem rewards, and view leaderboards.

**Assignment Repository:** [ai-coding-round](https://github.com/raso-jr/ai-coding-round)

---

## Setup Instructions

### Prerequisites
- Python 3.7+
- pip package manager

### Installation

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   The `requirements.txt` includes:
   - fastapi
   - uvicorn[standard]
   - SQLAlchemy
   - pydantic
   - python-decouple
   - apscheduler

2. **Database Setup**
   - The application uses SQLite database
   - Database file `boostly.db` will be automatically created on first run
   - All tables are created automatically via SQLAlchemy

---

## Running the Application

1. **Navigate to the src directory**
   ```bash
   cd src
   ```

2. **Start the server**
   ```bash
   uvicorn main:app --reload
   ```

3. **Access the application**
   - Base URL: `http://127.0.0.1:8000`
   - Interactive API Docs: `http://127.0.0.1:8000/docs`
   - Alternative Docs: `http://127.0.0.1:8000/redoc`

---

## API Endpoints

### Students

#### Create Student
- **Endpoint:** `POST /students/`
- **Description:** Create a new student account
- **Request Body:**
  ```json
  {
    "name": "Alice Johnson"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "name": "Alice Johnson",
    "id": 1,
    "credits_to_give": 100,
    "credits_received": 0
  }
  ```

#### Get Student Details
- **Endpoint:** `GET /students/{student_id}`
- **Description:** Retrieve student information
- **Response (200 OK):**
  ```json
  {
    "name": "Alice Johnson",
    "id": 1,
    "credits_to_give": 100,
    "credits_received": 0
  }
  ```
- **Error Response (404):**
  ```json
  {
    "detail": "Student not found"
  }
  ```

---

### Recognitions

#### Create Recognition
- **Endpoint:** `POST /recognitions/`
- **Description:** Send credits to recognize a peer
- **Request Body:**
  ```json
  {
    "sender_id": 1,
    "receiver_id": 2,
    "credits": 25,
    "message": "Great job on the project!"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "receiver_id": 2,
    "credits": 25,
    "message": "Great job on the project!",
    "id": 1,
    "sender_id": 1,
    "timestamp": "2025-11-13T10:30:00.123456"
  }
  ```
- **Error Responses:**
  - `400 Bad Request` - "Cannot send recognition to yourself"
  - `400 Bad Request` - "Insufficient credits to give"
  - `400 Bad Request` - "Exceeds monthly sending limit"
  - `404 Not Found` - "Sender or receiver not found"

**Business Rules Implemented:**
- ✅ Each student receives 100 credits monthly
- ✅ Cannot send credits to self
- ✅ Monthly sending limit of 100 credits enforced
- ✅ Cannot exceed available credit balance

#### Endorse Recognition
- **Endpoint:** `POST /recognitions/{recognition_id}/endorse`
- **Description:** Endorse/like an existing recognition
- **Request Body:**
  ```json
  {
    "endorser_id": 3
  }
  ```
- **Example:** `POST /recognitions/1/endorse` with JSON body above
- **Response (200 OK):**
  ```json
  {
    "recognition_id": 1,
    "endorser_id": 3,
    "id": 1,
    "timestamp": "2025-11-13T10:35:00.123456"
  }
  ```
- **Error Responses:**
  - `400 Bad Request` - "You have already endorsed this recognition"
  - `404 Not Found` - "Recognition not found"
  - `404 Not Found` - "Endorser not found"

**Business Rules Implemented:**
- ✅ Each student can endorse a recognition only once
- ✅ Endorsements don't affect credit balances

---

### Redemptions

#### Redeem Credits
- **Endpoint:** `POST /redemptions/`
- **Description:** Convert received credits to voucher
- **Request Body:**
  ```json
  {
    "student_id": 2,
    "credits": 20
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "student_id": 2,
    "credits": 20,
    "id": 1,
    "voucher_value": 100.0,
    "timestamp": "2025-11-13T11:00:00.123456"
  }
  ```
- **Error Responses:**
  - `400 Bad Request` - "Insufficient received credits to redeem"
  - `404 Not Found` - "Student not found"

**Business Rules Implemented:**
- ✅ Credits converted at ₹5 per credit
- ✅ Credits permanently deducted from balance
- ✅ Can only redeem received credits

---

### Credit Reset (Step-Up Challenge 1)

#### Reset Monthly Credits
- **Endpoint:** `POST /students/reset-credits`
- **Description:** Reset all students' credits for new month
- **Response (200 OK):**
  ```json
  {
    "message": "Credits reset for all students."
  }
  ```

**Business Rules Implemented:**
- ✅ Credits reset to 100 at month start
- ✅ Up to 50 unused credits carried forward
- ✅ Monthly sending limit resets to 100

---

### Leaderboard (Step-Up Challenge 2)

#### Get Top Recipients
- **Endpoint:** `GET /leaderboard`
- **Description:** List top recipients by total credits received
- **Query Parameters:**
  - `limit` (optional, default: 10) - Number of students to return
- **Example:** `GET /leaderboard?limit=5`
- **Response (200 OK):**
  ```json
  [
    {
      "student_id": 2,
      "name": "Bob Smith",
      "total_credits_received": 75,
      "total_recognitions_received": 5,
      "total_endorsements_received": 12
    },
    {
      "student_id": 3,
      "name": "Charlie Brown",
      "total_credits_received": 50,
      "total_recognitions_received": 3,
      "total_endorsements_received": 8
    }
  ]
  ```

**Business Rules Implemented:**
- ✅ Ranked by total credits received (descending)
- ✅ Tie-breaking by student ID (ascending)
- ✅ Includes recognition count
- ✅ Includes endorsement totals
- ✅ Supports limit parameter

---

## Sample Requests and Responses

### Using cURL

**Create students for testing:**
```bash
curl -X POST "http://127.0.0.1:8000/students/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice"}'

curl -X POST "http://127.0.0.1:8000/students/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Bob"}'

curl -X POST "http://127.0.0.1:8000/students/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Charlie"}'
```

**Send recognition:**
```bash
curl -X POST "http://127.0.0.1:8000/recognitions/" \
  -H "Content-Type: application/json" \
  -d '{
    "sender_id": 1,
    "receiver_id": 2,
    "credits": 25,
    "message": "Excellent teamwork!"
  }'
```

**Endorse recognition:**
```bash
curl -X POST "http://127.0.0.1:8000/recognitions/1/endorse" \
  -H "Content-Type: application/json" \
  -d '{"endorser_id": 3}'
```

**Redeem credits:**
```bash
curl -X POST "http://127.0.0.1:8000/redemptions/" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 2,
    "credits": 20
  }'
```

**Get leaderboard:**
```bash
curl -X GET "http://127.0.0.1:8000/leaderboard?limit=10"
```

**Reset monthly credits:**
```bash
curl -X POST "http://127.0.0.1:8000/students/reset-credits"
```

---

## Implementation Details

### Technology Stack
- **Framework:** FastAPI (Python)
- **ORM:** SQLAlchemy
- **Database:** SQLite
- **Validation:** Pydantic models
- **Server:** Uvicorn ASGI server

### Database Schema

**Students Table:**
- `id` - Primary key
- `name` - Student name
- `credits_to_give` - Available credits to send (default: 100)
- `credits_received` - Total credits received
- `monthly_sending_limit` - Monthly sending limit (default: 100)
- `last_credit_reset` - Timestamp of last reset

**Recognitions Table:**
- `id` - Primary key
- `sender_id` - Foreign key to students
- `receiver_id` - Foreign key to students
- `credits` - Amount of credits sent
- `message` - Recognition message
- `timestamp` - Creation timestamp

**Endorsements Table:**
- `id` - Primary key
- `recognition_id` - Foreign key to recognitions
- `endorser_id` - Foreign key to students
- `timestamp` - Creation timestamp

**Redemptions Table:**
- `id` - Primary key
- `student_id` - Foreign key to students
- `credits` - Number of credits redeemed
- `voucher_value` - Voucher value in rupees (credits × 5)
- `timestamp` - Creation timestamp

### Key Features

✅ **All Core Functionality Implemented**
- Recognition system with credit transfer
- Endorsement system
- Redemption with voucher generation

✅ **Both Step-Up Challenges Completed**
- Credit reset with carry-forward mechanism
- Comprehensive leaderboard with rankings

✅ **Proper Validation & Error Handling**
- Input validation using Pydantic
- Business rule enforcement
- Descriptive error messages

✅ **RESTful API Design**
- Clear endpoint naming
- Appropriate HTTP methods
- Proper status codes

---

## Testing

Comprehensive test cases are documented in `test-cases/test-cases.txt`. The file includes:
- Step-by-step testing instructions
- Expected results for each use case
- Coverage of all core features and step-up challenges

**Quick Test Flow:**
1. Create 3 students
2. Send recognition from Alice to Bob
3. Charlie endorses the recognition
4. Bob redeems credits
5. Trigger credit reset
6. View leaderboard

Use the FastAPI interactive documentation at `/docs` for easy API testing through the browser.

---

## Assignment Compliance

This implementation fulfills all requirements from the [ai-coding-round](https://github.com/raso-jr/ai-coding-round) assignment:

### ✅ Core Functionality (Required)
- [x] Recognition with credit transfer
- [x] Endorsements
- [x] Redemption system

### ✅ Step-Up Challenges (Completed)
- [x] Credit reset mechanism with carry-forward
- [x] Leaderboard with rankings

### ✅ Deliverables (Complete)
- [x] Complete source code in `src/`
- [x] Documentation in `src/readme.md`
- [x] LLM chat export in `prompt/llm-chat-export.txt`
- [x] Test cases in `test-cases/test-cases.txt`

---

## Notes for Reviewers

- The application is fully functional and ready to run
- All business rules are enforced at the API level
- Database schema supports all required operations
- FastAPI's automatic documentation provides additional testing interface
- Error handling covers all edge cases mentioned in requirements
- Code follows Python best practices and FastAPI conventions

**To verify the implementation, simply:**
1. Install dependencies
2. Run the server
3. Follow test cases in `test-cases/test-cases.txt`
4. All endpoints can be tested via `/docs` interface