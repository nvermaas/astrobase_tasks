import os
import math
import json
from astropy.io import fits
from astropy.io.fits import tabledump
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord, get_constellation
from astropy.coordinates import Angle, Latitude, Longitude  # Angles
from astroquery.simbad import Simbad

import astropy.units as u
from PIL import Image, ImageDraw, ImageFont

def get_world_coordinate_system(path_to_fits_file):

    hdu = fits.open(path_to_fits_file)[0]

    # retrieve some settings from the header
    # First remove the 3rd axis from the header (RGB slices) because WCS works only in 2D.
    my_header = hdu.header
    my_header['NAXIS'] = 2

    ra_reference = my_header['CRVAL1']
    dec_reference = my_header['CRVAL2']
    width = my_header['NAXIS1']
    height = my_header['NAXIS2']
    x_reference_pixel = my_header['CRPIX1']
    y_reference_pixel = my_header['CRPIX1']

    wcs = WCS(my_header, naxis=2)
    return wcs, width, height, ra_reference, dec_reference


def draw_sky_cross(wcs, draw, ra, dec, size=20, width=2, fill=(255, 255, 0), frame='icrs'):
    sky = SkyCoord(Longitude([ra], unit=u.deg),Latitude([dec], unit=u.deg),frame=frame)
    
    x,y = wcs.world_to_pixel(sky)

    # do not draw offscreen
    if x < 0 or y < 0:
        return

    draw.line(((x-size,y), (x+size,y)), fill=fill, width=width)
    draw.line(((x,y-size), (x,y+size)), fill=fill, width=width)


def draw_sky_circle(wcs, draw, ra, dec, size=20, width=2, outline='yellow', fill=None):
    sky = SkyCoord(Longitude([ra], unit=u.deg), Latitude([dec], unit=u.deg), frame='icrs')

    x, y = wcs.world_to_pixel(sky)

    # do not draw offscreen
    if x < 0 or y < 0:
        return

    draw.ellipse(((x - size, y - size), (x + size, y + size)), outline=outline, fill=fill, width=width)


def draw_degree_grid(wcs, draw, scale, ra, dec, ra_labels, dec_labels, step, frame='icrs'):
    sky1 = SkyCoord(Longitude([ra], unit=u.deg),Latitude([dec], unit=u.deg),frame=frame)
    sky2 = SkyCoord(Longitude([ra+step], unit=u.deg), Latitude([dec], unit=u.deg), frame=frame)
    sky3 = SkyCoord(Longitude([ra+step], unit=u.deg),Latitude([dec+step], unit=u.deg),frame=frame)
    sky4 = SkyCoord(Longitude([ra], unit=u.deg), Latitude([dec+step], unit=u.deg), frame=frame)

    x1,y1 = wcs.world_to_pixel(sky1)
    x2,y2 = wcs.world_to_pixel(sky2)
    x3,y3 = wcs.world_to_pixel(sky3)
    x4,y4 = wcs.world_to_pixel(sky4)

    # do not draw offscreen
    if x1<0 and y1<0 and x2<0 and y2<0 and x3<0 and y3<0 and x4<0 and y4<0:
        return

    xy = ((x1, y1), (x2, y2), (x3, y3), (x4, y4), (x1, y1))
    draw.polygon((xy))

    if dec == round(dec_labels):
        a = Angle(ra, u.deg)
        ra_string = a.to_string(unit=u.hour)
        font = ImageFont.truetype("arial.ttf", int(scale/2), encoding="unic")
        draw.text((x1, (y1+y3)/2), str(ra_string), (255, 255, 0),font=font)

    if ra == round(ra_labels):
        dec_string = str(dec)+'deg'
        font = ImageFont.truetype("arial.ttf", int(scale/2), encoding="unic")
        draw.text((x1+10, y1), dec_string, (255, 255, 0),font=font)


