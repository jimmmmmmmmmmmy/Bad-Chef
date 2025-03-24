import { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "./App.css";

function LoginSignup() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSignup, setIsSignup] = useState(false); // Toggle between signup/login
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const API_BASE_URL = import.meta.env.VITE_BACKEND_URL

  const handleSubmit = async () => {
    setError(null);
    try {
      if (isSignup) {
        // Signup
        await axios.post(`${API_BASE_URL}/users/`, {
          username,
          email,
          password,
        });
        // Auto-login after signup
        const loginResponse = await axios.post(`${API_BASE_URL}/users/token`, {
          username,
          password,
        });
        const token = loginResponse.data.access_token;
        localStorage.setItem("token", token);
        axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
        navigate("/recipes");
      } else {
        // Login
        const response = await axios.post(`${API_BASE_URL}/users/token`, {
          username,
          password,
        });
        console.log("Login response:", response.status, response.data);
        const token = response.data.access_token;
        localStorage.setItem("token", token);
        console.log("Navigating to /recipes");
        axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
        navigate("/recipes");
      }
    } catch (err: any) {
      console.log("Raw error:", err); // Full error object
      if (err.response) {
        console.log("Response status:", err.response.status);
        console.log("Response data:", err.response.data);
        const status = err.response.status;
        const detail = err.response.data?.detail || "An error occurred";
        if (status === 400) {
          setError(`Bad request: ${detail}`);
        } else if (status === 401) {
          setError(`Unauthorized: ${detail}`);
        } else {
          setError(`Login failed: ${detail}`);
        }
      } else {
        setError("Login failed - network error or server unreachable");
      }
    }
  };

  return (
    <div className="App">
      <h1>{isSignup ? "Sign Up" : "Log In"}</h1>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <input
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        placeholder="Username"
      />
      {isSignup && (
        <input
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
        />
      )}
      <input
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        type="password"
        placeholder="Password"
      />
      <button onClick={handleSubmit}>{isSignup ? "Sign Up" : "Log In"}</button>
      <p>
        {isSignup ? "Already have an account?" : "Need an account?"}{" "}
        <button onClick={() => setIsSignup(!isSignup)}>
          {isSignup ? "Log In" : "Sign Up"}
        </button>
      </p>
    </div>
  );
}

export default LoginSignup;