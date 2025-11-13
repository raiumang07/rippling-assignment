# Boostly API Documentation

This document provides instructions on how to set up and run the Boostly application, along with details about the available API endpoints.

## Setup and Running the Application

1.  **Prerequisites:**
    *   Python 3.7+
    *   pip

2.  **Installation:**
    *   Clone the repository.
    *   Navigate to the project directory.
    *   Install the required dependencies:
        ```bash
        pip install -r requirements.txt
        ```

3.  **Running the Application:**
    *   Navigate to the `src` directory.
    *   Run the following command to start the FastAPI server:
        ```bash
        uvicorn main:app --reload
        ```
    *   The application will be available at `http://127.0.0.1:8000`.

## API Endpoints

The base URL for all endpoints is `http://127.0.0.1:8000`.

### Error Responses

The API uses standard HTTP status codes to indicate the success or failure of a request. In case of an error, the response body will contain a JSON object with a `detail` key explaining the error.

*   **404 Not Found:** This error is returned when a specific resource is not found.
    *   **Example:** Requesting a student with an ID that does not exist (`GET /students/999`).
        ```json
        {
          "detail": "Student not found"
        }
        ```

*   **400 Bad Request:** This error is returned when a business rule is violated.
    *   **Example:** A student tries to send more credits than they have.
        ```json
        {
          "detail": "Insufficient credits to give"
        }
        ```
    *   **Example:** A student tries to endorse the same recognition twice.
        ```json
        {
          "detail": "You have already endorsed this recognition"
        }
        ```

*   **422 Unprocessable Entity:** This error is returned by FastAPI automatically if the request body does not match the expected schema.
    *   **Example:** Sending a non-integer value for `credits`.
        ```json
        {
          "detail": [
            {
              "loc": [
                "body",
                "credits"
              ],
              "msg": "value is not a valid integer",
              "type": "type_error.integer"
            }
          ]
        }
        ```


### Students

*   **Create a new student**
    *   **Endpoint:** `POST /students/`
    *   **Request Body:**
        ```json
        {
          "name": "John Doe"
        }
        ```
    *   **Response:**
        ```json
        {
          "name": "John Doe",
          "id": 1,
          "credits_to_give": 100,
          "credits_received": 0
        }
        ```

*   **Get student details**
    *   **Endpoint:** `GET /students/{student_id}`
    *   **Response:**
        ```json
        {
          "name": "John Doe",
          "id": 1,
          "credits_to_give": 100,
          "credits_received": 0
        }
        ```

### Recognitions

*   **Create a new recognition**
    *   **Endpoint:** `POST /recognitions/`
    *   **Request Body:**
        ```json
        {
          "sender_id": 1,
          "receiver_id": 2,
          "credits": 10,
          "message": "Great job on the presentation!"
        }
        ```
    *   **Response:**
        ```json
        {
          "receiver_id": 2,
          "credits": 10,
          "message": "Great job on the presentation!",
          "id": 1,
          "sender_id": 1,
          "timestamp": "2025-11-13T12:00:00.000Z"
        }
        ```

*   **Endorse a recognition**
    *   **Endpoint:** `POST /recognitions/{recognition_id}/endorse`
    *   **Request Body:**
        ```json
        {
          "endorser_id": 3
        }
        ```
    *   **Response:**
        ```json
        {
          "recognition_id": 1,
          "endorser_id": 3,
          "id": 1,
          "timestamp": "2025-11-13T12:05:00.000Z"
        }
        ```

### Redemptions

*   **Redeem credits**
    *   **Endpoint:** `POST /redemptions/`
    *   **Request Body:**
        ```json
        {
          "student_id": 2,
          "credits": 10
        }
        ```
    *   **Response:**
        ```json
        {
          "student_id": 2,
          "credits": 10,
          "id": 1,
          "voucher_value": 50.0,
          "timestamp": "2025-11-13T12:10:00.000Z"
        }
        ```

### Credit Reset

*   **Reset credits for all students**
    *   **Endpoint:** `POST /students/reset-credits`
    *   **Response:**
        ```json
        {
          "message": "Credits reset for all students."
        }
        ```

### Leaderboard

*   **Get the leaderboard**
    *   **Endpoint:** `GET /leaderboard`
    *   **Query Parameters:**
        *   `limit` (optional): The number of top students to return (default: 10).
    *   **Response:**
        ```json
        [
          {
            "student_id": 2,
            "name": "Jane Smith",
            "total_credits_received": 50,
            "total_recognitions_received": 3,
            "total_endorsements_received": 5
          }
        ]
        ```
