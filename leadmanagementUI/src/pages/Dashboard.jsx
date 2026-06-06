import { useEffect, useState } from "react";
import axios from "axios";

import Sidebar from "../components/Sidebar";
import ChatWindow from "../components/ChatWindow";
import DraftBox from "../components/DraftBox"; 

const API_BASE = "http://127.0.0.1:8000";

function Dashboard() {
  const [chats, setChats] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [messages, setMessages] = useState([]);
  const [draft, setDraft] = useState("");
  const [draftId, setDraftId] = useState(null);
  
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [windowWidth, setWindowWidth] = useState(
    typeof window !== "undefined" ? window.innerWidth : 1200
  );

  useEffect(() => {
    loadChats();
    const handleResize = () => setWindowWidth(window.innerWidth);
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const loadChats = async () => {
    try {
      const response = await axios.get(`${API_BASE}/chats`);
      setChats(response.data);
    } catch (error) {
      console.error("Error loading pipeline chats:", error);
    }
  };

  const openChat = async (userId) => {
    setSelectedUser(userId);
    setDraft(""); 
    setDraftId(null);

    try {
      const chatResponse = await axios.get(`${API_BASE}/chats/${userId}`);
      setMessages(chatResponse.data.messages);

      const draftResponse = await axios.get(`${API_BASE}/drafts/${userId}`);
      if (draftResponse.data) {
        setDraft(draftResponse.data.draft_text || "");
        setDraftId(draftResponse.data.draft_id || null);
      }
    } catch (error) {
      console.error("Error synchronizing conversational node metadata:", error);
      setDraft("");
      setDraftId(null);
    }
  };

  const sendMessage = async () => {
    if (!draft.trim()) return;
    try {
      await axios.post(`${API_BASE}/send`, {
        user_id: selectedUser,
        draft_id: draftId,
        message: draft
      });
      setDraft(""); 
      openChat(selectedUser);
    } catch (error) {
      console.error("Failed transmission routing dispatch:", error);
    }
  };

  const activeLead = chats.find(c => c.user_id === selectedUser);
  const isMobile = windowWidth < 768;

  const theme = {
    bg: isDarkMode ? "#0B141A" : "#F8FAFC", 
    canvasBg: isDarkMode ? "#0B141A" : "#FAFAFA",
    border: isDarkMode ? "#2F3B43" : "#E2E8F0",
    textPrimary: isDarkMode ? "#E9EDEF" : "#0F172A",
    textSecondary: isDarkMode ? "#8696A0" : "#64748B",
    rightPanelBg: isDarkMode ? "#111B21" : "#FFFFFF"
  };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: isMobile ? "column" : "row",
        height: "100vh",
        width: "100vw",
        maxHeight: "100vh",
        maxWidth: "100vw",
        backgroundColor: theme.bg,
        overflow: "hidden",
        margin: 0,
        padding: 0,
        boxSizing: "border-box",
        position: "fixed",
        top: 0,
        left: 0,
        fontFamily: "Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, sans-serif"
      }}
    >
      {/* COLUMN 1: PIPELINE SIDEBAR */}
      {(!isMobile || !selectedUser) && (
        <div style={{ width: isMobile ? "100%" : "360px", height: "100%", display: "flex", flexDirection: "column", flexShrink: 0 }}>
          <Sidebar chats={chats} onSelect={openChat} isDarkMode={isDarkMode} />
        </div>
      )}

      {/* COLUMN 2: CENTER CHAT WINDOW */}
{(!isMobile || selectedUser) && (
  <div style={{ flex: 1, display: "flex", flexDirection: "column", backgroundColor: theme.canvasBg, height: "100%", position: "relative", overflow: "hidden" }}>
    
    {/* Main Top Header Bar with Fixed Lead Details */}
    <div style={{ 
      height: "70px", // Expanded slightly from 60px to accommodate subtitles perfectly
      borderBottom: `1px solid ${theme.border}`, 
      backgroundColor: isDarkMode ? "#202C33" : "#F0F2F5", 
      display: "flex", 
      alignItems: "center", 
      justifyContent: "space-between", 
      padding: "0 16px", 
      boxSizing: "border-box", 
      zIndex: 10, 
      flexShrink: 0 
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
        {isMobile && selectedUser && (
          <button onClick={() => setSelectedUser(null)} style={{ backgroundColor: "transparent", border: "none", cursor: "pointer", padding: "8px 8px 8px 0px", color: isDarkMode ? "#00A884" : "#008069", fontSize: "14px", fontWeight: "600" }}>
            ← Back
          </button>
        )}
        {selectedUser ? (
          <div>
            {/* Lead Name */}
            <h4 style={{ margin: 0, fontSize: "15px", fontWeight: "600", color: theme.textPrimary }}>
              {activeLead ? (activeLead.name || activeLead.phone_number) : "Active Conversation"}
            </h4>
            
            {/* Metadata Subtitle Ribbon */}
            {activeLead && (
              <div style={{ display: "flex", alignItems: "center", gap: "12px", marginTop: "2px", fontSize: "12px", color: theme.textSecondary }}>
                <span>📞 {activeLead.phone_number || activeLead.phone || "No Phone"}</span>
                {(activeLead.email || activeLead.email_address) && (
                  <>
                    <span style={{ opacity: 0.4 }}>•</span>
                    <span>✉️ {activeLead.email || activeLead.email_address}</span>
                  </>
                )}
              </div>
            )}
          </div>
        ) : (
          <h4 style={{ margin: 0, fontSize: "15px", fontWeight: "600", color: theme.textSecondary }}>Select a Pipeline Lead</h4>
        )}
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
        <button onClick={() => setIsDarkMode(!isDarkMode)} style={{ background: "transparent", border: "none", cursor: "pointer", color: isDarkMode ? "#FFD700" : "#54656F", display: "flex", alignItems: "center", justifyContent: "center", padding: "6px" }}>
          {isDarkMode ? (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.22" x2="5.64" y2="17.78"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>
          ) : (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
          )}
        </button>
      </div>
    </div>

    {/* Chat Threads Content Frame */}
    <div style={{ flex: 1, overflowY: "auto", display: "flex", flexDirection: "column", minHeight: 0 }}>
      <ChatWindow messages={messages} isDarkMode={isDarkMode} activeLead={activeLead} />
    </div>
  </div>
)}

      {/* COLUMN 3: RIGHT PANEL (DRAFTBOX WORKSPACE PANEL) */}
     {/* COLUMN 3: RIGHT PANEL (FIXED FOR FULL VERTICAL STRETCH) */}
      {selectedUser && (!isMobile) && (
        <div
          style={{
            width: "420px",
            maxWidth: "420px",
            minWidth: "420px",
            height: "100vh",                  // Force container to match the app viewport height
            backgroundColor: theme.rightPanelBg,
            borderLeft: `1px solid ${theme.border}`,
            display: "flex",
            flexDirection: "column",         // Stack header and content vertically
            flexShrink: 0,
            boxSizing: "border-box"
          }}
        >
          {/* Panel Identifier Header Widget */}
          <div style={{
            height: "60px",
            padding: "0 16px",
            backgroundColor: isDarkMode ? "#202C33" : "#F0F2F5",
            borderBottom: `1px solid ${theme.border}`,
            display: "flex",
            alignItems: "center",
            boxSizing: "border-box",
            flexShrink: 0
          }}>
            <h3 style={{ margin: 0, fontSize: "14px", fontWeight: "600", color: theme.textPrimary, display: "flex", alignItems: "center", gap: "6px" }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#4F46E5" strokeWidth="2.5">
                <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/>
              </svg>
              AI Co-Pilot Console
            </h3>
          </div>

          {/* This wrapper layout handles pushing the inner components down */}
          <div style={{ flex: 1, display: "flex", flexDirection: "column", minHeight: 0 }}>
            <DraftBox draft={draft} setDraft={setDraft} onSend={sendMessage} isDarkMode={isDarkMode} />
          </div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;