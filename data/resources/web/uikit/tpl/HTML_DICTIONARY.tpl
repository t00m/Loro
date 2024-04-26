<!DOCTYPE html>
<html lang="en">
<head>
    <title>${var['html']['title']}</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="generator" content="Loro">
    <meta name="description" content="Loro report">
    <meta name="author" content="github.com/t00m/Loro">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="keywords" content="${var['workbook']['stats']['summary']['topics']}, ${var['workbook']['stats']['summary']['subtopics']}" />
    <link rel="icon" type="image/svg+xml" href="${var['html']['favicon']}">
    <link rel="stylesheet" href="${var['html']['uikit']['css']}" />
    <link rel="stylesheet" href="${var['html']['uikit']['css_print']}" />
    <link rel="stylesheet" href="${var['html']['uikit']['datatables']}/dataTables.uikit.css" />
    <script src="${var['html']['uikit']['js']}"></script>
    <script src="${var['html']['uikit']['icon']}"></script>
    <script src="${var['html']['uikit']['datatables']}/jquery-3.5.1.js"></script>
    <script src="${var['html']['uikit']['datatables']}/jquery.dataTables.min.js"></script>
    <script src="${var['html']['uikit']['datatables']}/dataTables.uikit.min.js"></script>
    <script type="text/javascript" class="init">
        $(document).ready(function() {
            $('#datatable').DataTable( {
                dom: "<'bottom'flp><'clear'>i",
                serverSide: false,
                ordering: true,
                searching: true,
                //~ data:           data,
                deferRender:    true,
                scrollY:        400,
                scrollCollapse: false,
                scroller:       false,
                stateSave: false,
                paging:   false,
                info:     true,
                order: [[ 0, "desc" ]]
            } );
        } );
    </script>
</head>
<body>
    <section id="home" class="home-area" style="min-height: max(0px, 100vh);">
        <div class="uk-container">
            <div class="uk-margin-large-top">
                <h1 class="uk-text-center uk-padding-large">${var['html']['title']}</h1>
            </div>
            <div class="uk-grid-divider" uk-grid>
                <div class="uk-width-1-1@m">
                    <table id="datatable" class="uk-table uk-table-small uk-table-hover uk-table-striped uk-text-small" style="width: 100%">
                        <thead class="">
                            <tr class="">
                                <th class=""><span class="uk-text-secondary">Word</span></th>
                                <th class=""><span class="uk-text-secondary">Meaning</span></th>
                            </tr>
                        </thead>
                        <tbody class="">
                                <tr class="">
                                    <td class="">Abend</td>
                                    <td class="">Evening</td>
                                </tr>
                                <tr class="">
                                    <td class="">Nacht</td>
                                    <td class="">Night</td>
                                </tr>
                        </tbody>
                        <tfoot class="">
                        </tfoot>
                    </table>
                </div>
            </div>
        </div>
    </section>
</body>
</html>
