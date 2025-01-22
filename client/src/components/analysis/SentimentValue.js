import React from 'react';
import { useApp } from '../../AppContext';

const SentimentValue = () => {
  const { sentimentScore, setSentimentScore } = useApp()
  const color = sentimentScore > 0.5 ? 'green' : 'red';

  return (
    <div style={{ margin: '10px', color }}>
      감성 분석 값: {sentimentScore?{sentimentScore}:'없음'}
    </div>
  );
}

export default SentimentValue;
