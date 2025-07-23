import React, { useEffect, useState } from "react";
import "./NewsCards.css";
import newsData from "../data/newsData.json";

const PAGE_SIZE = 4;

const NewsCards = () => {
  const [news, setNews] = useState([]);
  const [cursor, setCursor] = useState(0);

  useEffect(() => {
    // Первичная загрузка
    const initialNews = newsData.slice(0, PAGE_SIZE);
    setNews(initialNews);
    setCursor(PAGE_SIZE);
  }, []);

  const handleLoadMore = () => {
    const nextSlice = newsData.slice(cursor, cursor + PAGE_SIZE);
    setNews((prev) => [...prev, ...nextSlice]);
    setCursor((prev) => prev + PAGE_SIZE);
  };

  return (
    <div>
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

      {cursor < newsData.length && (
        <div className="load-more-wrapper">
          <button className="load-more-button" onClick={handleLoadMore}>
            Загрузить ещё
          </button>
        </div>
      )}
    </div>
  );
};

export default NewsCards;
