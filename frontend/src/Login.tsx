// frontend/src/Login.tsx
import { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleLogin = async () => {
    try {
      const response = await axios.post("http://localhost:8000/users/token", { username, password });
      const token = response.data.access_token;
      localStorage.setItem("token", token);
      axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
      navigate("/recipes");
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
    <div>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <form onSubmit={(e) => { e.preventDefault(); handleLogin(); }}>
        <input
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Username"
        />
        <input
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          type="password"
          placeholder="Password"
        />
        <button type="submit">Login</button>
      </form>
    </div>
  );
}

export default Login;