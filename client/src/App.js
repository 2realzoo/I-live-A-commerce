import React from 'react';
import CategorySelector from './components/CategorySelector';
import ChannelSelector from './components/ChannelSelector';
import VideoPlayer from './components/VideoPlayer';
import SentimentValue from './components/SentimentValue';
import RealTimeChart from './components/RealTimeChart'
import styled from 'styled-components';
import { AppProvider } from './AppContext';
import ChatContainer from './components/chat/ChatContainer';

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
  padding: 0px 10px;
  flex-direction: column;
  box-sizing: border-box;
`;

function App() {
  return (
    <AppProvider>
      <AppContainer>
        <HeaderSection>
          {/* 카테고리 선택 스크롤 버튼 */}
          <CategorySelector />
        </HeaderSection>

        <MainSection>
          <LeftSection>
            {/* 채널 선택 스크롤 버튼 */}
            <ChannelSelector/>

            {/* 동영상 플레이어 */}
            <VideoPlayer 
              src="/home/ujoo/workspace/I-live-A-commerce/DB/1_1552806/1_1552806_data/output.m3u8"
              autoPlay={true}
              controls={true}
              width="100%"
              height="auto"
            />

            {/* 감정분석 수치 값 */}
            <SentimentValue />

            {/* 실시간 차트 */}
            <RealTimeChart />
          </LeftSection>
          <ChatContainer/>
        </MainSection>
      </AppContainer>
    </AppProvider>
  );
}

export default App;
