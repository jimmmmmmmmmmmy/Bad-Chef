import axios from "axios";

// Validate token via  backend
export const validateToken = async (token: string | null): Promise<boolean> => {
  if (!token) return false;

  try {
    const response = await axios.get("http://192.168.1.203:8000/users/me", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    // If request succeeds (status 200), the token is valid
    return response.status === 200;
  } catch (error: any) {
    // If request fails, the token is invalid
    console.error("Token validation failed:", error.response?.data || error.message);
    return false;
  }
};

// Function to log out/clear token and redirect back tgo login
export const logout = (navigate: (path: string) => void) => {
  localStorage.removeItem("token");
  navigate("/");
};