// Client listeners
var clientList = document.getElementById("client_list");
clientList.addEventListener("change", client_endpoint);
clientList.addEventListener("change", function(){graph_endpoint("2~3", "3~4");});
clientList.addEventListener("change", get_notes);
clientList.addEventListener("change", get_transactions);
clientList.addEventListener("change", stock_endpoint);

// Stock listeners
var stockList = document.getElementById("stock_list");
stockList.addEventListener("change", stock_endpoint);

// Watchlist listeners
var toggle = document.getElementById("cardToggle");
toggle.addEventListener("click", watchlist_endpoint);

// Transaction stock listener
var transacStock = document.getElementById("transac_stock");
transacStock.addEventListener("change", transac_stock_price);

// Listeners for top movers
document.getElementById("ms_p1").addEventListener("click", top_3_click);
document.getElementById("ms_p2").addEventListener("click", top_3_click);
document.getElementById("ms_p3").addEventListener("click", top_3_click);
document.getElementById("ms_m1").addEventListener("click", top_3_click);
document.getElementById("ms_m2").addEventListener("click", top_3_click);
document.getElementById("ms_m3").addEventListener("click", top_3_click);
function top_3_click(event){
    content = event.target.innerHTML;
    if(content != '-'){
        stock = content.split(":")[0];
        var stockList = document.getElementById("stock_list");
        stockList.value = stock;
        stockList.dispatchEvent(new Event('change'));
    }
}

// Listener for transaction cost
document.getElementById("transac_quantity").addEventListener("keyup", update_transac_cost);
document.getElementById("transac_price").addEventListener("keyup", update_transac_cost);
document.getElementById("transac_note").addEventListener("keyup", update_transac_cost);
function update_transac_cost(event){
    document.getElementById("transac_resp").innerHTML = "";
    var price = document.getElementById("transac_price").value;
    var quant = document.getElementById("transac_quantity").value;
    if(price == '')
        price = 0;
    if(quant == '')
        quant = 0;
    var cost = (quant * price).toFixed(2);
    document.getElementById("transac_cost").innerHTML = "$" + cost;
}

// Setup notes listener
var noteInput = document.getElementById("current_note");
var noteTimeout;
noteInput.addEventListener("keydown", noteDelay);
function noteDelay(){
    clearTimeout(noteTimeout);
    noteTimeout = setTimeout(save_note, 1500);
    document.getElementById("saved").innerHTML = "";
}

// Fire initial change events
window.onload = function(){
    var startup = new Event('change');
    clientList.dispatchEvent(startup);
    stockList.dispatchEvent(startup);
    transacStock.dispatchEvent(startup);
    ai_dist_endpoint(startup);
    graph_endpoint("2~3", "3~4");
}

// Filter transactions
function transacFilter(){

    // Get search term + transactions
    var search = document.getElementById("transac_filter").value.toLowerCase();
    var transactions = document.getElementById("transactions-container").children;

    // Iterate and filter by search term
    for(var i = 0; i < transactions.length; i++){
        var current = transactions[i];
        var heading = current.firstChild.firstChild.firstChild.firstChild.firstChild.innerHTML.toLowerCase();
        if(heading.indexOf(search) > -1)
            current.style.display = "";
        else
            current.style.display = "none";
    }

}

// Get current price for tramsaction
function transac_stock_price(event){

    // Create param string
    var stockList = document.getElementById("transac_stock");
    var stock = stockList.options[stockList.selectedIndex].value;
    var param = "stock=" + stock;

    // AJAX server request
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function(){

        // Valid response
        if(this.readyState==4 && this.status==200){

            // Security check
            if(this.responseText === "SECURITY BREACH"){
                window.location.replace("/");
                return;
            }

            document.getElementById("transac_price").value = this.responseText;

        }

    }
    xhttp.open("POST", "/stock_price", true);
    xhttp.setRequestHeader('content-type',
        'application/x-www-form-urlencoded;charset=UTF-8');
    xhttp.send(param);
}

// Add new transaction
function new_transac(){

    // Get inputs
    var clientList = document.getElementById("client_list");
    var client = clientList.options[clientList.selectedIndex].value;
    var action = "S"
    if(document.getElementById("transac_buy").checked)
        action = "B";
    var stockList = document.getElementById("transac_stock");
    var stock = stockList.options[stockList.selectedIndex].value;
    var quantity = document.getElementById("transac_quantity").value;
    var price = document.getElementById("transac_price").value;
    var note = document.getElementById("transac_note").value;

    var param = "client=" + client + "&action=" + action + "&stock=" + stock
        + "&quantity=" + quantity + "&price=" + price + "&note=" + note;

    // Output
    var errorMsg = document.getElementById("transac_resp")

    // AJAX server request
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function(){

        // Valid response
        if(this.readyState==4 && this.status==200){

            // Security check
            if(this.responseText === "SECURITY BREACH"){
                window.location.replace("/");
            }

            var resp = JSON.parse(this.responseText);
            if(resp['status'] === "SUCCESS"){
                errorMsg.innerHTML = "Transaction Successful";
                errorMsg.style.color = "green";
                get_transactions(null);
                graph_endpoint("-", "-");
                if(document.getElementById("client").classList.contains("active"))
                    client_endpoint(null);
                else{
                    document.getElementById("update_princ_cur").innerHTML = resp['new_princ']
                    $("a[href='#client']").one('shown.bs.tab', client_endpoint);
                }
                document.getElementById("transac_quantity").value = 0;
                document.getElementById("transac_note").value = "";
                transac_stock_price(null);
            }
            else{
                errorMsg.innerHTML = resp['msg'];
                errorMsg.style.color = "red";
            }

        }

    }
    xhttp.open("POST", "/new_transac", true);
    xhttp.setRequestHeader('content-type',
        'application/x-www-form-urlencoded;charset=UTF-8');
    xhttp.send(param);

}

// Add new transaction
function update_principal(){

    // Get inputs
    var clientList = document.getElementById("client_list");
    var client = clientList.options[clientList.selectedIndex].value;
    var action = "D"
    if(document.getElementById("update_princ_withdrawal").checked)
        action = "W";
    var quantity = document.getElementById("update_princ_quant").value;

    var param = "client=" + client + "&action=" + action + "&quantity=" + quantity

    // AJAX server request
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function(){

        // Valid response
        if(this.readyState==4 && this.status==200){

            // Security check
            if(this.responseText === "SECURITY BREACH"){
                window.location.replace("/");
            }

            // Change principal points and reset form
            document.getElementById("client_principal").innerHTML = this.responseText;
            document.getElementById("update_princ_cur").innerHTML = this.responseText;
            document.getElementById("update_princ_quant").value = 0;

        }

    }
    xhttp.open("POST", "/update_principal", true);
    xhttp.setRequestHeader('content-type',
        'application/x-www-form-urlencoded;charset=UTF-8');
    xhttp.send(param);

}

