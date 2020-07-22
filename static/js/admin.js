// AJAX server request - check if is admin
var xhttp = new XMLHttpRequest();
xhttp.onreadystatechange = function(){

    // Valid response
    if(this.readyState==4 && this.status==200){
        if(this.responseText === "SECURITY BREACH")
            window.location.replace("/");    
    }

}
xhttp.open("POST", "/admin_sec_check", true);
xhttp.setRequestHeader('content-type',
    'application/x-www-form-urlencoded;charset=UTF-8');
xhttp.send();