import React from "react";
import "./RecipeCard.css";

interface RecipeCardProps {
  imageSource: string;
  title: string;
  creator: string;
  onClick: () => void;
}

const RecipeCard: React.FC<RecipeCardProps> = ({
  imageSource,
  title,
  creator,
  onClick,
}) => {
  return (
    <div className="recipe-card" onClick={onClick}>
      <img src={imageSource} alt={title} className="recipe-image" />
      <div className="recipe-info">
        <h3 className="recipe-title">{title}</h3>
        <p className="recipe-creator">{creator}</p>
      </div>
    </div>
  );
};

export default RecipeCard;