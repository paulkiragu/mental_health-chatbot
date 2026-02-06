import { useState, useRef, useEffect } from 'react'

function ChatInput({ onSend, disabled }) {
  const [message, setMessage] = useState('')
  const inputRef = useRef(null)

  useEffect(() => {
    if (!disabled && inputRef.current) {
      inputRef.current.focus()
    }
  }, [disabled])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (message.trim() && !disabled) {
      onSend(message)
      setMessage('')
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="p-4 bg-white border-t border-gray-100">
      <div className="flex items-center space-x-3">
        <div className="flex-1 relative">
          <input
            ref={inputRef}
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message..."
            disabled={disabled}
            className="w-full px-4 py-3 bg-gray-100 rounded-xl text-gray-700 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          />
        </div>
        <button
          type="submit"
          disabled={disabled || !message.trim()}
          className="w-12 h-12 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center text-white hover:shadow-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed hover:scale-105 active:scale-95"
        >
          {disabled ? (
            <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
          ) : (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          )}
        </button>
      </div>
      
      {/* Quick suggestions */}
      <div className="flex flex-wrap gap-2 mt-3">
        {['How are you?', "I'm feeling anxious", 'I need help', 'Tell me about depression'].map((suggestion) => (
          <button
            key={suggestion}
            type="button"
            onClick={() => !disabled && onSend(suggestion)}
            disabled={disabled}
            className="px-3 py-1.5 text-xs bg-gray-100 text-gray-600 rounded-full hover:bg-indigo-100 hover:text-indigo-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {suggestion}
          </button>
        ))}
      </div>
    </form>
  )
}

export default ChatInput
