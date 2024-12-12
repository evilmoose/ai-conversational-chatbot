# Flask, React, Redux, and Three.js Integration Example

This project demonstrates a scalable application integrating Flask, React, Redux, and Three.js, with PostgreSQL as the database and a well-structured code organization for maintainability and scalability.

---

## Table of Contents
- [Flask, React, Redux, and Three.js Integration Example](#flask-react-redux-and-threejs-integration-example)
  - [Table of Contents](#table-of-contents)
  - [File Structure](#file-structure)
  - [Setup Instructions](#setup-instructions)
    - [Backend Setup](#backend-setup)
    - [Frontend Setup](#frontend-setup)
  - [Backend Configuration](#backend-configuration)
    - [Flask Configuration](#flask-configuration)
  - [Frontend Configuration](#frontend-configuration)
  - [Vite Configuration](#vite-configuration)
  - [Deployment](#deployment)
  - [Contributing](#contributing)
  - [License](#license)

---

## File Structure

The project follows a modular structure to separate concerns and ensure scalability:

```
project/
|-- backend/
|   |-- app.py
|   |-- routes/
|   |   |-- __init__.py
|   |   |-- auth_routes.py
|   |   |-- chat_routes.py
|   |-- utils/
|   |   |-- __init__.py
|   |   |-- db_utils.py
|-- frontend/
|   |-- public/
|   |-- src/
|   |   |-- components/
|   |   |   |-- Header.jsx
|   |   |   |-- Sidebar.jsx
|   |   |   |-- ThreeJSContainer.jsx
|   |   |   |-- ChatContainer.jsx
|   |   |-- store/
|   |   |   |-- chatSlice.js
|   |   |   |-- index.js
|   |   |-- App.js
|   |   |-- main.js
|   |   |-- pages/
|   |   |   |-- Register.jsx
|   |   |   |-- Login.jsx
|   |   |   |-- Home.jsx
|   |-- package.json
|   |-- vite.config.js
|-- .env
|-- requirements.txt
```

---

## Setup Instructions

### Backend Setup
1. **Create a Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # On Windows: .venv\Scripts\activate
   ```
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run Flask Server**:
   ```bash
   python backend/app.py
   ```
   The backend server will be available at `http://127.0.0.1:5000`.

### Frontend Setup
1. **Install Node.js Dependencies**:
   ```bash
   cd frontend
   npm install
   ```
2. **Run Development Server**:
   ```bash
   npm run dev
   ```
   The React app will be available at `http://127.0.0.1:5173`.

---

## Backend Configuration

### Flask Configuration
1. **Serve Static React App**: Update `app.py` to serve React's static files and API routes:

   ```python
   from flask import Flask, send_from_directory
   from routes.auth_routes import auth_routes
   from routes.chat_routes import chat_routes
   from flask_cors import CORS

   app = Flask(__name__, static_folder='../frontend/dist', static_url_path='')
   CORS(app)

   # Register blueprints
   app.register_blueprint(auth_routes, url_prefix='/auth')
   app.register_blueprint(chat_routes, url_prefix='/chat')

   # Serve React static files
   @app.route('/')
   @app.route('/<path:path>')
   def serve_react_app(path=''):
       if path and (app.static_folder / path).exists():
           return send_from_directory(app.static_folder, path)
       return send_from_directory(app.static_folder, 'index.html')

   if __name__ == '__main__':
       app.run(debug=True)
   ```

2. **API Endpoints**:
   - Auth routes: `/auth/login`, `/auth/register`
   - Chat routes: `/chat/conversations`, `/chat/add`

3. **Database Utilities**: Utilize `db_utils.py` for PostgreSQL queries.

---

## Frontend Configuration

1. **React Router**:
   Ensure routing is configured in `src/App.js`:

   ```javascript
   import React from 'react';
   import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
   import Register from './pages/Register';
   import Login from './pages/Login';
   import Home from './pages/Home';

   const App = () => (
     <Router>
       <Routes>
         <Route path="/" element={<Home />} />
         <Route path="/register" element={<Register />} />
         <Route path="/login" element={<Login />} />
       </Routes>
     </Router>
   );

   export default App;
   ```

2. **Components**:
   - Split `index.html` into reusable React components (e.g., `Header`, `Sidebar`, etc.).

3. **Redux Store**:
   Use Redux Toolkit to manage the global state (`store/chatSlice.js`).

4. **API Integration**:
   Use `fetch` or `Axios` to interact with Flask APIs.

---

## Vite Configuration

1. **Proxy API Requests**:
   Add proxy settings in `vite.config.js`:

   ```javascript
   import { defineConfig } from 'vite';
   import react from '@vitejs/plugin-react';

   export default defineConfig({
     plugins: [react()],
     server: {
       proxy: {
         '/auth': 'http://127.0.0.1:5000',
         '/chat': 'http://127.0.0.1:5000',
       },
     },
   });
   ```

---

## Deployment

1. **Backend Deployment**:
   Deploy the Flask app using platforms like Heroku, Render, or AWS.

2. **Frontend Deployment**:
   Deploy the React app using Netlify or Vercel. Ensure the build files are served from Flask in production.

3. **Environment Variables**:
   Use `.env` files to manage sensitive configurations for both backend and frontend.

---

## Contributing

1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add feature description"
   ```
4. Push to the branch:
   ```bash
   git push origin feature-name
   ```
5. Open a Pull Request.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

