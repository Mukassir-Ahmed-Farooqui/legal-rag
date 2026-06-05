import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, AuthContext } from './context/AuthContext';
import { useAuth } from './hooks/useAuth';
import { useDocuments } from './hooks/useDocuments';
import { useChat } from './hooks/useChat';
import { LoginPage } from './components/auth/LoginPage';
import { RegisterPage } from './components/auth/RegisterPage';
import { ProtectedRoute } from './components/ProtectedRoute';
import { DocumentsPanel } from './components/documents/DocumentsPanel';
import { ChatArea } from './components/chat/ChatArea';
import { InputBar } from './components/chat/InputBar';
import { Toaster } from 'react-hot-toast';
import { truncateFilename } from './services/api';
import {
  Shield,
  LogOut,
  Globe,
  FileText,
  Trash2,
  ListFilter,
  Plus,
  MessageSquare,
  Edit,
  Check,
  X,
  Database,
} from 'lucide-react';


const DashboardLayout = () => {
  const { user, logout } = useAuth();
  const { documents, uploadProgress, uploadDocument, deleteDocument } = useDocuments();
  
  const { isAuthenticated } = useAuth();
  const {
    chats,
    activeChatId,
    activeChat,
    selectedDocId,
    messages,
    isQuerying,
    isLoadingChats,
    isLoadingMessages,
    askQuestion,
    selectChat,
    handleCreateChat,
    handleRenameChat,
    handleDeleteChat,
    handleUpdateScope,
  } = useChat(isAuthenticated);

  // Layout states
  const [isDocsOpen, setIsDocsOpen] = useState(true);
  const [editingChatId, setEditingChatId] = useState(null);
  const [editingTitle, setEditingTitle] = useState('');

  const handleLogout = () => {
    const confirm = window.confirm('Are you sure you want to sign out?');
    if (confirm) {
      logout();
    }
  };

  // Find active doc filename
  const activeDocName = documents.find((doc) => doc.doc_id === selectedDocId)?.filename || '';

  const startEditing = (chat, e) => {
    e.stopPropagation();
    setEditingChatId(chat.id);
    setEditingTitle(chat.title);
  };

  const saveRename = (chatId) => {
    if (editingTitle.trim() && editingTitle.trim() !== chats.find(c => c.id === chatId)?.title) {
      handleRenameChat(chatId, editingTitle.trim());
    }
    setEditingChatId(null);
  };

  const cancelRename = (e) => {
    e.stopPropagation();
    setEditingChatId(null);
  };

  return (
    <div className="flex flex-col h-screen w-screen bg-slate-100 overflow-hidden font-sans">
      {/* Premium Top Navigation Bar */}
      <header className="h-14 bg-slate-900 border-b border-slate-800 flex items-center justify-between px-6 shrink-0 shadow-md z-10 select-none">
        <div className="flex items-center gap-2.5">
          <div className="h-9 w-9 rounded-lg bg-blue-650 flex items-center justify-center text-white shadow-lg">
            <Shield className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-sm font-extrabold text-white tracking-wider uppercase flex items-center gap-1.5">
              ClauseScope <span className="text-[10px] bg-blue-500/20 text-blue-400 px-1.5 py-0.5 rounded font-normal normal-case">AI</span>
            </h1>
            <p className="text-[9px] text-slate-400 font-medium">AI-Powered Contract Intelligence Platform</p>
          </div>
        </div>

        {/* User Identity and Logout */}
        <div className="flex items-center gap-4">
          <div className="text-right">
            <p className="text-xs font-bold text-slate-200">{user?.full_name || 'Legal Analyst'}</p>
            <p className="text-[10px] text-slate-400 font-mono">{user?.email}</p>
          </div>
          <div className="h-8 w-px bg-slate-800" />
          <button
            onClick={handleLogout}
            className="flex items-center justify-center p-2 rounded-lg bg-slate-800/50 hover:bg-red-950/40 text-slate-400 hover:text-red-400 border border-slate-800 transition-all cursor-pointer"
            title="Sign out of platform"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </header>

      {/* Main Workspace (Three Columns Layout) */}
      <main className="flex-1 flex min-h-0 overflow-hidden">
        
        {/* Column 1: Left Chat Sidebar (245px width) */}
        <aside className="w-[245px] bg-slate-900 border-r border-slate-800 flex flex-col min-h-0 shrink-0 text-slate-350 select-none">
          <div className="p-4 border-b border-slate-800 shrink-0">
            <button
              onClick={() => handleCreateChat('corpus')}
              className="w-full py-2.5 px-4 bg-blue-650 hover:bg-blue-600 active:bg-blue-700 text-white text-xs font-extrabold rounded-xl shadow-md transition-all flex items-center justify-center gap-2 cursor-pointer border border-blue-500/30"
              title="Create a clean chat session"
            >
              <Plus className="h-4 w-4" />
              <span>New Chat</span>
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-2 space-y-1">
            <div className="px-2 py-1.5 text-[10px] font-extrabold text-slate-500 uppercase tracking-wider">
              Chat History
            </div>
            {isLoadingChats && chats.length === 0 ? (
              <div className="p-4 text-center text-xs text-slate-555">
                Loading history...
              </div>
            ) : chats.length === 0 ? (
              <div className="p-4 text-center text-xs text-slate-555">
                No chats yet.
              </div>
            ) : (
              chats.map((c) => {
                const isActive = c.id === activeChatId;
                const isEditing = c.id === editingChatId;

                return (
                  <div
                    key={c.id}
                    onClick={() => !isEditing && selectChat(c.id)}
                    className={`group relative flex items-center justify-between px-3 py-2.5 rounded-xl transition-all cursor-pointer select-none text-xs font-semibold ${
                      isActive
                        ? 'bg-slate-800 text-white shadow-inner border-l-4 border-blue-500'
                        : 'hover:bg-slate-850 hover:text-slate-200 text-slate-400'
                    }`}
                  >
                    <div className="flex items-center gap-2 min-w-0 flex-1">
                      <MessageSquare className={`h-4 w-4 shrink-0 ${isActive ? 'text-blue-400' : 'text-slate-500'}`} />
                      {isEditing ? (
                        <input
                          type="text"
                          value={editingTitle}
                          onChange={(e) => setEditingTitle(e.target.value)}
                          onClick={(e) => e.stopPropagation()}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') saveRename(c.id);
                            if (e.key === 'Escape') cancelRename(e);
                          }}
                          className="bg-slate-950 border border-slate-750 text-white text-xs px-1.5 py-0.5 rounded w-full outline-none focus:border-blue-500 font-medium"
                          autoFocus
                        />
                      ) : (
                        <span className="truncate pr-4" title={c.title}>
                          {c.title}
                        </span>
                      )}
                    </div>

                    {/* Action buttons visible on hover / active */}
                    {!isEditing && (
                      <div className="absolute right-2 opacity-0 group-hover:opacity-100 flex items-center gap-1 transition-opacity">
                        <button
                          onClick={(e) => startEditing(c, e)}
                          className="p-1 hover:bg-slate-700 rounded text-slate-400 hover:text-white"
                          title="Rename Chat"
                        >
                          <Edit className="h-3 w-3" />
                        </button>

                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteChat(c.id);
                          }}
                          className="p-1 hover:bg-red-950 rounded text-slate-500 hover:text-red-400"
                          title="Delete Chat"
                        >
                          <Trash2 className="h-3 w-3" />
                        </button>
                      </div>
                    )}

                    {isEditing && (
                      <div className="flex items-center gap-1 shrink-0 ml-1 z-10">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            saveRename(c.id);
                          }}
                          className="p-1 hover:bg-slate-700 rounded text-green-400 hover:text-green-300"
                        >
                          <Check className="h-3 w-3" />
                        </button>
                        <button
                          onClick={cancelRename}
                          className="p-1 hover:bg-slate-700 rounded text-red-400 hover:text-red-350"
                        >
                          <X className="h-3 w-3" />
                        </button>
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </aside>

        {/* Column 2: Query Workspace (Center) */}
        <section className="flex-1 flex flex-col min-h-0 bg-slate-50/30">
          {/* Query Context / Scope Selector Header */}
          <div className="p-4 bg-white border-b border-slate-200 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 shrink-0 select-none">
            <div className="min-w-0 flex flex-col gap-1.5">
              <h3 className="text-xs font-extrabold text-slate-400 uppercase tracking-wider">
                Audit Query Workspace
              </h3>
              <div className="flex items-center gap-2">
                <span className="text-[10.5px] uppercase font-bold text-slate-405 select-none">Current Scope:</span>
                <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold border transition-all ${
                  selectedDocId 
                    ? 'bg-blue-50 text-blue-700 border-blue-100 shadow-2xs' 
                    : 'bg-slate-100 text-slate-700 border-slate-200'
                }`}>
                  {selectedDocId ? (
                    <>
                      <FileText className="h-3.5 w-3.5 shrink-0 text-blue-600" />
                      <span className="truncate" title={activeDocName}>{truncateFilename(activeDocName, 32)}</span>
                    </>
                  ) : (
                    <>
                      <Globe className="h-3.5 w-3.5 shrink-0 text-slate-500" />
                      <span>All Contracts (Corpus-wide)</span>
                    </>
                  )}
                </span>
              </div>
            </div>

            {/* Scope Control UI */}
            <div className="flex items-center gap-2 shrink-0">
              <div className="flex items-center gap-1.5 bg-slate-100 border border-slate-200 rounded-xl px-2.5 py-1.5">
                <ListFilter className="h-3.5 w-3.5 text-slate-500 shrink-0" />
                <span className="text-[11px] font-bold text-slate-600 uppercase select-none">Scope:</span>
                <select
                  value={selectedDocId}
                  onChange={(e) => {
                    if (activeChatId) {
                      handleUpdateScope(
                        activeChatId,
                        e.target.value ? 'document' : 'corpus',
                        e.target.value || null
                      );
                    }
                  }}
                  className="bg-transparent border-none text-[11px] font-bold text-slate-800 outline-none pr-1 max-w-[180px] truncate cursor-pointer"
                >
                  <option value="">All Contracts (Corpus-wide)</option>
                  {documents.map((doc) => (
                    <option key={doc.doc_id} value={doc.doc_id}>
                      {truncateFilename(doc.filename, 28)}
                    </option>
                  ))}
                </select>
              </div>

              {/* Toggle Document Panel Button */}
              <button
                onClick={() => setIsDocsOpen(!isDocsOpen)}
                className={`p-1.5 rounded-xl border transition-all flex items-center gap-1 cursor-pointer text-xs font-semibold ${
                  isDocsOpen 
                    ? 'border-blue-200 text-blue-700 bg-blue-50 hover:bg-blue-100/50' 
                    : 'border-slate-200 text-slate-500 hover:bg-slate-100'
                }`}
                title={isDocsOpen ? "Collapse Document Repository" : "Expand Document Repository"}
              >
                <Database className="h-3.5 w-3.5" />
                <span className="hidden md:inline select-none">Documents</span>
              </button>
            </div>
          </div>

          {/* Messages Scrolling Area */}
          {isLoadingMessages ? (
            <div className="flex-1 flex items-center justify-center bg-slate-50/20 text-slate-400 text-xs">
              Loading chat messages...
            </div>
          ) : (
            <ChatArea
              messages={messages}
              isQuerying={isQuerying}
              documents={documents}
              onSuggestionClick={askQuestion}
            />
          )}

          {/* Message Prompt Input Bar */}
          <InputBar
            onSend={askQuestion}
            disabled={isQuerying || isLoadingMessages}
            selectedDocId={selectedDocId}
            placeholder={
              selectedDocId 
                ? `Ask a question about this agreement...` 
                : 'Analyze agreements, retrieve evidence, and get citation-backed answers...'
            }
          />
        </section>

        {/* Column 3: Collapsible Documents Panel (280px width) */}
        {isDocsOpen && (
          <aside className="w-[280px] bg-white border-l border-slate-200 flex flex-col min-h-0 shrink-0">
            <div className="p-4 border-b border-slate-100 bg-slate-50/50 select-none flex items-center justify-between shrink-0">
              <div>
                <h2 className="text-xs font-extrabold text-slate-800 uppercase tracking-wider">
                  Documents
                </h2>
                <p className="text-[10px] text-slate-400 font-medium">
                  RAG source vector database.
                </p>
              </div>
              <span className="text-[10px] font-bold font-mono bg-slate-200 text-slate-700 px-2 py-0.5 rounded-full">
                {documents.length} File{documents.length !== 1 ? 's' : ''}
              </span>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              <DocumentsPanel
                documents={documents}
                uploadProgress={uploadProgress}
                onUpload={uploadDocument}
                onDeleteDoc={deleteDocument}
              />
            </div>
          </aside>
        )}
      </main>
    </div>
  );
};

export const App = () => {
  return (
    <AuthProvider>
      <Routes>
        {/* Public Login/Register Routes */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Protected Dashboard Route */}
        <Route element={<ProtectedRoute />}>
          <Route path="/" element={<DashboardLayout />} />
        </Route>

        {/* Catch-all Redirect */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <Toaster position="top-right" toastOptions={{ duration: 4000 }} />
    </AuthProvider>
  );
};


export default App;
