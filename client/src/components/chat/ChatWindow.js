// src/components/ChatWindow.js
import React from 'react';

function ChatWindow({ messages }) {
  return (
    <div
      style={{
        margin: '10px',
        padding: '10px',
        border: '1px solid #ccc',
        width: '300px',
        height: '200px',
        overflowY: 'auto',
      }}
    >
      {messages.map((msg, index) => (
        <div key={index} style={{ marginBottom: '5px' }}>
          {msg}
        </div>
      ))}
    </div>
  );
}

export default ChatWindow;
