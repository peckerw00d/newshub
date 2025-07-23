import React, { useState } from "react";
import "./SearchBar.css";

const SearchBar = ({ onSearch }) => {
  const [query, setQuery] = useState("");

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      onSearch(query.trim());
    }
  };

  return (
    <div className="search-bar-wrapper">
      <input
        type="text"
        className="search-input"
        placeholder="Поиск..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={handleKeyDown}
      />
      <span className="search-icon">🔍</span>
    </div>
  );
};

export default SearchBar;