def draw_minutes_grid(wcs, draw, scale, ra, dec, ra_labels, dec_labels, step, frame='icrs'):
    sky1 = SkyCoord(Longitude([ra], unit=u.deg), Latitude([dec], unit=u.deg), frame=frame)
    sky2 = SkyCoord(Longitude([ra + step], unit=u.deg), Latitude([dec], unit=u.deg), frame=frame)
    sky3 = SkyCoord(Longitude([ra + step], unit=u.deg), Latitude([dec + step], unit=u.deg), frame=frame)
    sky4 = SkyCoord(Longitude([ra], unit=u.deg), Latitude([dec + step], unit=u.deg), frame=frame)

    x1, y1 = wcs.world_to_pixel(sky1)
    x2, y2 = wcs.world_to_pixel(sky2)
    x3, y3 = wcs.world_to_pixel(sky3)
    x4, y4 = wcs.world_to_pixel(sky4)

    # do not draw offscreen
    if x1<0 and y1<0 and x2<0 and y2<0 and x3<0 and y3<0 and x4<0 and y4<0:
        return

    xy = ((x1, y1), (x2, y2), (x3, y3), (x4, y4), (x1, y1))
    draw.polygon((xy))

    if dec == round(dec_labels):
        a = Angle(ra, u.deg)
        ra_string = a.to_string(unit=u.hour)
        font = ImageFont.truetype("arial.ttf", int(scale/2), encoding="unic")
        draw.text((x1, (y1+y3)/2), str(ra_string), (255, 255, 0),font=font)

    if ra == round(ra_labels):
        dec_string = str(dec)+'deg'
        font = ImageFont.truetype("arial.ttf", int(scale/2), encoding="unic")
        draw.text((x1+10, y1), dec_string, (255, 255, 0),font=font)


