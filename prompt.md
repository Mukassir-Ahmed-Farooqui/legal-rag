# ClauseScope Hotfix — Login Race Condition & Workspace Initialization

## Problem

On login, the workspace loads in a broken intermediate state:
- Documents load correctly (auth token available in time)
- Chat history shows "No chats yet" (auth token NOT available in time)
- Manual page refresh fixes everything

This is a race condition. The chat fetch fires before the JWT is
committed to the Axios interceptor, receives a 401, silently fails,
and never retries.

Manual reload starts with the token already in localStorage so
everything works correctly.

DO NOT modify:
- Backend APIs
- Auth logic
- Retrieval pipeline
- Database schema

Frontend initialization logic only.

---

## Root Cause Investigation

### Step 1 — Find where chat fetch is triggered

Open the main layout or dashboard component (App.tsx or equivalent).

Locate where `GET /api/v1/chats` is called.

Answer:
- Is it called inside a useEffect with [] dependency (on mount)?
- Is it called before or after the auth token is set in the
  Axios interceptor?
- Is there any await or guard ensuring the token exists before
  the fetch fires?

### Step 2 — Find where token is set after login

Locate the login flow:
- Where is the token written to localStorage?
- Where is the Axios Authorization header set?
- Is there a timing gap between "token written to localStorage"
  and "Axios interceptor picks it up"?

### Step 3 — Identify the gap

The bug is almost certainly one of these:

**Pattern A (most common)**:
```javascript
// Token stored here
localStorage.setItem('token', data.access_token)

// But Axios interceptor reads token at request time, not set time
// If chat fetch fires in the same render cycle, interceptor
// may read stale/empty token from a closure

useEffect(() => {
  fetchChats() // fires immediately, before token is in interceptor
}, [])
```

**Pattern B**:
```javascript
// Login sets auth state
setUser(userData)

// useEffect depends on user but fires one render too early
useEffect(() => {
  if (user) fetchChats() // correct pattern but timing still off
}, [user])
```

Document which pattern exists in the current codebase.

---

## Required Fixes

### Fix 1 — Guard chat fetch behind confirmed auth state

The chat fetch must ONLY fire after:
1. Token exists in localStorage AND
2. Token is set in Axios default headers AND
3. User object is confirmed in auth context

```javascript
// In your auth context or API service, ensure this runs on init:
const token = localStorage.getItem('token')
if (token) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
}

// Chat fetch must check this explicitly:
useEffect(() => {
  const token = localStorage.getItem('token')
  if (!token) return  // do not fetch without token
  fetchChats()
}, [isAuthenticated]) // depend on auth state, not just mount
```

### Fix 2 — Auto-create chat if list is empty

After chat list fetch completes:

```javascript
const loadWorkspace = async () => {
  try {
    const chats = await api.get('/chats')
    if (chats.data.length === 0) {
      // No chats exist — create one automatically
      const newChat = await api.post('/chats', {
        scope_type: 'corpus',
        scope_doc_id: null
      })
      setActiveChat(newChat.data)
      setChatList([newChat.data])
    } else {
      // Load most recent chat
      setChatList(chats.data)
      setActiveChat(chats.data[0]) // sorted by updated_at DESC
    }
  } catch (err) {
    // Do not show "No chats yet" on auth failure
    // Retry once after 500ms in case of token timing issue
    if (err.response?.status === 401) {
      setTimeout(loadWorkspace, 500)
    }
  }
}
```

### Fix 3 — Add skeleton loading states

Replace "No chats yet" with skeleton placeholders while fetching.

In the sidebar chat list:

```javascript
if (chatsLoading) {
  return (
    <div>
      {[1,2,3].map(i => (
        <div key={i} className="skeleton-chat-item">
          {/* Pulsing placeholder */}
        </div>
      ))}
    </div>
  )
}

if (chatList.length === 0 && !chatsLoading) {
  // This state should rarely be seen because Fix 2 auto-creates a chat
  return <div>Starting workspace...</div>
}
```

