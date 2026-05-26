'use client'

export type AiStep = {
  id: string
  label: string
  description?: string
  status: 'done' | 'active' | 'pending'
}

interface AiProgressModalProps {
  title: string
  subtitle?: string
  steps: AiStep[]
  progress: number
  open: boolean
}

export function AiProgressModal({ title, subtitle, steps, progress, open }: AiProgressModalProps) {
  if (!open) return null
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm">
      <div style={{ background: 'rgb(var(--panel))', border: '1px solid rgb(var(--line))' }} className="rounded-2xl p-6 w-full max-w-md shadow-xl">
        <p className="text-[15px] font-medium mb-1" style={{ color: 'rgb(var(--ink))' }}>{title}</p>
        {subtitle && <p className="text-[12px] mb-5" style={{ color: 'rgb(var(--text-muted))' }}>{subtitle}</p>}

        <div className="flex flex-col" style={{ borderTop: '1px solid rgb(var(--line))' }}>
          {steps.map((step) => (
            <div key={step.id} className="flex gap-3 py-3 items-start" style={{ borderBottom: '1px solid rgb(var(--line))' }}>
              <StepIcon status={step.status} />
              <div className="flex-1 pt-0.5">
                <p className="text-[13px] font-medium" style={{ color: step.status === 'pending' ? 'rgb(var(--text-soft))' : 'rgb(var(--ink))' }}>
                  {step.label}
                </p>
                {step.description && (
                  <p className="text-[12px] mt-0.5" style={{ color: 'rgb(var(--text-muted))' }}>{step.description}</p>
                )}
                {step.status === 'active' && <PulseDots />}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-4 h-1 rounded-full overflow-hidden" style={{ background: 'rgb(var(--line))' }}>
          <div
            className="h-full rounded-full"
            style={{
              width: `${progress}%`,
              background: 'rgb(var(--primary))',
              transition: 'width 500ms ease-out',
            }}
          />
        </div>
      </div>
    </div>
  )
}

function StepIcon({ status }: { status: AiStep['status'] }) {
  if (status === 'done') return (
    <div className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-[14px]" style={{ background: 'rgb(var(--success-bg))', color: 'var(--success-text)' }}>✓</div>
  )
  if (status === 'active') return (
    <div className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-[14px]" style={{ background: 'var(--info-bg)', color: 'var(--info-text)' }}>◉</div>
  )
  return (
    <div className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-[14px]" style={{ background: 'rgb(var(--surface))', color: 'rgb(var(--text-soft))' }}>○</div>
  )
}

function PulseDots() {
  return (
    <div className="flex gap-1.5 mt-1.5">
      {[0, 1, 2].map(i => (
        <div
          key={i}
          className="w-1.5 h-1.5 rounded-full"
          style={{
            background: 'var(--primary-light)',
            animation: `ep-pulse 1.4s ease-in-out ${i * 0.2}s infinite`,
          }}
        />
      ))}
    </div>
  )
}
