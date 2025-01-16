import React, {useEffect} from 'react';
import styled from 'styled-components';
import axios from 'axios';

// 컨테이너 스타일
const CategorySelectorContainer = styled.div`
  display: flex;
  flex-wrap: nowrap;
  gap: 8px;
  margin: 10px;
  /* 필요하면 스크롤 추가
  overflow-x: auto;
  */
`;

// 버튼 스타일
const CategoryButton = styled.button`
  padding: 8px 12px;
  border: 1px solid #ccc;
  background-color: #fff;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.2s, color 0.2s;

  &:hover {
    background-color: #f0f0f0;
  }

  /* 선택된(active) 상태 */
  &.active {
    background-color: #007bff;
    color: #ffffff;
    border-color: #007bff;
  }
`;

function CategorySelector({ selectedCategory, setSelectedCategory, channelList, setChannelList }) {
  const categories = ['뷰티', '푸드', '패션', '라이프', '여행/체험', '키즈', '테크', '취미레저', '문화생활'];
  
  // 카테고리 선택 시 실행될 함수
  const handleSelectCategory = async (category) => {
    setSelectedCategory(category);
    try {
      const response = await axios.get('/channels', {
        params: { category },
      });
      setChannelList(response.date);
    } catch (error) {
      console.error('Error fetching channel List:', error);
    }
  };

  
  useEffect(() => {

  }, [selectedCategory])

  return (
    <CategorySelectorContainer>
      {categories.map((cat) => (
        <CategoryButton
          key={cat}
          className={cat === selectedCategory ? 'active' : ''}
          onClick={() => handleSelectCategory(cat)}
        >
          {cat}
        </CategoryButton>
      ))}
    </CategorySelectorContainer>
  );
}

export default CategorySelector;
