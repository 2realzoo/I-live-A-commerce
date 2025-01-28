import React from 'react';
import { useApp } from '../../AppContext';

const SentimentValue = () => {
  const { sentimentScores, selectedCategory, selectedChannel } = useApp()
  // const sentimentScore = sentimentScores[selectedCategory][selectedChannel]
  const sentimentScore = 1
  const color =  sentimentScore > 0.5 ? 'green' : 'red';

  return (
    <div style={{ margin: '10px', color }}>
      감성 분석 값: {sentimentScore? sentimentScore : '89.3점'}
    </div>
  );
}

export default SentimentValue;
