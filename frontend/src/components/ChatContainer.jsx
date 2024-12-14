// eslint-disable-next-line no-unused-vars
import React, { useState, useEffect } from 'react';

const ChatContainer = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  const handleSend = () => {

    const userMessage = { user: 'User', text: input };
    console.log(userMessage)
    console.log(setMessages([...messages, userMessage]));

   

    // Use EventSource for streaming responses

  setInput(''); // Clear the input
};


  return (
    <div id="chat-container" className="d-flex flex-column border bg-white p-3">
      <div id="chat-display" className="flex-grow-1 overflow-auto mb-2">
      {messages.map((msg, index) => (
          <div key={index}>
            <strong>{msg.user}:</strong> {msg.text}
          </div>
        ))}
      </div>
      <div id="typing-indicator" className="text-muted small mb-2" style={{ display: 'none' }}>Rebecca is typing...</div>
      <div className="input-group">
        <input
          type="text"
          className="form-control"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          aria-label="Message input"
        />
        <button id="send-button" className="btn btn-primary" onClick={handleSend}>
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatContainer;
