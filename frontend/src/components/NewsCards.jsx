import React, { useEffect, useState } from "react";
import "./NewsCards.css";

const API_URL = "http://localhost:8000/api/news";

const NewsCards = () => {
  const [news, setNews] = useState([]);
  const [cursor, setCursor] = useState(null);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);

  const fetchNews = async () => {
    setLoading(true);
    try {
      const url = cursor ? `${API_URL}?cursor=${cursor}` : API_URL;
      const response = await fetch(url);
      const data = await response.json();

      setNews((prev) => [...prev, ...data.items]);
      setCursor(data.next_cursor);
      setHasMore(!!data.next_cursor); // если курсора нет — больше данных нет
    } catch (error) {
      console.error("Ошибка загрузки новостей:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNews(); // первая загрузка
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
          <button
            className="load-more-button"
            onClick={fetchNews}
            disabled={loading}
          >
            {loading ? "Загрузка..." : "Загрузить ещё"}
          </button>
        </div>
      )}
    </div>
  );
};

export default NewsCards;
