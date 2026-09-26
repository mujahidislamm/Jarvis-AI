export type ChatMessage = {
  id: string
  role: 'user' | 'assistant'
  content: string
}

export type AIServiceAdapter = {
  sendMessage: (message: string) => Promise<ChatMessage>
  streamMessage: (message: string) => AsyncIterable<string>
  getSuggestions: () => Promise<string[]>
  executeCommand: (command: string) => Promise<string>
}

const mockResponses = [
  'I have routed this to the coordinating intelligence layer.',
  'The system is prioritizing the most relevant tasks for this request.',
  'I am preparing a short plan and recommended next actions.',
  'This is queued for the secure backend service once the API is connected.',
]

const mockSuggestions = [
  'Summarize workspace health',
  'Prioritize my top tasks',
  'Open deployment status',
  'Find blockers in the backlog',
]

export const aiAdapter: AIServiceAdapter = {
  async sendMessage(message: string) {
    // TODO: replace with secure backend call.
    // Example: fetch('/api/assistant/chat', { method: 'POST', headers: { Authorization: 'Bearer ...' }, body: JSON.stringify({ message }) })
    const response = mockResponses[Math.floor(Math.random() * mockResponses.length)]

    return {
      id: `assistant-${Date.now()}`,
      role: 'assistant',
      content: `${response} User request: ${message}`,
    }
  },

  async *streamMessage(message: string) {
    // TODO: replace with SSE or streaming API from secure backend.
    const response = await this.sendMessage(message)
    yield response.content
  },

  async getSuggestions() {
    return mockSuggestions
  },

  async executeCommand(command: string) {
    // TODO: secure backend command execution endpoint with validation and permission checks.
    return `Mock command execution for: ${command}`
  },
}
