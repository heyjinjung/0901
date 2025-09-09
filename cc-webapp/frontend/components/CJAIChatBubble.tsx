'use client';

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Send, 
  Bot, 
  User, 
  Loader2, 
  MessageCircle, 
  X, 
  Sparkles,
  Zap
} from 'lucide-react';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  isTyping?: boolean;
}

interface CJAIChatBubbleProps {
  className?: string;
  position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';
  onSendMessage?: (message: string) => Promise<string>;
}

export function CJAIChatBubble({ 
  className = '', 
  position = 'bottom-right',
  onSendMessage 
}: CJAIChatBubbleProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: '1',
      text: '안녕하세요! CJ AI 어시스턴트입니다. 무엇을 도와드릴까요? 😊',
      sender: 'ai',
      timestamp: new Date(),
    }
  ] as Message[]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null as HTMLDivElement | null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const getPositionClasses = () => {
    switch (position) {
      case 'bottom-left':
        return 'bottom-4 left-4';
      case 'top-right':
        return 'top-4 right-4';
      case 'top-left':
        return 'top-4 left-4';
      default:
        return 'bottom-4 right-4';
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date(),
    };

  setMessages((prev: Message[]) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    // Add typing indicator
    const typingMessage: Message = {
      id: 'typing',
      text: '...',
      sender: 'ai',
      timestamp: new Date(),
      isTyping: true,
    };
  setMessages((prev: Message[]) => [...prev, typingMessage]);

    try {
      const response = onSendMessage 
        ? await onSendMessage(inputValue)
        : `네, "${inputValue}"에 대해 도움을 드릴 수 있습니다. CJ AI가 최선을 다해 답변드리겠습니다! ✨`;

      // Remove typing indicator and add real response
      setMessages((prev: Message[]) => {
        const filtered = prev.filter((m: Message) => m.id !== 'typing');
        return [...filtered, {
          id: Date.now().toString(),
          text: response,
          sender: 'ai',
          timestamp: new Date(),
        }];
      });
    } catch (error) {
      setMessages((prev: Message[]) => {
        const filtered = prev.filter((m: Message) => m.id !== 'typing');
        return [...filtered, {
          id: Date.now().toString(),
          text: '죄송합니다. 일시적인 오류가 발생했습니다. 다시 시도해 주세요.',
          sender: 'ai',
          timestamp: new Date(),
        }];
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className={`fixed ${getPositionClasses()} z-50 ${className}`}>
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: 20 }}
            transition={{ duration: 0.3, type: "spring", stiffness: 200 }}
            className="mb-4 w-80 md:w-96 h-96 bg-slate-900/95 backdrop-blur-xl border border-slate-700/50 rounded-2xl shadow-2xl shadow-blue-500/10 overflow-hidden"
          >
            {/* Header */}
            <div className="p-4 border-b border-slate-700/50 bg-gradient-to-r from-blue-500/10 to-purple-500/10">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="relative">
                    <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                      <Bot className="w-4 h-4 text-white" />
                    </div>
                    <motion.div
                      animate={{ scale: [1, 1.2, 1] }}
                      transition={{ duration: 2, repeat: Infinity, type: 'tween' }}
                      className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-500 rounded-full"
                    />
                  </div>
                  <div>
                    <h3 className="text-slate-100 font-medium">CJ AI Assistant</h3>
                    <p className="text-slate-400 text-xs">온라인</p>
                  </div>
                </div>
                <button
                  onClick={() => setIsOpen(false)}
                  className="p-1 hover:bg-slate-700/50 rounded-lg transition-colors"
                >
                  <X className="w-4 h-4 text-slate-400" />
                </button>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 p-4 overflow-y-auto max-h-64 space-y-4">
              {messages.map((message: Message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                  className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`flex items-start gap-2 max-w-[80%] ${
                    message.sender === 'user' ? 'flex-row-reverse' : 'flex-row'
                  }`}>
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center shrink-0 ${
                      message.sender === 'user' 
                        ? 'bg-blue-500' 
                        : 'bg-gradient-to-r from-purple-500 to-blue-500'
                    }`}>
                      {message.sender === 'user' ? (
                        <User className="w-3 h-3 text-white" />
                      ) : (
                        <Sparkles className="w-3 h-3 text-white" />
                      )}
                    </div>
                    <div className={`px-3 py-2 rounded-2xl ${
                      message.sender === 'user'
                        ? 'bg-blue-500 text-white'
                        : 'bg-slate-800 text-slate-100 border border-slate-700/50'
                    }`}>
                      {message.isTyping ? (
                        <div className="flex items-center gap-1">
                          <motion.div
                            animate={{ opacity: [0.4, 1, 0.4] }}
                            transition={{ duration: 1.5, repeat: Infinity, delay: 0, type: 'tween' }}
                            className="w-1 h-1 bg-slate-400 rounded-full"
                          />
                          <motion.div
                            animate={{ opacity: [0.4, 1, 0.4] }}
                            transition={{ duration: 1.5, repeat: Infinity, delay: 0.2, type: 'tween' }}
                            className="w-1 h-1 bg-slate-400 rounded-full"
                          />
                          <motion.div
                            animate={{ opacity: [0.4, 1, 0.4] }}
                            transition={{ duration: 1.5, repeat: Infinity, delay: 0.4, type: 'tween' }}
                            className="w-1 h-1 bg-slate-400 rounded-full"
                          />
                        </div>
                      ) : (
                        <p className="text-sm">{message.text}</p>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-4 border-t border-slate-700/50 bg-slate-900/50">
              <div className="flex items-center gap-2">
                <div className="flex-1 relative">
                  <input
                    type="text"
                    value={inputValue}
                    onChange={(e: any) => setInputValue(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="메시지를 입력하세요..."
                    disabled={isLoading}
                    className="w-full px-4 py-2 bg-slate-800 border border-slate-700/50 rounded-xl text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 disabled:opacity-50"
                  />
                </div>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim() || isLoading}
                  className="p-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl text-white disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-blue-500/25 transition-shadow"
                >
                  {isLoading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                </motion.button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Chat Button */}
      <motion.button
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        onClick={() => setIsOpen(!isOpen)}
        className="relative w-14 h-14 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full shadow-lg shadow-blue-500/25 flex items-center justify-center group overflow-hidden"
      >
        <AnimatePresence mode="wait">
          {isOpen ? (
            <motion.div
              key="close"
              initial={{ rotate: -90, opacity: 0 }}
              animate={{ rotate: 0, opacity: 1 }}
              exit={{ rotate: 90, opacity: 0 }}
              transition={{ duration: 0.2 }}
            >
              <X className="w-6 h-6 text-white" />
            </motion.div>
          ) : (
            <motion.div
              key="chat"
              initial={{ rotate: 90, opacity: 0 }}
              animate={{ rotate: 0, opacity: 1 }}
              exit={{ rotate: -90, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="relative"
            >
              <MessageCircle className="w-6 h-6 text-white" />
              <motion.div
                animate={{ scale: [1, 1.3, 1] }}
                transition={{ duration: 2, repeat: Infinity, type: 'tween' }}
                className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-400 rounded-full"
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Pulse Effect */}
        <motion.div
          animate={{ scale: [1, 1.5, 1], opacity: [0.5, 0, 0.5] }}
          transition={{ duration: 2, repeat: Infinity, type: 'tween' }}
          className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full"
        />

        {/* Hover Effect */}
        <div className="absolute inset-0 bg-white/20 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      </motion.button>
    </div>
  );
}