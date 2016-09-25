//Toggle sliding sidebar
$("#menu-toggle").click(function(e) {
    e.preventDefault();
    $("#wrapper").toggleClass("toggled");
});

//toggle colour switching of checkmark
//and toggle dropdown menu for team selection
$(".glyph-check").click(function() {
    $( this ).toggleClass( "highlight" );
    $(".team-form").toggleClass("form-hidden");
});

//slidey Oscar the Grouch Data Loader
$("#data-submitter").click(function() {
    oscar = $("#oscar-the-loader");

    //oscar is hidden to start, unhide on click
    oscar.toggleClass( "hide-oscar" );
    console.log('fire1');
    //when submit button is clicked, activate oscar-the-grouch loader
    oscar.slideUp( 'slow', function() {
        console.log('fire2');
        oscar.fadeOut('slow').delay( 4000, function() {
            console.log('fire3?');
            //delay a few seconds to load, and hide again.
            oscar.toggleClass( "hide-oscar" );
        });
    });

    //
});
