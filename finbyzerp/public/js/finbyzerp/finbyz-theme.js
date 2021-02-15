$(window).on("load resize scroll",function(){
    setTimeout(function(){
		
        var wh = $(window).height();
		var topPosition = wh - $('.page-form').height()
		// console.log('Nav: '+$('.navbar').height())
		// console.log('page head: '+$('.page-head').height())
		// console.log('page form: '+$('.page-form').height())
		// console.log('Dt Header: '+$('.dt-header').height())

		// console.log('window: '+wh)
        // console.log('window: '+wh)
        // console.log(wh)
        // console.log(topPosition)
        let final = topPosition - 200
		// console.log(final)
		$('.dt-scrollable').height(final)
		//$('.dt-scrollable').css('height','500px');
	 },10);
});
$('.dt-scrollable').ready(function(){
	
	setTimeout(function(){
        var wh = $(window).height();
		var topPosition = wh - $('.page-form').height();
	
		var final = topPosition - 200
		// console.log(final)
		// console.log($('.dt-scrollable'))
		// console.log($('.page-form').height())
		//$('.dt-scrollable').height(final)
		$('.dt-scrollable').attr('style', 'height: 100px !important');
		//$('.dt-scrollable').css('height','500');
	},10);
	
});

frappe.ui.form.setup_user_image_event = function(frm) {
	
	// bind click on image_wrapper
	frm.sidebar.image_wrapper.on('click', '.sidebar-image-change, .sidebar-image-remove', function(e) {
		let $target = $(e.currentTarget);
		var field = frm.get_field(frm.meta.image_field);
		if ($target.is('.sidebar-image-change')) {
			if(!field.$input) {
				field.make_input();
			}
			if ($(".form-sidebar.overlay-sidebar").hasClass("opened")) {
				$(".form-sidebar.overlay-sidebar").removeClass("opened");
			}
			field.$input.trigger('click');
		} else {
			/// on remove event for a sidebar image wrapper remove attach file.
			frm.attachments.remove_attachment_by_filename(frm.doc[frm.meta.image_field], function() {
				field.set_value('').then(() => frm.save());
			});
		}

	});
	
}

frappe.provide("frappe.ui.toolbar");
frappe.provide('frappe.search');

frappe.ui.toolbar.Toolbar = Class.extend({
	init: function() {
		$('header').append(frappe.render_template("navbar", {
			avatar: frappe.avatar(frappe.session.user)
		}));
		$('.dropdown-toggle').dropdown();

		let awesome_bar = new frappe.search.AwesomeBar();
		awesome_bar.setup("#navbar-search");
		awesome_bar.setup("#modal-search");

		this.setup_notifications();
		this.make();
	},

	make: function() {
		this.setup_sidebar();
		this.setup_help();

		this.bind_events();

		$(document).trigger('toolbar_setup');
	},

	bind_events: function() {
		// clear all custom menus on page change
		$(document).on("page-change", function() {
			$("header .navbar .custom-menu").remove();
		});

		//focus search-modal on show in mobile view
		$('#search-modal').on('shown.bs.modal', function() {
			var search_modal = $(this);
			setTimeout(function() {
				search_modal.find('#modal-search').focus();
			}, 300);
		});
		$('.navbar-toggle-full-width').click(() => {
			frappe.ui.toolbar.toggle_full_width();
		});
		
		$('.navbar-pin').click(() => {
			toggle_sidebar()
		});
		// frappe.ui.keys.add_shortcut({
		// 	shortcut: 'Ctrl+K',
		// 	action: () => toggle_sidebar()
		// })
	},

	setup_sidebar: function() {
		var header = $('header');
		header.find(".toggle-sidebar").on("click", function() {
			var layout_side_section = $('.layout-side-section');
			var overlay_sidebar = layout_side_section.find('.overlay-sidebar');

			overlay_sidebar.addClass('opened');
			overlay_sidebar.find('.reports-dropdown')
				.removeClass('dropdown-menu')
				.addClass('list-unstyled');
			overlay_sidebar.find('.dropdown-toggle')
				.addClass('text-muted').find('.caret')
				.addClass('hidden-xs hidden-sm');

			$('<div class="close-sidebar">').hide().appendTo(layout_side_section).fadeIn();

			var scroll_container = $('html');
			scroll_container.css("overflow-y", "hidden");

			layout_side_section.find(".close-sidebar").on('click', close_sidebar);
			layout_side_section.on("click", "a:not(.dropdown-toggle)", close_sidebar);

			function close_sidebar(e) {
				scroll_container.css("overflow-y", "");

				layout_side_section.find("div.close-sidebar").fadeOut(function() {
					overlay_sidebar.removeClass('opened')
						.find('.dropdown-toggle')
						.removeClass('text-muted');
					overlay_sidebar.find('.reports-dropdown')
						.addClass('dropdown-menu');
				});
			}
		});
	},

	setup_help: function() {
		frappe.provide('frappe.help');
		frappe.help.show_results = show_results;

		this.search = new frappe.search.SearchDialog();
		frappe.provide('frappe.searchdialog');
		frappe.searchdialog.search = this.search;

		$(".dropdown-help .dropdown-toggle").on("click", function() {
			$(".dropdown-help input").focus();
		});

		$(".dropdown-help .dropdown-menu").on("click", "input, button", function(e) {
			e.stopPropagation();
		});

		$("#input-help").on("keydown", function(e) {
			if(e.which == 13) {
				$(this).val("");
			}
		});

		$(document).on("page-change", function () {
			var $help_links = $(".dropdown-help #help-links");
			$help_links.html("");

			var route = frappe.get_route_str();
			var breadcrumbs = route.split("/");

			var links = [];
			for (var i = 0; i < breadcrumbs.length; i++) {
				var r = route.split("/", i + 1);
				var key = r.join("/");
				var help_links = frappe.help.help_links[key] || [];
				links = $.merge(links, help_links);
			}

			if(links.length === 0) {
				$help_links.next().hide();
			} else {
				$help_links.next().show();
			}

			for (var i = 0; i < links.length; i++) {
				var link = links[i];
				var url = link.url;
				$("<a>", {
					href: link.url,
					text: link.label,
					target: "_blank"
				}).appendTo($help_links);
			}

			$('.dropdown-help .dropdown-menu').on('click', 'a', show_results);
		});

		var $result_modal = frappe.get_modal("", "");
		$result_modal.addClass("help-modal");

		$(document).on("click", ".help-modal a", show_results);

		function show_results(e) {
			//edit links
			var href = e.target.href;
			if(href.indexOf('blob') > 0) {
				window.open(href, '_blank');
			}
			var path = $(e.target).attr("data-path");
			if(path) {
				e.preventDefault();
			}
		}
	},

	setup_notifications: function() {
		this.notifications = new frappe.ui.Notifications();
	}

});
// $.extend(frappe.ui.toolbar, {
// 	navpin: function(){
// 		console.log('extented')
// 	}
// });

