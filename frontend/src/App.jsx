import React, { useState } from "react";
import Header from "./components/Header";
import SearchBar from "./components/SearchBar";
import NewsCards from "./components/NewsCards";
import Footer from "./components/Footer";

function App() {
  const [query, setQuery] = useState("");

  return (
    <>
      <Header />
      <SearchBar onSearch={setQuery} />
      <NewsCards searchQuery={query} />
      <Footer />
    </>
  );
}

export default App;