// Get transactions for current client
function get_transactions(event){

    // Get inputs
    var clientList = document.getElementById("client_list");
    var client = clientList.options[clientList.selectedIndex].value;
    var param = "client=" + client;

    // Get output objects
    var transacContainer = document.getElementById("transactions-container");

    // AJAX server request
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function(){

        // Valid response
        if(this.readyState==4 && this.status==200){

            // Security check
            if(this.responseText === "SECURITY BREACH"){
                window.location.replace("/");
                return;
            }

            // Get response
            var resp = JSON.parse(this.responseText);

            // Delete all existing transactions
            while (transacContainer.firstChild)
                transacContainer.removeChild(transacContainer.firstChild);

            // Add all
            for(var i = 0; i < resp.length; i++){

                cur = resp[i]
                curHeader = cur['time'] + " - " + cur['action'] + " " + cur['stock'] + " - " + cur['cost'];
                var prevDiv;
                var div;

                // Add top div
                var topDiv = document.createElement("div");
                topDiv.classList.add("panel-group");
                transacContainer.appendChild(topDiv);

                // Add heading divs
                div = document.createElement("div");
                div.classList.add("panel");
                div.classList.add("panel-default");
                topDiv.appendChild(div);
                prevDiv = div;
                div = document.createElement("div");
                div.classList.add("panel-heading");
                prevDiv.appendChild(div);
                prevDiv = div;
                div = document.createElement("h4");
                div.classList.add("panel-title");
                prevDiv.appendChild(div);
                prevDiv = div;
                div = document.createElement("a");
                div.classList.add("accordion-toggle");
                div.setAttribute("data-toggle", "collapse");
                div.setAttribute("data-parent", "#accordion");
                div.href = "#collapseTransac" + i;
                prevDiv.appendChild(div);
                prevDiv = div;
                div = document.createElement("span");
                div.id = "transac_header";
                div.innerHTML = curHeader;
                prevDiv.appendChild(div);

                // Add contents divs
                div = document.createElement("div");
                div.id = "collapseTransac" + i;
                div.classList.add("panel-collapse");
                div.classList.add("collapse");
                topDiv.appendChild(div);
                prevDiv = div;
                div = document.createElement("div");
                div.classList.add("panel-body");
                prevDiv.appendChild(div);
                prevDiv = div;
                div = document.createElement("div");
                div.innerHTML = cur['action'] + " Price: " + cur['price'];
                prevDiv.appendChild(div);
                div = document.createElement("div");
                div.innerHTML = "Current Price: " + cur['current_price'];
                prevDiv.appendChild(div);
                div = document.createElement("div");
                div.innerHTML = "Price Change: " + cur['price_change'];
                prevDiv.appendChild(div);
                div = document.createElement("div");
                div.innerHTML = "Quantity: " + cur['quantity'];
                prevDiv.appendChild(div);
                div = document.createElement("div");
                div.innerHTML = "Value: " + cur['cost'];
                prevDiv.appendChild(div);
                if(cur['note'] != ''){
                    div = document.createElement("div");
                    div.innerHTML = "Note: " + cur['note']
                    prevDiv.appendChild(div);
                }

            }

        }

    }
    xhttp.open("POST", "/get_transac", true);
    xhttp.setRequestHeader('content-type',
        'application/x-www-form-urlencoded;charset=UTF-8');
    xhttp.send(param);

}

// Save changes to current note
function save_note(event){

    // Get inputs
    var clientList = document.getElementById("client_list");
    var client = clientList.options[clientList.selectedIndex].value;
    var noteInput = document.getElementById("current_note");
    var note = noteInput.value
    var param = "client=" + client + "&note=" + note;

    // AJAX server request
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function(){

        // Valid response
        if(this.readyState==4 && this.status==200){

            // Security check
            if(this.responseText === "SECURITY BREACH"){
                window.location.replace("/");
                return;
            }
            document.getElementById("saved").innerHTML = "Saved";

        }

    }
    xhttp.open("POST", "/save_note", true);
    xhttp.setRequestHeader('content-type',
        'application/x-www-form-urlencoded;charset=UTF-8');
    xhttp.send(param);

}

// Get current notes
function get_notes(event){

    // Get inputs
    var clientList = document.getElementById("client_list");
    var client = clientList.options[clientList.selectedIndex].value;
    var param = "client=" + client;

    // Get output objects
    var currentNote = document.getElementById("current_note");
    var noteContainer = document.getElementById("notes-container");

    // AJAX server request
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function(){

        // Valid response
        if(this.readyState==4 && this.status==200){

            // Security check
            if(this.responseText === "SECURITY BREACH"){
                window.location.replace("/");
                return;
            }

            // Get response and set current note
            var resp = JSON.parse(this.responseText);
            currentNote.value = resp["current"];
            document.getElementById("saved").innerHTML = "";

            // Delete all existing notes
            while (noteContainer.firstChild)
                noteContainer.removeChild(noteContainer.firstChild);

            // Add all new
            saved = resp["saved"];
            for(var i = 0; i < saved.length; i++){

                curDate = saved[i]['note_time'];
                curNote = saved[i]['notes'];
                var prevDiv;
                var div;

                // Add top div
                var topDiv = document.createElement("div");
                topDiv.classList.add("panel-group");
                noteContainer.appendChild(topDiv);

                // Add heading divs
                div = document.createElement("div");
                div.classList.add("panel");
                div.classList.add("panel-default");
                topDiv.appendChild(div);
                prevDiv = div;
                div = document.createElement("div");
                div.classList.add("panel-heading");
                prevDiv.appendChild(div);
                prevDiv = div;
                div = document.createElement("h4");
                div.classList.add("panel-title");
                prevDiv.appendChild(div);
                prevDiv = div;
                div = document.createElement("a");
                div.classList.add("accordion-toggle");
                div.setAttribute("data-toggle", "collapse");
                div.setAttribute("data-parent", "#accordion");
                div.href = "#collapse" + i;
                prevDiv.appendChild(div);
                prevDiv = div;
                div = document.createElement("span");
                div.id = "note_date";
                div.innerHTML = curDate;
                prevDiv.appendChild(div);

                // Add contents divs
                div = document.createElement("div");
                div.id = "collapse" + i;
                div.classList.add("panel-collapse");
                div.classList.add("collapse");
                topDiv.appendChild(div);
                prevDiv = div;
                div = document.createElement("div");
                div.classList.add("panel-body");
                prevDiv.appendChild(div);
                prevDiv = div;
                div = document.createElement("span");
                div.id = "note";
                div.innerHTML = curNote;
                prevDiv.appendChild(div);

            }

        }

    }
    xhttp.open("POST", "/notes", true);
    xhttp.setRequestHeader('content-type',
        'application/x-www-form-urlencoded;charset=UTF-8');
    xhttp.send(param);

}

