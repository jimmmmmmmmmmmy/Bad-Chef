## Installation:

How to set up and run this locally

1)	Install Poetry via Homebrew	`brew install poetry`
2)	Install backend dependencies `cd app; poetry install`
3)	Create an `.env` file in `/frontend`and add VITE_BACKEND_URL, VITE_FRONTEND_URL 

```
VITE_BACKEND_URL='http://localhost:8000'   
VITE_FRONTEND_URL='http://localhost:5173'  
```

Create root `.env` file and add a secret key:

```
SECRET_KEY='<your-random-hex-string>'  # Generate via `openssl rand -hex 32`
```

4)	Install frontend dependencies	`cd frontend; npm install`
5)	Run backend server	`poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
6)	Run frontend server	`npx vite --host` from frontend directory
7)	Access application	Open browser at FRONTEND_URL (e.g., localhost:5173)


![Screenshot 2025-03-23 at 9 48 40 PM](https://github.com/user-attachments/assets/14ebd092-3b12-4649-9a93-95cfe43ae6cb)
