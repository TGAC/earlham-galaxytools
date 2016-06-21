<%
    default_title = "Aequatus of"

    # Use root for resource loading.
    root = h.url_for( '/' )
    app_root    = root + "plugins/visualizations/aequatus/static/"
%>
## ----------------------------------------------------------------------------

<!DOCTYPE HTML>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title> ${visualization_name}</title>

## install shared libraries
        ${h.js( 'libs/jquery/jquery',
                'libs/jquery/jquery.migrate',
                'libs/jquery/jquery-ui',
                'libs/bootstrap',
                'libs/d3')}

## aequatus-vis
        ${h.javascript_link( app_root + "aequatus-vis/scripts/init.js" )}
        ${h.javascript_link( app_root + "aequatus-vis/scripts/geneView.js" )}
        ${h.javascript_link( app_root + "aequatus-vis/scripts/drawGene.js" )}
        ${h.javascript_link( app_root + "aequatus-vis/scripts/drawGeneExonOnly.js" )}
        ${h.javascript_link( app_root + "aequatus-vis/scripts/drawCIGARs.js" )}
        ${h.javascript_link( app_root + "aequatus-vis/scripts/util.js" )}
        ${h.javascript_link( app_root + "aequatus-vis/scripts/d3_tree.js" )}
        ${h.javascript_link( app_root + "aequatus-vis/scripts/newick.js" )}


## aequatus plugin script
        ${h.javascript_link( app_root + "controls.js" )}
        ${h.javascript_link( app_root + "popup.js" )}


## external scripts
        ${h.javascript_link( app_root + "aequatus-vis/scripts/scriptaculous/prototype.js" )}
        ${h.javascript_link( app_root + "aequatus-vis/scripts/jquery/js/jquery.svg.js" )}


## external css
        ${h.stylesheet_link( app_root + "aequatus-vis/scripts/jquery/jquery.svg.css" )}
        ${h.stylesheet_link( app_root + "aequatus-vis/styles/font-awesome-4.2.0/css/font-awesome.css" )}
        ${h.stylesheet_link( app_root + "aequatus-vis/styles/style.css" )}

## aequatus css
        ${h.stylesheet_link( app_root + "aequatus.css" )}
       
</head>

## ----------------------------------------------------------------------------
<body style="cursor: auto; height: 100%; position: absolute; width: 100%; z-index: 1999;">

<script type="text/javascript">

        kickOff();

        var hda_id = '${ trans.security.encode_id( hda.id ) }'

        var ajax_url = "${h.url_for( controller='/datasets', action='index')}/" + hda_id + "/display"
        
        var json_result;

        var datasetFetch = jQuery.ajax( {
            url: ajax_url,
            success: function(result){
                var temp  = result;
                json_result = temp;
                start(json_result)
        }});


    function start(json){
        var syntenic_data = json

        init(syntenic_data, "#settings_div")

        drawTree(syntenic_data.tree, "#gene_tree", newpopup)
    }




</script>
<div id="control_panel">
    <table cellspacing="0" cellpadding="0" border="0">
        <tbody>
        <tr valign=top>
            <td width="300px" id=control_divs>

                <div id="settings_div">
                </div>
              
                <div id="info_div">
                    <table width="50%" cellpadding=5px>
                        <tbody>
                        <tr>
                            <td align="left" colspan="2"><b> Tree Legends </b></td>
                        </tr>
                        <tr>
                            <td>
                                <div class="circleBase type2" style="background: rgb(166,206,227);"></div>
                            </td>
                            <td align="left">
                                Duplication
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <div class="circleBase type2" style="background: rgb(31,120,180);"></div>
                            </td>
                            <td align="left">
                                Dubious
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <div class="circleBase type2" style="background: rgb(178,223,138)"></div>
                            </td>
                            <td align="left">
                                Speciation
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <div class="circleBase type2" style="background: rgb(51,160,44)"></div>
                            </td>
                            <td align="left">
                                Gene Split
                            </td>
                        </tr>
                        </tbody>
                    </table>
                </div>
            </td>
            <td width="50px">
                <div id="control_panel_handle">
                    <b> ... </b>
                </div>
                
                <div id="settings_div_handle" onclick="openPanel('#settings_div')" >
                    <i style="color: white;" class="fa fa-cogs fa-3x"></i>
                </div>

                <div id="info_panel_handle" onclick="openPanel('#info_div')">
                    <i style="color: white;" class="fa fa-info fa-3x"></i>
                </div>

                <div id="openclose_handle" onclick="openClosePanel('#settings_div')">
                    <i style="color: white;" class="fa fa-exchange fa-3x"> </i>
                </div>
            </td>
        </tr>
        </tbody>
    </table>
</div>


<div id="canvas">
    <div id="gene_tree">
    </div>
</div>


<div id="popup" class="bubbleleft" >
    <div id="popup_header">
        <div id="stable_id_header">
            <span id="name_label"></span>
            <i onclick="removePopup();" class="fa fa-close "  style="color: white; position: absolute; right: 5px; cursor: pointer; "></i>
        </div>
    </div>
    <div id="popup_body">
        <table width="100%" cellspacing="0" border="0">
            <tbody>
            <tr>
                <td>
                    <div id="ref_name"></div>
                </td>
            </tr>
            <tr>
                <td>
                    <div id="position"></div>
                </td>
            </tr>
            <tr>
                <td>
                    <div id="id_label"></div>
                </td>
            </tr>
            <tr>
                <td>
                    <div id="gene_desc"></div>
                </td>
            </tr>
            <tr align="right">
                <td>
                    <table>
                        <tbody>
                        <tr>
                            <td>
                                <div id="makemetop_button"></div>
                            </td>
                        </tr>
                        </tbody>
                    </table>
                </td>
            </tr>
            </tbody>
        </table>
    </div>

</div>

<span id="ruler"></span>
      
</body>

</html>
