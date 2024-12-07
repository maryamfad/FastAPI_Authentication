
# FastAPI Todo list app with SQLite Database

This project is a FastAPI-based REST API that handles user todos . The responses are stored in a SQLite database. The app provides endpoints to authenticate users and retrieve/create/delete todos.
** Features
* Fast and Asynchronous: Utilizes Python's async capabilities for improved performance.
* OpenAPI Documentation: Auto-generated API documentation using Swagger UI and ReDoc.
* Secure: Includes authentication and authorization features.
* Extensible: Easily customizable and scalable.
* Database Integration: Supports integration with SQL and NoSQL databases.

## Prerequisites

Before running the application, make sure you have the following installed on your system:

- Python 3.x
- `pip` (Python package installer)

## Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/maryamfad/FastAPI_Authentication.git
   ```
2. **Create a Virtual Environment (Optional but Recommended)**:
   ```bash
   python3 -m venv fastapitodoenv
   ```
3. **Activate the Virtual Environment**:

* On Windows:
  ```bash
  fastapitodoenv\Scripts\activate

* On macOS/Linux:
  ```bash
  source fastapitodoenv/bin/activate

4. **Install Dependencies**:

```bash
pip install -r requirements.txt
```

5. **Run the Flask App**:
```bash
cd ToDoApp
uvicorn main:app --reload
```
6. **Access the Application**:
Once the server is running, you can access the application at http://127.0.0.1:8000/.



## API Endpoints
* Authentication APIs (/auth)

| Method | Endpoint                    | Description              |
|--------|-----------------------------|--------------------------|
| `GET`  | `/auth/users`               | Retrieve all users.      |
| `GET`  | `/auth/user/{userId}`       | Get user by ID.          |
| `PUT`  | `/auth/user/{userId}`       | Update user details.     |
| `POST` | `/auth/create_auth`         | Create a new user.       |
| `DELETE` | `/auth/users/{userId}`    | Delete user by ID.       |
| `POST` | `/auth/token`               | Login to get access token.|



* Authentication APIs (/auth)

| Method | Endpoint                    | Description              |
|--------|-----------------------------|--------------------------|
| `GET`  | `/todo/`                    | Retrieve all to-dos.     |
| `GET`  | `/todo/todo/{todoId}`       | Get to-do by ID.         |
| `PUT`  | `/todo/todo/{todoId}`       | Update a to-do.          |
| `DELETE` | `/todo/todo/{todoId}`     | Delete a to-do.          |
| `POST` | `/todo/todo`                | Create a new to-do.      |

<img width="727" alt="1" src="https://github.com/user-attachments/assets/bd15e687-53b5-488c-993a-a768944917fc">
