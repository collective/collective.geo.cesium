from zope.interface import implements, Interface

from Products.Five import BrowserView

class ICesiumTestView(Interface):
    """
    File Kml view interface
    """

class CesiumTestView(BrowserView):
    """
    browser view to display a map for a kml file
    """
    implements(ICesiumTestView)
