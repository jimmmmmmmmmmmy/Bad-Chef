import { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "./App.css";

function LoginSignup() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSignup, setIsSignup] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const API_BASE_URL = `${import.meta.env.VITE_BACKEND_URL}`;
  console.log("API_BASE_URL:", API_BASE_URL);  // Log URL on render

  const handleSubmit = async () => {
    console.log("handleSubmit called, isSignup:", isSignup);  // Confirm function runs
    console.log("Request data:", { username, email, password });  // Log payload
    setError(null);
    try {
      if (isSignup) {
        console.log("Sending signup request to:", `${API_BASE_URL}/users/`);
        await axios.post(`${API_BASE_URL}/users/`, { username, email, password });
        console.log("Signup successful, attempting login...");
        const loginResponse = await axios.post(`${API_BASE_URL}/users/token`, { username, password });
        const token = loginResponse.data.access_token;
        localStorage.setItem("token", token);
        axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
        navigate("/recipes");
      } else {
        console.log("Sending login request to:", `${API_BASE_URL}/users/token`);
        const response = await axios.post(`${API_BASE_URL}/users/token`, { username, password });
        console.log("Login response:", response.data);
        const token = response.data.access_token;
        localStorage.setItem("token", token);
        axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
        navigate("/recipes");
      }
    } catch (err: any) {
      console.log("Full error:", err);
      if (err.response) {
        console.log("Status:", err.response.status);
        console.log("Data:", err.response.data);
        const status = err.response.status;
        const detail = err.response.data?.detail || "An error occurred";
        setError(`Login failed: ${detail} (Status: ${status})`);
      } else {
        console.log("Network error:", err.message);
        setError("Login failed - network error or server unreachable");
      }
    }
  };

  return (
    <div className="App">
      <h1>{isSignup ? "Sign Up" : "Log In"}</h1>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <input value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Username" />
      {isSignup && (
        <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
      )}
      <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" placeholder="Password" />
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