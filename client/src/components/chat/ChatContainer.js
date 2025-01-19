import React from 'react';
import styled from 'styled-components';
import ChatInput from './ChatInput';
import SendChatButton from './SendChatButton';
import ChatWindow from './ChatWindow';
import Chatbot from './Chatbot';

// 전체 컨테이너 중앙 정렬
const ChatContainerWrapper = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center; /* 가로축 중앙 정렬 */
  min-height: 100vh; /* 화면 전체 높이 */
`;

const InputContainer = styled.div`
  margin-top: 10px;
  display: flex;
  align-items: stretch;
  justify-content: space-between;
  border: none;
  background-color: #f9f9f9;
`;

const ChatContainer = () => {
    return (
        <ChatContainerWrapper>
            <Chatbot />
            <ChatWindow />
            <InputContainer>
                <ChatInput />
                <SendChatButton />
            </InputContainer>  
        </ChatContainerWrapper>
    );
};

export default ChatContainer;