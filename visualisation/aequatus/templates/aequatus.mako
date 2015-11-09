<%
    default_title = "Aequatus of"
   

    # optionally bootstrap data from dprov


    # Use root for resource loading.
    root = h.url_for( '/' )

    history_id = trans.security.encode_id( trans.history.id )
%>
## ----------------------------------------------------------------------------

<!DOCTYPE HTML>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title> ${visualization_name}</title>
<link type="text/css" rel="Stylesheet" media="screen" href="/plugins/visualizations/aequatus/static/aequatus.css"">


<script type="text/javascript" src="/plugins/visualizations/aequatus/static/aequatus-vis/scripts/init.js"></script>
<script type="text/javascript" src="/plugins/visualizations/aequatus/static/scripts/search_compara.js"></script>
<script type="text/javascript" src="/plugins/visualizations/aequatus/static/aequatus-vis/scripts/geneView.js"></script>
<script type="text/javascript" src="/plugins/visualizations/aequatus/static/aequatus-vis/scripts/drawGene.js"></script>
<script type="text/javascript" src="/plugins/visualizations/aequatus/static/aequatus-vis/scripts/drawGeneExonOnly.js"></script>
<script type="text/javascript" src="/plugins/visualizations/aequatus/static/aequatus-vis/scripts/drawCIGARs.js"></script>
<script type="text/javascript" src="/plugins/visualizations/aequatus/static/controls.js"></script>
<script type="text/javascript" src="/plugins/visualizations/aequatus/static/aequatus-vis/scripts/util.js"></script>
<script type="text/javascript" src="/plugins/visualizations/aequatus/static/popup.js"></script>
<script type="text/javascript" src="/plugins/visualizations/aequatus/static/aequatus-vis/scripts/d3_tree.js"></script> 
<script type="text/javascript" src="/plugins/visualizations/aequatus/static/aequatus-vis/scripts/jquery/js/jquery-1.11.2.min.js"></script>
<script type="text/javascript" src="/plugins/visualizations/aequatus/static/aequatus-vis/scripts/jquery/js/jquery.cookie.js"></script>
<script type="text/javascript" src="/plugins/visualizations/aequatus/static/aequatus-vis/scripts/jquery/js/jquery-migrate-1.2.1.min.js"></script>
<script type="text/javascript" src="/plugins/visualizations/aequatus/static/aequatus-vis/scripts/bootstrap-css/bootstrap.js"></script>
<script type="text/javascript" src="/plugins/visualizations/aequatus/static/aequatus-vis/scripts/d3.js/d3.v3.min.js"></script>
<script type="text/javascript" src="/plugins/visualizations/aequatus/static/aequatus-vis/scripts/newick.js"></script>

<script type="text/javascript" src="/plugins/visualizations/aequatus/static/aequatus-vis/scripts/jquery/js/jquery-1.11.2.min.js"></script>
<script type="text/javascript" src="/plugins/visualizations/aequatus/static/aequatus-vis/scripts/jquery/js/jquery-ui-1.11.2.js"></script>
<script type="text/javascript" src="/plugins/visualizations/aequatus/static/aequatus-vis/scripts/jquery/js/jquery.cookie.js"></script>
<script type="text/javascript" src="/plugins/visualizations/aequatus/static/aequatus-vis/scripts/jquery/js/jquery-migrate-1.2.1.min.js"></script>
<script type="text/javascript" src="/plugins/visualizations/aequatus/static/aequatus-vis/scripts/scriptaculous/prototype.js"></script>

<link rel="stylesheet" type="text/css" href="/plugins/visualizations/aequatus/static/aequatus-vis/scripts/jquery/jquery.svg.css">
<script type="text/javascript" src="/plugins/visualizations/aequatus/static/aequatus-vis/scripts/jquery/js/jquery.svg.js"></script>


