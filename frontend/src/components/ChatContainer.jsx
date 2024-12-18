// eslint-disable-next-line no-unused-vars
import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';

const ChatContainer = () => {
  const [messages, setMessages] = useState([]); // Chat history
  const [userInput, setUserInput] = useState(""); // User input
  const [isStreaming, setIsStreaming] = useState(false); // Streaming state

  // Retrieve username from localStorage
  const username = localStorage.getItem('username') || 'User';
  const token = localStorage.getItem('token');

  const handleSendMessage = async () => {
    setMessages((prev) => [...prev, { role: 'user', content: userInput, name: username }]);
    setIsStreaming(true);
  
    const response = await fetch("http://127.0.0.1:5000/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
      },
      body: JSON.stringify({
        model: "llama3.2",
        messages: messages,
        user_input: userInput,
      }),
    });
  
    if (!response.body) return;
  
    // Use ReadableStream to process the response
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let botResponse = "";
  
    while (true) {
      const { value, done } = await reader.read();
      
      if (done) break;
      const chunk = decoder.decode(value, { stream: true });
      botResponse += chunk;
  
      setMessages((prev) => {
        const updatedMessages = [...prev];
        if (
          updatedMessages.length > 0 &&
          updatedMessages[updatedMessages.length - 1].role === "assistant"
        ) {
          updatedMessages[updatedMessages.length - 1].content = botResponse;
        } else {
          updatedMessages.push({ role: "assistant", content: botResponse, name: "Rebecca" });
        }
        return updatedMessages;
      });
    }

    // Send the bot's response for TTS and play audio
    fetch("http://127.0.0.1:5000/api/text-to-speech", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: botResponse }),
    })
    .then((res) => res.blob())
    .then((blob) => {
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      audio.play();
    })
    .catch((err) => console.error("TTS Error:", err));
  
    setIsStreaming(false);
    setUserInput("");
  };

  return (
    <div id="chat-container" className="d-flex flex-column border bg-white p-3">
      <div id="chat-display" className="flex-grow-1 overflow-auto mb-2">
        {messages.map((msg, index) => (
          <div 
            key={index}>
            <strong>{msg.role === "user" ? `${msg.name}: ` : "Rebecca: "}</strong>
            {msg.role === "assistant" ? (
        <ReactMarkdown className="markdown">{msg.content}</ReactMarkdown>
      ) : (
        <span><p>{msg.role === "user" ? `${msg.content}` : ""} </p></span>
      )}
          </div>
        ))}
      </div>
      <div id="typing-indicator" className="text-muted small mb-2" style={{ display: 'none' }}>Rebecca is typing...</div>
      <div className="input-group">
        <input
          type="text"
          className="form-control"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          placeholder="Type your message..."
          aria-label="Message input"
        />
        <button 
          id="send-button" 
          className="btn btn-primary" 
          onClick={handleSendMessage}
          disabled={isStreaming || !userInput.trim()}
          >
          {isStreaming ? "Sending..." : "Send"}
        </button>
      </div> 
    </div>
  );
};

export default ChatContainer;
