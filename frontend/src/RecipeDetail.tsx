import { useEffect, useState } from "react";
import axios from "axios";
import { useParams, useNavigate } from "react-router-dom";
import { Recipe } from "./types";
import "./RecipeDetail.css";

function RecipeDetail() {
  const { id } = useParams<{ id: string }>();
  const [recipe, setRecipe] = useState<Recipe | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const BACKEND_URL = `${import.meta.env.VITE_BACKEND_URL}`;

  useEffect(() => {
    const fetchRecipe = async () => {
      try {
        const response = await axios.get(`${BACKEND_URL}/recipes/${id}`);
        setRecipe(response.data);
      } catch (err) {
        setError("Failed to fetch recipe");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchRecipe();
  }, [id]);

  if (loading) return <div className="loading">Loading...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!recipe) return <div className="not-found">Recipe not found</div>;

  // Split ingredients into an array for rendering as a list
  const ingredientsList = recipe.ingredients ? recipe.ingredients.split(", ") : [];
  // Split instructions into an array for rendering as a list
  const instructionsList = recipe.instructions ? recipe.instructions.split("\n") : [];

  // Format each ingredient to capitalize the item name (e.g., chicken_breast -> Chicken Breast)
  const formatIngredient = (ingredient: string) => {
    // Split into amount, unit, and item (e.g., "2 piece chicken_breast")
    const parts = ingredient.split(" ");
    if (parts.length < 3) return ingredient; // Fallback if format is unexpected

    const amount = parts[0]; // e.g., "2"
    const unit = parts[1]; // e.g., "piece"
    const item = parts.slice(2).join(" ").replace("_", " "); // e.g., "chicken breast"

    // Capitalize each word in the item name
    const formattedItem = item
      .split(" ")
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");

    return `${amount} ${unit} ${formattedItem}`; // e.g., "2 piece Chicken Breast"
  };

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


    <div className="recipe-detail-container">
      <h1 className="recipe-title-full">{recipe.title}</h1>
      <section className="recipe-section">
        <h2>Description</h2>
        <p>{recipe.description}</p>
        <div className="recipe-details">
          <h3>Time</h3>
          <p>{recipe.time}</p>
          <h3>Serving Size</h3>
          <p>{recipe.serves}</p>
        </div>
      </section>
      <section className="recipe-section">
        <h2>Ingredients</h2>
        <ul className="recipe-list">
          {ingredientsList.map((ingredient, index) => (
            <li key={index}>{formatIngredient(ingredient)}</li>
          ))}
        </ul>
      </section>
      <section className="recipe-section">
        <h2>Instructions</h2>
        <ol className="recipe-list">
          {instructionsList.map((instruction, index) => (
            <li key={index}>{instruction}</li>
          ))}
        </ol>
      </section>
      {/* <section className="recipe-section">
      <h2>Details</h2>
        <p>
          <strong>Created At:</strong>{" "}
          {new Date(recipe.created_at).toLocaleString()}
        </p>
      </section> */}
    </div>
  </div>
  );
}

export default RecipeDetail;