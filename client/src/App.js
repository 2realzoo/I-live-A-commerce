import Header from './components/Header';
import React, { useState } from 'react';
import CategorySelector from './components/CategorySelector';
import ChannelSelector from './components/ChannelSelector';
import VideoPlayer from './components/VideoPlayer';
import SentimentValue from './components/SentimentValue';
import ChatInput from './components/chat/ChatInput';
import RealTimeChart from './components/RealTimeChart'
import ChatWindow from './components/chat/ChatWindow';
import SendChatButton from './components/chat/SendChatButton'
import ChatReader from './components/chat/ChatReader'
import styled from 'styled-components';

const AppContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100vh;
  /* 배경색 & 폰트 */
  background-color: ${(props) => props.theme.colors.background};
  color: ${(props) => props.theme.colors.text};
  font-family: ${(props) => props.theme.fonts.base};
`;

const HeaderSection = styled.header`
  background-color: ${(props) => props.theme.colors.primary};
  padding: 12px 20px;
  color: #fff;
  display: flex;
  align-items: center;
`;

const MainSection = styled.div`
  flex: 1;
  display: flex;
  flex-direction: row;
`;
const LeftSection = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 20px;
  box-sizing: border-box;
`;

/**
 * 3) 오른쪽 섹션 (채팅 등)
 *    - 고정 너비 350px 예시
 */
const RightSection = styled.div`
  width: 350px;
  display: flex;
  flex-direction: column;
  padding: 20px;
  box-sizing: border-box;
  border-left: 1px solid ${(props) => props.theme.colors.border};
`;

function App() {
  const [selectedCategory, setSelectedCategory] = useState('뷰티');
  const [selectedChannel, setSelectedChannel] = useState();
  const [sentimentScore, setSentimentScore] = useState(undefined); // 감성 분석 값 예시
  const [messages, setMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [chatReaderMode, setChatReaderMode] = useState('잇섭'); // (잇섭, 아이유)
  const [channelList, setChannelList] = useState([])

  const handleSendMessage = () => {
    if (currentMessage.trim() === '') return;
    setMessages([...messages, currentMessage]);
    setCurrentMessage('');
  };

  return (
    <AppContainer>
      <HeaderSection>
        {/* 카테고리 선택 스크롤 버튼 */}
        <CategorySelector
        selectedCategory={selectedCategory}
        setSelectedCategory={setSelectedCategory}
        channelList={channelList}
        setChannelList={setChannelList}
        />
      </HeaderSection>

      <MainSection>
        <LeftSection>
          {/* 채널 선택 스크롤 버튼 */}
          <ChannelSelector
            selectedChannel={selectedChannel}
            setSelectedChannel={setSelectedChannel}
            channelList={channelList}
          />

          {/* 감정분석 수치 값 */}
          <SentimentValue 
            sentimentScore={sentimentScore}
            setSentimentScore={setSentimentScore}
          />

          {/* 동영상 플레이어 */}
          <VideoPlayer 
            src=""
            autoPlay={true}
            controls={true}
            width="100%"
            height="auto"
          />

          {/* 실시간 차트 */}
          <RealTimeChart />
        </LeftSection>
        <RightSection>
          {/* 채팅창 */}
          <ChatWindow messages={messages} />

          {/* 채팅 입력창 */}
          <ChatInput
            currentMessage={currentMessage}
            setCurrentMessage={setCurrentMessage}
          />

          {/* 채팅 보내기 버튼 */}
          <SendChatButton onSend={handleSendMessage} />

          {/* 채팅 읽어주기 버튼 (잇섭, 아이유) */}
          <ChatReader 
            mode={chatReaderMode} 
            setMode={setChatReaderMode} 
          />
        </RightSection>
      </MainSection>
    </AppContainer>
  );
}

export default App;
