function toggleBasicDetails() {
    var basicDetails = document.getElementById("basicDetails");
    var arrowIcon = document.getElementById("basicDetailsArrowIcon");

    if (basicDetails.style.display === "none") {
        basicDetails.style.display = "block";
        arrowIcon.classList.remove("bi-arrow-right");
        arrowIcon.classList.add("bi-arrow-up");
    } else {
        basicDetails.style.display = "none";
        arrowIcon.classList.remove("bi-arrow-up");
        arrowIcon.classList.add("bi-arrow-right");
    }
}

function toggleChangePassword() {
    var changePassword = document.getElementById("changePassword");
    var arrowIcon = document.getElementById("changePasswordArrowIcon");

    if (changePassword.style.display === "none") {
        changePassword.style.display = "block";
        arrowIcon.classList.remove("bi-arrow-right");
        arrowIcon.classList.add("bi-arrow-up");
    } else {
        changePassword.style.display = "none";
        arrowIcon.classList.remove("bi-arrow-up");
        arrowIcon.classList.add("bi-arrow-right");
    }
}
