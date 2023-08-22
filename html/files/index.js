const files = document.getElementById("files");
const embed = document.getElementById("embed");
const filebuttonclose = document.getElementById("fileclose");
const filebuttonhide = document.getElementById("fileshide");
const but1 = document.getElementById("buttonback");
const but2 = document.getElementById("buttonnext");
const buton1 =
  '<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 0 24 24" width="24px" fill="#000000"><path d="M0 0h24v24H0V0z" fill="none"/><path d="M12 8c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z"/></svg>';
let numpages;
let listpages = "";
let totalpages;
function fileclick() {
  event.preventDefault();
  let type = "embed";
  switch (event.currentTarget.type.split("/")[0]) {
    case "video":
      type = "video";
      break;
    case "image":
      type = "img";
      break;
    default:
      type = "embed";
      break;
  }
  document.getElementById("display").remove();
  embed.innerHTML =
    "<" + type + ' id="display" width="100%" controls autoplay></' + type + ">";
  document.getElementById("display").type = event.currentTarget.type;
  document.getElementById("display").src = event.currentTarget.href;
  files.style = "width: 20%";
  embed.style = "display: flex;";
  filebuttonclose.style = "display: inline-block;";
  filebuttonhide.style = "display: inline-block;";
  but1.name = parseInt(event.currentTarget.id) - 1;
  but2.name = parseInt(event.currentTarget.id) + 1;
  but1.style = "display: inline-block;";
  but2.style = "display: inline-block;";
}

function nextfile(id) {
  switch (id) {
    case "-1":
      if (_("selectpage").title.split("/")[0] != "1") {
        refreshui(parseInt(_("selectpage").title.split("/")[0]) - 1);
        but1.name = parseInt(numpages) - 1;
        but2.name = numpages;
        setTimeout(() => {
          nextfile(parseInt(numpages) - 1);
        }, 500);
      }
      break;
    case `${numpages}`:
      if (
        _("selectpage").title.split("/")[0] !=
        _("selectpage").title.split("/")[1]
      ) {
        refreshui(parseInt(_("selectpage").title.split("/")[0]) + 1);
        but1.name = -1;
        but2.name = 0;
        setTimeout(() => {
          nextfile(0);
        }, 500);
      }
      break;
    default:
      but1.name = parseInt(id) - 1;
      but2.name = parseInt(id) + 1;
      break;
  }
  let file = document.getElementById(id);
  let type = "embed";
  switch (file.type.split("/")[0]) {
    case "video":
      type = "video";
      break;
    case "image":
      type = "img";
      break;
    default:
      type = "embed";
      break;
  }
  document.getElementById("display").remove();
  embed.innerHTML =
    "<" + type + ' id="display" width="100%" controls autoplay></' + type + ">";
  document.getElementById("display").type = file.type;
  document.getElementById("display").src = file.href;
  //files.style = "width: 20%";
  embed.style = "display: flex;";
  filebuttonclose.style = "display: inline-block;";
  filebuttonhide.style = "display: inline-block;";
}

function pages(e) {
  const xmlhttp = new XMLHttpRequest();
  xmlhttp.onload = function () {
    let myArr = JSON.parse(this.responseText);
    numpages = myArr.pagelimit;
    totalpages = myArr.pages;
    listpages += `<button>Server: ${bytes(myArr.size)} Files: ${
      myArr.files
    }</button>`;
    for (let i = 1; i <= myArr.pages; i++) {
      listpages += `<button onclick="refreshui(${i})" id="page/${i}">${i}</button>`;
    }
    _("selectpage").innerHTML = listpages;
    if (e !== undefined) {
      _("selectpage").title = e + "/" + myArr.pages;
    } else {
      _("selectpage").title = "n/" + myArr.pages;
    }
  };
  xmlhttp.open("GET", "/../user/pages", true);
  if (listpages === "") {
    xmlhttp.send();
  } else {
    _("selectpage").innerHTML = listpages;
    if (e !== undefined) {
      _("selectpage").title = e + "/" + totalpages;
      _(`page/${e}`).style = "color: blue;";
    } else {
      _("selectpage").title = "n/" + totalpages;
    }
  }
}

