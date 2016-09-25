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
    $( "#oscar-the-loader" ).animate({ "top": "-=250px" }, 2500, function() {
        $("#oscar-the-loader").delay( 800 ).fadeOut( "fast", function() {
            $( ".data-upload-status" ).toggleClass( "hide-oscar" );

        });

    });

    //
});

//reset the modal animations when modal is closed
$('.modal').on('hide.bs.modal', function (e) {
    $( "#oscar-the-loader" ).animate({ "top": "+=250px" }, 100);
    $( "#oscar-the-loader" ).toggleClass( "hide-oscar" );
    $( ".data-upload-status" ).toggleClass( "hide-oscar" );
});
