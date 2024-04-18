async function passwordChange() {
    const { value: password, isConfirmed } = await Swal.fire({
        input: "password",
        inputLabel: "Input New Password",
        inputPlaceholder: "Enter your password",
        inputAttributes: {
            autocorrect: "off"
        },
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "Confirm",
        cancelButtonText: "Cancel",
        closeOnCancel: false
    });

    if (isConfirmed) {
        axios.post('/changepassword', {
            password: password
        }).then(function (result) {
            console.log(result);
            document.querySelector('#userpasswordText').textContent = password
            Swal.fire({
                text: "Password successfully changed",
                icon: "success"
            });
        }).catch(function (error) {
            console.log(error.response.data);
        });
    } else {

    }
}