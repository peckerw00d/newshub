import React from "react";
import SearchBar from "./SearchBar";
import NewsCards from "./NewsCards";
import "./Main.css";

const Main = () => {
  return (
    <main className="main-content">
      <SearchBar />
      <NewsCards />
    </main>
  );
};

export default Main;
