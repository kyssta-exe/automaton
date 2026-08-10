import { useEffect, useState } from 'react'
import { automatonBridge } from './lib/automaton-bridge'
import './theme.css'

type IconName = 'home' | 'video' | 'folder' | 'help' | 'settings' | 'search' | 'plus' | 'arrow' | 'check' | 'clock' | 'cloud' | 'play' | 'spark' | 'back'
type PageName = 'home' | 'videos' | 'processing' | 'drive' | 'help' | 'attach' | 'plan'
type SavedPlan = { id: string; description: string; format: string; subtitles: boolean; clips: string[]; status: string; createdAt: string }

const Icon = ({ name, size = 24 }: { name: IconName; size?: number }) => {
  const paths: Record<IconName, string> = {
    home: 'M3 10.5 12 3l9 7.5M5.5 9v11h13V9M9 20v-6h6v6',
    video: 'M4 5.5A2.5 2.5 0 0 1 6.5 3h9A2.5 2.5 0 0 1 18 5.5v13a2.5 2.5 0 0 1-2.5 2.5h-9A2.5 2.5 0 0 1 4 18.5zM18 9l3-2v10l-3-2',
    folder: 'M3 7.5A2.5 2.5 0 0 1 5.5 5H10l2 2h6.5A2.5 2.5 0 0 1 21 9.5v7A2.5 2.5 0 0 1 18.5 19h-13A2.5 2.5 0 0 1 3 16.5z',
    help: 'M9.5 9a2.7 2.7 0 1 1 4.5 2c-1.4 1.1-2 1.5-2 3M12 17.5v.1M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z',
    settings: 'M12 8.5a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7Zm0-6v3m0 15v3m10-11h-3M5 12H2m17.1-7.1-2.1 2.1M7 17l-2.1 2.1m12.2 0L15 17M7 7 4.9 4.9',
    search: 'm20 20-4.4-4.4m2.4-5.1a7.5 7.5 0 1 1-15 0 7.5 7.5 0 0 1 15 0Z',
    plus: 'M12 5v14M5 12h14',
    arrow: 'M5 12h13m-5-5 5 5-5 5',
    check: 'm5 12 4 4L19 6',
    clock: 'M12 7v5l3 2m7-2a10 10 0 1 1-20 0 10 10 0 0 1 20 0Z',
    cloud: 'M7 18a5 5 0 0 1-.5-10A6 6 0 0 1 18 9a4.5 4.5 0 0 1 0 9H7Z',
    play: 'm9 7 8 5-8 5z',
    spark: 'm12 2 1.8 7.2L21 11l-7.2 1.8L12 20l-1.8-7.2L3 11l7.2-1.8z',
    back: 'm15 18-6-6 6-6M9 12h11',
  }
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d={paths[name]} /></svg>
}

const choices = [
  { title: 'Make a new video', text: 'Use video clips from your computer or online files.', icon: 'plus' as IconName, color: 'purple' },
  { title: 'See my videos', text: 'Look at videos that are ready or still being made.', icon: 'video' as IconName, color: 'blue' },
  { title: 'Get help', text: 'See simple answers or contact support.', icon: 'help' as IconName, color: 'green' },
]

