mapboxgl.accessToken = 'pk.eyJ1IjoiZ2dmaXR6ZyIsImEiOiJjaXRobThsY3QwMjd1MnlvM2dxZ2pmaTZtIn0.n4RmIQ1KVIJF3p8qqWKL4A';

var map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/ggfitzg/cithqq1u9002e2jplddtrzmnb',
    center: [-123.107,49.248], // starting position
    zoom: 10.9 // starting zoom
});


map.on('load', function() {
  map.addSource('cov_localareas', {
    type: 'geojson',
    data: '/data/cov_localareas.geojson'
  });
  map.addLayer({
    id: 'cov_localareas',
    type: 'fill',
    source: 'cov_localareas',
    'source-layer': 'cov_localareas',
    layout: {
      visibility: 'visible'
    },
	paint: {
        'fill-color': {
            property: 'wpc',
            stops: [
            	[0, '#fff5f0'],
                [0.1, '#fee0d2'],
                [0.2, '#fcbba1'],
                [0.3, '#fc9272'],
                [0.4, '#fb6a4a'],
                [0.5, '#ef3b2c'],
                [0.6, '#cb181d'],
                [0.7, '#a50f15'],
                [0.8, '#67000d']
            ]
        },
        'fill-opacity': 0.75,
        'fill-outline-color': '#fff',
    }
    /*
    paint: {
    	'fill-color': 'hsla(188, 100%, 53%, 0.2)',
    	'fill-outline-color': 'hsla(188, 100%, 53%, 1.0)',
    }*/
  });
  map.addLayer({
    id: 'route-hover',
    type: 'fill',
    source: 'cov_localareas',
    layout: {},
    paint: {
        'fill-color': '#000',
        'fill-opacity': 0.2
    },
    filter: ['==', 'name', '']
   });
});


// Create a popup, but don't add it to the map yet.
var popup = new mapboxgl.Popup({
    closeButton: false,
    closeOnClick: false
});


map.on('mousemove', function(e) {
    var features = map.queryRenderedFeatures(e.point, { layers: ['cov_localareas'] });
    // Change the cursor style as a UI indicator.
    map.getCanvas().style.cursor = (features.length) ? 'pointer' : '';

    if (!features.length) {
        popup.remove();
        return;
    }

    if (features.length) {
        map.setFilter("route-hover", ["==", "name", features[0].properties.name]);
    } else {
        map.setFilter("route-hover", ["==", "name", ""]);
    }

    var feature = features[0];
    var poptext = '<p><b>'+feature.properties.name+'</b></p><p>'+feature.properties.wpc+' tonnes per capita</p>';

    popup.setLngLat(e.lngLat)
        .setHTML(poptext)
        .addTo(map);


});

var areaLegendEl = document.getElementById('area-legend');