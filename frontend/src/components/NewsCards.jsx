import React, { useEffect, useState } from "react";
import "./NewsCards.css";
// импорт как JSON (если используешь Vite/Webpack, это работает)
import newsData from "../data/newsData.json";

const NewsCards = () => {
  const [news, setNews] = useState([]);

  useEffect(() => {
    // эмуляция fetch-запроса
    setTimeout(() => {
      setNews(newsData);
    }, 500); // псевдо-задержка
  }, []);

  return (
    <section className="news-cards">
      {news.map((item) => (
        <div key={item.id} className="news-card">
          <div
            className="news-card-photo"
            style={{
              backgroundImage: `url(${item.image})`,
              backgroundSize: "cover",
            }}
          />
          <div className="news-card-content">
            <h3>{item.title}</h3>
            <p>{item.description}</p>
          </div>
          <div className="news-card-footer">
            <span className="news-date">{item.date}</span>
            <span className="news-author">{item.author}</span>
          </div>
        </div>
      ))}
    </section>
  );
};

export default NewsCards;
