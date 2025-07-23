import React from "react";
import "./Footer.css";

const Footer = () => {
  return (
    <footer className="app-footer">
      <div className="footer-text">© 2025 NewsHub — Учебный проект</div>
      <div className="footer-socials">
        <a
          href="https://github.com/yourusername"
          target="_blank"
          rel="noopener noreferrer"
        >
          GitHub
        </a>
        <a
          href="https://t.me/yourusername"
          target="_blank"
          rel="noopener noreferrer"
        >
          Telegram
        </a>
        {/* Добавь другие ссылки при необходимости */}
      </div>
    </footer>
  );
};

export default Footer;
