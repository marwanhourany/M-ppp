var year_select, origin_select, destination_select, basket_select,
	currency_label, amount_input, swap_button, convert_button, ppp_amount_element, xr_amount_element, interpretation_element, results_element,
	previous_year_idx, year_idx, origin_idx, destination_idx, basket_idx, amount, null_amount;

var database_version, countries, baskets, year_request_pending;

window.onload = function() {
	year_select = document.getElementById("year");
	origin_select = document.getElementById("origin");
	destination_select = document.getElementById("destination");
	basket_select = document.getElementById("basket");
	currency_label = document.getElementById("currency");
	amount_input = document.getElementById("amount");
	swap_button = document.getElementById("swap");
	convert_button = document.getElementById("convert");
        ppp_amount_element = document.getElementById("ppp_amount");
        xr_amount_element = document.getElementById("xr_amount");
	interpretation_element = document.getElementById("interpretation");
        results_element = document.getElementById("results");

	previous_year_idx = -1;
	year_idx = -1;
	origin_idx = -1;
	destination_idx = -1;
	basket_idx = -1;
	null_amount = true;

	year_select.selectedIndex = 0;
	origin_select.selectedIndex = 0;
	destination_select.selectedIndex = 0;
	basket_select.selectedIndex = 0;
	amount_input.value = "";

	year_request_pending = false;

	year_select.onchange = year_changed;
	origin_select.onchange = origin_changed;
	destination_select.onchange = destination_changed;
	basket_select.onchange = basket_changed;
	amount_input.oninput = amount_changed;
	swap_button.onclick = swap;
	convert_button.onclick = convert;
	
	update_control_state();

	init();
}

function clear_year()
{
	for (i = year_select.length - 1; i >= 1; i--)
	{
		year_select.remove(i);
	}
}

function clear_origin()
{
	for (i = origin_select.length - 1; i >= 1; i--)
	{
		origin_select.remove(i);
	}
}

function clear_destination()
{
	for (i = destination_select.length - 1; i >= 1; i--)
	{
		destination_select.remove(i);
	}
}

function clear_basket()
{
	for (i = basket_select.length - 1; i >= 1; i--)
	{
		basket_select.remove(i);
	}
}

function init()
{
	clear_year();
	clear_origin();
	clear_destination();
	clear_basket();
	
	$.get("fetch/init", fetch_init_callback);
}

function fetch_init_callback(data, status)
{
	database_version = data["version"];
	
	data["years"].forEach(function(year) {
		var year_option = document.createElement("option");
		year_option.text = year;
		year_select.add(year_option);
	});
}

function check_database_version(data)
{
	if(database_version != data["version"]) {
		alert(`Database version changed (${database_version} -> ${data["version"]}). Reloading.`);
		init();
		return true;
	}
	return false;
}

function year_changed() {
	previous_year_idx = year_idx;
	year_idx = year_select.selectedIndex;

	if(year_idx > 0) {
		$.get("fetch/country", {"year": year_select.value}, year_changed_callback);
		year_request_pending = true;
	}

	update_control_state();
}

function year_changed_callback(data, status) {
	if(check_database_version(data)) { return; }

	var previous_origin_country_idx;
	var previous_destination_country_idx;
	var previous_basket_idx;
	if (previous_year_idx == -1) {
		previous_origin_country_idx = -1;
		previous_destination_country_idx = -1;
		previous_basket_idx = -1;
	}
	else {
		if (origin_idx == -1) {
			previous_origin_country_idx = -1;
		}
		else {
			previous_origin_country_idx = countries[origin_idx][0];
		}
		
		if (destination_idx == -1) {
			previous_destination_country_idx = -1;
		}
		else {
			previous_destination_country_idx = countries[destination_idx][0];
		}
		
		if (basket_idx == -1) {
			previous_basket_idx = -1;
		}
		else {
			previous_basket_idx = baskets[basket_idx][0];
		}
	}

	clear_origin();
	clear_destination();
	clear_basket();

	countries = data["countries"];
	baskets = data["baskets"];

	var origin_matched = false;
	var destination_matched = false;
	var basket_matched = false;

	countries.forEach(function(country) {
		var origin_country_option = document.createElement("option");
		origin_country_option.text = country[1];
		origin_select.add(origin_country_option);

		if (previous_origin_country_idx == country[0]) {
			origin_select.selectedIndex = origin_select.length - 1;
			origin_matched = true;
		}
	});

	if (!origin_matched) { origin_select.selectedIndex = 0; }
	
	countries.forEach(function(country) {
		var destination_country_option = document.createElement("option");
		destination_country_option.text = country[1];
		destination_select.add(destination_country_option);

		if (previous_destination_country_idx == country[0]) {
			destination_select.selectedIndex = destination_select.length - 1;
			destination_matched = true;
		}
	});

	if (!destination_matched) { destination_select.selectedIndex = 0; }

	baskets.forEach(function(basket) {
		var basket_option = document.createElement("option");
		basket_option.text = basket[1];
		basket_select.add(basket_option);

		if (previous_basket_idx == basket[0]) {
			basket_select.selectedIndex = basket_select.length - 1;
			basket_matched = true;
		}
	});

	if (!basket_matched) { basket_select.selectedIndex = 0; }

	year_request_pending = false;

	origin_changed();
	destination_changed();
	basket_changed();
}

