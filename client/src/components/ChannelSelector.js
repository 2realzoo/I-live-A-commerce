import React from 'react';
import styled from 'styled-components';
import { useApp } from '../AppContext';

// 컨테이너 스타일
const SelectorContainer = styled.div`
  display: flex;
  align-items: center; /* 수직 정렬 */
  gap: 10px; /* 레이블과 드롭다운 사이 간격 */
  margin: 10px;
  font-family: ${(props) => props.theme.fonts.base};
`;

// 레이블 스타일
const Label = styled.label`
  font-size: 16px;
  color: ${(props) => props.theme.colors.text};
  font-weight: bold;
`;

// 드롭다운 스타일
const StyledSelect = styled.select`
  padding: 8px 12px;
  border: 1px solid ${(props) => props.theme.colors.border};
  background-color: white;
  font-size: 14px;
  color: ${(props) => props.theme.colors.text};
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s;

  &:focus {
    border-color: ${(props) => props.theme.colors.primary};
    box-shadow: 0 0 4px ${(props) => props.theme.colors.primary};
    outline: none;
  }

  &:hover {
    border-color: ${(props) => props.theme.colors.primaryLight};
  }
`;

function ChannelSelector() {
  const { selectedChannel, setSelectedChannel, channelList } = useApp();

  const handleChange = (e) => {
    setSelectedChannel(e.target.value);
  };

  return (
    <SelectorContainer>
      <Label htmlFor="channel-select">채널 선택:</Label>
      <StyledSelect
        id="channel-select"
        value={selectedChannel}
        onChange={handleChange}
      >
        {channelList.map((ch, index) => (
          <option key={index} value={ch}>
            {ch}
          </option>
        ))}
      </StyledSelect>
    </SelectorContainer>
  );
}

export default ChannelSelector;
