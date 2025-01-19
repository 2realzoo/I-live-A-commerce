import React, { createContext, useContext, useState } from 'react';
import axios from 'axios';

const AppContext = createContext();

export const AppProvider = ({ children }) => {
  const [messages, setMessages] = useState([]); // 채팅 메시지 목록
  const [currentMessage, setCurrentMessage] = useState(''); // 현재 입력된 메시지
  const [useVoice, setUseVoice] = useState(false); // 음성 사용 여부
  const [voiceName, setVoiceName] = useState('잇섭'); // 음성 이름
  const [selectedCategory, setSelectedCategory] = useState('뷰티'); // 선택된 카테고리
  const [selectedChannel, setSelectedChannel] = useState(null); // 선택된 채널
  const [sentimentScore, setSentimentScore] = useState(undefined); // 감성 분석 점수
  const [channelList, setChannelList] = useState([]); // 채널 목록

  // 메시지 전송 핸들러
  const handleSendMessage = async () => {
    if (currentMessage.trim() === '') return; // 빈 메시지 방지

    // 유저 메시지 추가
    setMessages((prevMessages) => [
      ...prevMessages,
      { sender: 'user', text: currentMessage },
    ]);

    try {
      // 서버로 POST 요청
      const response = await axios.post('/chat', {
        Category: selectedCategory,
        Channel: selectedChannel,
        Text: currentMessage,
        Voice: useVoice,
        Who: voiceName,
      });

      // 서버 응답 메시지 추가
      if (response.data?.Text) {
        setMessages((prevMessages) => [
          ...prevMessages,
          { text: response.data.Text, sender: 'bot' },
        ]);
      }

      // 음성 데이터 처리
      if (useVoice && response.data?.Audio) {
        console.log('Received audio file URL:', response.data.Audio);
      }
    } catch (error) {
      console.error('Error sending message to /chat:', error);
    } finally {
      // 메시지 입력창 초기화
      setCurrentMessage('');
    }
  };

  return (
    <AppContext.Provider
      value={{
        messages,
        setMessages,
        currentMessage,
        setCurrentMessage,
        handleSendMessage,
        useVoice,
        setUseVoice,
        voiceName,
        setVoiceName,
        selectedCategory,
        setSelectedCategory,
        selectedChannel,
        setSelectedChannel,
        sentimentScore,
        setSentimentScore,
        channelList,
        setChannelList,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

// Context를 쉽게 사용할 수 있도록 제공
export const useApp = () => useContext(AppContext);
