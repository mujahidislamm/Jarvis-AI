import { useEffect, useMemo, useRef, useState } from 'react'
import './App.css'
import { aiAdapter, type ChatMessage } from './services/aiAdapter'

type PanelId =
  | 'overview'
  | 'systems'
  | 'orbit'
  | 'workstreams'
  | 'activity'
  | 'tasks'
  | 'intel'

type PanelDefinition = {
  id: PanelId
  title: string
  accent: string
  position: { x: number; y: number }
  size: { w: number; h: number }
  visible: boolean
  minimized: boolean
}

type DragState = {
  panelId: PanelId
  mode: 'move' | 'resize'
  startX: number
  startY: number
  originX: number
  originY: number
  originW: number
  originH: number
}

const STORAGE_KEY = 'aurora-workspace-layout-v1'
const GRID_STEP = 28
const GRID_COLUMNS = 24
const GRID_ROWS = 16

const defaultPanels: PanelDefinition[] = [
  { id: 'overview', title: 'Overview', accent: '#69f0ff', position: { x: 0, y: 0 }, size: { w: 8, h: 6 }, visible: true, minimized: false },
  { id: 'systems', title: 'Systems', accent: '#7ef7d2', position: { x: 8, y: 0 }, size: { w: 8, h: 6 }, visible: true, minimized: false },
  { id: 'orbit', title: 'Orbital View', accent: '#ffb170', position: { x: 16, y: 0 }, size: { w: 8, h: 7 }, visible: true, minimized: false },
  { id: 'workstreams', title: 'Workstreams', accent: '#d3a5ff', position: { x: 0, y: 6 }, size: { w: 10, h: 7 }, visible: true, minimized: false },
  { id: 'activity', title: 'Activity', accent: '#8ee8ff', position: { x: 10, y: 6 }, size: { w: 8, h: 7 }, visible: true, minimized: false },
  { id: 'tasks', title: 'Task Queue', accent: '#ff7fa8', position: { x: 18, y: 7 }, size: { w: 6, h: 6 }, visible: true, minimized: false },
  { id: 'intel', title: 'Intel Feed', accent: '#76ffb8', position: { x: 0, y: 13 }, size: { w: 24, h: 3 }, visible: true, minimized: false },
]

const clamp = (value: number, min: number, max: number) => Math.min(Math.max(value, min), max)
const roundToGrid = (value: number, step = GRID_STEP) => Math.round(value / step) * step

