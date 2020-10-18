var tableCount = 1
function get_table_change_num() {

    index_regex = /(?<=tokens_list-)\d/g

    // get table parent - <li> (since applying .html() to <table> will give <tbody>
    orig_table = $("table[id=tokens_list-0]")
    table = orig_table.clone()

    // table.remove("label[for=tokens_list-0]").remove("input[type=hidden]")
	alert(table.html())
    alert(orig_table.html())
    // put the correct ids into place
        fix = table.html().replace(index_regex, tableCount)
		alert(fix)
        alert(orig_table.html())
    table.html(fix)
    alert(table.html())
    alert(orig_table.html())

    code = `<div><li><h3>Словоформа ${tableCount + 1}</h3><table></table></li></div>`
    new_table = $(code)
    $("table", new_table).attr("id", `tokens_list-${tableCount}`)
        .append(table.html())
//    alert(new_table.html())


	// append our new <li> as a child to <ul> of tokens
    $("ul[id=tokens_list]").append(new_table.html())
    tableCount++
}


// more complex version below

////<script>
//        $(document).ready(function() {
//            var addCount = 1;
//            $("#addNewField").click(function() {
////                var newInput = $("#tokens_list");
////                newInput.append(GetDynamicTextBox("", addCount));
////                $("#tokens_list").append(newInput);
//                var newInput =
//                addCount += 1;
//            });
//        });
//
//        function GetDynamicTextBox(value, addCount) {
////            return '<div>' + 'Subdirectory&nbsp' + addCount + ':&nbsp' +
////            '<input name = "subdir' + addCount + '"type="text" value = "' + value + '" />&nbsp;' +
////            '<input type="button" value="Remove" class="remove" />' + '</div>' ;
//            return '<table>'+
//            '<tbody><tr>'+
//              '<th><label for="tokens_list-"' + addCount + '"-word_form">Словоформа (итл)</label></th>'+
//              '<th><input id="tokens_list-"' + addCount + '"-word_form" name="tokens_list-"' + addCount + '"-word_form" size="40" type="text" value=""></th>'+
//            '</tr>'+
//            '<tr>'+
//              '<th><label for="tokens_list-"' + addCount + '"-gloss">Глосса</label></th>'+
//              '<th><input id="tokens_list-"' + addCount + '"-gloss" name="tokens_list-"' + addCount + '"-gloss" size="40" type="text" value=""></th>'+
//            '</tr>'+
//            '<tr>'+
//             ' <th><label for="tokens_list-"' + addCount + '"-rus_lexeme">Лексема (рус)</label></th>'+
//              '<th><input id="tokens_list-"' + addCount + '"-rus_lexeme" name="tokens_list-"' + addCount + '"-rus_lexeme" size="40" type="text" value=""></th>'+
//            '</tr>' +
//            '<tr>' +
//              '<th><label for="tokens_list-"' + addCount + '"-itl_lexeme">Лексема (итл)</label></th>'+
//              '<th><input id="tokens_list-"' + addCount + "-itl_lexeme" name="tokens_list-" + addCount + '"-itl_lexeme" size="40" type="text" value=""></th>'+
//            '</tr>'+
//          '</tbody></table>';
//        }
//
//        $(function () {
//            $("#addNewField").click(function() {
//                $("#tokens_list").append(GetDynamicTextBox("", addCount));
//
//            });
//
//            $("body").on("click", ".remove", function () {
//                $(this).closest("div").remove();
//                addCount -= 1;
//            });
//        });
////    </script>