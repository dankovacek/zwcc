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
    //oscar is hidden to start, unhide on click
    //when submit button is clicked, activate oscar-the-grouch loader
    $("#oscar-the-loader").slideUp( 'slow', function() {
/*        $("#oscar-the-loader").fadeOut('slow', function() {
            //delay a few seconds to load, and hide again.
            //$("#oscar-the-loader").toggleClass( "hide-oscar" );
        });*/
    });

    //
});