// Get list of clients
function client_endpoint(event) {

	// Create param string
	var clientList = document.getElementById("client_list");
	var client = clientList.options[clientList.selectedIndex].value;
	var param = "client=" + client;

    // Get output objects
    var principal_resp = document.getElementById("client_principal");
    var portfolio_resp = document.getElementById("portfolio_value");
    var port_change_resp = document.getElementById("percentage_of_change");
    var update_princ_cur = document.getElementById("update_princ_cur");

	// AJAX server request
	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function () {

		// Valid response
		if (this.readyState == 4 && this.status == 200) {

			// Security check
			if (this.responseText === "SECURITY BREACH") {
				window.location.replace("/");
				return;
			}

            // Process response
            var resp = JSON.parse(this.responseText);
            principal_resp.innerHTML = resp["principal"];
            portfolio_resp.innerHTML = resp["portfolio_value"];
            port_change_resp.innerHTML = resp["portfolio_change"];
            var change_value = resp["portfolio_change"];
            if(parseFloat(change_value) > 0) {
                document.getElementById("arrow").src = "../static/img/triangle-green.png";
            }
            else if (parseFloat(change_value) < 0) {
                document.getElementById("arrow").src = "../static/img/triangle-red.png";
            }
            else if (parseFloat(change_value) < 0.0000000001) {
                document.getElementById("arrow").src = "../static/img/non-change.png";
            }
            update_princ_cur.innerHTML = resp["principal"];

            // Fill in Market Summary
            document.getElementById("ms_p1").innerHTML = resp["top_personal"][0];
            var temp = resp["top_personal"][0];
            var p1 = temp.substring(5,12);
            if(parseFloat(p1) > 0) {
                document.getElementById("p1").src = "../static/img/triangle-green.png";
            }
            else if (parseFloat(p1) < 0) {
                document.getElementById("p1").src = "../static/img/triangle-red.png";
            }
            else if (parseFloat(p1) < 0.0000000001) {
                document.getElementById("p1").src = "../static/img/non-change.png";
            }
            document.getElementById("ms_p2").innerHTML = resp["top_personal"][1];
            var temp = resp["top_personal"][1];
            var p2 = temp.substring(5,12);
            if(parseFloat(p2) > 0) {
                document.getElementById("p2").src = "../static/img/triangle-green.png";
            }
            else if (parseFloat(p2) < 0) {
                document.getElementById("p2").src = "../static/img/triangle-red.png";
            }
            else if (parseFloat(p2) < 0.0000000001) {
                document.getElementById("p2").src = "../static/img/non-change.png";
            }
            document.getElementById("ms_p3").innerHTML = resp["top_personal"][2];
            var temp = resp["top_personal"][2];
            var p3 = temp.substring(5,12);
            if(parseFloat(p3) > 0) {
                document.getElementById("p3").src = "../static/img/triangle-green.png";
            }
            else if (parseFloat(p3) < 0) {
                document.getElementById("p3").src = "../static/img/triangle-red.png";
            }
            else if (parseFloat(p3) < 0.0000000001) {
                document.getElementById("p3").src = "../static/img/non-change.png";
            }
            document.getElementById("ms_m1").innerHTML = resp["top_market"][0];
            var temp = resp["top_market"][0];
            var m1 = temp.substring(5,12);
            if(parseFloat(m1) > 0) {
                document.getElementById("m1").src = "../static/img/triangle-green.png";
            }
            else if (parseFloat(m1) < 0) {
                document.getElementById("m1").src = "../static/img/triangle-red.png";
            }
            else if (parseFloat(m1) < 0.0000000001) {
                document.getElementById("m1").src = "../static/img/non-change.png";
            }
            document.getElementById("ms_m2").innerHTML = resp["top_market"][1];
            var temp = resp["top_market"][1];
            var m2 = temp.substring(5,12);
            if(parseFloat(m2) > 0) {
                document.getElementById("m2").src = "../static/img/triangle-green.png";
            }
            else if (parseFloat(m2) < 0) {
                document.getElementById("m2").src = "../static/img/triangle-red.png";
            }
            else if (parseFloat(m2) < 0.0000000001) {
                document.getElementById("m2").src = "../static/img/non-change.png";
            }
            document.getElementById("ms_m3").innerHTML = resp["top_market"][2];
            var temp = resp["top_market"][2];
            var m3 = temp.substring(5,12);
            if(parseFloat(m3) > 0) {
                document.getElementById("m3").src = "../static/img/triangle-green.png";
            }
            else if (parseFloat(m3) < 0) {
                document.getElementById("m3").src = "../static/img/triangle-red.png";
            }
            else if (parseFloat(m3) < 0.0000000001) {
                document.getElementById("m3").src = "../static/img/non-change.png";
            }
            // Create pie chart

            industry_spread_endpoint(event);

		}

	}
	xhttp.open("POST", "/client_info", true);
	xhttp.setRequestHeader('content-type',
		'application/x-www-form-urlencoded;charset=UTF-8');
	xhttp.send(param);

}

// Get portfolio for given client
function stock_endpoint(event){

    // Create param string
    var stockList = document.getElementById("stock_list");
    var stock = stockList.options[stockList.selectedIndex].value;
    var clientList = document.getElementById("client_list");
    var client = clientList.options[clientList.selectedIndex].value;
    var param = "stock=" + stock + "&client=" + client;

    // Get output objects
    var company_resp = document.getElementById("stock_company");
    var ind_resp = document.getElementById("stock_ind");
    var price_resp = document.getElementById("stock_price");
    var held_resp = document.getElementById("stock_held");
    var var_resp = document.getElementById("stock_var");
    var trend_resp = document.getElementById("stock_trend");
    var action_resp = document.getElementById("stock_action");
    var conf_resp = document.getElementById("stock_conf");
    var toggle = document.getElementById("cardToggle");

    // AJAX server request
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function(){

        // Valid response
        if(this.readyState==4 && this.status==200){

            // Security check
            if(this.responseText === "SECURITY BREACH"){
                window.location.replace("/");
                return;
            }

            // Process response
            var resp = JSON.parse(this.responseText);
            company_resp.innerHTML = resp["company"];
            ind_resp.innerHTML = resp["industry"];
            price_resp.innerHTML = resp["price"];
            held_resp.innerHTML = resp['owned'];
            var_resp.innerHTML = resp["variance"];
            trend_resp.innerHTML = resp["trend"];
            if(resp["action"] == 'B')
                action_resp.innerHTML = "Buy";
            else if(resp["action"] == 'S')
                action_resp.innerHTML = "Sell";
            else
                action_resp.innerHTML = "Unknown";
            conf_resp.innerHTML = resp["confidence"];
            if(resp['inWatchlist'])
                toggle.checked = true;
            else
                toggle.checked = false;

            // Create graph
            price_history_endpoint(event);

        }

    }
    xhttp.open("POST", "/stock_info", true);
    xhttp.setRequestHeader('content-type',
        'application/x-www-form-urlencoded;charset=UTF-8');
    xhttp.send(param);

}