def draw_grid(path_to_fits_file, path_to_input_image_file, path_to_output_image_file, title, grid_type="degrees"):

    try:
        wcs, width, height, ra_reference, dec_reference = get_world_coordinate_system(path_to_fits_file)

        # use the astropy WCS package to convert pixel to world coordinates
        # https://docs.astropy.org/en/stable/wcs/
        # https://docs.astropy.org/en/stable/wcs/wcsapi.html

        coord = wcs.pixel_to_world(0, 0)
        ra_end = (coord.ra.dms.d) + ((coord.ra.dms.m)/60) + ((coord.ra.dms.s)/3600)
        dec_end = (coord.dec.signed_dms.sign) * ((coord.dec.signed_dms.d) + ((coord.dec.signed_dms.m)/60) + ((coord.dec.signed_dms.s)/3600))

        coord = wcs.pixel_to_world(width, height)
        ra_start = (coord.ra.dms.d) + ((coord.ra.dms.m)/60) + ((coord.ra.dms.s)/3600)
        dec_start = (coord.dec.signed_dms.sign) * ((coord.dec.signed_dms.d) + ((coord.dec.signed_dms.m)/60) + ((coord.dec.signed_dms.s)/3600))

        constellation = coord.get_constellation()

        print('open('+path_to_input_image_file+')')
        im = Image.open(path_to_input_image_file)
        im_new = im.copy()
        draw = ImageDraw.Draw(im_new)

        # scale the font based on the image size
        scale = int(width/ 60)

        try:
            # localhost
            font_title = ImageFont.truetype("arial.ttf", scale * 2, encoding="unic")
            font_subtitle = ImageFont.truetype("arial.ttf", scale, encoding="unic")
        except:
            # production
            font_title = ImageFont.truetype("home/nvermaas/www/astrobase", scale * 2, encoding="unic")
            font_subtitle = ImageFont.truetype("home/nvermaas/www/astrobase", scale, encoding="unic")

        text_start_x = scale * 2
        text_start_y = scale * 2
        line_spacing = int(scale*2*0.7)

        draw.text((text_start_x, text_start_y), title, (255, 255, 255),font=font_title)
        #draw.text((text_start_x, text_start_y), title, (255, 255, 255),font=font_title)
        # draw.text((text_start_x, text_start_y + (2 * scale)), constellation, (255, 255, 255),font=font_subtitle)

        # draw.text((text_start_x, text_start_y + line_spacing*2), title, (255, 255, 255),font=font_subtitle)
        s1 = round(ra_reference,0)
        s2 = round(dec_reference,0)
        location = 'RA,dec = ' + str(s1) + ',' + str(s2)
        draw.text((text_start_x, text_start_y + line_spacing*2), location, (255, 255, 255),font=font_subtitle)

        draw_sky_cross(wcs, draw, s1, s2, int(scale / 2), width=int(scale / 5), fill=(255, 0, 0), frame='icrs')

        # around the pole the decs could be switched
        if dec_start > dec_end:
            ff = dec_start
            dec_start = dec_end
            dec_end = ff

        if ra_start > ra_end:
            ff = ra_start
            ra_start = ra_end
            ra_end = ff

        # find the field-of-view for both RA and dec
        fov_dec = dec_end - dec_start
        fov_ra = ra_end - ra_start
        fov = str(round(fov_ra,1))+', '+str(round(fov_dec,1))
        
        if fov_ra > 15 or fov_dec > 15:
            # for large field of views, increase the space between the grid lines
            # because of polar distortions, just try to draw the full globe.
            step = 10
            x_start = 0
            x_end = 360
            y_start = -90
            y_end = +90
        else:
            # for smaller fov's, take some extra margin to make sure
            # that the grids cover the full image and not show up as single squares
            step = 1
            x_start = int(ra_start) - 6
            x_end =int(ra_end) + 6
            y_start = int(dec_start) - 6
            y_end = int(dec_end) + 6

        for x in range(x_start, x_end, step):
            # print(x)
            for y in range(y_start, y_end, step):
                try:
                    draw_sky_cross(wcs, draw, x, y, int(scale / 5))
                    draw_degree_grid(wcs, draw, scale, x, y, ra_reference, dec_reference, step)
                except:
                    pass

            # save result
        #path_to_new_file = path_to_image_file.replace(".", "_grid.")
        path_to_new_file = path_to_output_image_file

        if grid_type == "equatorial":
            # calculate rotation
            sky1 = SkyCoord(Longitude([ra_reference], unit=u.deg), Latitude([dec_reference], unit=u.deg), frame='icrs')
            sky2 = SkyCoord(Longitude([ra_reference+1], unit=u.deg), Latitude([dec_reference], unit=u.deg), frame='icrs')
            x1, y1 = wcs.world_to_pixel(sky1)
            x2, y2 = wcs.world_to_pixel(sky2)

            dx = x1 - x2
            dy = y2 - y1
            rotation = math.degrees(math.atan(dy/dx))
            im_new = im_new.rotate(-rotation)

            # save result
            path_to_new_file = path_to_input_image_file.replace(".", "_grid_eq.")
            #path_to_new_file = path_to_output_image_file

        print("path_to_new_file = " + path_to_new_file)
        im_new.save(path_to_new_file)
        print("saved")
        im_new.show()

        return path_to_new_file, ra_start,ra_end,dec_start,dec_end, fov


    except Exception as error:
        print(str(error))


def get_min_max_ra_dec(path_to_fits_file):

    try:
        wcs, width, height, _, _ = get_world_coordinate_system(path_to_fits_file)


        coord = wcs.pixel_to_world(0, 0)
        ra_end = (coord.ra.dms.d) + ((coord.ra.dms.m)/60) + ((coord.ra.dms.s)/3600)
        dec_end = (coord.dec.signed_dms.sign) * ((coord.dec.signed_dms.d) + ((coord.dec.signed_dms.m)/60) + ((coord.dec.signed_dms.s)/3600))

        coord = wcs.pixel_to_world(width, height)
        ra_start = (coord.ra.dms.d) + ((coord.ra.dms.m)/60) + ((coord.ra.dms.s)/3600)
        dec_start = (coord.dec.signed_dms.sign) * ((coord.dec.signed_dms.d) + ((coord.dec.signed_dms.m)/60) + ((coord.dec.signed_dms.s)/3600))

        # the image could be upside down
        if dec_start > dec_end:
            ff = dec_start
            dec_start = dec_end
            dec_end = ff

        if ra_start > ra_end:
            ff = ra_start
            ra_start = ra_end
            ra_end = ff

        # find the field-of-view for both RA and dec
        fov_dec = dec_end - dec_start
        fov_ra = ra_end - ra_start
        fov = str(round(fov_ra,1))+', '+str(round(fov_dec,1))

        return ra_start,ra_end,dec_start,dec_end, fov

    except Exception as error:
        print(str(error))


