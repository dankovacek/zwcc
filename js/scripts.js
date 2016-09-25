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
    //
    // $('#oscar-the-loader').animate({
    //     "transform": "translate(0px,100px)",
    //     "transition": "transform 500ms"
    // });
    $( "#oscar-the-loader" ).animate({ "top": "-=200px" }, 4000, function() {
        $("#oscar-the-loader").delay( 2000 ).fadeOut( "fast", function() {

        });

    });

    //
});
