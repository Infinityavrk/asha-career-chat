import React, { useState, useEffect, useRef } from 'react';
import styles from './ChatWindow.module.css';
import ChatBubble from './ChatBubble';
import { askQuestion } from '../Api';


interface Props {
  chat: { role: 'user' | 'bot'; content: string }[];
  setChat: React.Dispatch<React.SetStateAction<{ role: 'user' | 'bot'; content: string }[]>>;
  loading: boolean;
}

const ChatWindow: React.FC<Props> = ({ chat, setChat }) => {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);


  const handleSend = async () => {
    if (!input.trim()) return;
  
    const updatedChat = [...chat, { role: 'user' as const, content: input }];
    setChat(updatedChat);
    setInput('');
    setLoading(true);
  
    try {
      const history = updatedChat.map(m => m.content);
      const response = await askQuestion(input, history); // Your backend API call
  
      console.log('🚨 API response:', response);
  
      // ✅ Step 1: Extract conversation and jobs separately
      let conversation = response.conversation;
      let jobs = response.jobs;
      let events = response.events;
  
      // ✅ Step 2: Merge them cleanly
      let combinedBotReply = conversation;
  
      if (jobs) {
        combinedBotReply += "\n\n---\n\n"; // optional separator
        combinedBotReply += jobs;
      }

      if (events) {
        combinedBotReply += "\n\n---\n\n"; // optional separator
        combinedBotReply += events;
      }
  
      // ✅ Step 3: Set only the combined final message
      setChat(prev => [...prev, { role: 'bot', content: combinedBotReply }]);
      setLoading(false);
  
    } catch (error) {
      console.error(error);
      setChat(prev => [...prev, { role: 'bot', content: '⚠️ Error fetching response.' }]);
      setLoading(false);
    }
  };

  /*
  const handleSend = async () => {
    if (!input.trim()) return;
    const updatedChat = [...chat, { role: 'user' as const, content: input }];
    setChat(updatedChat);
    setInput('');
    setLoading(true);

    try {
      const history = updatedChat.map(m => m.content);
      const response = await askQuestion(input, history);
      setChat(prev => [...prev, { role: 'bot' as const, content: response }]);
    } catch {
      setChat(prev => [...prev, { role: 'bot', content: '⚠️ Error fetching response.' }]);
    }

    setLoading(false);
  };
*/
  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chat, loading]);

  return (
    <div className={styles.chatContainer}>
      <div className={styles.header}>
        <div className={styles.avatar}>A</div>
        <h3 className={styles.title}>Asha - JobsForHer AI Assistant</h3>
      </div>

      <div className={styles.chatBody}>
        {chat.map((msg, i) => (
          <ChatBubble key={i} sender={msg.role} message={msg.content} />
        ))}
        
    {loading && (
  <div className={`${styles.bubbleWrapper} ${styles.bot}`}>
    <div className={styles.bubble}>
      💬 Asha is typing...
    </div>
  </div>
)}
        <div ref={scrollRef} />
      </div>

      <div className={styles.inputArea}>
        <input
          type="text"
          placeholder="Type your message here..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
};

export default ChatWindow;