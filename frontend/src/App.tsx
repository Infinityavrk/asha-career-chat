import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import ChatWindow from './components/ChatWindow';
import styles from './App.module.css';
import { askQuestion } from './Api';

function App() {
  const [chat, setChat] = useState<{ role: 'user' | 'bot', content: string }[]>([]);
  const [careerStage, setCareerStage] = useState<'Beginner' | 'Mid-Career' | 'Advanced'>('Beginner');
  const [loading, setLoading] = useState(false);
  
  const handleSendMessage = async (input: string) => {
    if (!input.trim()) return;
  
    setChat(prev => [...prev, { role: 'user', content: input }, { role: 'bot', content: '💬 Asha is typing...' }]);
    setLoading(true);
  
    try {
      const history = [...chat.map(m => m.content), input];
      const response = await askQuestion(input, history);
  
      let conversation = response.conversation || '';
      let jobs = response.jobs || '';
      let events = response.events || '';
  
      let combinedBotReply = conversation;
      if (jobs) combinedBotReply += "\n\n---\n\n" + jobs;
      if (events) combinedBotReply += "\n\n---\n\n" + events;
  
      setChat(prev => {
        // remove the "Asha is typing..." before adding the actual bot response
        const updated = [...prev];
        updated.pop();  // remove last "typing..." message
        return [...updated, { role: 'bot', content: combinedBotReply }];
      });
  
    } catch (err) {
      console.error(err);
      setChat(prev => {
        const updated = [...prev];
        updated.pop(); // remove "typing..." message
        return [...updated, { role: 'bot', content: '⚠️ Error fetching response.' }];
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <Sidebar
        careerStage={careerStage}
        setCareerStage={setCareerStage}
        chat={chat}
        setChat={setChat}
        onSendMessage={handleSendMessage} 
      />
      <ChatWindow chat={chat} setChat={setChat} loading={loading}  />
    </div>
  );
}

export default App;