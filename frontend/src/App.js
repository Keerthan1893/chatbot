import React, { useState } from "react";
import axios from "axios";

function App() {
  const [query, setQuery] = useState(""); // Stores user input
  const [answer, setAnswer] = useState(""); // Stores API response
  const [loading, setLoading] = useState(false); // Shows loading state

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!query.toLowerCase().startsWith("how to") && !query.toLowerCase().startsWith("how do i")) {
      setAnswer("❌ Sorry, I only answer 'how-to' questions.");
      return;
    }

    setLoading(true);
    setAnswer(""); // Clear previous answer

    try {
      const response = await axios.post("http://127.0.0.1:8000/ask", 
        { query },  
        { headers: { "Content-Type": "application/json" } }
      );
      
      setAnswer(response.data.answer); // Display API response
    } catch (error) {
      console.error("Error fetching response:", error);
      setAnswer("⚠️ Error fetching response. Check your API.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ textAlign: "center", padding: "20px" }}>
      <h1>CDP Chatbot 🤖</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask a 'how-to' question..."
          style={{ padding: "10px", width: "300px" }}
        />
        <button type="submit" style={{ padding: "10px 15px", marginLeft: "10px" }}>
          Ask
        </button>
      </form>
      
      {loading && <p>⏳ Thinking...</p>}
      {answer && <p style={{ marginTop: "20px", fontWeight: "bold" }}>{answer}</p>}
    </div>
  );
}

export default App;
