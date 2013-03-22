import json
import urllib, urllib2
import urlparse
from zope.interface import implements, Interface
from zope.component import getUtility

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from plone.registry.interfaces import IRegistry
from collective.geo.settings.interfaces import IGeoSettings

layer_map= {
'osm':
{'title': 'Open Street Map', 'js':"""
var osm = new Cesium.OpenStreetMapImageryProvider({
    url : 'http://tile.openstreetmap.org/'
});
centralBody.getImageryLayers().addImageryProvider(osm);
"""},
'bing_aer':
{'title': 'Bing Satellite', 'js':"""
var bing_aerial = new Cesium.BingMapsImageryProvider({
    url : 'http://dev.virtualearth.net',
    mapStyle : Cesium.BingMapsStyle.AERIAL,
    key: '%(bing_api_key)s'
    // Some versions of Safari support WebGL, but don't correctly implement
    // cross-origin image loading, so we need to load Bing imagery using a proxy.
    //proxy : Cesium.FeatureDetection.supportsCrossOriginImagery() ? undefined : new Cesium.DefaultProxy('/proxy/')
});
centralBody.getImageryLayers().addImageryProvider(bing_aerial);
"""},
'bing_rod' :
{'title': 'Bing Map', 'js':"""
var bing_road = new Cesium.BingMapsImageryProvider({
    url : 'http://dev.virtualearth.net',
    mapStyle : Cesium.BingMapsStyle.ROAD,
    key: '%(bing_api_key)s'
});
centralBody.getImageryLayers().addImageryProvider(bing_road);
"""},
'bing_hyb':
{'title': 'Bing Hybrid', 'js':"""
var bing_hybrid = new Cesium.BingMapsImageryProvider({
    url : 'http://dev.virtualearth.net',
    mapStyle : Cesium.BingMapsStyle.AERIAL_WITH_LABELS,
    key: '%(bing_api_key)s'
});
centralBody.getImageryLayers().addImageryProvider(bing_hybrid);
"""},
'wms_base':
    {'title': 'WMS', 'js': """
var %(name)s = new Cesium.WebMapServiceImageryProvider({
    url: '%(url)s',
    layers : %(layer)s,
    extent : new Cesium.Extent(
        Cesium.Math.toRadians(%(west)f),
        Cesium.Math.toRadians(%(south)f),
        Cesium.Math.toRadians(%(east)f),
        Cesium.Math.toRadians(%(north)f)),
    proxy: new Cesium.DefaultProxy('%(proxy)s')
});
centralBody.getImageryLayers().addImageryProvider(%(name)s);
//%(name)s.alpha = %(transparancy).1f;
"""},
'wms_overlay':
    {'title': 'WMS', 'js': """
var %(name)s = new Cesium.WebMapServiceImageryProvider({
    url: '%(url)s',
    layers : %(layer)s,
    extent : new Cesium.Extent(
        Cesium.Math.toRadians(%(west)f),
        Cesium.Math.toRadians(%(south)f),
        Cesium.Math.toRadians(%(east)f),
        Cesium.Math.toRadians(%(north)f)),
    parameters:{
        transparent: 'true',
        format: 'image/%(format)s'
    },
    proxy: new Cesium.DefaultProxy('%(proxy)s')
});
%(name)s.alpha = %(transparancy).1f;
centralBody.getImageryLayers().addImageryProvider(%(name)s);
"""},

'tms_base':
    {'title': 'TMS', 'js': """
var %(name)s = new Cesium.TileMapServiceImageryProvider({
    url: '%(url)s',
    fileExtension : %(format)s,
    extent : new Cesium.Extent(
        Cesium.Math.toRadians(%(west)f),
        Cesium.Math.toRadians(%(south)f),
        Cesium.Math.toRadians(%(east)f),
        Cesium.Math.toRadians(%(north)f)),
    proxy: new Cesium.DefaultProxy('%(proxy)s')
});
centralBody.getImageryLayers().addImageryProvider(%(name)s);
//%(name)s.alpha = %(transparancy).1f;
"""},
'tms_overlay':
    {'title': 'TMS', 'js': """
var %(name)s = new Cesium.TileMapServiceImageryProvider({
    url: '%(url)s',
    fileExtension : %(format)s,
    extent : new Cesium.Extent(
        Cesium.Math.toRadians(%(west)f),
        Cesium.Math.toRadians(%(south)f),
        Cesium.Math.toRadians(%(east)f),
        Cesium.Math.toRadians(%(north)f)),
    proxy: new Cesium.DefaultProxy('%(proxy)s')
});
centralBody.getImageryLayers().addImageryProvider(%(name)s);
%(name)s.alpha = %(transparancy).1f;
"""},



}



