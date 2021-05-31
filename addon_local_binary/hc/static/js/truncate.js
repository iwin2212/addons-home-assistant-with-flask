function AddReadMore() {
    //This limit you can set after how much characters you want to show Read More.
    var carLmt = 50;
    // Text to show when text is collapsed
    var readMoreTxt = " ...";
    // Text to show when text is expanded
    var readLessTxt = " Thu gọn";


    //Traverse all selectors with this class and manupulate HTML part to show Read More
    $(".addReadMore").each(function () {
        if ($(this).find(".firstSec").length)
            return;

        var allstr = $(this).text();
        if (allstr.length > carLmt) {
            var firstSet = allstr.substring(0, carLmt);
            var secdHalf = allstr.substring(carLmt, allstr.length);
            var strtoadd = firstSet + "<span class='SecSec'>" + secdHalf + "</span><span class='readMore'  title='Click to Show More'>" + readMoreTxt + "</span><span class='readLess' title='Click to Show Less'>" + readLessTxt + "</span>";
            $(this).html(strtoadd);
        }

    });
    //Read More and Read Less Click Event binding
    $(document).on("click", ".readMore,.readLess", function () {
        $(this).closest(".addReadMore").toggleClass("showlesscontent showmorecontent");
    });
}
$(function () {
    //Calling function after Page Load
    AddReadMore();
});