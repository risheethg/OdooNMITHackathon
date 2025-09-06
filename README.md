# ✨ SynergySphere

A full-stack project management application designed to enhance team productivity and streamline collaboration. Built with React and FastAPI.

![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![MongoDB](https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=for-the-badge&logo=mongodb&logoColor=white)
![TypeScript](https://img.shields.io/badge/typescript-%23007ACC.svg?style=for-the-badge&logo=typescript&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

---

SynergySphere is a full-stack web application designed to enhance team productivity and streamline project management. It features a modern, responsive frontend built with React and a robust, high-performance backend powered by FastAPI.



## 🚀 Core Features

### 🖥️ Frontend (Client-Side)
* 🔐 **Authentication:** Secure user login and registration flows.
* 📊 **Interactive Dashboard:** A central hub to view all projects, active tasks, and key statistics at a glance.
* 🗂️ **Project Management:** Create, update, and delete projects with details like priority and due dates.
* 📌 **Kanban Board:** Visualize and manage tasks within each project using "To Do", "In Progress", and "Done" columns.
* 💬 **Real-time Project Chat:** A dedicated WebSocket-based chat for each project to facilitate seamless communication.
* 👥 **Team Management:** Easily add or remove members from projects.
* 📈 **Data Visualization:** A dedicated analytics page with charts showing project and task statistics.
* 📱 **Responsive Design:** A beautiful and functional UI that works on all screen sizes, built with *shadcn/ui* and *Tailwind CSS*.

### ⚙️ Backend (Server-Side)
* 🔗 **RESTful API:** A well-structured API built with FastAPI and Pydantic for data validation.
* 🛡️ **JWT Authentication:** Secure endpoints using JSON Web Tokens.
* 🗃️ **MongoDB Integration:** Flexible and scalable NoSQL database for storing all application data.
* ⚡ **WebSocket Support:** Powers the real-time chat functionality for instant messaging.
* 🔔 **Notification System:** A backend system to generate notifications for key events (e.g., task assignment, project updates).
* 🧠 **Statistics Engine:** An endpoint (`/stats`) that aggregates and provides data for the frontend analytics page.
* 🤖 **LLM Integration Ready:** Includes a connection module for Google's Gemini API, paving the way for future AI-powered features.

---

## 🛠️ Tech Stack

| Area      | Technology                                                                          |
| :-------- | :---------------------------------------------------------------------------------- |
| **Frontend** | React, Vite, TypeScript, Tailwind CSS, shadcn/ui, React Query, Recharts             |
| **Backend** | FastAPI, Python, MongoDB, Pydantic, JWT, WebSockets                                 |
| **Database** | MongoDB (via `pymongo`)                                                             |

---

## 🏁 Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

* **Node.js** (v18 or newer) and npm
* **Python** (v3.9 or newer) and pip
* **MongoDB** instance (local or cloud-based like MongoDB Atlas)

---

### Server-Side Setup (Backend)

1.  **Navigate to the backend directory:**
    ```sh
    cd backend
    ```

2.  **Create and activate a virtual environment:**
    * *On macOS/Linux:*
        ```sh
        python3 -m venv venv
        source venv/bin/activate
        ```
    * *On Windows:*
        ```sh
        python -m venv venv
        .\venv\Scripts\activate
        ```

3.  **Install Python dependencies:**
    *(Note: If a `requirements.txt` file is not present, you can generate one using `pip freeze > requirements.txt` after installing the packages manually.)*
    ```sh
    pip install fastapi "uvicorn[standard]" pymongo pydantic pydantic-settings python-jose passlib[bcrypt] python-dotenv google-generativeai
    ```

4.  **Configure Environment Variables:**
    * Create a `.env` file in the `backend` directory. You can copy the structure from `.env.template`.
    * Fill in the required values. The JIRA variables are not currently used but are placeholders.

    ```env
    # .env
    MONGODB_URI="mongodb://localhost:27017/"
    MONGODB_NAME="synergysphere"
    GEMINI_API_KEY="your_gemini_api_key_here"

    # Future use placeholders
    JIRA_URL=""
    JIRA_USERNAME=""
    JIRA_API_KEY=""
    ```

5.  **Run the backend server:**
    ```sh
    uvicorn app.main:app --reload
    ```
    The backend API will now be available at `http://127.0.0.1:8000`.

---

### Client-Side Setup (Frontend)

1.  **Navigate to the frontend directory:**
    ```sh
    cd frontend
    ```

2.  **Install npm dependencies:**
    ```sh
    npm install
    ```

3.  **Run the development server:**
    ```sh
    npm run dev
    ```
    The frontend application will be available at `http://localhost:8080` (or another port if 8080 is in use).

---

## 📝 API Documentation

Once the backend server is running, you can access the auto-generated API documentation:

* **Swagger UI:** [`http://127.0.0.1:8000/docs`](http://127.0.0.1:8000/docs)
* **ReDoc:** [`http://127.0.0.1:8000/redoc`](http://127.0.0.1:8000/redoc)

---

## 📁 Project Structure

```text
.
|-- backend/
|   |-- app/
|   |   |-- core/         # Config, DB connection, Security
|   |   |-- models/       # Pydantic data models
|   |   |-- repos/        # Database repository layer
|   |   |-- routes/       # API endpoint definitions
|   |   +-- services/     # Business logic (to be added)
|   +-- main.py           # FastAPI app entry point
|
+-- frontend/
    |-- public/           # Static assets
    |-- src/
    |   |-- components/   # Reusable React components (UI and layout)
    |   |-- hooks/        # Custom React hooks
    |   |-- lib/          # Utility functions
    |   |-- pages/        # Page components for routing
    |   |-- App.tsx       # Main app component with routing
    |   +-- main.tsx      # React app entry point
    +-- package.json      # Frontend dependencies and scripts