<link rel="stylesheet" href="/plugins/visualizations/aequatus/static/aequatus-vis/styles/bootstrap-css/bootstrap.css" type="text/css">
<link rel="stylesheet" href="/plugins/visualizations/aequatus/static/aequatus-vis/styles/bootstrap-css/bootstrap-theme.min.css" type="text/css">
<link rel="stylesheet" href="/plugins/visualizations/aequatus/static/aequatus-vis/styles/font-awesome-4.2.0/css/font-awesome.css" type="text/css">

<link rel="stylesheet" href="/plugins/visualizations/aequatus/static/aequatus-vis/scripts/jquery/css/smoothness/jquery-ui-1.11.2.css" type="text/css">
<link rel="stylesheet" href="/plugins/visualizations/aequatus/static/aequatus-vis/styles/style.css" type="text/css">

</head>

## ----------------------------------------------------------------------------
<body style="cursor: auto; height: 100%; position: absolute; width: 100%; z-index: 1999;">

<script>

        console.log("here")

        kickOff();

        var history_id = '${ trans.security.encode_id( trans.history.id ) }'

        var hda_id = '${ trans.security.encode_id( hda.id ) }'

        var json_result;

        var datasetFetch = jQuery.ajax( {
            url: '/api/histories/' + '${ trans.security.encode_id( trans.history.id ) }/contents/' + '${ trans.security.encode_id( hda.id ) }'+ '/display',
            success: function(result){
                var temp  = result;
                json_result = temp;
                start(json_result)
        }});


    function start(json){
        console.log("start")
        var json_obj = json

        console.log(json_obj)
        for (first in json_obj.member) break;
        member_id = first;

        syntenic_data = json_obj;


       // syntenic_data.tree = toNewick(syntenic_data.tree)

        var ref_id = Object.keys(syntenic_data.member)[0]

        console.log(ref_id)
        
        syntenic_data.ref = syntenic_data.member[ref_id].id
        syntenic_data.protein_id = syntenic_data.member[ref_id].Transcript[0].Translation.id

        console.log(syntenic_data.ref)


        member_id = syntenic_data.ref
        init(syntenic_data)


        console.log(member_id)

        drawTree(syntenic_data.tree, "#gene_tree_nj", newpopup)
    }