// Get portfolio for given client
function watchlist_endpoint(event){

    // Create param string
    var stockList = document.getElementById("stock_list");
    var stock = stockList.options[stockList.selectedIndex].value;
    var clientList = document.getElementById("client_list");
    var client = clientList.options[clientList.selectedIndex].value;
    var param = "stock=" + stock + "&client=" + client;

    // Get output object
    var toggle = document.getElementById("cardToggle");

    // AJAX server request
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function(){

        // Valid response
        if(this.readyState==4 && this.status==200){

            // Security check
            if(this.responseText === "SECURITY BREACH"){
                window.location.replace("/");
                return;
            }

            // Set button accordingly and update graph
            if(this.responseText === "t")
                toggle.checked = true;
            else
                toggle.checked = false;
            graph_endpoint("-", "-");

        }

    }
    xhttp.open("POST", "/watchlist", true);
    xhttp.setRequestHeader('content-type',
        'application/x-www-form-urlencoded;charset=UTF-8');
    xhttp.send(param);

}

// Create line graph for changing prices
function price_history_endpoint(event){

    // Create param string
    var stockList = document.getElementById("stock_list");
    var stock = stockList.options[stockList.selectedIndex].value;
    var param = "stock=" + stock;

    // AJAX server request
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function(){

        // Valid response
        if(this.readyState==4 && this.status==200){

            // Security check
            if(this.responseText === "SECURITY BREACH"){
                window.location.replace("/");
                return;
            }

            // Process response - create graph
            var data = JSON.parse(this.responseText);
            visualise_line_graph(data['times'], data['prices']);

        }

    }
    xhttp.open("POST", "/price_hist", true);
    xhttp.setRequestHeader('content-type',
        'application/x-www-form-urlencoded;charset=UTF-8');
    xhttp.send(param);

}

// Create pie chart for spread of holdings across industries
function industry_spread_endpoint(event){

    // Create param string
    var clientList = document.getElementById("client_list");
    var client = clientList.options[clientList.selectedIndex].value;
    var param = "client=" + client;

    // AJAX server request
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function(){

        // Valid response
        if(this.readyState==4 && this.status==200){

            // Security check
            if(this.responseText === "SECURITY BREACH"){
                window.location.replace("/");
                return;
            }

            // Process response - create pie chart
            var data = JSON.parse(this.responseText);
            visualise_pie_graph(data['industries'], data['portion'], data['stocks'], data['stocksPortions']);

        }

    }
    xhttp.open("POST", "/industry_spread", true);
    xhttp.setRequestHeader('content-type',
        'application/x-www-form-urlencoded;charset=UTF-8');
    xhttp.send(param);

}

// Create heatmap for distribution of AI suggestions
function ai_dist_endpoint(event){

    // AJAX server request
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function(){

        // Valid response
        if(this.readyState==4 && this.status==200){

            // Security check
            if(this.responseText === "SECURITY BREACH"){
                window.location.replace("/");
                return;
            }

            // Process response - create heatmap
            visualise_heatmap(JSON.parse(this.responseText));

        }

    }
    xhttp.open("POST", "/ai_dist", true);
    xhttp.setRequestHeader('content-type',
        'application/x-www-form-urlencoded;charset=UTF-8');
    xhttp.send();

}

// Get latest JSON of graph points and update visual
function graph_endpoint(variance, trend) {

    // Create param string
    var clientList = document.getElementById("client_list");
    var client = clientList.options[clientList.selectedIndex].value;
    var param = "client=" + client + "&var=" + variance + "&trend=" + trend;

    // AJAX server request
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {

        // Valid response
        if (this.readyState == 4 && this.status == 200) {

            // Security check
            if (this.responseText === "SECURITY BREACH") {
                window.location.replace("/");
                return;
            }

            // Process response
            var resp = JSON.parse(this.responseText);
            // document.getElementById("current_ai").innerHTML = "Variance: " +
            //     resp['variance'] + " - Trend: " + resp['trend'];
            visualise_graph(JSON.parse(resp['data']));

        }

    }
    xhttp.open("POST", "/graph", true);
    xhttp.setRequestHeader('content-type',
            'application/x-www-form-urlencoded;charset=UTF-8');
    xhttp.send(param);
}

