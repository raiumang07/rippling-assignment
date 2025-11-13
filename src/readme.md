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
    *   **Request Parameters:**
        *   `recognition_id`: The ID of the recognition to endorse.
        *   `endorser_id`: The ID of the student endorsing the recognition.
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
