import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { profileService } from '../../services/api';
import { ArrowLeft, Shield, Settings, Save, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';

export const SettingsPage = () => {
  const { user, updateUser } = useAuth();
  const navigate = useNavigate();

  const [isEditing, setIsEditing] = useState(false);
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = async () => {
    if (!fullName.trim()) {
      toast.error("Name cannot be empty");
      return;
    }
    
    setIsSaving(true);
    try {
      const updatedUser = await profileService.updateProfile({ full_name: fullName.trim() });
      updateUser({ full_name: updatedUser.full_name });
      toast.success("Profile updated successfully");
      setIsEditing(false);
    } catch (err) {
      console.error(err);
      toast.error("Failed to update profile");
    } finally {
      setIsSaving(false);
    }
  };

  // Extract initials
  const getInitials = (name) => {
    if (!name) return 'LA';
    return name
      .split(' ')
      .map((part) => part[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const formattedDate = user?.created_at
    ? new Date(user.created_at).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    : 'June 5, 2026';

  return (
    <div className="flex flex-col h-screen w-screen bg-slate-50 dark:bg-slate-950 font-sans overflow-y-auto">
      {/* Top Header */}
      <header className="h-14 bg-slate-900 border-b border-slate-800 flex items-center justify-between px-6 shrink-0 shadow-md">
        <button
          onClick={() => navigate('/chat')}
          className="flex items-center gap-2 text-xs font-bold text-slate-300 hover:text-white transition-all cursor-pointer"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back to Workspace</span>
        </button>

        <div className="flex items-center gap-2.5">
          <div className="h-8 w-8 rounded-lg bg-blue-650 flex items-center justify-center text-white shadow-lg">
            <Settings className="h-4.5 w-4.5" />
          </div>
          <h1 className="text-sm font-extrabold text-white tracking-wider uppercase">
            Platform Settings
          </h1>
        </div>
      </header>

      {/* Main Settings Form Panel */}
      <main className="flex-1 max-w-3xl w-full mx-auto p-6 md:p-8 space-y-8">
        
        {/* Profile Card Section */}
        <section className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm space-y-6">
          <div className="flex items-center gap-4 border-b border-slate-100 dark:border-slate-800 pb-4">
            <div className="h-14 w-14 rounded-full bg-blue-600 text-white flex items-center justify-center text-lg font-extrabold shadow-md uppercase">
              {getInitials(user?.full_name)}
            </div>
            <div className="flex-1">
              {isEditing ? (
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full max-w-sm px-3 py-1.5 text-base font-extrabold text-slate-800 dark:text-slate-100 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  placeholder="Enter your full name"
                />
              ) : (
                <h2 className="text-base font-extrabold text-slate-800 dark:text-slate-100">
                  {user?.full_name || 'System Analyst'}
                </h2>
              )}
              <p className="text-xs font-medium text-slate-400 font-mono mt-0.5">
                {user?.email || 'analyst@opendoc.ai'}
              </p>
            </div>
            <div>
              {isEditing ? (
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => {
                      setIsEditing(false);
                      setFullName(user?.full_name || '');
                    }}
                    className="px-3 py-1.5 text-xs font-bold text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"
                    disabled={isSaving}
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleSave}
                    disabled={isSaving}
                    className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors disabled:opacity-50"
                  >
                    {isSaving ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Save className="h-3.5 w-3.5" />}
                    Save
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => setIsEditing(true)}
                  className="px-3 py-1.5 text-xs font-bold text-blue-600 bg-blue-50 hover:bg-blue-100 dark:bg-blue-900/30 dark:hover:bg-blue-900/50 rounded-lg transition-colors"
                >
                  Edit Profile
                </button>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-1">
              <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-widest block">
                User Role
              </span>
              <p className="text-xs font-bold text-slate-700 dark:text-slate-300 flex items-center gap-1.5">
                <Shield className="h-3.5 w-3.5 text-blue-600 shrink-0" />
                <span>Standard User</span>
              </p>
            </div>

            <div className="space-y-1">
              <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-widest block">
                Member Since
              </span>
              <p className="text-xs font-mono font-bold text-slate-700 dark:text-slate-300">
                {formattedDate}
              </p>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
};

export default SettingsPage;
