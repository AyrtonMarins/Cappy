const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
  getActivities: () => ipcRenderer.invoke('get-activities'),
  addActivity: (activityData) => ipcRenderer.invoke('add-activity', activityData),
  getActivityDetails: (activityId) => ipcRenderer.invoke('get-activity-details', activityId),
  // --- NOVA LINHA PARA O CHAT ---
  processChatMessage: (message) => ipcRenderer.invoke('process-chat-message', message)
});