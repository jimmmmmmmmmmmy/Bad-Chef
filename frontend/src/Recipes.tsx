// frontend/src/Recipes.tsx
import { useEffect, useState } from "react";
import axios from "axios";
import { Recipe } from "./types";
import { Link, useNavigate } from "react-router-dom";
import "./App.css"; // Reuse styles

function Recipes() {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      navigate("/"); // Redirect to login if not authenticated
      return;
    }

    const fetchRecipes = async () => {
      try {
        const response = await axios.get("http://localhost:8000/recipes/");
        setRecipes(response.data);
      } catch (err) {
        setError("Failed to fetch recipes");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchRecipes();
  }, [navigate]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div className="App">
      <h1>Recipe Platform</h1>
      <button onClick={() => { localStorage.removeItem("token"); navigate("/"); }}>Log Out</button>
      <ul>
        {recipes.map((recipe) => (
          <li key={recipe.id}>
            <Link to={`/recipe/${recipe.id}`}>{recipe.title}</Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Recipes;