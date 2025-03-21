import { useEffect, useState } from "react";
import axios from "axios";
import { Recipe } from "./types";
import { Link, useNavigate } from "react-router-dom";
import SearchField from "./components/SearchField"; // Adapted for React
import ScrollableRecipeList from "./components/ScrollableRecipeList.tsx"; // Adapted for React
import "./Recipes.css"; // New CSS file for web styling


function Recipes() {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [filteredRecipes, setFilteredRecipes] = useState<Recipe[]>([]);
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
        setFilteredRecipes(response.data); // Initially, no filtering
      } catch (err) {
        setError("Failed to fetch recipes");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchRecipes();
  }, [navigate]);

  const handleSearch = (query: string) => {
    if (query) {
      const lowercasedQuery = query.toLowerCase();
      const filtered = recipes.filter(
        (recipe) =>
          recipe.title.toLowerCase().includes(lowercasedQuery) ||
          (recipe.ingredients &&
            recipe.ingredients.some((ingredient: string) =>
              ingredient.toLowerCase().includes(lowercasedQuery)
            ))
      );
      setFilteredRecipes(filtered);
    } else {
      setFilteredRecipes(recipes);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div className="recipes-container">
      {/* Header */}
      <div className="header">
        <Link to="/">
          <img
            className="icon"
            src="/vuesaxlineararrowleft2.png"
            alt="Back"
          />
        </Link>
        <h1 className="title">Recipe Catalog</h1>
        <a href="/support">
          <img
            className="icon"
            src="/help-circle.png"
            alt="Help"
          />
        </a>
      </div>

      {/* Search Bar and Filter */}
      <div className="search-container">
        <div className="search-field-wrapper">
          <SearchField onSearch={handleSearch} placeholder="Search recipes" />
        </div>
        <button className="filter-button">
          <img
            className="filter-icon"
            src="/union1.png"
            alt="Filter"
          />
        </button>
      </div>

      {/* Content */}
      <div className="content-container">
        <h2 className="source-text">All Recipes</h2>
        <div className="recipe-list-wrapper">
          <div className="faded-edge" />
          <ScrollableRecipeList recipes={filteredRecipes} />
        </div>
      </div>

      {/* Logout Button (Fixed at Bottom) */}
      <div className="logout-container">
        <button
          className="logout-button"
          onClick={() => {
            localStorage.removeItem("token");
            navigate("/");
          }}
        >
          Log Out
        </button>
      </div>
    </div>
  );
}

export default Recipes;