// Draw graph
function visualise_graph(response){

    // Setup config
    var config = {
        dataSource: response,
        forceLocked: false,
        // graphHeight: function(){ return screen.height*0.6; },
    	// graphWidth: function(){ return screen.width*0.6; },
        backgroundColor: "#c7d6d5",
        initialScale: 0.9,
        nodeCaption: function(node){
            if (node.root) { return node.id;}
            if (node.type == 'legend') {return node.price;}
            else {return node.id + " - $" + node.price;}
        },
        nodeCaptionsOnByDefault: true,
        // edgeCaption: function(edge) {
		// 	return edge.quantity
        // },
        // edgeCaptionsOnByDefault: true,
        fixRootNodes: true,
        nodeClick: function(node) {
            var code = node.getProperties().id;
            if(code === "Portfolio" || code === "Watchlist" || code === "Recommendations") return;
            var stockList = document.getElementById("stock_list");
            stockList.value = code;
            stockList.dispatchEvent(new Event('change'));
            var transacStock = document.getElementById("transac_stock");
            transacStock.value = code;
            transacStock.dispatchEvent(new Event('change'));
        },
        zoomControls: true,
        nodeMouseOver: function(node){nodeHover(node);},
        rootNodeRadius: "100",
        nodeTypes: { "type":
            ["root", "stock"]
        },
        nodeStyle: {
            "all": {
                //"captionSize": 200,
                "borderWidth": function(node, radius) {
                    return radius / 4
                },
            },
            "root": {
                "color": "#1e4547",
                "radius": 6,
                "captionSize": 20,
                "borderColor": "#12263f",
                "highlighted": {
                    "color": "#1e4547",
                },
                "selected": {
                    "color": "#1e4547"}
                    //"radius": "15"
        	},
	        "stock": {
                "color": function(node) {
                    if (node.getProperties().quantity >0)
                        return "#6c6c6c";
                else return "#bcbcbc"
                },
                "borderColor": function(node) {
                    if (node.getProperties().action =='B') return "#7af26f";
					if (node.getProperties().action =='S') return "#ed3b3b";
                    else return "#6c6c6c"
                },
                "highlighted": {
                    "color": function(node) {
                        if (node.getProperties().quantity >0)
                    	return "#bcbcbc";
                        else return "#ffffff"
                    }
                },
                "selected": {
                "color": function(node) {
                        if (node.getProperties().quantity >0)
                            return "#bcbcbc";
                        else return "#ffffff"
                    }
                },
                "radius": function(node) {
                    var value = node.getProperties().price * node.getProperties().quantity;
                    if (value<300) return 8;
                    if ((value>=300 && value<700)) return 12;
                    if (value>1100) return 18;
                    else return 15
                }
            },
            "legend": {
                "color": "#6c6c6c",
                "borderColor": function(node) {
                    if (node.getProperties().action =='B') return "#7af26f";
                    if (node.getProperties().action =='S') return "#ed3b3b";
                    else return "#6c6c6c"
                },
                "radius": function(node) {
                    var legendid = node.getProperties().id
                    if (legendid == 'Small') return 8;
                    if (legendid == 'Medium') return 12;
                    if (legendid == 'Huge') return 18;
                    else return 15
                }
            }
        },
        edgeTypes: { "type":
            ["link", "Portfolio", "Watchlist", "Recommendations"]
        },
        edgeStyle: {
        	"all":{
                "width": 2,
                "color": "#000000",
                "opacity": 0.4
        	},
            "link":{
                "width": 1,
                "color": "#ffffff",
                "opacity": 0
            }
        },
        linkDistancefn: function(edge, k){

            // Set position of root nodes
            if(edge.source.self.getProperties().root && edge.target.self.getProperties().root){

                // Get properties
                var node = edge.source
                var height = node.self.a.conf.graphHeight();
                var width = node.self.a.conf.graphWidth();

                // Set position
                if(node.self.getProperties().id == "Portfolio"){
                    node.y = height * 0.7;
                    node.x = width * 0.7;
                }
                else if(node.self.getProperties().id == "Watchlist"){
                    node.y = height * 0.7;
                    node.x= width * 0.4;
                }
                else if(node.self.getProperties().id == "Recommendations"){
                    node.y = height * 0.3;
                    node.x = width * 0.55;
                }

                // Match
                node.px = node.x;
                node.py = node.y;

            }
            // Return default dist
            return 20;

        }

    };

	// Display graph
	alchemy = new Alchemy(config)
}

var totalDistance = 0;
var lastSeenAt = {x: null, y: null};

$(document).mousemove(function(event) {
    totalDistance += Math.sqrt(Math.pow(lastSeenAt.y - event.clientY, 2) + Math.pow(lastSeenAt.x - event.clientX, 2));
    if(totalDistance > 100){
        deleteHover();
        totalDistance = 0;
    }
    lastSeenAt.x = event.clientX;
    lastSeenAt.y = event.clientY;
});

// Delete hover box
function deleteHover(){
    var popup = document.getElementById("popup-hover");
    while (popup.firstChild)
        popup.removeChild(popup.firstChild);
}

// Howver over node
function nodeHover(node){

    // Setup - delete existing and get required
    deleteHover();
    totalDistance = 0;
    var popup = document.getElementById("popup-hover");
    var nodeProp = node.getProperties();

    // Get connected edges
    edge = {'Watchlist': false, 'Recommendations': false, 'Portfolio': false}
    for(var i = 0; i < node._adjacentEdges.length; i++){
        edge[node._adjacentEdges[i].getProperties().source] = true;
    }

    // Skip root and legend
    if(nodeProp.type === "root" || nodeProp.type === "legend")
        return;

    // Base features
    span = document.createElement("span");
    // span.innerHTML = "Code:";
    // span.style.display = "inline";
    // span.style.fontWeight = "bold";
    // popup.appendChild(span);
    // span = document.createElement("span");
    // span.innerHTML = " " + nodeProp.id + " &nbsp&nbsp";
    // span.style.fontWeight = "bold";
    // popup.appendChild(span);
    // popup.appendChild(document.createElement("br"));
    // span = document.createElement("span");
    // span.innerHTML = "Price:";
    // span.style.display = "inline";
    // span.style.fontWeight = "bold";
    // popup.appendChild(span);
    span = document.createElement("legend");
    span.innerHTML = " " + nodeProp.id + " &nbsp&nbsp&nbsp&nbsp"+ " $" + nodeProp.price;
    span.style.fontWeight = "bold";
    popup.appendChild(span);
    // popup.appendChild(document.createElement("br"));


    // Special features
    if(edge['Portfolio']){
        span = document.createElement("span");
        span.innerHTML = "Quantity:";
        span.style.display = "inline";
        span.style.fontWeight = "bold";
        popup.appendChild(span);
        span = document.createElement("span");
        span.innerHTML = " " + nodeProp.quantity;
        popup.appendChild(span);
        popup.appendChild(document.createElement("br"));
    }
    if(edge['Recommendations']){
        span = document.createElement("span");
        span.innerHTML = "Variance:";
        span.style.display = "inline";
        span.style.fontWeight = "bold";
        popup.appendChild(span);
        span = document.createElement("span");
        span.innerHTML = " " + nodeProp.variance;
        popup.appendChild(span);
        popup.appendChild(document.createElement("br"));
        span = document.createElement("span");
        span.innerHTML = "Trend:";
        span.style.display = "inline";
        span.style.fontWeight = "bold";
        popup.appendChild(span);
        span = document.createElement("span");
        span.innerHTML = " " + nodeProp.trend;
        popup.appendChild(span);
        popup.appendChild(document.createElement("br"));
        span = document.createElement("span");
        span.innerHTML = "Confidence:";
        span.style.display = "inline";
        span.style.fontWeight = "bold";
        popup.appendChild(span);
        span = document.createElement("span");
        span.innerHTML = " " + nodeProp.confidence;
        popup.appendChild(span);
        popup.appendChild(document.createElement("br"));
        popup.appendChild(document.createElement("br"));
        span = document.createElement("span");

        // span.innerHTML = "Summary:";
        // span.style.display = "inline";
        // span.style.fontWeight = "bold";
        popup.appendChild(span);
        span = document.createElement("span");
        span.innerHTML = " " + nodeProp.summary;
        popup.appendChild(span);
        // popup.appendChild(document.createElement("br"));
    }

}