function refreshui(e) {
  let inner = `<div class="navsett" id="selectpage"></div>`;
  let temp;
  files.innerHTML = inner;
  pages(e);

  const xmlhttp = new XMLHttpRequest();
  xmlhttp.onload = function () {
    let myArr = JSON.parse(this.responseText);
    for (let i = 0; i < Object.keys(myArr).length; i++) {
      temp = myArr[i];
      let thumbnail =
        '<img type="image/svg" width="140px" src="' +
        temp.filetype.split("/")[0] +
        '.svg"><br>';
      if (temp.filetype.split("/")[1] === "pdf") {
        thumbnail = `
      <img type="image/svg" width="140px" src="pdf.svg"><br>
      `;
      }
      if (temp.filetype.split("/")[0] === "image") {
        thumbnail =
          '<img width="140px" src="/../file/' +
          temp.filetype +
          "/" +
          temp.filename +
          '/" type="' +
          temp.filetype +
          '" ><br>';
      }
      inner = `
    <div class='container'>
    <a id="${i}" onclick=fileclick() href="/../file/${temp.filetype}/${temp.filename}/" type="${temp.filetype}">
    ${thumbnail}
    ${temp.filename}
    </a>
    <div class='settingscontainer'>
    <button class='settings'>
    ${buton1}
    </button>
    <button class='deletefile' onclick=deletefile(this.value) value='${temp.filetype}/${temp.filename}'>
    Delete
    </button>
    <button class='deletefile'><a href="/../file/${temp.filetype}/${temp.filename}/" type="${temp.filetype}" download>Download</a></button>
    </div>
    </div>
      `;

      files.innerHTML += inner;
    }
  };
  if (e === undefined) {
    xmlhttp.open("GET", "/../user/files", true);
  } else {
    xmlhttp.open("GET", `/../user/files?page=${e}`, true);
  }
  xmlhttp.send();
}
refreshui(1);

function filesclose() {
  embed.style = "display: none";
  files.style = "width: 100%";
  filebuttonclose.style = "display: none";
  filebuttonhide.style = "display: none;";
  document.getElementById("display").remove();
  embed.innerHTML = '<embed id="display">';
  but1.style = "display: none;";
  but2.style = "display: none;";
  _("bar").style = "display: flex;";
  _("body").style = "height: 90%";
}

function _(el) {
  return document.getElementById(el);
}

function fileshide() {
  if (files.style.width == "20%") {
    files.style = "width: 0%";
    _("bar").style = "display: none";
    _("body").style = "height: 100%";
  } else {
    files.style = "width: 20%";
    _("bar").style = "display: flex;";
    _("body").style = "height: 90%";
  }
}

function deletefile(file) {
  let del = new XMLHttpRequest();
  del.open("DELETE", "http://192.168.2.100:8000/file/" + file + "/");
  del.send();
  listpages = "";
  refreshui(1);
}

function settings() {}

let dn;
function uploadFile() {
  // alert(file.name+" | "+file.size+" | "+file.type);
  //let file = _("file1").files;
  dn = Date.now();
  var formdata = new FormData();
  for (let i = 0; i < _("file1").files.length; i++) {
    formdata.append("listfile", _("file1").files[i]);
  }
  var ajax = new XMLHttpRequest();
  ajax.upload.addEventListener("progress", progressHandler, false);
  ajax.addEventListener("load", completeHandler, false);
  ajax.addEventListener("error", errorHandler, false);
  ajax.addEventListener("abort", abortHandler, false);
  ajax.open("POST", "./../multifile");
  ajax.send(formdata);
}
let lastbyte = 0;
function progressHandler(event) {
  let dns = parseFloat((Date.now() - dn) / 1000);
  let lb = event.loaded - lastbyte;
  let speed = parseInt(lb / dns);
  lastbyte = event.loaded;
  dn = Date.now();
  _("progres").style.display = "inline-block";
  _("loaded_n_total").innerHTML =
    "Uploaded " +
    bytes(event.loaded) +
    " of " +
    bytes(event.total) +
    " " +
    bytes(speed) +
    "ps";
  var percent = (event.loaded / event.total) * 100;
  _("progressBar").value = Math.round(percent);
  _("status").innerHTML = Math.round(percent) + "% uploaded... please wait";
}

function completeHandler(event) {
  if (event.target.status === 200) {
    _("status").innerHTML = "";
    //_("link").innerHTML = event.target.responseText;
    //_("link").href = event.target.responseText;
    //_("progressBar").value = 0; //wil clear progress bar after successful upload
    setTimeout(function () {
      _("progres").style.display = "none";
      listpages = "";
      refreshui(1);
    }, 2000);
    lastbyte = 0;
  } else {
    _("status").innerHTML = event.target.responseText;
    //_("progressBar").value = 0;
    setTimeout(() => {
      _("progressBar").value = 0;
      _("progres").style.display = "none";
    }, 10000);
    lastbyte = 0;
  }
}

function errorHandler(event) {
  _("status").innerHTML = "Upload Failed";
}

function abortHandler(event) {
  _("status").innerHTML = "Upload Aborted";
}

function bytes(bytes) {
  if (bytes >= 1024) {
    if (bytes >= 1024 ** 2) {
      if (bytes >= 1024 ** 3) {
        return `${parseFloat(bytes / 1024 ** 3).toFixed(3)} GB`;
      } else {
        return `${parseInt(bytes / 1024 ** 2)} MB`;
      }
    } else {
      return `${parseInt(bytes / 1024)} KB`;
    }
  } else {
    return `${bytes} B`;
  }
}
