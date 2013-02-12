from zope.interface import implements, Interface
from zope.component import getUtility

from Products.Five import BrowserView
from plone.registry.interfaces import IRegistry
from collective.geo.settings.interfaces import IGeoSettings

class ICesiumTestView(Interface):
    """
    cesium test view interface
    """

class CesiumTestView(BrowserView):
    """
    browser view to display a cesium globe map
    """
    implements(ICesiumTestView)

    def get_baselayers(self):
        default_layers = self.geo_settings.default_layers
        #import ipdb; ipdb.set_trace()
        return ''


    @property
    def geo_settings(self):
        return getUtility(IRegistry).forInterface(IGeoSettings)


