const DEBUG = false;

function crawl_content() {
  let tag_elements = document.querySelectorAll("#question > div.post-layout > div.postcell.post-layout--right > div.mt24.mb12 > div > div > a");
  let title_element = document.querySelector("#question-header > h1 > a");
  let question_elements = document.querySelectorAll("#question > div.post-layout > div.postcell.post-layout--right > div.s-prose.js-post-body > p");
  // document.querySelector("#question > div.post-layout > div.postcell.post-layout--right > div.s-prose.js-post-body > pre.lang-java.s-code-block > code")
  let qcode_elements = document.querySelectorAll("#question > div.post-layout > div.postcell.post-layout--right > div.s-prose.js-post-body > pre > code");
  let answer_elements = document.querySelectorAll("#answer-11227902 > div > div.answercell.post-layout--right > div.s-prose.js-post-body > *");
  let acode_elements = document.querySelectorAll("#answer-11227902 > div > div.answercell.post-layout--right > div.s-prose.js-post-body > pre > code");

  for (let tag of tag_elements) {
    if (tag.textContent == "java") {
      let qtitle = title_element.textContent;
      let qbodies = [];
      for (let qe of question_elements) {
        qbodies.push(qe.textContent);
      }
      let qbody = qbodies.join(" ");
      let qcodes = [];
      for (let qce of qcode_elements) {
        qcodes.push(qce.textContent);
      }
      let abodies = [];
      for (let ae of answer_elements) {
        abodies.push(ae.textContent);
      }
      let abody = abodies.join(" ");
      let acodes = [];
      for (let ace of acode_elements) {
        acodes.push(ace);
      }
      return {
        java_related: true, 
        qtitle: qtitle, 
        qbody: qbody, 
        qcodes: qcodes, 
        abody: abody, 
        acodes: acodes
      }
    }
  }
  return {
    java_related: false, 
    qtitle: "", 
    qbody: "", 
    qcodes: [], 
    abody: "", 
    acodes: []
  }
}

let obj = crawl_content()
if (obj.java_related) {
  
}

// listening for message
chrome.runtime.onMessage.addListener((request, sender) => {
  if (request.type === "UpdateRecommendContent") {
    if (DEBUG) {
      console.log("[trendingPageContent] receive message from extension: ", request);
    }
    recs = Array.from(request.content);
  }
});

chrome.runtime.sendMessage({
  info: "我是 content.js"
}, res => {
  // 答复
  alert(res)
});


function send_so_content(qtitle, qbody, abody, qcodes, acodes) {
  chrome.runtime.sendMessage({
    qtitle: qtitle,
    qbody: qbody,
    abody: abody,
    qcodes: qcodes,
    acodes: acodes
  }, (res) => {
    console.log("[CONTENT] succeed receiving response for sending SO content");
  })
}