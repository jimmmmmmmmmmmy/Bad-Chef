import axios from "axios";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL

export async function validateToken(token: string): Promise<boolean> {
  try {
    const response = await axios.get(`${BACKEND_URL}/users/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.status === 200;
  } catch {
    return false;
  }
}

// Function to log out/clear token and redirect back tgo login
export const logout = (navigate: (path: string) => void) => {
  localStorage.removeItem("token");
  navigate("/");
};