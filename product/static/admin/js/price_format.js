// This script provides a user-friendly numeric input experience with real-time comma formatting while keeping the value backend-compatible on form submission

document.addEventListener("DOMContentLoaded", function () {
  const input = document.querySelector("#id_price");
  if (!input) return;

  input.type = "text"; // force text input

  input.addEventListener("keyup", function () {
    let raw = input.value.replace(/,/g, "");
    if (raw === "") return;

    const parts = raw.split(".");
    let intPart = parts[0];
    const decPart = parts[1] || "";

    intPart = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, ",");

    input.value = decPart ? `${intPart}.${decPart}` : intPart;
  });

  input.form.addEventListener("submit", function () {
    input.value = input.value.replace(/,/g, "");
  });
});
