import React, { useState } from "react";

function Sidebar({ chats, onSelect, isDarkMode }) {
  const [hoveredId, setHoveredId] = useState(null);
  const [activeId, setActiveId] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");

  // Clean HH:MM formatter
  const formatTime = (timeString) => {
    if (!timeString) return "";
    try {
      const timePart = timeString.split(" ")[1];
      if (timePart) {
        const [hours, minutes] = timePart.split(":");
        return `${hours}:${minutes}`;
      }
      return "";
    } catch (e) {
      return "";
    }
  };

  // Modern profile placeholders that adjust based on dark mode status
  const getAvatarStyle = (name, isActive) => {
    if (isActive) return { backgroundColor: "#00A884", color: "#FFFFFF" };
    const charCode = (name || "L").charCodeAt(0);
    const sets = [
      { bg: "linear-gradient(135deg, #FF9A8B 0%, #FF6A88 55%, #FF99AC 100%)", text: "#FFFFFF" },
      { bg: "linear-gradient(135deg, #6B11FF 0%, #A364FF 100%)", text: "#FFFFFF" },
      { bg: "linear-gradient(135deg, #E0C3FC 0%, #8EC5FC 100%)", text: "#1E293B" },
      { bg: "linear-gradient(135deg, #4158D0 0%, #C850C0 46%, #FFCC70 100%)", text: "#FFFFFF" },
      { bg: "linear-gradient(135deg, #0093E9 0%, #80D0C7 100%)", text: "#FFFFFF" }
    ];
    return {
      background: sets[charCode % sets.length].bg,
      color: sets[charCode % sets.length].text
    };
  };

  const filteredChats = chats.filter((chat) => {
    const searchTarget = `${chat.name || ""} ${chat.phone_number || ""}`.toLowerCase();
    return searchTarget.includes(searchQuery.toLowerCase());
  });

  // Dynamic Theme Styling Object
  const theme = {
    sidebarBg: isDarkMode ? "#111B21" : "#FFFFFF",
    headerBg: isDarkMode ? "#202C33" : "#F0F2F5",
    searchBg: isDarkMode ? "#111B21" : "#FFFFFF",
    inputBg: isDarkMode ? "#202C33" : "#F0F2F5",
    inputText: isDarkMode ? "#E9EDEF" : "#111B21",
    inputPlaceholder: isDarkMode ? "#8696A0" : "#667781",
    border: isDarkMode ? "#222E35" : "#E9EDEF",
    chatHoverBg: isDarkMode ? "#202C33" : "#F5F6F6",
    chatActiveBg: isDarkMode ? "#2A3942" : "#F0F2F5",
    textPrimary: isDarkMode ? "#E9EDEF" : "#111B21",
    textSecondary: isDarkMode ? "#8696A0" : "#667781",
    iconColor: isDarkMode ? "#AEBAC1" : "#54656F"
  };

  return (
    <div
      style={{
        width: "360px",
        maxWidth: "360px",
        minWidth: "360px",
        borderRight: `1px solid ${theme.border}`,
        backgroundColor: theme.sidebarBg,
        height: "100%",
        display: "flex",
        flexDirection: "column",
        boxSizing: "border-box",
        fontFamily: "Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, sans-serif",
        overflow: "hidden"
      }}
    >
      {/* 1. Dynamic Header Segment */}
      <div
        style={{
          height: "60px",
          padding: "10px 16px",
          backgroundColor: theme.headerBg,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          boxSizing: "border-box",
          flexShrink: 0
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <h2 style={{ margin: 0, fontSize: "16px", fontWeight: "700", color: theme.textPrimary }}>
            Leads
          </h2>
          <span style={{
            fontSize: "12px",
            fontWeight: "600",
            backgroundColor: "#00A884",
            color: "#FFFFFF",
            padding: "2px 8px",
            borderRadius: "12px",
            lineHeight: "1"
          }}>
            {chats.length}
          </span>
        </div>
        <div style={{ display: "flex", gap: "20px", color: theme.iconColor }}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ cursor: "pointer" }}><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ cursor: "pointer" }}><circle cx="12" cy="12" r="1"/><circle cx="12" cy="5" r="1"/><circle cx="12" cy="19" r="1"/></svg>
        </div>
      </div>

      {/* 2. Dynamic Search Strip */}
      <div
        style={{
          padding: "7px 12px",
          backgroundColor: theme.searchBg,
          borderBottom: `1px solid ${theme.border}`,
          display: "flex",
          alignItems: "center",
          boxSizing: "border-box",
          flexShrink: 0
        }}
      >
        <div style={{ position: "relative", width: "100%" }}>
          <input 
            type="text" 
            placeholder="Search or start new chat"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: "100%",
              boxSizing: "border-box",
              padding: "7px 12px 7px 42px",
              fontSize: "14px",
              borderRadius: "8px",
              border: "none",
              backgroundColor: theme.inputBg,
              color: theme.inputText,
              outline: "none"
            }}
          />
          {/* Inject style overlay to make placeholder look natural */}
          <style>{`
            input::placeholder { color: ${theme.inputPlaceholder} !important; }
          `}</style>
          <div style={{ position: "absolute", left: "14px", top: "8px", color: theme.inputPlaceholder, display: "flex", alignItems: "center" }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          </div>
        </div>
      </div>

      {/* 3. Main Dynamic Thread Feed Area */}
      <div style={{ flex: 1, overflowY: "auto", overflowX: "hidden", backgroundColor: theme.sidebarBg }}>
        {filteredChats.map((chat) => {
          const isHovered = hoveredId === chat.user_id;
          const isActive = activeId === chat.user_id;
          
          const leadName = chat.name || chat.phone_number || "Lead";
          const initial = leadName.charAt(0).toUpperCase();
          const avatarStyle = getAvatarStyle(leadName, isActive);

          return (
            <div
              key={chat.user_id}
              onClick={() => {
                setActiveId(chat.user_id);
                onSelect(chat.user_id);
              }}
              onMouseEnter={() => setHoveredId(chat.user_id)}
              onMouseLeave={() => setHoveredId(null)}
              style={{
                height: "74px",
                padding: "0 16px",
                cursor: "pointer",
                backgroundColor: isActive ? theme.chatActiveBg : isHovered ? theme.chatHoverBg : "transparent",
                display: "flex",
                alignItems: "center",
                boxSizing: "border-box",
                transition: "background-color 0.1s ease",
                width: "100%"
              }}
            >
              {/* Avatar Frame */}
              <div
                style={{
                  width: "49px",
                  height: "49px",
                  borderRadius: "50%",
                  background: avatarStyle.background || avatarStyle.backgroundColor,
                  color: avatarStyle.color,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "16px",
                  fontWeight: "600",
                  flexShrink: 0
                }}
              >
                {initial}
              </div>

              {/* Grid Content Blocks */}
              <div 
                style={{ 
                  flex: 1, 
                  minWidth: 0,
                  height: "100%",
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "center",
                  marginLeft: "14px",
                  borderBottom: isActive || isHovered ? "1px solid transparent" : `1px solid ${theme.border}`,
                  boxSizing: "border-box"
                }}
              >
                {/* ROW 1: Contact Title */}
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    width: "100%"
                  }}
                >
                  <span
                    style={{
                      fontSize: "16px",
                      fontWeight: "400",
                      color: theme.textPrimary,
                      whiteSpace: "nowrap",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      flex: 1,
                      paddingRight: "8px"
                    }}
                  >
                    {leadName}
                  </span>
                  
                  <span style={{ 
                    fontSize: "12px", 
                    color: "#00A884", 
                    flexShrink: 0, 
                    fontWeight: "600",
                    whiteSpace: "nowrap"
                  }}>
                    Active
                  </span>
                </div>

                {/* ROW 2: Snippet & Sorted Timestamp */}
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    width: "100%",
                    marginTop: "2px"
                  }}
                >
                  <span
                    style={{
                      color: theme.textSecondary,
                      fontSize: "14px",
                      whiteSpace: "nowrap",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      flex: 1,
                      paddingRight: "8px"
                    }}
                  >
                    {chat.latest_message || <span style={{ fontStyle: "italic", color: theme.textSecondary }}>No messages yet</span>}
                  </span>

                  <span
                    style={{
                      fontSize: "12px",
                      color: theme.textSecondary,
                      flexShrink: 0,
                      fontWeight: "400",
                      whiteSpace: "nowrap"
                    }}
                  >
                    {formatTime(chat.latest_message_time)}
                  </span>
                </div>

              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default Sidebar;