def get_box(path_to_fits_file):

    try:
        wcs, width, height,_,_ = get_world_coordinate_system(path_to_fits_file)

        box = ''

        coord = wcs.pixel_to_world(0, 0)
        x = round(((coord.ra.dms.d) + ((coord.ra.dms.m)/60) + ((coord.ra.dms.s)/3600)),2)
        y = round((coord.dec.signed_dms.sign) * ((coord.dec.signed_dms.d) + ((coord.dec.signed_dms.m)/60) + ((coord.dec.signed_dms.s)/3600)),2)
        box = box + str(x) + ','
        box = box + str(y) + ','

        coord = wcs.pixel_to_world(width, 0)
        x = round(((coord.ra.dms.d) + ((coord.ra.dms.m)/60) + ((coord.ra.dms.s)/3600)),2)
        y = round((coord.dec.signed_dms.sign) * ((coord.dec.signed_dms.d) + ((coord.dec.signed_dms.m)/60) + ((coord.dec.signed_dms.s)/3600)),2)
        box = box + str(x) + ','
        box = box + str(y) + ','

        coord = wcs.pixel_to_world(width, height)
        x = round(((coord.ra.dms.d) + ((coord.ra.dms.m)/60) + ((coord.ra.dms.s)/3600)),2)
        y = round((coord.dec.signed_dms.sign) * ((coord.dec.signed_dms.d) + ((coord.dec.signed_dms.m)/60) + ((coord.dec.signed_dms.s)/3600)),2)
        box = box + str(x) + ','
        box = box + str(y) + ','

        coord = wcs.pixel_to_world(0, height)
        x = round(((coord.ra.dms.d) + ((coord.ra.dms.m)/60) + ((coord.ra.dms.s)/3600)),2)
        y = round((coord.dec.signed_dms.sign) * ((coord.dec.signed_dms.d) + ((coord.dec.signed_dms.m)/60) + ((coord.dec.signed_dms.s)/3600)),2)
        box = box + str(x) + ','
        box = box + str(y)

        return box

    except Exception as error:
        print(str(error))


def draw_star_pixels(draw, x, y, size=20, width=4, fill='yellow'):
    draw.line(((x - size, y), (x + size, y)),fill=fill)
    draw.line(((x, y - size), (x, y + size)),fill=fill)


def draw_magnitude(draw, x, y, scale, magnitude, size=20, width=4, fill='yellow'):
    font_title = ImageFont.truetype("arial.ttf", scale, encoding="unic")
    draw.text((x, y), str(magnitude),fill=fill,font=font_title)


def get_simbad(ra, dec):
    print('get_simbad(' + str(ra)+','+str(dec)+ ')')
    # find an object on this ra, dec (in degrees) and retrieve its magnitude

    result = None
    try:
        # use astroquery to find and object with Simbad
        coords = SkyCoord(ra, dec, unit=(u.deg, u.deg), frame='icrs')

        t = Simbad.query_region(coords, radius='0d0m10s')

        # it is possible to find multiple objects on this location,
        # realistically I should find the brightest one.
        min_flux = 20

        for row in t.iterrows('MAIN_ID'):
            try:
                main_id = row[0].decode(encoding='UTF-8')
            except:
                main_id = row[0]
            print(main_id)

            customSimbad = Simbad()
            customSimbad.add_votable_fields('fluxdata(V)')
            t2 = customSimbad.query_object(main_id)

            for row in t2.iterrows('FLUX_V'):
                r = row[0]
                try:
                    flux = round(row[0],1)
                    print(flux)
                    if flux < min_flux:
                        min_flux = flux
                except:
                    if min_flux == 20:
                        return None
                    else:
                        return min_flux
        if min_flux == 20:
            return None
        else:
            return min_flux

    except Exception as error:
        print(str(error))

    return None


