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
		// console.log('Nav: '+$('.navbar').height())
		// console.log('page head: '+$('.page-head').height())
		// console.log('page form: '+$('.page-form').height())
		// console.log('Dt Header: '+$('.dt-header').height())

        // console.log('window: '+wh)
		// console.log(topPosition)
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
