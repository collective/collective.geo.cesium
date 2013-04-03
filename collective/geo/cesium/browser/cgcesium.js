<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"
    lang="en"
    xmlns:tal="http://xml.zope.org/namespaces/tal"
    xmlns:i18n="http://xml.zope.org/namespaces/i18n"
    tal:omit-tag="">
<script tal:omit-tag="">
/*<![CDATA[*/
$(window).bind("load", function(){
    // Create canvas element using jQuery:
    $('<canvas/>', {
        'id': 'glCanvas',
        'class': 'cesium-fullsize'
    }).appendTo('#cesiumContainer');

    var canvas = $('#glCanvas')[0];
    try {
        var scene = new Cesium.Scene(canvas);
        var primitives = scene.getPrimitives();
    } catch(e) {

        // display an error message
        $("#loadingOverlay h1").text('Error initializing WebGL');
        $('#cesiumContainer').hide();
        return false
    };

    scene.skyAtmosphere = new Cesium.SkyAtmosphere();
    var ellipsoid = Cesium.Ellipsoid.WGS84;
    var centralBody = new Cesium.CentralBody(ellipsoid);
    %(baselayerjs)s
    primitives.setCentralBody(centralBody);
    var numBaseLayers = centralBody.getImageryLayers().getLength();

    if (numBaseLayers>1){
        for (var i=1; i<numBaseLayers; ++i){
            centralBody.getImageryLayers().get(i).show = false;
        };
    };
    var has_visualizers = false;
    %(maplayerjs)s
    var transitioner = new Cesium.SceneTransitioner(scene, ellipsoid);
    // Prevent right-click from opening a context menu.
    canvas.oncontextmenu = function() {
        return false;
    };

    function animate() {
        // INSERT CODE HERE to update primitives based on changes to animation time, camera parameters, etc.
        if (has_visualizers) {
            // Construct a Julian date specifying the UTC time standard
            var date = new Date();
            var julianDate = Cesium.JulianDate.fromDate(date, Cesium.TimeStandard.UTC);
            visualizers.update(julianDate);
        };
    };

    function tick() {
        scene.initializeFrame();
        animate();
        scene.render();
        Cesium.requestAnimationFrame(tick);
    };
    tick();
    ///////////////////////////////////////////////////////////////////////////
    // Example resize handler

    var onResize = function() {
        var width = canvas.clientWidth;
        var height = canvas.clientHeight;

        if (canvas.width === width && canvas.height === height) {
            return;
        }

        canvas.width = width;
        canvas.height = height;
        scene.getCamera().frustum.aspectRatio = width / height;
    };
    window.addEventListener('resize', onResize, false);
    onResize();

    $('#loadingOverlay').hide()

    function onBaseLayerOptionChange() {
        if (numBaseLayers>1){
            for (var i=0; i<numBaseLayers; ++i){
                if (i != $(this).val()) {
                    centralBody.getImageryLayers().get(i).show = false;
                } else {
                    centralBody.getImageryLayers().get(i).show = true;
                }
            };
        };
    };

    $("#baselayerchoser").find("input").each(function(i) {
        $(this).change(onBaseLayerOptionChange);
    });

    function onMapLayerOptionChange() {
        var is_visible = $(this).is(':checked');
        i = numBaseLayers + parseInt($(this).val());
        centralBody.getImageryLayers().get(i).show = is_visible;
    };

    $("#maplayerchoser").find("input").each(function(i) {
        $(this).change(onMapLayerOptionChange);
    });

})
/*]]*/
</script>
</html>
