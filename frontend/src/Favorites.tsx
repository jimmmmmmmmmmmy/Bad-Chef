import { useEffect, useState } from "react";
import axios from "axios";
import { Recipe } from "./types";
import { Link, useNavigate } from "react-router-dom";
import ScrollableRecipeList from "./components/ScrollableRecipeList.tsx";
import "./Recipes.css";

function Favorites() {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      navigate("/");
      return;
    }

    const fetchFavorites = async () => {
      try {
        const response = await axios.get("http://localhost:8000/favorites/all", {
          headers: { Authorization: `Bearer ${token}` },
        });
        const favoriteRecipes = response.data.map((fav: any) => ({
          id: fav.recipe_id,
          title: fav.title,
          author_id: fav.author_id,
          imageSource: fav.image_source || "assets/bruschetta.png",
        }));
        setRecipes(favoriteRecipes);
      } catch (err) {
        console.error("Failed to fetch favorites:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchFavorites();
  }, [navigate]);

  const handleUnlike = (recipeId: number) => {
    setRecipes((prevRecipes) =>
      prevRecipes.filter((recipe) => recipe.id !== recipeId)
    );
  };

  if (loading) return <div className="loading">Loading...</div>;

  return (
    <div className="recipes-container">
      <nav className="nav-bar">
        <div className="nav-logo">
          <button className="logo-button" onClick={() => navigate("/")}>
            <img src="/logo.png" alt="Logo" className="logo-icon" />
            <span className="logo-text">Bad Chef</span>
          </button>
        </div>
        <ul className="nav-links">
          <li><a href="/Favorites">Favorites</a></li>
          <li><a href="#">Pantry</a></li>
          <li><a href="#">Travel</a></li>
          <li><a href="#">About</a></li>
        </ul>
      </nav>
      <div className="header">
        <h1 className="title">Favorites</h1>
      </div>
      <div className="content-container">
        <ScrollableRecipeList recipes={recipes} onUnlike={handleUnlike} />
      </div>
    </div>
  );
}

export default Favorites;