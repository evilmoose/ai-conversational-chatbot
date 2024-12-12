import { useState } from 'react';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (!input.trim()) return;
    setMessages([...messages, { user: 'You', text: input }]);
    setInput('');
    // Simulate response
    setMessages((prev) => [...prev, { user: 'Rebecca', text: 'Hello!' }]);
  };

  return (
    <div className="container-fluid vh-100 d-flex flex-column">
      <header className="d-flex align-items-center px-3 py-2 border-bottom">
        <h2>Rebecca&apos;s Chat</h2>
      </header>
      <main className="flex-grow-1 d-flex flex-column border p-3">
        <div id="chat-display" className="flex-grow-1 overflow-auto">
          {messages.map((msg, index) => (
            <div key={index}>
              <strong>{msg.user}:</strong> {msg.text}
            </div>
          ))}
        </div>
        <div className="input-group mt-3">
          <input
            type="text"
            className="form-control"
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <button className="btn btn-primary" onClick={handleSend}>Send</button>
        </div>
      </main>
    </div>
  );
};

export default Chat;