function App() {
  const workspaceRef = useRef<HTMLDivElement | null>(null)
  const dragStateRef = useRef<DragState | null>(null)

  const [panels, setPanels] = useState<PanelDefinition[]>(() => {
    const saved = window.localStorage.getItem(STORAGE_KEY)
    if (!saved) {
      return defaultPanels
    }

    try {
      const parsed = JSON.parse(saved) as PanelDefinition[]
      if (Array.isArray(parsed) && parsed.length > 0) {
        return parsed
      }
    } catch {
      return defaultPanels
    }

    return defaultPanels
  })

  const [editMode, setEditMode] = useState(false)
  const [selectedPanel, setSelectedPanel] = useState<PanelId>('overview')
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [assistantOpen, setAssistantOpen] = useState(true)
  const [commandOpen, setCommandOpen] = useState(false)
  const [draftMessage, setDraftMessage] = useState('')
  const [messages, setMessages] = useState<ChatMessage[]>([
    { id: 'intro', role: 'assistant', content: 'AURORA is monitoring the workspace. Ask for deployment status, task prioritization, or a system overview.' },
  ])
  const [suggestions, setSuggestions] = useState<string[]>([])

  useEffect(() => {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(panels))
  }, [panels])

  useEffect(() => {
    aiAdapter.getSuggestions().then((nextSuggestions) => setSuggestions(nextSuggestions))
  }, [])

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault()
        setCommandOpen((current) => !current)
      }

      if (event.key.toLowerCase() === 'e' && !event.metaKey && !event.ctrlKey) {
        setEditMode((current) => !current)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  useEffect(() => {
    const handlePointerMove = (event: PointerEvent) => {
      const dragState = dragStateRef.current
      if (!dragState || !workspaceRef.current) {
        return
      }

      const deltaX = event.clientX - dragState.startX
      const deltaY = event.clientY - dragState.startY

      setPanels((currentPanels) =>
        currentPanels.map((panel) => {
          if (panel.id !== dragState.panelId) {
            return panel
          }

          if (dragState.mode === 'move') {
            const nextX = clamp(
              dragState.originX + Math.round(deltaX / GRID_STEP),
              0,
              GRID_COLUMNS - panel.size.w,
            )
            const nextY = clamp(
              dragState.originY + Math.round(deltaY / GRID_STEP),
              0,
              GRID_ROWS - panel.size.h,
            )

            return { ...panel, position: { x: nextX, y: nextY } }
          }

          const nextW = clamp(
            dragState.originW + Math.round(deltaX / GRID_STEP),
            4,
            GRID_COLUMNS - panel.position.x,
          )
          const nextH = clamp(
            dragState.originH + Math.round(deltaY / GRID_STEP),
            3,
            GRID_ROWS - panel.position.y,
          )

          return { ...panel, size: { w: nextW, h: nextH } }
        }),
      )
    }

    const handlePointerUp = () => {
      dragStateRef.current = null
    }

    window.addEventListener('pointermove', handlePointerMove)
    window.addEventListener('pointerup', handlePointerUp)

    return () => {
      window.removeEventListener('pointermove', handlePointerMove)
      window.removeEventListener('pointerup', handlePointerUp)
    }
  }, [])

  const visiblePanels = useMemo(
    () => panels.filter((panel) => panel.visible),
    [panels],
  )

  const hiddenPanels = useMemo(
    () => panels.filter((panel) => !panel.visible),
    [panels],
  )

  const beginDrag = (
    panelId: PanelId,
    mode: 'move' | 'resize',
    event: React.PointerEvent<HTMLElement>,
  ) => {
    if (!editMode) {
      return
    }

    const panel = panels.find((item) => item.id === panelId)
    if (!panel) {
      return
    }

    event.preventDefault()
    dragStateRef.current = {
      panelId,
      mode,
      startX: event.clientX,
      startY: event.clientY,
      originX: panel.position.x,
      originY: panel.position.y,
      originW: panel.size.w,
      originH: panel.size.h,
    }
    setSelectedPanel(panelId)
  }

  const togglePanelVisibility = (panelId: PanelId) => {
    setPanels((currentPanels) =>
      currentPanels.map((panel) =>
        panel.id === panelId ? { ...panel, visible: !panel.visible } : panel,
      ),
    )
  }

  const resetWorkspace = () => {
    setPanels(defaultPanels)
    setEditMode(false)
    setSelectedPanel('overview')
  }

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    if (!draftMessage.trim()) {
      return
    }

    const message = draftMessage.trim()
    setDraftMessage('')
    const userMessage: ChatMessage = {
      id: `${Date.now()}-user`,
      role: 'user',
      content: message,
    }

    setMessages((current) => [...current, userMessage])

    const response = await aiAdapter.sendMessage(message)
    setMessages((current) => [...current, response])
  }

  const renderPanelBody = (panelId: PanelId) => {
    switch (panelId) {
      case 'overview':
        return (
          <div className="overview-grid">
            <div className="stat-block accent">
              <span className="stat-label">Actively running</span>
              <strong>27</strong>
              <small>systems</small>
            </div>
            <div className="stat-block">
              <span className="stat-label">Priority</span>
              <strong>92%</strong>
              <small>stability</small>
            </div>
            <div className="stat-block">
              <span className="stat-label">Tasks</span>
              <strong>14</strong>
              <small>ai queued</small>
            </div>
          </div>
        )
      case 'systems':
        return (
          <ul className="status-list">
            <li><span>Core engine</span><em>Nominal</em></li>
            <li><span>Data layer</span><em>Synced</em></li>
            <li><span>Deploy ring</span><em>Healthy</em></li>
            <li><span>Guardrails</span><em>Active</em></li>
          </ul>
        )
      case 'orbit':
        return (
          <div className="orbital-scene" aria-label="orbital map">
            <span className="planet planet-a" />
            <span className="planet planet-b" />
            <span className="planet planet-c" />
            <span className="orbit orbit-a" />
            <span className="orbit orbit-b" />
            <span className="orbit orbit-c" />
          </div>
        )
      case 'workstreams':
        return (
          <div className="chip-stack">
            <span>Ops Sync</span>
            <span>Research</span>
            <span>Build</span>
            <span>Automation</span>
            <span>Launch</span>
          </div>
        )
      case 'activity':
        return (
          <div className="activity-bars" aria-label="activity timeline">
            <span style={{ height: '38%' }} />
            <span style={{ height: '58%' }} />
            <span style={{ height: '72%' }} />
            <span style={{ height: '84%' }} />
            <span style={{ height: '66%' }} />
            <span style={{ height: '92%' }} />
            <span style={{ height: '76%' }} />
          </div>
        )
      case 'tasks':
        return (
          <ul className="task-list">
            <li><input type="checkbox" defaultChecked /><span>QA pass</span></li>
            <li><input type="checkbox" defaultChecked /><span>UI sync</span></li>
            <li><input type="checkbox" /><span>Deploy</span></li>
          </ul>
        )
      case 'intel':
        return (
          <div className="intel-strip">
            <span>Market pulse: stable</span>
            <span>Ops: no blockers</span>
            <span>Forecast: optimistic</span>
          </div>
        )
      default:
        return null
    }
  }

  return (
    <div className={`aurora-app ${editMode ? 'edit-mode' : ''}`}>
      <aside className="nav-rail" aria-label="primary navigation">
        <div className="brand-wrap">
          <div className="brand-mark">A</div>
          <div>
            <strong>AURORA</strong>
            <small>OS</small>
          </div>
        </div>

        <nav className="nav-links">
          <button className="nav-button active" type="button">Workspace</button>
          <button className="nav-button" type="button">Signals</button>
          <button className="nav-button" type="button">Research</button>
          <button className="nav-button" type="button">Agents</button>
        </nav>

        <div className="rail-footer">
          <button type="button" className="secondary-button" onClick={() => setEditMode((current) => !current)}>
            {editMode ? 'Exit Edit' : 'Edit Workspace'}
          </button>
        </div>
      </aside>

      <div className="main-shell">
        <header className="topbar">
          <div className="topbar-groups">
            <button type="button" className="ghost-button" onClick={() => setCommandOpen(true)}>
              Command Palette
            </button>
            <button type="button" className="ghost-button" onClick={() => setDrawerOpen((current) => !current)}>
              Hidden Panels
            </button>
          </div>

          <div className="topbar-center">
            <span className="status-dot" />
            <span>Systems online</span>
          </div>

          <div className="topbar-actions">
            <button type="button" className="action-button neutral" onClick={() => setAssistantOpen((current) => !current)}>
              {assistantOpen ? 'Hide assistant' : 'Show assistant'}
            </button>
            <button type="button" className="action-button accent" onClick={resetWorkspace}>
              Reset Workspace
            </button>
          </div>
        </header>

        <main className="workspace-shell">
          <section ref={workspaceRef} className="workspace-grid" aria-label="workspace layout">
            {visiblePanels.map((panel) => {
              const isSelected = selectedPanel === panel.id
              const panelStyle = {
                left: `${panel.position.x * GRID_STEP}px`,
                top: `${panel.position.y * GRID_STEP}px`,
                width: `${panel.size.w * GRID_STEP}px`,
                height: `${panel.minimized ? 64 : panel.size.h * GRID_STEP}px`,
              } as const

              return (
                <article
                  key={panel.id}
                  className={`workspace-panel ${isSelected ? 'selected' : ''} ${panel.minimized ? 'minimized' : ''}`}
                  style={panelStyle}
                  onPointerDown={() => setSelectedPanel(panel.id)}
                >
                  <div className="panel-header">
                    <div
                      className="panel-grip"
                      title={editMode ? 'Drag panel' : 'Focus panel'}
                      onPointerDown={(event) => beginDrag(panel.id, 'move', event)}
                    >
                      <span />
                      <span />
                      <span />
                    </div>

                    <div className="panel-title-wrap">
                      <span className="panel-dot" style={{ background: panel.accent }} />
                      <span>{panel.title}</span>
                    </div>

                    <div className="panel-actions">
                      <button type="button" className="panel-button" onClick={() => setPanels((current) => current.map((item) => item.id === panel.id ? { ...item, minimized: !item.minimized } : item))}>
                        {panel.minimized ? 'Max' : 'Min'}
                      </button>
                      <button type="button" className="panel-button" onClick={() => setPanels((current) => current.map((item) => item.id === panel.id ? { ...item, visible: false } : item))}>
                        Hide
                      </button>
                    </div>
                  </div>

                  {!panel.minimized && <div className="panel-body">{renderPanelBody(panel.id)}</div>}

                  {editMode && (
                    <button
                      type="button"
                      className="resize-handle"
                      aria-label={`Resize ${panel.title}`}
                      onPointerDown={(event) => beginDrag(panel.id, 'resize', event)}
                    />
                  )}
                </article>
              )
            })}
          </section>

          <aside className={`assistant-panel ${assistantOpen ? 'open' : 'closed'}`} aria-label="AURORA assistant">
            <div className="assistant-header">
              <div>
                <span className="eyebrow">AI assistant</span>
                <h2>AURORA</h2>
              </div>
              <button type="button" className="mini-button" onClick={() => setAssistantOpen(false)}>
                Collapse
              </button>
            </div>

            <div className="assistant-body">
              {messages.map((message) => (
                <div key={message.id} className={`message ${message.role}`}>
                  {message.content}
                </div>
              ))}
            </div>

            <div className="assistant-suggestions">
              {suggestions.map((suggestion) => (
                <button key={suggestion} type="button" className="suggestion-chip" onClick={() => setDraftMessage(suggestion)}>
                  {suggestion}
                </button>
              ))}
            </div>

            <form className="assistant-form" onSubmit={handleSubmit}>
              <input
                type="text"
                value={draftMessage}
                onChange={(event) => setDraftMessage(event.target.value)}
                placeholder="Ask AURORA to plan or automate..."
                aria-label="Type a message to the assistant"
              />
              <button type="submit" className="action-button accent">Send</button>
            </form>
          </aside>
        </main>
      </div>

      {drawerOpen && (
        <aside className="floating-drawer" aria-label="Hidden panels drawer">
          <div className="drawer-header">
            <strong>Available panels</strong>
            <button type="button" className="mini-button" onClick={() => setDrawerOpen(false)}>
              Close
            </button>
          </div>

          <div className="drawer-list">
            {hiddenPanels.length === 0 ? (
              <p>All panels are visible.</p>
            ) : (
              hiddenPanels.map((panel) => (
                <button key={panel.id} type="button" className="drawer-item" onClick={() => { togglePanelVisibility(panel.id); setDrawerOpen(false) }}>
                  {panel.title}
                </button>
              ))
            )}
          </div>
        </aside>
      )}

      {commandOpen && (
        <div className="command-overlay" role="dialog" aria-modal="true" aria-label="Command palette">
          <div className="command-panel">
            <div className="drawer-header">
              <strong>Command palette</strong>
              <button type="button" className="mini-button" onClick={() => setCommandOpen(false)}>
                Esc
              </button>
            </div>

            <div className="command-items">
              <button type="button" className="command-item" onClick={() => { setEditMode(true); setCommandOpen(false) }}>
                Open edit workspace mode
              </button>
              <button type="button" className="command-item" onClick={() => { setAssistantOpen(true); setCommandOpen(false) }}>
                Open AURORA assistant
              </button>
              <button type="button" className="command-item" onClick={() => { resetWorkspace(); setCommandOpen(false) }}>
                Reset layout
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
