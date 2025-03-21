import { useState } from "react";
import "./SearchField.css";

interface SearchFieldProps {
  onSearch: (query: string) => void;
  placeholder: string;
}

const SearchField: React.FC<SearchFieldProps> = ({ onSearch, placeholder }) => {
  const [searchText, setSearchText] = useState("");

  const handleSearch = () => {
    if (searchText.trim()) {
      onSearch(searchText.trim());
    }
  };

  return (
    <div className="search-field">
      <input
        className="search-input"
        placeholder={placeholder}
        value={searchText}
        onChange={(e) => setSearchText(e.target.value)}
        onKeyPress={(e) => e.key === "Enter" && handleSearch()}
      />
      <button onClick={handleSearch} className="search-button">
        🔍
      </button>
    </div>
  );
};

export default SearchField;