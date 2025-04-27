import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import ChatWindow from './components/ChatWindow';
import styles from './App.module.css';

function App() {
  const [chat, setChat] = useState<{ role: 'user' | 'bot', content: string }[]>([]);
  const [careerStage, setCareerStage] = useState<'Beginner' | 'Mid-Career' | 'Advanced'>('Beginner');

  return (
    <div className={styles.container}>
      <Sidebar
        careerStage={careerStage}
        setCareerStage={setCareerStage}
        chat={chat}
        setChat={setChat}
      />
      <ChatWindow chat={chat} setChat={setChat} />
    </div>
  );
}

export default App;