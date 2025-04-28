import React, { useState } from 'react';
import styles from './Sidebar.module.css';

type CareerStage = 'Beginner' | 'Mid-Career' | 'Advanced';
interface Props {
  careerStage: CareerStage;
  setCareerStage: (stage: CareerStage) => void;
  chat: { role: 'user' | 'bot'; content: string }[];
  setChat: React.Dispatch<React.SetStateAction<{ role: 'user' | 'bot'; content: string }[]>>;
  onSendMessage: (message: string) => void;  
}


const Sidebar: React.FC<Props> = ({ careerStage, setCareerStage, chat, setChat,onSendMessage }) => {
  const [input, setInput] = useState('');

  const questionBank: Record<CareerStage, string[]> = {
    Beginner: [
      "What factors should I consider when choosing a career?",
      "How do I identify my strengths and interests?",
      "What are the fastest growing career fields for beginners?",
    ],
    "Mid-Career": [
      "How can I switch to a tech role from a non-tech background?",
      "What are some good upskilling options for working professionals?",
      "How to manage a career break and return to work?",
    ],
    Advanced: [
      "How can I move into leadership roles?",
      "Are there government programs for women entrepreneurs?",
      "How can I mentor other professionals in my domain?",
    ],
  };
  
  const suggestions = questionBank[careerStage];

   const sendMessage = async () => {
      if (!input.trim()) return;
      onSendMessage(input);  
      setInput(''); 
     
    };
  /*
  const sendMessage = async () => {
    if (!input.trim()) return;
  
    const updatedChat = [...chat, { role: 'user' as const, content: input }];
    setChat(updatedChat);
    setInput('');
  
    try {
      const history = updatedChat.map(m => m.content); // Flattened history list
      const botResponse = await askQuestion(input, history);
  
      setChat(prev => [...prev, { role: 'bot' as const, content: botResponse }]);
    } catch (error) {
      console.error("Backend error:", error);
      setChat(prev => [...prev, { role: 'bot' as const, content: "⚠️ Unable to fetch response." }]);
    }
  };
  */

  const clearChat = () => setChat([]);

  return (
    <div className={styles.sidebar}>
      <h2>Your Career Journey</h2>
      <p>Select your career stage:</p>

      <div className={styles.radioGroup}>
        {["Beginner", "Mid-Career", "Advanced"].map(stage => (
          <label key={stage}>
            <input
              type="radio"
              value={stage}
              checked={careerStage === stage}
              onChange={() => setCareerStage(stage as typeof careerStage)}
            />
            {stage}
          </label>
        ))}
      </div>

      <p className={styles.subheading}>Ask me anything about careers:</p>

      <input
        className={styles.input}
        type="text"
        placeholder="Type your question here..."
        value={input}
        onChange={(e) => setInput(e.target.value)}
      />

      <div className={styles.buttons}>
        <button onClick={sendMessage}>Send Message 📩</button>
        <button onClick={clearChat}>🗑️</button>
      </div>

      <h4>Looking for inspiration?</h4>
<p>Try these questions:</p>
<div className={styles.suggestions}>
  {suggestions.map((q, i) => (
    <button key={i} onClick={() => setInput(q)}>
      {q}
    </button>
  ))}
</div>
    </div>
  );
};

export default Sidebar;