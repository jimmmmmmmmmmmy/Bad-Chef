import axios from "axios";

const BACKEND_URL = `${import.meta.env.VITE_BACKEND_URL}`;
console.log("auth.ts BACKEND_URL:", BACKEND_URL); 

export async function validateToken(token: string): Promise<boolean> {
  try {
    console.log("Validating token:", token); 
    const response = await axios.get(`${BACKEND_URL}/users/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.status === 200;
  } catch (err) {
    console.log("Token validation failed:", err); 
    return false;
  }
}

export const logout = (navigate: (path: string) => void) => {
  localStorage.removeItem("token");
  navigate("/");
};