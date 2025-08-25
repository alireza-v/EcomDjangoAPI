// This script provides a user-friendly numeric input experience with real-time comma formatting while keeping the value backend-compatible on form submission

document.addEventListener("DOMContentLoaded", function () {
  const input = document.querySelector("#id_price");
  if (!input) return;


  input.setAttribute("type", "text");


  input.form.addEventListener("submit", function () {
    input.value = input.value.replace(/,/g, "");
  });

  input.addEventListener("input", function () {
    const raw = input.value.replace(/,/g, "");

    // Allow only numbers and optional decimal part
    if (!/^(\d*)(\.\d{0,2})?$/.test(raw)) return;

    const parts = raw.split(".");
    let intPart = parts[0];
    let decPart = parts[1] || "";

    // Format integer part
    intPart = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, ",");


    input.value = decPart.length > 0 ? `${intPart}.${decPart}` : intPart;


  });
});