$(document).ready(function() {
	sidebar_based_on_image()
 });
 frappe.route.on('change', () => {
	sidebar_based_on_image()
 });

function sidebar_based_on_image(){
	$(document.body).addClass('custom-sidebar');
	var route = frappe.get_route();
	var doctype = route[1];
	var route_type = route[0];

	var sidebar_dict = JSON.parse(localStorage.getItem("sidebar_dict", sidebar_dict)) || {};
	// console.log(localStorage.sidebar_dict);
	// if(doctype && route[0] != "List") {
	// 	frappe.db.get_value('DocType',doctype,'image_field',function(r){
	// 		if(r.image_field){
	// 			$(document.body).removeClass('custom-sidebar');
	// 		}
	// 		else{
	// 			$(document.body).addClass('custom-sidebar');
	// 		}
	// 	});		
	// }
	// else{
	// 	$(document.body).addClass('custom-sidebar');
	// }
	if (Object.keys(sidebar_dict).indexOf(doctype)>-1){
		if (sidebar_dict[doctype].indexOf(route_type)>-1){
			$(document.body).toggleClass('custom-sidebar');
		}
	}

}

 function set_sidebar(){
	let sidebar = JSON.parse(localStorage.sidebar || 'false');
	$(document.body).toggleClass('custom-sidebar', sidebar);
}
function toggle_sidebar(){
	var sidebar_dict = JSON.parse(localStorage.getItem("sidebar_dict", sidebar_dict)) || {};

	var route = frappe.get_route();
	var doctype = route[1];
	var route_type = route[0];
	
	if (Object.keys(sidebar_dict).indexOf(doctype)>-1){
		if (sidebar_dict[doctype].indexOf(route_type)>-1){
			sidebar_dict[doctype].splice(sidebar_dict[doctype].indexOf(route_type), 1);
			if (sidebar_dict[doctype].length == 0){
				delete sidebar_dict[doctype];
			}
		}
		else{
			sidebar_dict[doctype].push(route_type)
		}
	}
	else {
		sidebar_dict[doctype] = []
		sidebar_dict[doctype].push(route_type)
	}

	sidebar_dict = JSON.stringify(sidebar_dict);
	
	localStorage.setItem("sidebar_dict", sidebar_dict);
	$(document.body).toggleClass('custom-sidebar');



	// let sidebar = JSON.parse(localStorage.sidebar || 'false');
	// sidebar = !sidebar;
	// localStorage.sidebar = sidebar;
	// set_sidebar()
 }
frappe.ui.keys.add_shortcut({
	description: "Focus on search field",
	shortcut: 'alt+f',
	action: () => {
		let d = document.querySelector("div.page-form.flex > div:nth-child(1)> input")
		if(d){
			d.focus()
		}
	}
})
// frappe.ui.keys.add_shortcut({
// 	description: "Toggle Sidebar",
// 	standard: true,
// 	shortcut: 'Ctrl+k',
// 	action: (e) => { 
// 		console.log('hi')
// 		e.preventDefault();
// 		$(document.body).toggleClass('custom-sidebar');
// 		return false; 
// 	}
// })
frappe.ui.keys.add_shortcut({
	description: "Toggle Sidebar",
	shortcut: 'ctrl+k',
	action: () => {
		toggle_sidebar();
	}
})

