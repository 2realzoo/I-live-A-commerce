// src/components/ChatReader.js
import React from 'react';

function ChatReader({ mode, setMode }) {
  const modes = ['잇섭', '아이유'];

  const handleModeChange = (e) => {
    setMode(e.target.value);
  };

  return (
    <div style={{ margin: '10px' }}>
      <label>채팅 읽어주기: </label>
      <select value={mode} onChange={handleModeChange}>
        {modes.map((m) => (
          <option key={m} value={m}>
            {m}
          </option>
        ))}
      </select>
      {/* 실제로는 모드에 따라 TTS(Text To Speech) 기능을 변경 적용하는 로직 필요 */}
    </div>
  );
}

export default ChatReader;
