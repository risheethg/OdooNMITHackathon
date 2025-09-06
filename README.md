SynergySphere is a full-stack web application designed to enhance team productivity and streamline project management. It features a modern, responsive frontend built with React and a robust, high-performance backend powered by FastAPI.

## ✨ Features

### Frontend (Client-Side)
- *Authentication:* Secure user login and registration.
- *Interactive Dashboard:* A central hub to view all projects, active tasks, and key statistics at a glance.
- *Project Management:* Create, update, and delete projects with details like priority and due dates.
- *Kanban-style Task Board:* Visualize and manage tasks within each project using "To Do", "In Progress", and "Done" columns.
- *Real-time Project Chat:* A dedicated WebSocket-based chat for each project to facilitate seamless communication.
- *Team Management:* Easily add or remove members from projects.
- *Data Visualization:* A dedicated analytics page with charts showing project and task statistics.
- *Responsive Design:* A beautiful and functional UI that works on all screen sizes, built with *shadcn/ui* and *Tailwind CSS*.

### Backend (Server-Side)
- *RESTful API:* A well-structured API built with FastAPI and Pydantic for data validation.
- *JWT Authentication:* Secure endpoints using JSON Web Tokens.
- *MongoDB Integration:* Flexible and scalable NoSQL database for storing all application data.
- *WebSocket Support:* Powers the real-time chat functionality for instant messaging.
- *Notification System:* A backend-only system to generate notifications for key events (e.g., task assignment, project updates). *Note: The UI for displaying these notifications is not yet implemented.*
- *Statistics Engine:* An endpoint (/stats) that aggregates and provides data for the frontend analytics page.
- *LLM Integration Ready:* Includes a connection module for Google's Gemini API, paving the way for future AI-powered features.

---

## 🛠️ Tech Stack

| Area      | Technology                                                                                             |
| :-------- | :----------------------------------------------------------------------------------------------------- |
| *Frontend*  | React, Vite, TypeScript, Tailwind CSS, shadcn/ui, React Query, Recharts |
| *Backend*   | FastAPI, Python, MongoDB, Pydantic, JWT, WebSockets |
| *Database*  | MongoDB (via pymongo)                                                    |

---

## 🚀 Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

- *Node.js* (v18 or newer) and npm
- *Python* (v3.9 or newer) and pip
- *MongoDB* instance (local or cloud-based like MongoDB Atlas)

### Backend Setup

1.  *Navigate to the backend directory:*
    sh
    cd backend
    

2.  *Create and activate a virtual environment:*
    sh
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    

3.  *Install Python dependencies:*
    (You may need to generate a requirements.txt file first: pip freeze > requirements.txt)
    sh
    pip install -r requirements.txt
    
    (If requirements.txt doesn't exist, install manually: pip install fastapi "uvicorn[standard]" pymongo pydantic pydantic-settings python-jose passlib[bcrypt] python-dotenv google-generativeai)

4.  *Configure Environment Variables:*
    -   Create a .env file in the backend directory by copying from .env.template.
    -   Fill in your MONGODB_URI, MONGODB_NAME, and GEMINI_API_KEY.
    env
    # .env
    MONGODB_URI="mongodb://localhost:27017/"
    MONGODB_NAME="synergysphere"
    GEMINI_API_KEY="your_gemini_api_key_here"
    JIRA_URL=""
    JIRA_USERNAME=""
    JIRA_API_KEY=""

    

5.  *Run the backend server:*
    sh
    uvicorn app.main:app --reload
    
    The backend API will be available at http://127.0.0.1:8000.

### Frontend Setup

1.  *Navigate to the frontend directory:*
    sh
    cd frontend
    

2.  *Install npm dependencies:*
    sh
    npm install
    

3.  *Run the development server:*
    sh
    npm run dev
    
    The frontend application will be available at http://localhost:8080 (or another port if 8080 is busy).

---

## 📁 Project Structure


.
├── backend/
│   ├── app/
│   │   ├── core/         # Config, DB connection, Security
│   │   ├── models/       # Pydantic data models
│   │   ├── repos/        # Database repository layer
│   │   ├── routes/       # API endpoint definitions
│   │   └── services/     # Business logic (to be added)
│   └── main.py           # FastAPI app entry point
│
└── frontend/
    ├── public/           # Static assets
    ├── src/
    │   ├── components/   # Reusable React components (UI and layout)
    │   ├── hooks/        # Custom React hooks
    │   ├── lib/          # Utility functions
    │   ├── pages/        # Page components for routing
    │   ├── App.tsx       # Main app component with routing
    │   └── main.tsx      # React app entry point
    └── package.json      # Frontend dependencies and scripts