function origin_changed() {
	origin_idx = origin_select.selectedIndex - 1;
	if (origin_idx == -1) {
		currency_label.innerHTML = "";
	}
	else {
		currency_label.innerHTML = countries[origin_idx][2];
	}
	update_control_state();
}

function destination_changed() {
	destination_idx = destination_select.selectedIndex - 1;
	update_control_state();
}

function basket_changed() {
	basket_idx = basket_select.selectedIndex - 1;
	update_control_state();
}

function amount_changed() {
	if (amount_input.value == "")
	{
		null_amount = true;
	}
	else {
		amount = parseFloat(amount_input.value);
		null_amount = amount == 0.0;
	}
	update_control_state();
}

function update_control_state() {
	var year_idx_invalid = year_idx == -1;
	var origin_idx_invalid = origin_idx == -1;
	var destination_idx_invalid = destination_idx == -1;
	var country_idx_invalid = origin_idx_invalid || destination_idx_invalid;
	var basket_idx_invalid = basket_idx == -1;
	var idx_invalid = year_idx_invalid || country_idx_invalid || basket_idx_invalid;
	origin_select.disabled = year_idx_invalid || year_request_pending;
	destination_select.disabled = year_idx_invalid || year_request_pending;
	basket_select.disabled = year_idx_invalid || year_request_pending;
	amount_input.disabled = idx_invalid;
	swap_button.disabled = country_idx_invalid || (origin_idx == destination_idx) || year_request_pending;
	convert_button.disabled = idx_invalid || (origin_idx == destination_idx) || null_amount || year_request_pending;
}

function swap() {
	var origin_selected_idx = origin_select.selectedIndex;
	origin_select.selectedIndex = destination_select.selectedIndex;
	destination_select.selectedIndex = origin_selected_idx;
	origin_changed();
	destination_changed();
}

function convert()
{
	$.get("fetch/convert", {
			"year": year_select.value,
			"origin": countries[origin_idx][0],
			"destination": countries[destination_idx][0],
			"basket": baskets[basket_idx][0]
		},
		convert_callback);
}

function convert_callback(data, result) {
	if (check_database_version(data)) { return; }

	var ppp = data["ppp"];
	var exchange_rate = data["exchange_rate"];
	
	var adjusted_amount_ppp = amount * ppp;
	var adjusted_amount_ppp_rounded = adjusted_amount_ppp.toFixed(0);

	var adjusted_amount_exchange_rate = amount / exchange_rate;
	var adjusted_amount_exchange_rate_rounded = adjusted_amount_exchange_rate.toFixed(0);

	var price_level_index = 1 / (ppp * exchange_rate);
	
	var origin_country_currency = countries[origin_idx][2];
	var destination_country_currency = countries[destination_idx][2];
	var basket_name = basket_select.value;

	var origin_country_name = origin_select.value;
	var destination_country_name = destination_select.value;
	var year = year_select.value;

        ppp_amount_element.innerHTML = `${adjusted_amount_ppp_rounded} ${destination_country_currency}`;
        xr_amount_element.innerHTML = `${adjusted_amount_exchange_rate_rounded} ${destination_country_currency}`;

	interpretation_element.innerHTML = `<p>PPPs give a rounded estimation of the real purchasing power of a country's currency relative to another country's currency. In this case, an amount of ${amount} ${origin_country_currency} is equivalent to ${adjusted_amount_ppp_rounded} ${destination_country_currency} in PPP terms in contrast to ${adjusted_amount_exchange_rate_rounded} ${destination_country_currency} when converted using the market exchange rate.</p><p style="margin: 0"><i>In this conversion, the PPP estimation applies for the reference year ${year} at the level of ${basket_name}.</i></p>`;

        results_element.style.display = "block";
        results_element.scrollIntoView(true);
}
