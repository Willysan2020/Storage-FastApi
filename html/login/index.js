const login = document.getElementById("login");
const sign = document.getElementById("sign");

function change(element) {
  switch (element) {
    case "login":
      login.style.display = "flex";
      sign.style.display = "none";
      break;
    case "sign":
      sign.style.display = "flex";
      login.style.display = "none";
      break;
    default:
      break;
  }
}
