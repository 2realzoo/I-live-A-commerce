import React from 'react';
import styled, { ThemeProvider } from 'styled-components';
import CategorySelector from './components/CategorySelector';
import ChannelSelector from './components/ChannelSelector';
import VideoPlayer from './components/VideoPlayer';
import SentimentValue from './components/analysis/SentimentValue';
import { AppProvider } from './AppContext';
import ChatContainer from './components/chat/ChatContainer';
import HighlightChart from './components/analysis/HighlightChart';

const AppContainer = styled.div`
  display: flex;
  flex-direction: column;
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
  flex-direction: column;
`;

const TopSection = styled.div`
  display: flex;
  flex: 1;
  padding: 10px;
  gap: 10px; /* 가로 간격 추가 */
  box-sizing: border-box;
`;

const VideoContainer = styled.div`
  flex: 3; /* 비디오 크기 비율 */
  display: flex;
  flex-direction: column;
  gap: 10px;
`;

const ChatContainerWrapper = styled.div`
  flex: 2; /* 채팅 크기 비율 */
  background-color: ${(props) => props.theme.colors.surface};
`;

const BottomSection = styled.div`
  flex: 1;
  margin-top: 20px;
  padding: 20px;
  box-sizing: border-box;
  border: 1px solid ${(props) => props.theme.colors.border};
  border-radius: 8px;
  background-color: ${(props) => props.theme.colors.surface};
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  gap: 20px;
`;

function App() {
  return (
      <AppProvider>
        <AppContainer>
          <HeaderSection>
            <CategorySelector />
          </HeaderSection>

          <MainSection>
            <TopSection>
              <VideoContainer>
                <ChannelSelector />
                <VideoPlayer autoPlay={true} controls={true} width="100%" height="auto" />
              </VideoContainer>

              <ChatContainerWrapper>
                <ChatContainer />
              </ChatContainerWrapper>
            </TopSection>

            <BottomSection>
              <SentimentValue />
              <HighlightChart />
            </BottomSection>
          </MainSection>
        </AppContainer>
      </AppProvider>
  );
}

export default App;