CSS for skeleton (add to stylesheet):
```css
.skeleton-chat-item {
  height: 40px;
  background: linear-gradient(90deg, #2a2a2a 25%, #333 50%, #2a2a2a 75%);
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.4s ease-in-out infinite;
  border-radius: 6px;
  margin: 4px 8px;
}

@keyframes skeleton-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

### Fix 4 — Parallel fetch on init (performance)

Currently fetches are likely sequential:
```
fetch chats → wait → fetch documents → wait → render
```

Make them parallel:
```javascript
const loadWorkspace = async () => {
  setChatsLoading(true)
  setDocsLoading(true)

  // Fire both simultaneously
  const [chatsResult, docsResult] = await Promise.allSettled([
    api.get('/chats'),
    api.get('/documents')
  ])

  // Handle chats
  if (chatsResult.status === 'fulfilled') {
    const chats = chatsResult.value.data
    if (chats.length === 0) {
      // auto-create
    } else {
      setChatList(chats)
      setActiveChat(chats[0])
    }
  }
  setChatsLoading(false)

  // Handle docs
  if (docsResult.status === 'fulfilled') {
    setDocuments(docsResult.value.data)
  }
  setDocsLoading(false)
}
```

`Promise.allSettled` (not `Promise.all`) means a chat failure
does not prevent documents from loading and vice versa.

### Fix 5 — Call loadWorkspace at the right moment

The workspace initialization must be called ONCE after login,
at the correct moment:

```javascript
// In your login handler:
const handleLogin = async (email, password) => {
  const response = await api.post('/auth/login', { email, password })
  const token = response.data.access_token

  // 1. Store token
  localStorage.setItem('token', token)

  // 2. Set on Axios IMMEDIATELY (synchronously, before any navigation)
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`

  // 3. Set auth state
  setUser(response.data.user)
  setIsAuthenticated(true)

  // 4. Navigate to workspace
  navigate('/chat')

  // loadWorkspace will fire in the workspace component's useEffect
  // because isAuthenticated is now true BEFORE the component mounts
}
```

The key: step 2 (setting Axios header) must happen BEFORE step 4
(navigation). This ensures the workspace component never mounts
without a valid token in the Axios interceptor.

---

## Validation

After implementing all fixes:

### Test 1 — Clean login (primary fix)
1. Log out completely (clear localStorage)
2. Log in fresh
3. Workspace must load with chat history visible in < 500ms
4. No manual refresh required
5. "No chats yet" must never appear if chats exist

### Test 2 — First-time user (auto-chat)
1. Delete all chats via API or DB
2. Log in
3. New chat must be auto-created and visible immediately
4. Workspace ready without any clicks

### Test 3 — Skeleton loading
1. Throttle network to "Slow 3G" in browser devtools
2. Log in
3. Sidebar must show skeleton placeholders, NOT "No chats yet"
4. Skeletons replace with real content when fetch completes

### Test 4 — Parallel fetch speed
Open browser devtools → Network tab
Log in and observe:
- GET /chats and GET /documents must fire at the same time
- NOT one after the other
- Total workspace load time must be < 800ms on local network

### Test 5 — No regression
- Document checkboxes still work
- Chat switching still works
- Query still works
- Citations still display

---

## Deliverables

1. Root cause statement (one paragraph — which pattern A or B)
2. Files modified (list only)
3. Code diff for each fix
4. Network waterfall screenshot showing parallel fetches
5. Validation results:

```
[PASS] Login → workspace loads without manual refresh
[PASS] Chat history visible immediately on login
[PASS] Auto-chat created when no chats exist
[PASS] Skeleton shown during loading (not blank/error)
[PASS] Chats and documents fetch in parallel
[PASS] Workspace ready in < 800ms
[PASS] No regression on chat/query/citations
```

## Success Condition

Login → workspace is fully ready in under 800ms.
Zero manual refreshes required.
Zero "No chats yet" flash on login.
Zero glitch or blank intermediate state.