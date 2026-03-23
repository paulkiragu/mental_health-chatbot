import { useState } from 'react'
import ChatWidget from './components/ChatWidget'
import Header from './components/Header'

function App() {
  const [isChatOpen, setIsChatOpen] = useState(false)

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-100 via-purple-50 to-pink-100">
      <Header />
      
      <main className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl font-bold text-gray-800 mb-6">
            Mental Health Support
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            A safe space to share your thoughts and feelings without judgment.
            Our AI-powered assistant is here to listen and support you.
          </p>
          
          <div className="grid md:grid-cols-3 gap-6 mt-12">
            <FeatureCard 
              icon="🛡️"
              title="Safe & Private"
              description="Your conversations are confidential and secure"
            />
            <FeatureCard 
              icon="🤖"
              title="AI-Powered"
              description="Advanced NLP for better understanding"
            />
            <FeatureCard 
              icon="🌍"
              title="Multilingual"
              description="Supports English and Swahili"
            />
          </div>

          <button
            onClick={() => setIsChatOpen(true)}
            className="mt-12 px-8 py-4 bg-indigo-600 text-white text-lg font-semibold rounded-full hover:bg-indigo-700 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
          >
            Start Chatting
          </button>
        </div>
      </main>

      <ChatWidget
        isOpen={isChatOpen}
        onOpen={() => setIsChatOpen(true)}
        onClose={() => setIsChatOpen(false)}
      />
    </div>
  )
}

function FeatureCard({ icon, title, description }) {
  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg hover:shadow-xl transition-shadow duration-300">
      <div className="text-4xl mb-4">{icon}</div>
      <h3 className="text-xl font-semibold text-gray-800 mb-2">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  )
}

export default App
