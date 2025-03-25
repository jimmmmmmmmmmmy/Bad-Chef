import React from "react";
import "./RecipeCard.css";

interface RecipeCardProps {
  image_source: string;
  title: string;
  creator: string;
  onClick: () => void;
}

const RecipeCard: React.FC<RecipeCardProps> = ({
  image_source,
  title,
  creator,
  onClick,
}) => {
  return (
    <div className="recipe-card" onClick={onClick}>
      <img src={image_source} alt={title} className="recipe-image" />
      <div className="recipe-info">
        <h3 className="recipe-title">{title}</h3>
        <p className="recipe-creator">{creator}</p>
      </div>
    </div>
  );
};

export default RecipeCard;