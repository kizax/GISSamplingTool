
from osgeo import gdal, ogr, osr
# import struct, numpy
import os


class looker(object):
    """let you look up pixel value"""

    def __init__(self, tifname='test.tif'):
        """Give name of tif file (or other raster data?)"""

        # open the raster and its spatial reference
        self.ds = gdal.Open(tifname)
        srRaster = osr.SpatialReference(self.ds.GetProjection())

        # get the WGS84 spatial reference
        srPoint = osr.SpatialReference()
        srPoint.ImportFromEPSG(4326) # WGS84

        # coordinate transformation
        self.ct = osr.CoordinateTransformation(srPoint, srRaster)

        # geotranformation and its inverse
        gt = self.ds.GetGeoTransform()
        dev = (gt[1]*gt[5] - gt[2]*gt[4])
        gtinv = ( gt[0] , gt[5]/dev, -gt[2]/dev,
                gt[3], -gt[4]/dev, gt[1]/dev)
        self.gt = gt
        self.gtinv = gtinv

        # band as array
        b = self.ds.GetRasterBand(1)
        self.arr = b.ReadAsArray()

    def lookup(self, lon, lat):
        """look up value at lon, lat"""

        # get coordinate of the raster
        xgeo,ygeo,zgeo = self.ct.TransformPoint(lon, lat, 0)

        # convert it to pixel/line on band
        u = xgeo - self.gtinv[0]
        v = ygeo - self.gtinv[3]
        # FIXME this int() is probably bad idea, there should be
        # half cell size thing needed
        xpix =  int(self.gtinv[1] * u + self.gtinv[2] * v)
        ylin = int(self.gtinv[4] * u + self.gtinv[5] * v)

        # look the value up
        return self.arr[ylin,xpix]


os.system("swtif -p 123batch_swath")


srcTif = "C:/Users/hunter/Desktop/GIS/MOD04_L2.A2011028.0155.051.2011033055902_mod04.tif"
convertedTif = './test2.tif'
siteShp = 'C:/Users/hunter/Desktop/GIS/site/site.shp'

os.system("\"C:/Program Files (x86)/GDAL/gdalwarp.exe\" -overwrite -s_srs EPSG:53008 -t_srs EPSG:3826 -dstnodata -9999 -of GTiff " + srcTif +" "+ convertedTif+"")

src_ds=gdal.Open(convertedTif)
gt=src_ds.GetGeoTransform()
rb=src_ds.GetRasterBand(1)

ds=ogr.Open(siteShp)

layer=ds.GetLayer()
print(layer.GetFeatureCount())

for feature in layer:
    mx = feature.GetFieldAsDouble(6)
    my = feature.GetFieldAsDouble(7)
    print(mx)
    print(my)

    l = looker(convertedTif)
    lon, lat = mx, my
    print l.lookup(lon, lat)




