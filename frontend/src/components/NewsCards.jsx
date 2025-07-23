import React, { useState, useEffect } from "react";
import "./NewsCards.css";

const NewsCards = ({ searchQuery }) => {
  const [news, setNews] = useState([]);
  const [cursor, setCursor] = useState(null);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);

  const API_URL = searchQuery
    ? `http://localhost:8000/api/news/search/?query=${encodeURIComponent(searchQuery)}`
    : "http://localhost:8000/api/news";

  const fetchNews = async (reset = false) => {
    setLoading(true);
    try {
      const url = cursor && !reset ? `${API_URL}&cursor=${cursor}` : API_URL;
      const response = await fetch(url);
      const data = await response.json();

      setNews((prev) => (reset ? data.items : [...prev, ...data.items]));
      setCursor(data.next_cursor);
      setHasMore(!!data.next_cursor);
    } catch (error) {
      console.error("Ошибка загрузки новостей:", error);
    } finally {
      setLoading(false);
    }
  };

  // Загрузка при смене поискового запроса
  useEffect(() => {
    setCursor(null);
    fetchNews(true); // reset = true
  }, [searchQuery]);

  useEffect(() => {
    if (!searchQuery) fetchNews(true); // первая загрузка
  }, []);

  return (
    <div>
      <section className="news-cards">
        {news.map((item, index) => (
          <div key={index} className="news-card">
            <div
              className="news-card-photo"
              style={{
                backgroundImage: `url(${item.url})`,
                backgroundSize: "cover",
              }}
            />
            <div className="news-card-content">
              <h3>{item.title}</h3>
              <p>{item.description}</p>
            </div>
            <div className="news-card-footer">
              <span className="news-date">
                {new Date(item.published_at).toLocaleDateString("ru-RU")}
              </span>
              <span className="news-author">NewsHub</span>
            </div>
          </div>
        ))}
      </section>

      {hasMore && (
        <div className="load-more-wrapper">
          <button className="load-more-button" onClick={() => fetchNews()}>
            {loading ? "Загрузка..." : "Загрузить ещё"}
          </button>
        </div>
      )}
    </div>
  );
};
export default NewsCards;
