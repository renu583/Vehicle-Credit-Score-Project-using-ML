const API_BASE = "http://127.0.0.1:5000";

async function registerVehicle() {
  const vehicle_number = document.getElementById("vehicle_number").value;
  const owner_name = document.getElementById("owner_name").value;

  const res = await fetch(`${API_BASE}/register_vehicle`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ vehicle_number, owner_name }),
  });

  const data = await res.json();
  alert(data.message || "Registered!");
}

async function reportViolation() {
  const vehicle_number = document.getElementById("violation_vehicle").value;
  const violation_type = document.getElementById("violation_type").value;

  const res = await fetch(`${API_BASE}/report_violation`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ vehicle_number, violation_type }),
  });

  const data = await res.json();
  alert(data.message || "Violation reported!");
}

async function checkScore() {
  const vehicle_number = document.getElementById("score_vehicle").value;

  const res = await fetch(`${API_BASE}/predict_score/${vehicle_number}`);
  const data = await res.json();

  document.getElementById("score_result").innerText = `Credit Score: ${data.credit_score}`;
}
