function validatePassword() {
    var password = document.getElementById("Password1").value;
    var strengthText = document.getElementById("passwordStrength");
    var password2 = document.getElementById("Password2").value;
    var matchText = document.getElementById("passwordMatch");

    if (password.length < 8) {
        strengthText.innerHTML = "Weak";
        strengthText.style.color = "red";
    }
    else if (password.length < 16) {
        strengthText.innerHTML = "Good";
        strengthText.style.color = "orange";
    } 
    else if (password.length >= 16) {
        strengthText.innerHTML = "Excellent";
        strengthText.style.color = "green";
    } 
    else {
        strengthText.innerHTML = "";
    }
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