import React, { useState } from 'react';
import './App.css';

function App() {
  const [input, setInput] = useState('');
  const [chatLog, setChatLog] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    // 사용자 메시지를 채팅 로그에 추가
    setChatLog([...chatLog, { type: 'user', message: input }]);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: input }),
      });

      if (!response.ok) {
        throw new Error('서버 응답에 문제가 있습니다.');
      }

      const data = await response.json();
      console.log("Server response:", data);

      // 서버 응답에서 메시지 추출 (응답 구조에 따라 조정 필요)
      const botMessage = data.response || '응답을 받을 수 없습니다.';

      // 봇 메시지를 채팅 로그에 추가
      setChatLog(prevLog => [...prevLog, { type: 'bot', message: botMessage }]);
    } catch (error) {
      console.error("Error:", error);
      setChatLog(prevLog => [...prevLog, { type: 'error', message: error.message }]);
    }

    setInput(''); // 입력 필드 초기화
  };

  return (
    <div className="chat-container">
      <h1>Chatbot</h1>
      <div className="chat-log">
        {chatLog.map((entry, index) => (
          <div key={index} className={`chat-message ${entry.type}`}>
            {entry.message}
          </div>
        ))}
      </div>
      <form onSubmit={handleSubmit} className="chat-input-form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="메시지를 입력하세요..."
          className="chat-input"
        />
        <button type="submit" className="chat-submit">전송</button>
      </form>
    </div>
  );
}

export default App;