import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App.jsx";
import { TickerProvider } from "./context/TickerContext.jsx";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <TickerProvider>
        <App />
      </TickerProvider>
    </BrowserRouter>
  </React.StrictMode>
);
