// src/components/SentimentValue.js
import React from 'react';

function SentimentValue({ SentimentScore, setSentimentScore }) {
  // 점수에 따라 색상 달리 표시하는 간단한 예시
  const color = SentimentScore > 0.5 ? 'green' : 'red';

  return (
    <div style={{ margin: '10px', color }}>
      감성 분석 값: {SentimentScore}
    </div>
  );
}

export default SentimentValue;
