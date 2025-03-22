import { useEffect, useState } from "react";
import axios from "axios";
import { Recipe } from "./types";
import { Link, useNavigate } from "react-router-dom";
import SearchField from "./components/SearchField";
import ScrollableRecipeList from "./components/ScrollableRecipeList.tsx";
import "./Recipes.css";

function Recipes() {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [filteredRecipes, setFilteredRecipes] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeFilter, setActiveFilter] = useState<string>("All");
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      navigate("/");
      return;
    }

    const fetchRecipes = async () => {
      try {
        const response = await axios.get("http://localhost:8000/recipes/");
        setRecipes(response.data);
        setFilteredRecipes(response.data);
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

  const handleFilter = (category: string) => {
    setActiveFilter(category);
    if (category === "All") {
      setFilteredRecipes(recipes);
    } else {
      const filtered = recipes.filter((recipe) =>
        recipe.category === category
      );
      setFilteredRecipes(filtered);
    }
  };

  if (loading) return <div className="loading">Loading...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="recipes-container">
      {/* Navigation Bar */}
      <nav className="nav-bar">
        <div className="nav-logo">
          <button className="logo-button" onClick={() => window.location.href = '/'}>
            <img src="/logo.png" alt="Logo" className="logo-icon" />
            <span className="logo-text">Bad Chef</span>
          </button>
        </div>
        <ul className="nav-links">
          <li><a href="#">All Recipes</a></li>
          <li><a href="#">Favorites</a></li>
          <li><a href="#">Pantry</a></li>
          <li><a href="#">Travel</a></li>
          <li><a href="#">About</a></li>
        </ul>
      </nav>

      {/* Header */}
      <div className="header">
        <h1 className="title">Recipes</h1>
              {/* Filter Buttons */}
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

      {/* Search Bar and Filter
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
       */}



      {/* Content */}
      <div className="content-container">
        <div className="recipe-list-wrapper">
          <div className="faded-edge" />
          <ScrollableRecipeList recipes={filteredRecipes} />
        </div>
      </div>

      {/* Logout Button (Fixed at Bottom) 
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
      */}
    </div>
  );
}

export default Recipes;