//function for drawing line-graph for showing historical stock's values
function visualise_line_graph(times_line, values_line) {

    //specify variables for modifying date attributes
    var localTimes = [];
    localTimes = times_line;

    //modify date formats for cleaner presentation
    for(i=0; i < localTimes.length; i++){
        var splitedTime = localTimes[i].split("-");
        localTimes[i] = splitedTime[1] + "-" + splitedTime[2];
    }

    //duplicate the array first
    var localValues = [];
    localValues = values_line;

    //specify variables for finding the lowest value of the stock
    var precisionRatio = 10000;
    var lowest_value = Number.MAX_SAFE_INTEGER;
    var largest_value = -1;
    var middle_value = -1;

    //find the lowest value of the graph and used to adjust the graph's layout
    for (i = 0; i < localValues.length; i++) {
        //find minimum value in the give data
        if(localValues[i] * precisionRatio < lowest_value * precisionRatio){
            lowest_value = localValues[i];
        }

        //find maximum value in the give data
        if(localValues[i] * precisionRatio > largest_value * precisionRatio){
            largest_value = localValues[i];
        }
    }

    //find the middle value, used to set tickers after
    middle_value = (lowest_value + largest_value) / 2;

    //set tickers manually (because Chartist.js has a bug that actually affect decimal accuracies for line graph)
    ticksCreated = [lowest_value, middle_value, largest_value];
    ticksCreated.sort();

	//////////////////////////////for drawing line graph for stocks, using chartist.js
    // var stockList = document.getElementById("stock_list");
	var chart = new Chartist.Line(document.getElementById("chart_stock"), {
		//input x_values and y_values here (Jiawei's note)
		labels: localTimes,
		series: [values_line]
	}, {
			//set the lowest, highest and middle point of the y-axis
            low: lowest_value,
            high: largest_value,

            //other useful attributes
			fullWidth: false,
            showArea: false,
            showPoint: false,


			//please change the width and height for the div allocated
			width: "100%",
			height: "35%",

            //disable grid lines
            axisX: {
                showLabel: true,
                showGrid: true
            },

			// As this is axis specific we need to tell Chartist to use whole numbers only on the concerned axis
			axisY: {
                type: Chartist.FixedScaleAxis,
                ticks: ticksCreated,
                divisor: 3,
                showLabel: true,
                showGrid: true
            },

            //plugin to show title for the line graph
            plugins: [
                //call the plugin by specifying all related attributes
                Chartist.plugins.ctAxisTitle({

                    //specify related attributesd for x axis
                    axisX: {
                        //the title for horizontal axis
                        axisTitle: 'Date',
                        axisClass: 'ct-axis-title',
                        textAnchor: 'middle',

                        //changing x offset will move it up/down, whereas y offset will move the title left/right
                        offset: {
                            x: 0,
                            y: 50   //tested to be best-fitted
                        },
                    },

                    //specify related attributes for y axis
                    axisY: {
                        //the title for vertical axis
                        axisTitle: 'Price($)',
                        axisClass: 'ct-axis-title',
                        textAnchor: 'middle',
                        flipTitle: true,

                        //changing x offset will move it up/down, whereas y offset will move the title left/right
                        offset: {
                            x: 0,   //tested to be best-fitted
                            y: 17
                        },
                    }
                })
            ]
		});

	// Let's put a sequence number aside so we can use it in the event callbacks
	var seq = 0,
		delays = 30,
		durations = 500;

	// Once the chart is fully created we reset the sequence
	chart.on('created', function () {
		seq = 0;
	});

	// On each drawn element by Chartist we use the Chartist.Svg API to trigger SMIL animations
	chart.on('draw', function (data) {
		seq++;

		if (data.type === 'line' || data.type === 'area') {
			data.element.animate({
				d: {
					begin: 2000 * data.index,
					dur: 3500,
					from: data.path.clone().scale(1, 0).translate(0, data.chartRect.height()).stringify(),
					to: data.path.clone().stringify(),
					easing: Chartist.Svg.Easing.easeOutQuint
				}
			});
		}

		if (data.type === 'line') {
		} else if (data.type === 'label' && data.axis === 'x') {
			data.element.animate({
				y: {
					begin: seq * delays,
					dur: durations,
					from: data.y + 100,
					to: data.y,
					// We can specify an easing function from Chartist.Svg.Easing
					easing: 'easeOutQuart'
				}
			});
		} else if (data.type === 'label' && data.axis === 'y') {
			data.element.animate({
				x: {
					begin: seq * delays,
					dur: durations,
					from: data.x - 100,
					to: data.x,
					easing: 'easeOutQuart'
				}
			});
		} else if (data.type === 'point') {
			data.element.animate({
				x1: {
					begin: seq * delays,
					dur: durations,
					from: data.x - 10,
					to: data.x,
					easing: 'easeOutQuart'
				},
				x2: {
					begin: seq * delays,
					dur: durations,
					from: data.x - 10,
					to: data.x,
					easing: 'easeOutQuart'
				},
				opacity: {
					begin: seq * delays,
					dur: durations,
					from: 0,
					to: 1,
					easing: 'easeOutQuart'
				}
			});
		} else if (data.type === 'grid') {
			// Using data.axis we get x or y which we can use to construct our animation definition objects
			var pos1Animation = {
				begin: seq * delays,
				dur: durations,
				from: data[data.axis.units.pos + '1'] - 30,
				to: data[data.axis.units.pos + '1'],
				easing: 'easeOutQuart'
			};

			var pos2Animation = {
				begin: seq * delays,
				dur: durations,
				from: data[data.axis.units.pos + '2'] - 100,
				to: data[data.axis.units.pos + '2'],
				easing: 'easeOutQuart'
			};

			var animations = {};
			animations[data.axis.units.pos + '1'] = pos1Animation;
			animations[data.axis.units.pos + '2'] = pos2Animation;
			animations['opacity'] = {
				begin: seq * delays,
				dur: durations,
				from: 0,
				to: 1,
				easing: 'easeOutQuart'
			};

			data.element.animate(animations);
		}
	});

	//customization of the grid style
	chart.on('draw', function (data) {
		if (data.type === 'grid' && data.index === 0) {
			data.element.attr({ "style": "stroke:rgb(0,0,0);stroke-width:3; stroke-dasharray: 0px 0px;" });
		}
	});
}

//globally accessible chart used to destory and recreate the double donut graph;
var myChart;