def get_stars(path_to_fits, astrometry_job):
    print('get_stars(' + path_to_fits + ')')

    # determine the filenames
    fits_filename = astrometry_job+"_axy_file.fits"
    image_filename = astrometry_job+"_annotated.jpg"
    wcs_filename = astrometry_job + ".fits"

    path_to_fits_file = os.path.join(path_to_fits, fits_filename)
    path_to_image_file = os.path.join(path_to_fits, image_filename)
    path_to_wcs_file = os.path.join(path_to_fits, wcs_filename)
    path_to_new_file = path_to_image_file.replace(".", "_stars.")

    # open the wcs file with transformation information
    wcs, width, height,_,_ = get_world_coordinate_system(path_to_wcs_file)
    scale = int(width / 60)

    # open datafile with pixel locatoins of the stars
    hdul = fits.open(path_to_fits_file)
    data = hdul[1].data

    # open image file with PIL
    print('open(' + path_to_image_file + ')')
    im = Image.open(path_to_image_file)
    im_new = im.copy()

    draw = ImageDraw.Draw(im_new)

    # parse data
    list = data[:50]
    # print(list)

    max_magnitude = 0
    for fits_record in data:
        x = fits_record.field(0)
        y = fits_record.field(1)

        # convert pixel to world
        coord = wcs.pixel_to_world(x, y)
        ra = (coord.ra.dms.d) + ((coord.ra.dms.m)/60) + ((coord.ra.dms.s)/3600)
        dec = (coord.dec.signed_dms.sign) * ((coord.dec.signed_dms.d) + ((coord.dec.signed_dms.m)/60) + ((coord.dec.signed_dms.s)/3600))

        # try to retrieve the magnitudes from simbad
        magnitude = get_simbad(ra, dec)
        try:
            if magnitude > max_magnitude:
                max_magnitude = magnitude
        except:
            pass

        if magnitude!=None:
            # draw_star_pixels(draw, x, y, int(scale / 2), width=int(scale / 5), fill=(255, 255, 0))
            draw_magnitude(draw, x,y, scale, magnitude)

    # save result
    print("path_to_new_file = " + path_to_new_file)
    im_new.save(path_to_new_file)
    im_new.show()
    return path_to_new_file, max_magnitude


def draw_extra(path_to_fits_file, path_to_input_image_file, path_to_output_image_file, extra):
    try:
        print('draw_extra(' + path_to_fits_file + ')')
        wcs, width, height,_,_ = get_world_coordinate_system(path_to_fits_file)

        im = Image.open(path_to_input_image_file)
        im_new = im.copy()
        draw = ImageDraw.Draw(im_new, 'RGBA')

        try:
            # localhost
            font_title = ImageFont.truetype("arial.ttf", 50, encoding="unic")
            font_ticks = ImageFont.truetype("arial.ttf", 25, encoding="unic")
        except:
            # production
            font_title = ImageFont.truetype("home/nvermaas/www/astrobase", 50, encoding="unic")
            font_ticks = ImageFont.truetype("home/nvermaas/www/astrobase", 25, encoding="unic")

        list_of_symbols = json.loads(extra)
        for symbol in list_of_symbols:
            print(str(symbol))
            ra = symbol['ra']
            dec = symbol['dec']
            size = symbol['size']

            sky = SkyCoord(Longitude([ra], unit=u.deg), Latitude([dec], unit=u.deg))
            x, y = wcs.world_to_pixel(sky)

            if symbol['shape'] == 'cross':
                draw_sky_cross(wcs, draw, ra, dec, size, width=1, fill=symbol['color'], frame='icrs')
                draw.text((x, y+size), symbol['label'], symbol['color'], font=font_ticks)

            if symbol['shape'] == 'circle':
                draw_sky_circle(wcs, draw, ra, dec, size=int(size), width=2, outline=symbol['color'], fill=None)
                draw.text((x-size,y-(size*2)-50), symbol['label'], symbol['color'], font=font_title)

            if symbol['shape'] == 'exoplanet':
                draw_sky_circle(wcs, draw, ra, dec, size=int(size), width=2, outline=symbol['color'], fill=None)
                draw.text((x-size,y-(size*2)-5), symbol['label'], symbol['color'], font=font_ticks)

        # save result
        path_to_new_file = path_to_output_image_file
        im_new.save(path_to_new_file)
        im_new.show()

        return path_to_new_file

    except Exception as error:
        print(str(error))


