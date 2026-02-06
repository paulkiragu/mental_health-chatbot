function TypingIndicator() {
  return (
    <div className="flex justify-start animate-fade-in">
      <div className="flex items-end space-x-2">
        {/* Avatar */}
        <div className="w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center bg-gradient-to-br from-indigo-500 to-purple-600">
          <svg className="w-5 h-5 text-white" viewBox="0 0 640 512" fill="currentColor">
            <path d="M32,224H64V416H32A31.96166,31.96166,0,0,1,0,384V256A31.96166,31.96166,0,0,1,32,224Zm512-48V448a64.06328,64.06328,0,0,1-64,64H160a64.06328,64.06328,0,0,1-64-64V176a79.974,79.974,0,0,1,80-80H288V32a32,32,0,0,1,64,0V96H464A79.974,79.974,0,0,1,544,176ZM264,256a40,40,0,1,0-40,40A39.997,39.997,0,0,0,264,256Zm-8,128H192v32h64Zm96,0H288v32h64ZM456,256a40,40,0,1,0-40,40A39.997,39.997,0,0,0,456,256Zm-8,128H384v32h64ZM640,256V384a31.96166,31.96166,0,0,1-32,32H576V224h32A31.96166,31.96166,0,0,1,640,256Z" />
          </svg>
        </div>

        {/* Typing bubble */}
        <div className="bg-white shadow-sm border border-gray-100 rounded-2xl rounded-bl-md px-4 py-3">
          <div className="typing-indicator flex space-x-1">
            <span className="w-2 h-2 bg-gray-400 rounded-full"></span>
            <span className="w-2 h-2 bg-gray-400 rounded-full"></span>
            <span className="w-2 h-2 bg-gray-400 rounded-full"></span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default TypingIndicator