//function for drawing double donut graph for showing the industrial percentages of all stocks that a client owns
//for double donut graph for industrial showing using chartist.js
//industralNames_pie simply takes the list of strings as labels on the graph (can be used to display anything and will not be used to draw the pie graph)
function visualise_pie_graph(industralNames_pie, industralPercentage_pie, stocks, stocksPortions) {
    //declare industry names for showing pie graph
    var modifiedNames = [];

    // modify industry names for proper showing (adding new line characters for plotly.js using <br>)
    for (i = 0; i < industralNames_pie.length; i++) {

        //if it contains both ',' and '&', add new line character accordingly
        if(industralNames_pie[i].includes(',') && industralNames_pie[i].includes('&')){
            splitedNames = industralNames_pie[i].split(/,|&/);
            modifiedNames.push(splitedNames[0].trim());

            // trim the given industries' names
            for (j = 1; j < splitedNames.length; j++) {
                modifiedNames[i] +=  ',\n' + splitedNames[j].trim();
            }

        //if it contains only ','  add new line character accordingly
        }else if(industralNames_pie[i].includes('&')){
            splitedNames = industralNames_pie[i].split('&');
            modifiedNames.push(splitedNames[0].trim());

            for (j = 1; j < splitedNames.length; j++) {
                modifiedNames[i] +=  '&\n' + splitedNames[j].trim();
            }

        //if it contains only '&'  add new line character accordingly
        }else if(industralNames_pie[i].includes(',')){
            splitedNames = industralNames_pie[i].split(',');
            modifiedNames.push(splitedNames[0].trim());

            for (j = 1; j < splitedNames.length; j++) {
                modifiedNames[i] +=  ',\n' + splitedNames[j].trim();
            }

        //push original text if nothing needs to be converted
        }else{
            modifiedNames.push(industralNames_pie[i].trim());
        }
    }

    //declare array for rounding percentages given
    // var roundedPercentages  = [];

    //round up all decimals to integers for the percentages given
    // for (i = 0; i < industralPercentage_pie.length; i++) {
    //     roundedPercentages.push(Math.round(industralPercentage_pie[i]));
    // }

    //assign random colour to an industry, as a function
    // var dynamicColors = function () {
    //     //tested to be the best ratio between randomising stocks colours and industries colours
    //     var r = Math.floor(Math.random() * 210);
    //     var g = Math.floor(Math.random() * 210);
    //     var b = Math.floor(Math.random() * 210);
    //     return "rgb(" + r + "," + g + "," + b + ")";
    // };

    // industries labels
    var industriesLabels = industralNames_pie;

    // industreis frequencies
    var industriesFreq = industralPercentage_pie;

    // stocks labels
    var stocksLabels = stocks;

    // stocks frequencies
    //noted the sum of the industry-related stocks should added up to the frequencies of their industries e.g. 5 + 17 = 22
    var stocksFreq = stocksPortions;

    //declare all colours about to be inserted (for both industries and stocks)
    var allIndustriesColours = [];
    var allStocksColours = [];

    //first we assign random colours to each industry
    // for (i = 0; i < industriesLabels.length; i++) {
    //     allIndustriesColours.push(dynamicColors());
    // }

    // set the muted colours for all industries
    allIndustriesColours.push("rgb(242,224,144)");
    allIndustriesColours.push("rgb(221,119,136)");
    allIndustriesColours.push("rgb(102,119,153)");
    allIndustriesColours.push("rgb(122,148,96)");
    allIndustriesColours.push("rgb(221,153,119)");
    allIndustriesColours.push("rgb(102,85,102)");
    allIndustriesColours.push("rgb(165,42,42)");
    allIndustriesColours.push("rgb(138,43,226)");
    allIndustriesColours.push("rgb(0,206,209)");

    //declare index and var used to match "sum of stocks freq same as the industry's freq"
    var industryIndex = 0;
    var tempTotal = 0;

    //perform matching of "sum of stocks freq same as the industry's freq"
    for (j = 0; j < stocksFreq.length; j++) {

        //if the total did NOT reached the freq of the industry, then we assign them colours
        if (tempTotal < Number(Math.ceil(industriesFreq[industryIndex]* 100)) ) {

            //add the colours for stocks
            tempTotal += Number(Math.ceil(stocksFreq[j])) * 100;

            //get the colours as 'r', 'g' and 'b'
            splitedColours = allIndustriesColours[industryIndex].split(/,|\(|\)/); //splited by '(' and ')' and ',' , rgb should be in position 1,2,3

            //tested to be the best ratio between randomising stocks colours and industries colours
            newR = Number(Math.floor(Math.random() * 17)) + Number(splitedColours[1]);
            newG = Number(Math.floor(Math.random() * 17)) + Number(splitedColours[2]);
            newB = Number(Math.floor(Math.random() * 17)) + Number(splitedColours[3]);

            //put the new colours into a new whole
            newColour = "rgb(" + newR + "," + newG + "," + newB + ")";

            //put the new colour for a stock in the stocks list
            allStocksColours.push(newColour);

        //if the total freq of computing stocks reached the freq of their industry, then we move to another industry
        } else {

            //reset back tempTotal and increment industryIndex for new addition
            tempTotal = 0;
            industryIndex += 1;

            //check again after shifting to new industry
            if (tempTotal < Number(Math.ceil(industriesFreq[industryIndex]* 100)) ) {
                tempTotal += Number(Math.ceil(stocksFreq[j]) * 100);

                //get the colours as 'r', 'g' and 'b'
                splitedColours = allIndustriesColours[industryIndex].split(/,|\(|\)/); //splited by '(' and ')' and ',' , rgb should be in position 1,2,3

                //tested to be the best ratio between randomising stocks colours and industries colours
                newR = Number(Math.floor(Math.random() * 17)) + Number(splitedColours[1]);
                newG = Number(Math.floor(Math.random() * 17)) + Number(splitedColours[2]);
                newB = Number(Math.floor(Math.random() * 17)) + Number(splitedColours[3]);

                //put the new colours into a new whole
                newColour = "rgb(" + newR + "," + newG + "," + newB + ")";

                //put the new colour for a stock in the stocks list
                allStocksColours.push(newColour);
            }
        }
    }

    //get the elementID for drawing
    var ctx = document.getElementById("chart-area").getContext("2d");

    // destroy previous instance of chart
    if (myChart) {
        myChart.destroy();
    }
    
    //draw the double donut chart using chart.js and the data provided
    myChart = new Chart(ctx, {

        //double donut chart straightforwardly supported
        type: 'doughnut',

        //specify all data used to draw the chart
        data: {

            // the outer layer of the donut chart
            datasets: [{

                //frequencies for drawing stocks layer(no need to be exactly 100)
                data: stocksFreq,

                //set all the stocks colours specified above
                backgroundColor: allStocksColours,

                //labels for stocks
                labels: stocksLabels,
           
            }, {

                //frequencies for drawing industries layer(no need to be exactly 100)
                data: industriesFreq,

                //set all the industries colours specified above
                backgroundColor: allIndustriesColours,

                //labels for industries
                labels: industriesLabels
            },]
        },

        //additional options for drawing
        options: {
            
            //please turn off for forceful edition
            responsive: true,

            //legand display (better be off because I set the appropriate margin already)
            //cannot be splitted and managed elsewhere
            legend: {

                //setup the labels for showing for the legend section
                // labels: {
                //     // function to return legend text
                //     generateLabels: function() {

                //     // declare text to be displayed in the legend sections
                //     returningLegend = [];
                    
                //     // iteratively push in legend info, including colour, stroke style and industries names
                //     for(var i = 0; i < industriesLabels.length; i++){
                //         var obj = new Object();
                //         obj.text = industriesLabels[i];
                //         obj.fillStyle = allIndustriesColours[i];
                //         obj.strokeStyle = '#fff';
                //         returningLegend.push(obj);
                //     }

                //     // return the legend to render it
                //     return returningLegend;
                //    }
                // }
             },

            //turn off animation for "downloading data conflicts"
            animation: false,

            //set the margin for drawing
            layout: {

                //set to having left padding because otherwise it looks weird
                padding: {
                    left: 0,
                    right: 0,
                    top: 20,
                    bottom: 0
                }
            },

            //additional tooltips (manage info showing when you hover)
            tooltips: {
                callbacks: {
                    custom: function(tooltip) {
                        if (!tooltip) return;
                        // disable displaying the color box;
                        tooltip.displayColors = false;
                      },

                    //please modify this section for additional hover text
                    label: function (tooltipItem, data) {

                        //declare variable for displaying hover_text
                        var dataset = data.datasets[tooltipItem.datasetIndex];
                        var index = tooltipItem.index;

                        //convert the longer text to shorter one, adding new line break
                        if(dataset.labels[index].includes('Pharmaceuticals')){
                            return ["Pharmaceuticals, life," , "science: " + Number((dataset.data[index]).toFixed(1)) + '%'];

                        //remove ambiguous results
                        }else if(dataset.labels[index].includes('Not')){
                            return ["others: " + Number((dataset.data[index]).toFixed(1)) + '%'];
                        }

                        //do not need any convertion, simply display label and percentage
                        return dataset.labels[index] + ': ' + Number((dataset.data[index]).toFixed(1)) + '%';
                    }
                }
            }
        }
    });
}