def image_cutout(path_to_fits_file, path_to_input_image_file, path_to_output_image_file, extra):

    print('image_cutout(' + path_to_fits_file + ')')

    try:
       wcs, width, height, ra_reference, dec_reference = get_world_coordinate_system(path_to_fits_file)
    except:
        raise (Exception("ERROR: " + path_to_fits_file + ' not found'))

    try:
        im = Image.open(path_to_input_image_file)
    except:
        raise (Exception("ERROR: " + path_to_output_image_file + ' not found'))

    im_new = im.copy()
    draw = ImageDraw.Draw(im_new, 'RGBA')

    # do the magic

    # the cone information is in the 'extra' parameters
    extra_parameters = extra.split(',')
    search_ra = float(extra_parameters[0].strip())
    search_dec = float(extra_parameters[1].strip())
    field_of_view = float(extra_parameters[2].strip())
    title = str(extra_parameters[3])
    size_in_pixels = int(extra_parameters[4])

    # cut out a square the size of 'field_of_view'
    ra_left = search_ra + (0.5 * field_of_view)
    ra_right = search_ra - (0.5 * field_of_view)
    dec_top = search_dec + (0.5 * field_of_view)
    dec_bottom = search_dec - (0.5 * field_of_view)

    # get the bounding box and central point in pixels and world coordinates
    sky0 = SkyCoord(Longitude([search_ra], unit=u.deg), Latitude([search_dec], unit=u.deg), frame='icrs')
    sky1 = SkyCoord(Longitude([ra_left], unit=u.deg), Latitude([dec_top], unit=u.deg), frame='icrs')
    sky2 = SkyCoord(Longitude([ra_right], unit=u.deg), Latitude([dec_bottom], unit=u.deg), frame='icrs')
    x0, y0 = wcs.world_to_pixel(sky0)
    x1, y1 = wcs.world_to_pixel(sky1)
    x2, y2 = wcs.world_to_pixel(sky2)

    # calculate radius in pixels using pythagoras
    dx = x2 - x1
    dy = y2 - y1
    d_pixels = math.hypot(dx,dy)

    d_ra = ra_right - ra_left
    d_dec = dec_top - dec_bottom
    d_radec = math.hypot(d_ra,d_dec)

    pixels_per_degree = d_pixels / d_radec
    radius_in_pixels = field_of_view * pixels_per_degree / 2

    # crop the image
    left = int(x0 - radius_in_pixels)
    top = int(y0 - radius_in_pixels)
    right = int(x0 + radius_in_pixels)
    bottom = int(y0 + radius_in_pixels)

    try:
        im_new = im_new.crop((left, top, right, bottom))
    except:
        raise (Exception("ERROR: crop failed for "+path_to_output_image_file))

    # rotate the image
    sky1 = SkyCoord(Longitude([search_ra], unit=u.deg), Latitude([search_dec], unit=u.deg), frame='icrs')
    sky2 = SkyCoord(Longitude([search_ra + 1], unit=u.deg), Latitude([search_dec], unit=u.deg), frame='icrs')
    x1, y1 = wcs.world_to_pixel(sky1)
    x2, y2 = wcs.world_to_pixel(sky2)

    dx = x1 - x2
    dy = y2 - y1
    rotation = math.degrees(math.atan(dy / dx))
    im_new = im_new.rotate(-rotation)

    # resize to a common size
    im_new = im_new.resize((size_in_pixels,size_in_pixels))

    # save result
    os.makedirs(os.path.dirname(path_to_output_image_file), exist_ok=True)
    path_to_new_file = path_to_output_image_file
    im_new.save(path_to_new_file)
    #im_new.show()

    return path_to_new_file


