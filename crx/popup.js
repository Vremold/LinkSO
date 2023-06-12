const SERVER_IP = "162.105.16.52"

let matched_chapters = [];
let matched_sections = [
  ["1.1", "1.2", "1.3"],
  ["2.1", "2.2", "2.3"],
  ["3.1", "3.2", "3.3"]
];

function update_recommended(chapters, sections, persistent) {
  matched_chapters = chapters;
  matched_sections = sections;
  // 模拟按下第一个按钮，即选择top1匹配的章节
  $("div.list-group button:nth-child(1)").text("1. " + chapters[0]);
  $("div.list-group button:nth-child(2)").text("2. " + chapters[1]);
  $("div.list-group button:nth-child(3)").text("3. " + chapters[2]);
  $("div.list-group button:nth-child(1)").click();
  
  if (persistent === true) {
    chrome.storage.local.set({
      matched_chapters: chapters,
      matched_sections: sections
    });
  }
}

console.log("[PUPOP] I'm running");

// button element listening
$(document).on("click", "button", function () {
  let bidx = parseInt($(this).data("idx"));

  $("button").removeClass("active");
  $(this).addClass("active");

  $("ol li:nth-child(1)").text("1. " + matched_sections[bidx - 1][0]);
  $("ol li:nth-child(2)").text("2. " + matched_sections[bidx - 1][1]);
  $("ol li:nth-child(3)").text("3. " + matched_sections[bidx - 1][2]);
});

// select element listening 
$(document).on("change", "select", function () {
  let selected_textbook = $(this).children('option:selected').val();
  chrome.storage.local.set({ textbook: selected_textbook });
});

$(document).ready(function () {

  // set textbook select option according to the storage
  chrome.storage.local.get(["textbook"], (result) => {
    if ($("select option:nth-child(2)").text() == result.textbook) {
      $("select option:nth-child(2)").attr("selected", true);
    }
    if ($("select option:nth-child(3)").text() == result.textbook) {
      $("select option:nth-child(3)").attr("selected", true);
    }
    if ($("select option:nth-child(4)").text() == result.textbook) {
      $("select option:nth-child(4)").attr("selected", true);
    }
  });


  // request for recommendation
  chrome.storage.local.get(["qtitle", "qbody", "qcodes", "abody", "acodes"], (result) => {
    // not crawl these information still
    // TODO
    if (false) {
      return;
    } else {
      // TODO:
      let selected_textbook = $("option:selected").val();
      url = "http://" + SERVER_IP + "/get_recommend/textbook=";
      fetch(url, {
        method: 'GET',
        headers: new Headers({
          "Accept": "application/json; charset=utf-8"
        })
      })
        .then((response) => {
          if (response.ok) {
            return response.json();
          }
          throw new Error("Request to", url, "failed")
        })
        .then((result) => {
          if (!result.success) {
            return;
          }
          update_recommended(result.chapters, result.sections)
        })
        .catch((error) => {
          console.log(error);
        })
    }
  })
});