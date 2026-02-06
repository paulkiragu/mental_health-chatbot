function ChatMessage({ message }) {
  const isBot = message.sender === 'bot'
  
  const formatTime = (date) => {
    return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className={`flex ${isBot ? 'justify-start' : 'justify-end'} animate-fade-in`}>
      <div className={`flex items-end space-x-2 max-w-[80%] ${isBot ? '' : 'flex-row-reverse space-x-reverse'}`}>
        {/* Avatar */}
        <div className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center ${
          isBot 
            ? 'bg-gradient-to-br from-indigo-500 to-purple-600' 
            : 'bg-gradient-to-br from-green-400 to-emerald-500'
        }`}>
          {isBot ? (
            <svg className="w-5 h-5 text-white" viewBox="0 0 640 512" fill="currentColor">
              <path d="M32,224H64V416H32A31.96166,31.96166,0,0,1,0,384V256A31.96166,31.96166,0,0,1,32,224Zm512-48V448a64.06328,64.06328,0,0,1-64,64H160a64.06328,64.06328,0,0,1-64-64V176a79.974,79.974,0,0,1,80-80H288V32a32,32,0,0,1,64,0V96H464A79.974,79.974,0,0,1,544,176ZM264,256a40,40,0,1,0-40,40A39.997,39.997,0,0,0,264,256Zm-8,128H192v32h64Zm96,0H288v32h64ZM456,256a40,40,0,1,0-40,40A39.997,39.997,0,0,0,456,256Zm-8,128H384v32h64ZM640,256V384a31.96166,31.96166,0,0,1-32,32H576V224h32A31.96166,31.96166,0,0,1,640,256Z" />
            </svg>
          ) : (
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          )}
        </div>

        {/* Message bubble */}
        <div className={`rounded-2xl px-4 py-3 ${
          isBot 
            ? 'bg-white shadow-sm border border-gray-100 rounded-bl-md' 
            : 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-br-md'
        } ${message.isError ? 'border-red-200 bg-red-50' : ''}`}>
          <p className={`text-sm leading-relaxed ${isBot ? 'text-gray-700' : 'text-white'}`}>
            {message.text}
          </p>
          <p className={`text-xs mt-1 ${isBot ? 'text-gray-400' : 'text-white/70'}`}>
            {formatTime(message.timestamp)}
          </p>
        </div>
      </div>
    </div>
  )
}

export default ChatMessage
