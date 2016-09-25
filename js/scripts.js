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
    oscar = $(".oscar-the-loader");
    //oscar.toggleClass( ".hide-oscar" );
    oscar.show('slow').delay(800);
    console.log('fired click');
    //when submit button is clicked, activate oscar-the-grouch loader
/*    oscar.slideUp( 400 ).delay( 2000, function() {
        //slide up 100px
        ///$(".oscar-the-loader").delay( 2000, function() {
        //});
        //$(".oscar-the-loader").toggleClass( "hide-oscar" );
        console.log('here?');
        oscar.toggleClass( ".hide-oscar" );

        oscar.delay( 6000, function() {
            console.log('or here?');
            oscar.toggleClass( ".hide-oscar" );
        });
        console.log('how bout here?');
    });*/

    //
});
