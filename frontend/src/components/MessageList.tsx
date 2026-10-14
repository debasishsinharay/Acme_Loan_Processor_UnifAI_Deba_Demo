'use client'

import { Paperclip } from 'lucide-react'
import { Message } from './ChatInterface'

export function MessageList({ messages }: { messages: Message[] }) {
  return (
    <div className="mx-auto flex w-full max-w-4xl flex-col gap-4">
      {messages.map(message => {
        const mine = message.role === 'user'
        return (
          <div key={message.id} className={`fade-in-up flex ${mine ? 'justify-end' : 'justify-start'}`}>
            <div className="max-w-3xl">
              <div
                className={`rounded-[20px] border px-5 py-4 text-sm sm:text-[15px] ${
                  mine
                    ? 'border-slate-700 bg-slate-100 text-slate-900'
                    : message.isError
                      ? 'border-rose-500/40 bg-rose-950/40 text-rose-100'
                      : 'border-slate-700 bg-slate-900 text-slate-100'
                }`}
              >
                {message.attachmentName && (
                  <div className="mb-2 flex items-center gap-2 text-xs opacity-70">
                    <Paperclip className="h-3.5 w-3.5" />
                    {message.attachmentName}
                  </div>
                )}
                <div className="whitespace-pre-wrap break-words">{message.content}</div>
              </div>
              <div className={`mt-1.5 px-1 text-xs text-slate-500 ${mine ? 'text-right' : 'text-left'}`}>
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                {message.agent && ` · ${message.agent}`}
                {message.unifai && (
                  <span className={message.unifai === 'on' ? 'text-emerald-400' : 'text-amber-400'}>
                    {` · UnifAI ${message.unifai.toUpperCase()}`}
                  </span>
                )}
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
