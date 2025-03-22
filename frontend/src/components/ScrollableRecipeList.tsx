import { useState } from "react";
import { Recipe } from "../types";
import RecipeCard from "./RecipeCard";
import "./ScrollableRecipeList.css";
import { useNavigate } from "react-router-dom";

interface ScrollableRecipeListProps {
  recipes: Recipe[];
}

const ScrollableRecipeList: React.FC<ScrollableRecipeListProps> = ({
  recipes,
}) => {
  const [likedRecipes, setLikedRecipes] = useState<Set<number>>(new Set());
  const navigate = useNavigate();

  const toggleLike = (index: number) => {
    setLikedRecipes((prevLiked) => {
      const newLiked = new Set(prevLiked);
      if (newLiked.has(index)) {
        newLiked.delete(index);
      } else {
        newLiked.add(index);
      }
      return newLiked;
    });
  };

  const handleRecipePress = (recipe: Recipe) => {
    navigate(`/recipe/${recipe.id}`);
  };

  return (
    <div className="recipe-list-container">
      {recipes.map((item) => (
        <div className="card-wrapper" key={item.id}> {/* Use item.id as key */}
          <RecipeCard
            imageSource={item.imageSource || "assets/bruschetta.png"}
            title={item.title}
            creator={`by ${item.author_id || "Unknown"}`}
            onClick={() => handleRecipePress(item)}
          />
          <button
            className={`heart-icon-container ${
              likedRecipes.has(item.id) ? "heart-icon-container-liked" : ""
            }`}
            onClick={() => toggleLike(item.id)}
          >
            {likedRecipes.has(item.id) ? "❤️" : "🤍"}
          </button>
        </div>
      ))}
    </div>
  );
};

export default ScrollableRecipeList;