</script>
<div id="control_panel"
     style="top: 100px;position: fixed; height: auto; left: -300px; z-index: 2999">
    <table cellspacing="0" cellpadding="0" border="0">
        <tbody>
        <tr valign=top>
            <td width="300px" id=control_divs>

                <div id="settings_div"
                     style="padding: 10px; height: 248px; background: none repeat scroll 0% 0% darkcyan; font-size: large;">

                    <div class="checkbox">


                        <table width="75%" cellpadding="2px">
                            <tbody>
                            <tr>
                                <td align="left" colspan="2"><b> Visual Controls </b></td>
                            </tr>
                            <tr>
                                <td align="left">
                                    <label>
                                        <input type="checkbox" onclick="jQuery('.delete').toggle()" checked=""
                                               id="deleteCheck">
                                    </label>

                                    Deletion

                                </td>
                            </tr>
                            <tr>
                                <td>
                                    <label>
                                        <input type="checkbox" onclick="jQuery('.insert').toggle()" checked=""
                                               id="insertCheck">
                                    </label>

                                    Insertion

                                </td>
                            </tr>
                            <tr>
                                <td>
                                    <label> <input type="checkbox" onclick="jQuery('.match').toggle()" checked=""
                                                   id="matchCheck">
                                    </label>

                                    Match

                                </td>
                            </tr>

                            <tr>
                            <tr></tr>

                            <td align="left" colspan="2"><b> Label </b></td>
                            </tr>
                            <tr>
                                <td>
                                    <input type="radio" name="label_type" checked="" value="stable"
                                           onchange=" changeToStable()">
                                    Stable Id
                                </td>
                                <td align="left">
                                    <input type="radio" name="label_type" value="gene_info"
                                           onchange=" changeToGeneInfo()"> Gene Info

                                </td>
                            </tr>

                            <tr>
                                <td align="left" colspan="2"><b> Introns </b></td>
                            </tr>
                            <tr>
                                <td>
                                    <input type="radio" name="view_type" checked="" value="with"
                                           onchange="changeToNormal()">
                                    With
                                </td>
                                <td align="left">
                                    <input type="radio" name="view_type" value="without" onchange="changeToExon()">
                                    Without

                                </td>
                            </tr>
                            <tr>
                                <td>
                                    <div id="filter"></div>
                                </td>
                            </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

              
                <div style="display: none; background: none repeat scroll 0% 0% peru; padding: 10px; height: 248px; text-align: center; font-size: 20px;"
                     id="info_div">
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
                <div style="padding: 5px; text-align: center; cursor: move; background: none repeat scroll 0% 0% slategrey; color: white;"
                     id="control_panel_handle">
                    <b> ... </b>
                </div>
                <div onclick="openPanel('#settings_div')"
                     style="padding: 5px; text-align: center; background: none repeat scroll 0% 0% darkcyan;"><i
                        style="color: white;"
                        class="fa fa-cogs fa-3x"></i>
                </div>
                <div onclick="openPanel('#info_div')"
                     style="padding: 5px; text-align: center; background: none repeat scroll 0% 0% peru;"><i
                        style="color: white;"
                        class="fa fa-info fa-3x"></i>
                </div>
                <div onclick="openClosePanel('#settings_div')"
                     style="padding: 5px; text-align: center;  background: none repeat scroll 0% 0% gray;"><i
                        style="color: white;"
                        class="fa fa-exchange fa-3x"> </i>
                </div>
            </td>
        </tr>
        <tr>
            <td>
                <div id="search_result"
                     style="position: absolute; overflow-y: scroll; height: 500px; overflow: hidden; width:0px; height: 500px; overflow: auto;"></div>
            </td>
        </tr>
        </tbody>
    </table>
</div>


<div id="canvas">

   
    <div id="gene_tree_nj" style=" overflow: visible;   position: relative; top: 50px; width: 100%;">

    </div>
    <div style="height: auto; margin-left: auto; margin-right: auto; z-index: 1999; position: fixed;">


    </div>
</div>

<div id="gene_widget" style='position: relative; display:none'>

</div>
<div id="gene_widget_exons" style='position: relative; top: 100px; display:none'>

</div>
</div>
<div style='display:none'>

    <div id="gene_tree">
        <div id="gene_tree_upgma">

        </div>

    </div>
</div>
<div style='display:none'>

    <div id="gene_info" style=" ">

    </div>
</div>

</div>

<div id="popup" class="bubbleleft" style="width:200px; height:130px;">
    <div style="overflow: hidden; left: 0px; top: 0px; position: relative;">
        <table width="100%" cellspacing="0" border="0">
            <thead>
            <tr>
                <td bgcolor="darkcyan">
                    <div style="color: white; padding: 2px; width: 100%;" id="stable_id_header"><span
                            id="stable_label"></span>
                        <i onclick="removePopup();" class="fa fa-close "
                           style="color: white; position: absolute; right: 5px; cursor: pointer; "></i>
                    </div>
                </td>
            </tr>
            </thead>
        </table>

    </div>
    <div style="position: relative; padding: 5px;">
        <table width=100% cellspacing="0" border="0">
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
                    <div id="gene_desc"></div>
                </td>
            </tr>
            <tr align="right">
                <td align="">
                    <table >
                        <tbody>
                        <tr>
                            <td>
                                <div id="makemetop_button" style="float: right"></div>

                            </td>
                            <td>
                                <div id="ensemblLink" style="float: right"></div>
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

<p style="z-index:10; position:fixed;font-size: small;" id="besideMouse"></p>

<span id="ruler"></span>

      
</body>
