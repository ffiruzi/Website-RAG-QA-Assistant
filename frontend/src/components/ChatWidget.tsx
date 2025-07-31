import React, { useState, useEffect } from 'react';
import { MessageSquare, X, Send, Globe } from 'lucide-react';

interface Message {
  id: number;
  text: string;
  isUser: boolean;
  timestamp: Date;
  websiteId?: number;
}

interface Website {
  id: number;
  name: string;
  url: string;
}

export const ChatWidget: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [websites, setWebsites] = useState<Website[]>([]);
  const [selectedWebsiteId, setSelectedWebsiteId] = useState<number>(1);

  // Fetch available websites
  useEffect(() => {
    const fetchWebsites = async () => {
      try {
        const response = await fetch('/api/v1/websites/', {
          headers: { 'Authorization': 'Bearer mock_token' }
        });
        if (response.ok) {
          const data = await response.json();
          setWebsites(data.items || []);
          if (data.items && data.items.length > 0) {
            setSelectedWebsiteId(data.items[0].id);
          }
        }
      } catch (error) {
        console.log('Could not fetch websites:', error);
      }
    };

    if (isOpen && websites.length === 0) {
      fetchWebsites();
    }
  }, [isOpen]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const selectedWebsite = websites.find(w => w.id === selectedWebsiteId);
    const userMessage = {
      id: Date.now(),
      text: input,
      isUser: true,
      timestamp: new Date(),
      websiteId: selectedWebsiteId
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const queryParams = new URLSearchParams({
        query: input,
        session_id: `chat_widget_${selectedWebsiteId}`
      });

      const url = `/api/v1/qa/${selectedWebsiteId}/ask?${queryParams}`;
      console.log('🌐 Making request to:', url);

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('📦 Response data:', data);

      let responseText = data.answer || 'No response received';

      if (data.success && data.answer) {
        responseText = data.answer;
        if (data.sources && data.sources.length > 0) {
          responseText += `\n\n📚 Sources: ${data.sources.map((s: any) => s.title || s.url).join(', ')}`;
        }
      } else {
        responseText = `🤖 I don't have information about "${selectedWebsite?.name || 'this website'}" yet.

Please make sure:
1. The website has been crawled
2. Content has been processed into embeddings
3. Try asking a different question`;
      }

      const botMessage = {
        id: Date.now() + 1,
        text: responseText,
        isUser: false,
        timestamp: new Date(),
        websiteId: selectedWebsiteId
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        text: `Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        isUser: false,
        timestamp: new Date(),
        websiteId: selectedWebsiteId
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-4 right-4 bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-full shadow-lg transition-colors duration-200 z-50"
        aria-label="Open chat"
      >
        <MessageSquare size={24} />
      </button>
    );
  }

  return (
    <div className="fixed bottom-4 right-4 w-96 h-[32rem] bg-white rounded-lg shadow-xl border border-gray-200 flex flex-col z-50">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-blue-600 text-white rounded-t-lg">
        <div className="flex items-center gap-2">
          <MessageSquare size={20} />
          <span className="font-semibold">Chat Assistant</span>
        </div>
        <button
          onClick={() => setIsOpen(false)}
          className="text-white hover:text-gray-200 transition-colors"
          aria-label="Close chat"
        >
          <X size={20} />
        </button>
      </div>

      {/* Website Selector - FIXED VISIBILITY */}
      {websites.length > 0 && (
        <div className="p-3 border-b border-gray-100 bg-gray-50">
          <div className="flex items-center gap-2 text-sm">
            <Globe size={16} className="text-gray-600 flex-shrink-0" />
            <select
              value={selectedWebsiteId}
              onChange={(e) => setSelectedWebsiteId(Number(e.target.value))}
              className="flex-1 text-sm border border-gray-300 rounded px-3 py-2 bg-white text-gray-800 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 cursor-pointer"
            >
              {websites.map((website) => (
                <option
                  key={website.id}
                  value={website.id}
                  className="text-gray-800 bg-white py-2"
                >
                  {website.name}
                </option>
              ))}
            </select>
          </div>
          {/* Show selected website info */}
          <div className="mt-2 text-xs text-gray-600">
            Selected: {websites.find(w => w.id === selectedWebsiteId)?.name || 'Unknown'}
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 text-sm">
            {websites.length === 0
              ? "No websites available. Please add a website first."
              : `Ask me anything about "${websites.find(w => w.id === selectedWebsiteId)?.name || 'the selected website'}"`}
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg px-3 py-2 text-sm ${
                message.isUser
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-800 border border-gray-200'
              }`}
            >
              <div className="whitespace-pre-wrap">{message.text}</div>
              <div className={`text-xs mt-1 ${message.isUser ? 'text-blue-100' : 'text-gray-500'}`}>
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-600">
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-200 bg-white rounded-b-lg">
        <div className="flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={websites.length === 0 ? "Add a website first..." : "Type your message..."}
            className="flex-1 resize-none border border-gray-300 rounded-lg px-3 py-2 text-sm  placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows={1}
            disabled={loading || websites.length === 0}
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || loading || websites.length === 0}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white p-2 rounded-lg transition-colors duration-200 flex-shrink-0"
            aria-label="Send message"
          >
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  );
};