
function tableFresh(columns, urls, pk){
    $('table').bootstrapTable({
        url:urls,    //请求后台的URL（*）
        method: 'GET',   //请求方式（*）
        dataType: "json",
        uniqueId: pk,
        striped: true, //间隔行颜色
        cache: false,
        sortName: pk,
        sortable: true,
        sortOrder: 'desc',
        sidePagination: "server",
        undefinedText: '--',
        singleSelect: false,
        toolbar: '#soft-toolbar',
        search: false,
        strictSearch: true,
        clickToSelect: true,
        pagination: true,
        pageNumber: 1,
        pageSize: 20,
        pageList: [20, 50, 100],
        paginationPreText: "上一页",
        paginationNextText: "下一页",
        queryParamsType: "",
        queryParams : function (params){
            var temp = {
                pageSize : params.pageSize,
                pageNumber : params.pageNumber,
                searchText: params.searchText,
                sortName: params.sortName,
                sortOrder: params.sortOrder,
                search_kw: $('#search_keyword').val(), // 请求时向服务端传递的参数
            };
            return temp;
        },
        columns: columns,
        onLoadSuccess: function(data) {
            },
        onLoadError: function () {
            toastr.error("数据加载失败！", "错误提示");
        },
        onClickRow: function (row, $element) {
            //    EditViewById(id, 'view');
        }
    });
}

function tableFresh2(columns, urls, pk){
    $('table').bootstrapTable({
        url:urls,    //请求后台的URL（*）
        method: 'GET',   //请求方式（*）
        dataType: "json",
        uniqueId: pk,
        striped: true, //间隔行颜色
        cache: false,
        sortName: pk,
        sortable: true,
        sortOrder: 'desc',
        sidePagination: "server",
        undefinedText: '--',
        singleSelect: false,
        toolbar: '#soft-toolbar',
        search: false,
        strictSearch: true,
        clickToSelect: true,
        pagination: false,
        pageNumber: 1,
        pageSize: 20,
        pageList: [20, 50, 100],
        paginationPreText: "上一页",
        paginationNextText: "下一页",
        queryParamsType: "",
        queryParams : function (params){
            var temp = {
                // pageSize : params.pageSize,
                // pageNumber : params.pageNumber,
                // searchText: params.searchText,
                // sortName: params.sortName,
                // sortOrder: params.sortOrder,
                erp_no: $('#erpInput').val(), // 请求时向服务端传递的参数
                batch_num:$('#batchInput').val(),
            };
            return temp;
        },
        columns: columns,
        onLoadSuccess: function(data) {
            },
        onLoadError: function () {
            toastr.error('Error')
        },
        onClickRow: function (row, $element) {
            //    EditViewById(id, 'view');
        }
    });
}

// 搜索查询按钮触发事件
$(function() {
    $("#search_button").click(function () {
        $('table').bootstrapTable(('refresh')); // 很重要的一步，刷新url！
    })
});

// 重置按钮触发事件
function clean(){
                //先清空
                $('#search_keyword').val('');
                //清空后查询条件为空了，再次刷新页面，就是全部数据了
                $('table').bootstrapTable(('refresh')); // 很重要的一步，刷新url！
            }

function deleteconfirm(data) {
    var tmp = confirm("确认删除？")
    if(tmp === true){
        if(data.id === undefined){
            num = data.num;
        }else{
            num = data.id;
        }
        var data1 = {};
        data1.id = num;
        $.ajax({
            type: "POST",
            url: data.url,
            headers:{"X-CSRFToken":$.cookie("csrftoken")},
            data: data1,
            dataType: "json",

            success: function (data) {
                if (data.ret) {
                    toastr.success("数据删除成功！");
                    $('table').bootstrapTable('refresh');
                }else {
                    toastr.error("数据删除失败！");
                }
            },
            error: function (data) {
                toastr.error("数据删除失败！");
            }
        });   
    }
}