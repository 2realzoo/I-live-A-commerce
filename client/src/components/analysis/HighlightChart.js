import React from 'react';
import styled from 'styled-components';
import { useApp } from '../../AppContext';

// 스타일 정의
const ChartContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 20px;
  padding: 10px;
  border: 1px solid ${(props) => props.theme.colors.border};
  border-radius: 8px;
  background-color: ${(props) => props.theme.colors.surface};
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
`;

const StyledImage = styled.img`
  width: 100%;
  max-width: 800px;
  height: auto;
  border-radius: 8px;
  border: 1px solid ${(props) => props.theme.colors.border};
`;

const HighlightChart = () => {
  const { category_map, selectedCategory, selectedChannel } = useApp();

  const src = `http://localhost:1700/streaming/${category_map[selectedCategory]}_${selectedChannel}/${category_map[selectedCategory]}_${selectedChannel}_graph.png`;

  return (
    <ChartContainer>
      <StyledImage src={src} alt="Highlight Chart" />
    </ChartContainer>
  );
};

export default HighlightChart;