function App() {
  const [page, setPage] = useState<PageName>('home')
  const [message, setMessage] = useState('')
  const [requestNotice, setRequestNotice] = useState('')
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [savedPlans, setSavedPlans] = useState<SavedPlan[]>([])
  const bridgeReady = automatonBridge.status().configured
  useEffect(() => {
    try { setSavedPlans(JSON.parse(localStorage.getItem('automaton-saved-plans') || '[]') as SavedPlan[]) } catch { setSavedPlans([]) }
  }, [])
  const savePlan = (plan: SavedPlan) => {
    setSavedPlans((current) => { const next = [plan, ...current.filter((item) => item.id !== plan.id)].slice(0, 20); localStorage.setItem('automaton-saved-plans', JSON.stringify(next)); return next })
  }
  const notify = (text: string) => window.alert(text)
  const submit = async () => {
    const instruction = message.trim()
    if (!instruction) return
    setMessage('')
    if (!bridgeReady) { setRequestNotice('Your request is ready, but the video service is not connected yet.'); return }
    try { await automatonBridge.sendCommand({ instruction }); setRequestNotice('Your request was sent.') }
    catch { setRequestNotice('Your request could not be sent. Please try again or contact support.') }
  }

  return <div className="simple-app">
    <header className="simple-header"><button className="logo" onClick={() => setPage('home')}><span className="logo-dot" />Automaton</button><div className="header-right"><span className="saved-status"><span className="green-dot" /> Ready to guide you</span><button className="help-button" onClick={() => setPage('help')}><Icon name="help" size={23} /> Help</button></div></header>
    <div className="layout">
      <aside className="simple-sidebar" aria-label="Main navigation"><p className="menu-title">MENU</p><button className={`side-link ${page === 'home' ? 'selected' : ''}`} onClick={() => setPage('home')}><Icon name="home" /><span>Home</span></button><button className={`side-link ${page === 'videos' ? 'selected' : ''}`} onClick={() => setPage('videos')}><Icon name="video" /><span>My videos</span></button><button className={`side-link ${page === 'processing' ? 'selected' : ''}`} onClick={() => setPage('processing')}><Icon name="clock" /><span>Videos in progress</span></button><button className={`side-link ${page === 'drive' ? 'selected' : ''}`} onClick={() => setPage('drive')}><Icon name="cloud" /><span>Google Drive</span></button><button className={`side-link ${page === 'help' ? 'selected' : ''}`} onClick={() => setPage('help')}><Icon name="help" /><span>Help</span></button><div className="sidebar-bottom"><div className="privacy"><Icon name="check" size={19} /><div><strong>Your work is safe</strong><small>Nothing is published, deleted, or finished without your approval.</small></div></div><button className="side-link small-link" onClick={() => notify('Settings are managed for you. Please contact support if you need a change.')}><Icon name="settings" size={20} /><span>Settings</span></button></div></aside>
      <main className="main-area">
        {page === 'home' && <><section className="welcome"><p className="welcome-label">WELCOME</p><h1>What would you like to do?</h1><p>Choose one of the buttons below. You do not need to know anything technical.</p></section><div className="choice-grid">{choices.map((choice) => <button className={`choice-card ${choice.color}`} key={choice.title} onClick={() => choice.title === 'See my videos' ? setPage('videos') : choice.title === 'Get help' ? setPage('help') : setPage('attach')}><span className="choice-icon"><Icon name={choice.icon} size={31} /></span><span className="choice-title">{choice.title}</span><span className="choice-text">{choice.text}</span><span className="choice-arrow"><Icon name="arrow" size={21} /></span></button>)}</div><section className="ask-card"><div className="ask-icon"><Icon name="spark" size={25} /></div><div className="ask-content"><h2>Or just tell me what you need</h2><p>For example: “Make a short video from my latest video clips.”</p><div className="ask-row"><input value={message} onChange={(e) => setMessage(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter') submit() }} placeholder="Type your request here..." aria-label="Tell Automaton what you need" /><button className="send-button" onClick={submit} disabled={!message.trim()}><span>Send</span><Icon name="arrow" size={20} /></button></div>{requestNotice && <div className="request-saved"><Icon name="check" size={18} /> {requestNotice}</div>}</div></section><section className="steps"><h2>How it works</h2><div className="step-row"><Step number="1" title="You choose" text="Tell us what you want." /><Step number="2" title="We do the work" text="Automaton prepares your video." /><Step number="3" title="You check it" text="Nothing is finished until you approve it." /></div></section></>}
        {page === 'attach' && <AttachPage files={selectedFiles} setFiles={setSelectedFiles} onBack={() => setPage('home')} onContinue={() => setPage('plan')} />}
        {page === 'plan' && <PlanPage files={selectedFiles} onBack={() => setPage('attach')} onSave={savePlan} />}
        {page === 'videos' && <VideosPage plans={savedPlans} onBack={() => setPage('home')} onMake={() => setPage('attach')} />}
        {page === 'processing' && <ProcessingPage plans={savedPlans} onBack={() => setPage('home')} />}
        {page === 'drive' && <DrivePage onBack={() => setPage('home')} onMake={() => setPage('attach')} />}
        {page === 'help' && <HelpPage onBack={() => setPage('home')} />}
      </main>
    </div>
  </div>
}

function Step({ number, title, text }: { number: string; title: string; text: string }) { return <div className="step"><span className="step-number">{number}</span><div><strong>{title}</strong><p>{text}</p></div></div> }
function AttachPage({ files, setFiles, onBack, onContinue }: { files: File[]; setFiles: (files: File[]) => void; onBack: () => void; onContinue: () => void }) {
  const [fileNotice, setFileNotice] = useState('')
  const addFiles = (newFiles: FileList | null) => { if (!newFiles) return; const videoExtensions = /\.(mp4|mov|m4v|avi|mkv|webm|mpeg|mpg|3gp)$/i; const incoming = Array.from(newFiles); const valid = incoming.filter((file) => file.type.startsWith('video/') || videoExtensions.test(file.name)); const rejected = incoming.length - valid.length; setFiles([...files, ...valid]); setFileNotice(rejected ? `${rejected} file${rejected === 1 ? '' : 's'} skipped because it is not a video.` : '') }
  return <section className="inner-page"><button className="back-link" onClick={onBack}><Icon name="back" size={20} /> Back to home</button><p className="welcome-label attach-label">STEP 1 OF 2</p><h1>Attach your video clips</h1><p className="inner-intro">Choose the clips you want us to use. Your original files will stay safe.</p><label className="drop-zone" onDragOver={(event) => event.preventDefault()} onDrop={(event) => { event.preventDefault(); addFiles(event.dataTransfer.files) }}><input type="file" accept="video/*" multiple onChange={(event) => addFiles(event.target.files)} /><span className="drop-icon"><Icon name="folder" size={38} /></span><strong>Choose video clips</strong><span className="browse-button">Browse files</span><span>or drag video files into this box</span><small>You can select more than one clip</small></label>{fileNotice && <div className="request-saved"><Icon name="help" size={18} /> {fileNotice}</div>}{files.length > 0 && <div className="attached-list"><h2>Clips selected</h2>{files.map((file, index) => <div className="attached-file" key={`${file.name}-${index}`}><Icon name="video" size={22} /><span>{file.name}</span><small>{Math.max(1, Math.round(file.size / 1024 / 1024))} MB</small><button aria-label={`Remove ${file.name}`} onClick={() => setFiles(files.filter((_, itemIndex) => itemIndex !== index))}>×</button></div>)}<button className="big-action continue-button" onClick={onContinue}><span>Continue</span><Icon name="arrow" size={20} /></button></div>}<div className="online-files"><Icon name="cloud" size={25} /><div><strong>Have your clips online?</strong><p>Google Drive connection will be available here when it is set up.</p></div></div></section> }
function PlanPage({ files, onBack, onSave }: { files: File[]; onBack: () => void; onSave: (plan: SavedPlan) => void }) {
  const [description, setDescription] = useState('')
  const [format, setFormat] = useState('Vertical video for social media')
  const [subtitles, setSubtitles] = useState(true)
  const [notice, setNotice] = useState('')
  const [sending, setSending] = useState(false)
  const bridgeConfigured = automatonBridge.status().configured
  const start = async () => {
    if (!description.trim() || sending) return
    setSending(true)
    const plan: SavedPlan = { id: crypto.randomUUID(), description: description.trim(), format, subtitles, clips: files.map((file) => file.name), status: bridgeConfigured ? 'Sent to video service' : 'Saved on this computer', createdAt: new Date().toISOString() }
    const instruction = `Create a video from these attached clips: ${files.map((file) => file.name).join(', ')}. Format: ${format}. Subtitles: ${subtitles ? 'yes' : 'no'}. Request: ${description.trim()}`
    if (!automatonBridge.status().configured) { onSave(plan); setNotice('Your video plan was saved on this computer. The video service needs to be connected before we can start making it.'); setSending(false); return }
    try { await automatonBridge.sendCommand({ instruction }); onSave(plan); setNotice('Your video request was sent. We will show its progress in My videos.'); setSending(false) }
    catch { setNotice('We could not send the request yet. Please try again or contact support.'); setSending(false) }
  }
  return <section className="inner-page"><button className="back-link" onClick={onBack}><Icon name="back" size={20} /> Back to attached clips</button><p className="welcome-label attach-label">STEP 2 OF 2</p><h1>Tell us about your video</h1><p className="inner-intro">Answer these simple questions. We will use your answers to prepare the first version.</p><div className="plan-card"><label className="form-label" htmlFor="video-description">What should the video be about?</label><textarea id="video-description" className="plan-textarea" value={description} onChange={(event) => setDescription(event.target.value)} placeholder="For example: Make a short video showing our new product." rows={4} /><label className="form-label" htmlFor="video-format">Where will you use it?</label><select id="video-format" className="plan-select" value={format} onChange={(event) => setFormat(event.target.value)}><option>Vertical video for social media</option><option>Landscape video for YouTube</option><option>Square video for social media</option><option>I am not sure yet</option></select><label className="check-option"><input type="checkbox" checked={subtitles} onChange={(event) => setSubtitles(event.target.checked)} /><span><strong>Add large subtitles</strong><small>Helpful when people watch without sound.</small></span></label><div className="plan-files"><strong>Clips ready to use ({files.length})</strong>{files.map((file) => <span key={file.name}><Icon name="check" size={17} /> {file.name}</span>)}</div><button className="big-action start-button" onClick={start} disabled={!description.trim() || sending}>{sending ? 'Saving…' : bridgeConfigured ? 'Start my video' : 'Save my video plan'}<Icon name="arrow" size={20} /></button>{notice && <div className="request-saved plan-notice"><Icon name="check" size={18} /> {notice}</div>}</div></section> }
function VideosPage({ plans, onBack, onMake }: { plans: SavedPlan[]; onBack: () => void; onMake: () => void }) { return <section className="inner-page"><button className="back-link" onClick={onBack}><Icon name="back" size={20} /> Back to home</button><h1>My videos</h1><p className="inner-intro">Your saved plans and videos appear here.</p>{plans.length === 0 ? <div className="empty-card"><span className="empty-icon"><Icon name="video" size={34} /></span><h2>No videos yet</h2><p>When you start a video, you can follow its progress here.</p><button className="big-action" onClick={onMake}><Icon name="plus" size={21} /> Make a new video</button></div> : <div className="saved-plans"><button className="big-action" onClick={onMake}><Icon name="plus" size={21} /> Make another video</button>{plans.map((plan) => <article className="saved-plan" key={plan.id}><div className="saved-plan-top"><Icon name="video" size={24} /><strong>{plan.description}</strong></div><p>{plan.format} · {plan.subtitles ? 'Large subtitles' : 'No subtitles'}</p><small>{plan.clips.length} clip{plan.clips.length === 1 ? '' : 's'} · {plan.status}</small></article>)}</div>}</section> }
function HelpPage({ onBack }: { onBack: () => void }) { return <section className="inner-page"><button className="back-link" onClick={onBack}><Icon name="back" size={20} /> Back to home</button><h1>How can we help?</h1><p className="inner-intro">You can always come back here if you are unsure what to do.</p><div className="help-list"><div className="help-item"><span><Icon name="play" size={27} /></span><div><h2>How do I make a video?</h2><p>Choose “Make a new video” on the Home screen. We will guide you step by step.</p></div></div><div className="help-item"><span><Icon name="cloud" size={27} /></span><div><h2>Where are my files?</h2><p>Your original files are kept safe. We do not replace them.</p></div></div><div className="help-item"><span><Icon name="help" size={27} /></span><div><h2>Need to speak to someone?</h2><p>Please contact support and tell us what you see on your screen.</p></div></div></div></section> }
function ProcessingPage({ plans, onBack }: { plans: SavedPlan[]; onBack: () => void }) { const active = plans.filter((plan) => plan.status !== 'Saved on this computer'); return <section className="inner-page"><button className="back-link" onClick={onBack}><Icon name="back" size={20} /> Back to home</button><p className="welcome-label attach-label">VIDEO PROGRESS</p><h1>Videos in progress</h1><p className="inner-intro">See what Automaton is preparing from your clips and Google Drive.</p>{active.length === 0 ? <div className="empty-card"><span className="empty-icon"><Icon name="clock" size={34} /></span><h2>Nothing is being processed</h2><p>When a video starts, its progress will appear here.</p></div> : <div className="saved-plans">{active.map((plan) => <article className="saved-plan" key={plan.id}><div className="saved-plan-top"><Icon name="clock" size={24} /><strong>{plan.description}</strong></div><p>{plan.status}</p><small>{plan.clips.length} clip{plan.clips.length === 1 ? '' : 's'} · Waiting for the connected video service</small></article>)}</div>}</section> }
function DrivePage({ onBack, onMake }: { onBack: () => void; onMake: () => void }) { const [checking, setChecking] = useState(false); const [message, setMessage] = useState(''); const connected = automatonBridge.status().configured; const checkConnection = async () => { setChecking(true); const result = await automatonBridge.health(); setMessage(result.reachable ? 'Google Drive and the video service are connected.' : 'Google Drive is not connected yet. Please ask support to finish setup.'); setChecking(false) }; return <section className="inner-page"><button className="back-link" onClick={onBack}><Icon name="back" size={20} /> Back to home</button><p className="welcome-label attach-label">ONLINE FILES</p><h1>Google Drive</h1><p className="inner-intro">Use videos already saved online without changing your original files.</p><div className="drive-card"><span className={`drive-status-dot ${connected ? 'connected' : ''}`} /><div><h2>{connected ? 'Google Drive is ready' : 'Google Drive is not connected'}</h2><p>{connected ? 'You can choose online video clips when the video service is connected.' : 'This is a one-time setup. Your support person can connect it for you.'}</p></div></div><div className="drive-actions"><button className="big-action" onClick={checkConnection} disabled={checking}>{checking ? 'Checking…' : 'Check connection'}<Icon name="arrow" size={20} /></button><button className="secondary-action" onClick={onMake}><Icon name="folder" size={21} /> Use videos from my computer</button></div>{message && <div className="request-saved plan-notice"><Icon name="check" size={18} /> {message}</div>}<div className="online-files drive-note"><Icon name="check" size={25} /><div><strong>Your originals stay safe</strong><p>Automaton will only use a copy for video preparation. Nothing is deleted or published without your approval.</p></div></div></section> }

export default App
