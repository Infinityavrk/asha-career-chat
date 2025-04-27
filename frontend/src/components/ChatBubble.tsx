import React from 'react';
import styles from './ChatBubble.module.css';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';  // 🌟 Add GFM support (for bullets, tables etc.)


interface Props {
  sender: 'user' | 'bot';
  message: string;
}

const ChatBubble: React.FC<Props> = ({ sender, message }) => {
  const isUser = sender === 'user';
  return (
    <div className={`${styles.bubbleWrapper} ${isUser ? styles.user : styles.bot}`}>
      <div className={styles.bubble}>
        <ReactMarkdown remarkPlugins={[remarkGfm]} components={{
            a: ({ node, ...props }) => (
              <a {...props} target="_blank" rel="noopener noreferrer" />
            ),
          }}>{typeof message === 'string' ? message : JSON.stringify(message)}</ReactMarkdown>
      </div>
    </div>
  );
};

export default ChatBubble;