//function for drawing the graph for allowing consultant to select recommendation for clients, based on variance and trend selected
function visualise_heatmap(object) {

	//For heapmap drawing (AI recommendation) using plotly.js
	var chartHeatMap = document.getElementById('chart_recommendation');

	//set the axis labels
	var trends = object.trends;
	var variances = object.variances;

	//set the frequencies for each bracket
	var frequencies = [];
	for (i = 0; i < variances.length; i++) {
		frequencies.push(object.data[i]);
    }

    //declare the text showing when a mouse hover over a grid cell
    var textNew = [];

    //for each trend value
    for (i = 0; i < variances.length; i++) {

        //temporary array representing a list of values to be inserted
        var hover_text_info = [];

        //for each frequency value
        for (j = 0; j < object.data[i].length; j++) {

            //push in all information for showing for hover_text on heatmap
            hover_text_info.push('variance: '
                            + String(variances[i])
                            + '<br>trend: '
                            + String(trends[j])
                            + '<br>frequency: '
                            + String(object.data[i][j]) );
        }

        //push the horizontal labelling in the hover_text on heatmap
        textNew.push(hover_text_info);
    }

	//find the bracket with maximum frequency
	var maxFreq = 0;
	for (i = 0; i < variances.length; i++) {
		if (maxFreq < Math.max(...frequencies[i])) {
			maxFreq = Math.max(...frequencies[i]);
		}
	}

	//assign the ratio for logarithm function (we want the maximum value to be 100 in our heatmap)
	ratioConversion = Math.pow(maxFreq, (1 / 100));

	//conversion using self-defined logarithm function
	for ( i = 0; i < variances.length; i++ ) {
		for ( j = 0; j < trends.length; j++ ) {
			//cannot apply logarithm function to a "0" as we cannot divide anything by 0
            if (frequencies[i][j] != 0)

                //modified to show colour (only)
                frequencies[i][j] = 100 + Math.log(frequencies[i][j]) / Math.log(ratioConversion);
            else
                //default frequencies (tho just for colour showing)
                frequencies[i][j] = 50
        }
    }

	// values on axis
	var xValues = trends;
	var yValues = variances;
    var zValues = frequencies;

    //set the colours to heatmap showing, intermediate colours will be filled automatically
    //simply reverse the order if we prefer the other way around
	var colorscaleValue = [
        [0, '#ffffff'], // min
		[1, '#244749']  // max
	];

    //specify data for drawing heatmap
	var data = [{
		x: xValues,
		y: yValues,
		z: zValues,
        type: 'heatmap',
        text: textNew,
        hoverinfo: 'text',
		colorscale: colorscaleValue,
        showscale: false,

        //showing legend also requires a little plugin if needed
		showlegend: true
	}];

    //set the layout for the heatmap
	var layout = {
		annotations: [],
		xaxis: {
			ticks: '',
			side: 'bottom',
            title: 'Price Trend (%)',
            fixedrange: true,

            // set the font attributes
            titlefont: {
                family: 'Arial, serif',
                size: 14,
                color: 'black'
            },

            // change axis labels attributes
            showticklabels: true,
            tickangle: -45,
            tickfont: {
                family: 'Arial, serif',
                size: 12,
                color: '#808080',
            },

            // size: 11,
            // color: '#000000',
            // family: 'Arial, monospace',
            // autosize: false
		},
		yaxis: {
			ticks: '',
			ticksuffix: ' ',
            title: 'Variance (%)',
            fixedrange: true,

            // set the title font attributes
            titlefont: {
                family: 'Arial, serif',
                size: 14,
                color: 'black'
            },

            // change axis labels attributes
            showticklabels: true,
            // tickangle: 45,

            tickfont: {
                family: 'Arial, serif',
                size: 12,
                color: '#808080',
            },

			//please change the width and height for the div allocated
            width: 300,
            height: 250,
			autosize: false
        },

        //please also change the margin for appropriate presentation (frontend)
        margin:{
            l: 60,
            r: 20,
            b: 65,
            t: 0,
            pad: 4
        }
	};

    // Set init val to selected
    var prevIndex = [2,8]
    var prevVal = data[0].z[prevIndex[0]][prevIndex[1]];
    data[0].z[prevIndex[0]][prevIndex[1]] = 0

	//plot the heatmap and add onclick
	Plotly.newPlot('chart_recommendation', data, layout, { displayModeBar: false });
    chartHeatMap.on('plotly_click', onClick);

    // On-click function
    function onClick(clicked){

        //the values we needed to show stocks selected
        var clicked_x = clicked.points[0].x;
        var clicked_y = clicked.points[0].y;
        var clicked_z = clicked.points[0].z;

        // Reset old val and set new
        data[0].z[prevIndex[0]][prevIndex[1]] = prevVal;
        index = clicked.points[0].pointIndex;
        prevVal = data[0].z[index[0]][index[1]];
        data[0].z[index[0]][index[1]] = 0
        prevIndex = index;

        // Draw new plot
        Plotly.newPlot('chart_recommendation', data, layout, { displayModeBar: false })
        chartHeatMap.on('plotly_click', onClick);

        //update information on SVE
        graph_endpoint(clicked_y, clicked_x);
    };

}
