// src/components/ChannelSelector.js
import React from 'react';

function ChannelSelector({ selectedChannel, setSelectedChannel, channelList }) {
  const handleChange = (e) => {
    setSelectedChannel(e.target.value);
  };

  return (
    <div style={{ margin: '10px' }}>
      <label>채널 선택: </label>
      <select value={selectedChannel} onChange={handleChange}>
        {channelList.map((ch) => (
          <option key={ch} value={ch}>
            {ch}
          </option>
        ))}
      </select>
    </div>
  );
}

export default ChannelSelector;
