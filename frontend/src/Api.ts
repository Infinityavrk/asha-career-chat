import axios from 'axios';

const API_BASE = 'http://34.172.224.41:8000'; // Your FastAPI backend URL

// Call the /ask endpoint
export const askQuestion = async (message: string, history: string[]) => {
  const response = await axios.post(`/api/ask`, {
    message,
    history,
  });
  return response.data.response;
};

// Call the /suggestions endpoint
export const getSuggestions = async (): Promise<string[]> => {
  const response = await axios.post(`/api/suggestions`, {
  return response.data.suggestions;
};
