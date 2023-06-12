// installing crx
chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.set({
    textbook: "Think In Java",
  });
  console.log("欢迎使用LinkSO谷歌插件服务");
})

chrome.runtime.onMessage.addListener((request, sender) => {
  if (request.type == "GetSOInfo") {
    chrome.storage.local.set({ 
      qtitle: request.qtitle,
      qbody: request.qbody,
      qcodes: request.qcodes,
      abody: request.abody,
      acodes: request.acodes
    });
  }
});