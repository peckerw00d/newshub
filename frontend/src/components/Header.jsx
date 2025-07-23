import React from "react";
import "./Header.css";

const categories = [
  { key: "politics", label: "Politics" },
  { key: "business", label: "Business" },
  { key: "sports", label: "Sports" },
  { key: "world", label: "World" },
  { key: "travel", label: "Travel" },
  { key: "podcasts", label: "Podcasts" },
];

const Header = () => (
  <header className="app-header">
    <div className="header-content">
      <img src="/logo.png" alt="NewsHub Logo" className="logo-img" />
      <nav className="header-nav">
        {categories.map((cat) => (
          <button key={cat.key} className="nav-button">
            {cat.label}
          </button>
        ))}
      </nav>
    </div>
  </header>
);

export default Header;
