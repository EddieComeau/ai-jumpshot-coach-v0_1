const { contextBridge } = require("electron");

contextBridge.exposeInMainWorld("coachApp", {
  version: "0.1",
});
