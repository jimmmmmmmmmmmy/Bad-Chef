import { useEffect, useState } from "react";
import axios from "axios";
import { Recipe } from "./types";
import { useNavigate } from "react-router-dom";
import ScrollableRecipeList from "./components/ScrollableRecipeListFavs.tsx";
import "./Recipes.css";

function Favorites() {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [filteredRecipes, setFilteredRecipes] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeFilter, setActiveFilter] = useState<string>("All");
  const navigate = useNavigate();
  const API_BASE_URL = `${import.meta.env.VITE_BACKEND_URL}/favorites`; // Use .env

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      navigate("/");
      return;
    }

    const fetchFavorites = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/all`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const favoriteRecipes = response.data.map((fav: any) => ({
          id: fav.recipe_id,
          title: fav.title,
          author_id: fav.author_id,
          category: fav.category,
          imageSource: fav.imageSource || "assets/bruschetta.png",
        }));
        setRecipes(favoriteRecipes);
        setFilteredRecipes(favoriteRecipes);
      } catch (err) {
        console.error("Failed to fetch favorites:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchFavorites();
  }, [navigate]);

  const handleUnlike = (recipeId: number) => {
    setRecipes((prevRecipes) => prevRecipes.filter((recipe) => recipe.id !== recipeId));
    setFilteredRecipes((prevFiltered) => prevFiltered.filter((recipe) => recipe.id !== recipeId));
  };

  const handleFilter = (category: string) => {
    setActiveFilter(category);
    if (category === "All") {
      setFilteredRecipes(recipes);
    } else {
      const filtered = recipes.filter((recipe) => recipe.category === category);
      setFilteredRecipes(filtered);
    }
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
        <div className="filter-buttons">
          <button
            className={`filter-btn ${activeFilter === "All" ? "active" : ""}`}
            onClick={() => handleFilter("All")}
          >
            All
          </button>
          <button
            className={`filter-btn ${activeFilter === "Breakfast" ? "active" : ""}`}
            onClick={() => handleFilter("Breakfast")}
          >
            Breakfast
          </button>
          <button
            className={`filter-btn ${activeFilter === "Lunch" ? "active" : ""}`}
            onClick={() => handleFilter("Lunch")}
          >
            Lunch
          </button>
          <button
            className={`filter-btn ${activeFilter === "Appetizer" ? "active" : ""}`}
            onClick={() => handleFilter("Appetizer")}
          >
            Appetizers
          </button>
          <button
            className={`filter-btn ${activeFilter === "Dinner" ? "active" : ""}`}
            onClick={() => handleFilter("Dinner")}
          >
            Dinner
          </button>
        </div>
      </div>

      <div className="content-container">
        <ScrollableRecipeList recipes={filteredRecipes} onUnlike={handleUnlike} />
      </div>
    </div>
  );
}

export default Favorites;