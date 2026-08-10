# Integration contract

The renderer is deliberately local-first and provider-agnostic. It should not hold Google credentials, call ffmpeg directly, or guess at video state.

## Bridge interface

The future Vite/Electron bridge should expose:

```ts
export type AutomatonBridge = {
  workspace: {
    getStatus(): Promise<{ name: string; root: string; ready: boolean }>
  }
  drive: {
    getStatus(): Promise<{ connected: boolean; account?: string; folderId?: string }>
    connect(): Promise<{ connected: boolean }>
    listFolder(folderId: string): Promise<DriveItem[]>
    download(fileId: string, targetDir: string): Promise<{ path: string }>
  }
  projects: {
    list(): Promise<ProjectSummary[]>
    get(id: string): Promise<ProjectDetail>
    create(input: CreateProjectInput): Promise<ProjectDetail>
  }
  jobs: {
    enqueue(input: VideoJobInput): Promise<{ jobId: string }>
    get(jobId: string): Promise<JobStatus>
    subscribe(listener: (event: JobEvent) => void): () => void
  }
  commands: {
    run(input: CommandInput): Promise<{ commandId: string }>
  }
}
```

## Rules

- All paths must be returned by the bridge as absolute native paths and normalized before rendering.
- Originals stay untouched. Generated assets go into the source workspace `edit/` directory.
- Drive actions must report OAuth/account/folder state explicitly; never show a connected state based on local mock data.
- Video jobs must expose `queued`, `transcribing`, `review`, `rendering`, `verifying`, `complete`, and `failed` states.
- The UI should show source-of-truth timestamps and job IDs for every destructive or expensive action.
- Keep renderer code compatible with a browser build. Electron-specific APIs belong behind `window.automaton` or a preload adapter.

## Video workflow mapping

The existing video workflow remains the production authority: inspect source footage, cache word-level transcripts, confirm an editing strategy, render with subtitles last, and visually verify the output before delivery. The command center should orchestrate those steps, not duplicate their logic.
