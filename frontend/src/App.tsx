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

  const handleSubmit = async () => {
    setError(null);
    try {
      if (isSignup) {
        // Signup
        await axios.post("http://localhost:8000/users/", {
          username,
          email,
          password,
        });
        // Auto-login after signup
        const loginResponse = await axios.post("http://localhost:8000/users/token", {
          username,
          password,
        });
        const token = loginResponse.data.access_token;
        localStorage.setItem("token", token);
        axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
        navigate("/recipes");
      } else {
        // Login
        const response = await axios.post("http://localhost:8000/users/token", {
          username,
          password,
        });
        const token = response.data.access_token;
        localStorage.setItem("token", token);
        axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
        navigate("/recipes");
      }
    } catch (err) {
      setError(isSignup ? "Signup failed" : "Login failed");
      console.error(err);
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