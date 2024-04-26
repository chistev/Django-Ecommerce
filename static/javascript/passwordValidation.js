 function validatePassword() {
    var password = document.getElementById("Password1").value;
    var strengthText = document.getElementById("passwordStrength");
    var password2 = document.getElementById("Password2").value;
    var matchText = document.getElementById("passwordMatch");
    var progressBar = document.getElementById("passwordProgressBar");

    // Password strength check
    if (password.length < 8) {
        strengthText.innerHTML = "Weak";
        strengthText.style.color = "red";
        progressBar.style.width = "25%";
        progressBar.className = "progress-bar bg-danger";
    } else if (password.length < 16) {
        strengthText.innerHTML = "Good";
        strengthText.style.color = "orange";
        progressBar.style.width = "50%";
        progressBar.className = "progress-bar bg-warning";
    } else {
        strengthText.innerHTML = "Excellent";
        strengthText.style.color = "green";
        progressBar.style.width = "100%";
        progressBar.className = "progress-bar bg-success";
    }

    // Password match check
    if (password2.length > 1){
    matchText.innerHTML = "Both passwords must match"
    matchText.style.color = "red";
    }
    else {
        matchText.innerHTML = "";
    }
}

function validateForm() {
    var password = document.getElementById("Password1").value;

    if (password.length < 8) {
        alert("Password should be at least 8 characters long.");
        return false;
    }
    return true;
}


// Hook into input events to trigger validation
document.getElementById('Password1').addEventListener('input', validatePassword);
document.getElementById('Password2').addEventListener('input', validatePassword);