class ICesiumTestView(Interface):
    """
    cesium test view interface
    """

class CesiumTestView(BrowserView):
    """
    browser view to display a cesium globe map
    """
    implements(ICesiumTestView)


    js_template = template = ViewPageTemplateFile('cgcesium.js')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()


    def get_baselayers(self):
        default_layers = self.geo_settings.default_layers
        params = {'bing_api_key': self.geo_settings.bingapi}
        layers =[]
        for layer in default_layers:
            if layer in layer_map:
                layers.append({'js':layer_map[layer]['js'] % params,
                                'title': layer_map[layer]['title']})
        if len(layers) ==0:
            layers.append(layer_map['osm'])
        return layers

    def get_js(self):
        layers = self.get_baselayers()
        return self.js_template() % {'baselayerjs': ''.join([l['js'] for l in layers]),
                                    'maplayerjs': ''}


    @property
    def geo_settings(self):
        return getUtility(IRegistry).forInterface(IGeoSettings)

class ICesiumWMSView(Interface):
    """ """

class CesiumWMSView(CesiumTestView):
    implements(ICesiumWMSView)

    def get_baselayers(self):
        layers = []
        params = {'name': 'wms_baselayer',
            'url': self.context.server.to_object.remote_url,
            'west':-180, 'south':-90, 'east':180, 'north':90,
            'transparancy': self.context.opacity,
            'format': self.context.img_format,
            'proxy': self.context.server.to_object.absolute_url() +'/@@cesium_imagery_proxy'}
        if self.context.baselayer:
            if self.context.singlelayers:
                wms = self.context.server.to_object.get_service()
                params['layer'] = "'" + self.context.layers[0] + "'"
                title = wms.contents[self.context.layers[0]].title
                params['west']=wms.contents[self.context.layers[0]].boundingBoxWGS84[0]
                params['south']=wms.contents[self.context.layers[0]].boundingBoxWGS84[1]
                params['east']=wms.contents[self.context.layers[0]].boundingBoxWGS84[2]
                params['north']=wms.contents[self.context.layers[0]].boundingBoxWGS84[3]
            else:
                params['layer'] = json.dumps(self.context.layers)
                title = self.context.Title()
            layers.append({'js':layer_map['wms_base']['js'] % params,
                                'title': title})

        layers += super(CesiumWMSView, self).get_baselayers()
        return layers


    def get_maplayers(self):
        layers = []
        params = {'name': 'wms_layer',
            'url': self.context.server.to_object.remote_url,
            'west':-180, 'south':-90, 'east':180, 'north':90,
            'transparancy': self.context.opacity,
            'format': self.context.img_format,
            'proxy': self.context.server.to_object.absolute_url() +'/@@cesium_imagery_proxy'}
        if self.context.baselayer:
            if self.context.singlelayers:
                wms = self.context.server.to_object.get_service()
                for layer in self.context.layers[1:]:
                    params['layer'] = "'" + layer + "'"
                    title = wms.contents[layer].title
                    params['west']=wms.contents[layer].boundingBoxWGS84[0]
                    params['south']=wms.contents[layer].boundingBoxWGS84[1]
                    params['east']=wms.contents[layer].boundingBoxWGS84[2]
                    params['north']=wms.contents[layer].boundingBoxWGS84[3]
                    params['name']='wms_layer' #XXX
                    layers.append({'js':layer_map['wms_overlay']['js'] % params,
                                'title': title})
            else:
                return []
        else:
            if self.context.singlelayers:
                wms = self.context.server.to_object.get_service()
                for layer in self.context.layers:
                    params['layer'] = "'" +  + "'"
                    title = wms.contents[layer].title
                    params['west']=wms.contents[layer].boundingBoxWGS84[0]
                    params['south']=wms.contents[layer].boundingBoxWGS84[1]
                    params['east']=wms.contents[layer].boundingBoxWGS84[2]
                    params['north']=wms.contents[layer].boundingBoxWGS84[3]
                    layers.append({'js':layer_map['wms_overlay']['js'] % params,
                                'title': title})
            else:
                params['layer'] = json.dumps(self.context.layers)
                title = self.context.Title()
                layers.append({'js':layer_map['wms_overlay']['js'] % params,
                                'title': title})
        return layers



    def get_js(self):
        baselayers = self.get_baselayers()
        maplayers = self.get_maplayers()
        return self.js_template() % {'baselayerjs': ''.join([l['js'] for l in baselayers]),
                                    'maplayerjs': ''.join([l['js'] for l in maplayers])}

class ICesiumCZMLView(Interface):
    """ """

class CesiumCZMLView(CesiumTestView):
    implements(ICesiumCZMLView)


    def get_maplayers(self):
        layers = []
        js = """
        //Create a DynamicObjectCollection for handling the CZML
        var dynamicObjectCollection = new Cesium.DynamicObjectCollection();
        //Create the standard CZML visualizer collection
        var visualizers = Cesium.VisualizerCollection.createCzmlStandardCollection(scene, dynamicObjectCollection);
        var url = '%(url)s/@@czml.json';
        //Download and parse a CZML file
        Cesium.loadJson(url).then(function(czml) {
            Cesium.processCzml(czml, dynamicObjectCollection, url);
        });
        //Figure out the time span of the data
        // XXX needed? var availability = dynamicObjectCollection.computeAvailability();
        //Create a Clock object to drive time.
        /* do i need this ????
        var clock = new Cesium.Clock(availability.start, availability.stop);
        visualizers.update(clock.tick());
        */
        """ % {'url': self.context.absolute_url() }
        layers.append({'js':js,
                       'title': self.context.Title()})
        return layers

    def get_js(self):
        baselayers = self.get_baselayers()
        maplayers = self.get_maplayers()
        return self.js_template() % {'baselayerjs': ''.join([l['js'] for l in baselayers]),
                                    'maplayerjs': ''.join([l['js'] for l in maplayers])}


class ImageProxy(BrowserView):
    ALLOWED_CONTENT_TYPES = (
    "image/png",
    "image/jpeg",
    "image/gif",
    "image/tiff",
    "image/jpg",
    )


    def __call__(self):
        url = urllib.unquote(self.request.form.keys()[0])
        urlobj = urlparse.urlparse(url)
        if urlobj.scheme not in ['http', 'https']:
            logger.error('Invalid protocol %s' % urlobj.scheme)
            return
        if not urlobj.hostname:
            return
        baseurl = urlparse.urlunparse([urlobj.scheme, urlobj.netloc,
                    urlobj.path, None, None, None])
        if self.context.remote_url == baseurl:
            o = urllib.urlopen(url)
            if o.headers.type in self.ALLOWED_CONTENT_TYPES:
                data = o.read()
                return data
            else:
                logger.error('Response of type "%s" not allowed' %
                    o.headers.type)
        else:
            logger.error('URL: %s not allowed' % baseurl)

